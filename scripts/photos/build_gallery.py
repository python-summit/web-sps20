#!/usr/bin/env python3
"""Build one configured year's web-ready photos and Lektor data bag.

Source photos are never modified. Each gallery is described by a small JSON
file so new years and different day structures do not require code changes.
Two metadata-free WebP variants are written to an ignored staging directory
for upload as GitHub release assets.
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from PIL import Image, ImageOps


SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


@dataclass(frozen=True)
class BuildTask:
    source: Path
    output_directory: Path
    year: int
    day_id: str
    day_title: str
    release_tag: str
    repository: str
    index: int
    total: int
    thumb_size: int
    large_size: int
    thumb_quality: int
    large_quality: int
    force: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("scripts/photos/galleries/2026.json"),
        help="Gallery configuration JSON",
    )
    parser.add_argument("--source", type=Path, help="Override source directory")
    parser.add_argument("--output", type=Path, help="Override staging directory")
    parser.add_argument("--manifest", type=Path, help="Override data bag path")
    parser.add_argument("--repository", help="Override GitHub owner/repository")
    parser.add_argument("--thumb-size", type=int, default=640)
    parser.add_argument("--large-size", type=int, default=2400)
    parser.add_argument("--thumb-quality", type=int, default=72)
    parser.add_argument("--large-quality", type=int, default=82)
    parser.add_argument(
        "--workers",
        type=int,
        default=min(8, os.cpu_count() or 1),
        help="Parallel image workers (default: up to 8)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild images even when generated files are newer",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SystemExit(f"Missing gallery config: {path}") from error
    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON in {path}: {error}") from error

    required = ("year", "source", "days", "repository", "credit")
    missing = [key for key in required if key not in config]
    if missing:
        raise SystemExit(f"Missing config keys: {', '.join(missing)}")
    if not isinstance(config["days"], list) or not config["days"]:
        raise SystemExit("Gallery config must contain at least one day.")

    return config


def release_url(repository: str, tag: str, filename: str) -> str:
    return (
        f"https://github.com/{repository}/releases/download/"
        f"{quote(tag)}/{quote(filename)}"
    )


def save_webp(image: Image.Image, destination: Path, quality: int) -> None:
    temporary = destination.with_name(f".{destination.name}.tmp")
    image.save(temporary, "WEBP", quality=quality, method=4)
    temporary.replace(destination)


def build_photo(task: BuildTask) -> dict[str, Any]:
    stem = task.source.stem
    thumb_name = f"{stem}-thumb.webp"
    large_name = f"{stem}-large.webp"
    thumb_path = task.output_directory / thumb_name
    large_path = task.output_directory / large_name
    source_mtime = task.source.stat().st_mtime

    can_reuse = (
        not task.force
        and thumb_path.exists()
        and large_path.exists()
        and thumb_path.stat().st_mtime >= source_mtime
        and large_path.stat().st_mtime >= source_mtime
    )

    if can_reuse:
        with Image.open(large_path) as large:
            width, height = large.size
    else:
        with Image.open(task.source) as source:
            oriented = ImageOps.exif_transpose(source)
            if oriented.mode != "RGB":
                oriented = oriented.convert("RGB")

            large = oriented.copy()
            large.thumbnail(
                (task.large_size, task.large_size), Image.Resampling.LANCZOS
            )
            width, height = large.size
            save_webp(large, large_path, task.large_quality)

            thumb = large.copy()
            thumb.thumbnail(
                (task.thumb_size, task.thumb_size), Image.Resampling.LANCZOS
            )
            save_webp(thumb, thumb_path, task.thumb_quality)

    return {
        "id": stem,
        "width": width,
        "height": height,
        "thumb_url": release_url(
            task.repository, task.release_tag, thumb_name
        ),
        "large_url": release_url(
            task.repository, task.release_tag, large_name
        ),
        "alt": (
            f"Swiss Python Summit {task.year} on {task.day_title}, "
            f"photo {task.index} of {task.total}"
        ),
    }


def discover_photos(directory: Path, prefix: str) -> list[Path]:
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.name.startswith(prefix)
        and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def directory_size(directory: Path) -> int:
    return sum(path.stat().st_size for path in directory.iterdir() if path.is_file())


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    config = load_config(config_path)

    year = int(config["year"])
    source_root = (args.source or Path(config["source"])).resolve()
    output_root = (
        args.output or Path(config.get("output", f".gallery-build/{year}"))
    ).resolve()
    manifest_path = (
        args.manifest
        or Path(config.get("manifest", f"sps20/databags/photos-{year}.json"))
    ).resolve()
    repository = args.repository or str(config["repository"])
    filename_prefix = str(config.get("filename_prefix", "KSP_"))

    if args.thumb_size <= 0 or args.large_size <= 0:
        raise SystemExit("Image sizes must be positive integers.")
    if args.thumb_size > args.large_size:
        raise SystemExit("Thumbnail size must not exceed large image size.")
    if not 1 <= args.thumb_quality <= 100 or not 1 <= args.large_quality <= 100:
        raise SystemExit("WebP quality must be between 1 and 100.")

    credit = config["credit"]
    if not isinstance(credit, dict) or not credit.get("label") or not credit.get("url"):
        raise SystemExit("Credit must contain non-empty label and url values.")

    manifest: dict[str, Any] = {
        "year": year,
        "title": config.get("title", f"Swiss Python Summit {year}"),
        "credit": credit,
        "days": [],
    }

    all_tasks: list[BuildTask] = []
    day_records: dict[str, dict[str, Any]] = {}

    for day in config["days"]:
        try:
            day_id = str(day["id"])
            day_title = str(day["title"])
            source_name = str(day["source"])
        except (KeyError, TypeError) as error:
            raise SystemExit("Each day requires id, title and source values.") from error

        release_tag = str(day.get("release_tag", f"photos-{year}-{day_id}"))
        source_directory = source_root / source_name
        if not source_directory.is_dir():
            raise SystemExit(f"Missing photo directory: {source_directory}")

        photos = discover_photos(source_directory, filename_prefix)
        if not photos:
            raise SystemExit(f"No photos found in: {source_directory}")

        output_directory = output_root / day_id
        output_directory.mkdir(parents=True, exist_ok=True)
        day_record: dict[str, Any] = {
            "id": day_id,
            "title": day_title,
            "release_tag": release_tag,
            "photos": [],
        }
        day_records[day_id] = day_record
        manifest["days"].append(day_record)

        for index, source in enumerate(photos, start=1):
            all_tasks.append(
                BuildTask(
                    source=source,
                    output_directory=output_directory,
                    year=year,
                    day_id=day_id,
                    day_title=day_title,
                    release_tag=release_tag,
                    repository=repository,
                    index=index,
                    total=len(photos),
                    thumb_size=args.thumb_size,
                    large_size=args.large_size,
                    thumb_quality=args.thumb_quality,
                    large_quality=args.large_quality,
                    force=args.force,
                )
            )

    with ProcessPoolExecutor(max_workers=max(1, args.workers)) as executor:
        records = list(executor.map(build_photo, all_tasks))

    for task, record in zip(all_tasks, records, strict=True):
        day_records[task.day_id]["photos"].append(record)

    manifest["total_photos"] = len(all_tasks)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Generated gallery for {year}: {len(all_tasks)} photos")
    for day in manifest["days"]:
        output_directory = output_root / day["id"]
        size_mib = directory_size(output_directory) / (1024 * 1024)
        print(
            f"  {day['title']}: {len(day['photos'])} photos, "
            f"{len(day['photos']) * 2} assets, {size_mib:.1f} MiB, "
            f"release {day['release_tag']}"
        )
    print(f"Manifest: {manifest_path}")
    print(f"Release assets: {output_root}")


if __name__ == "__main__":
    main()
