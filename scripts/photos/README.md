# Photo gallery workflow

The source photos stay in `Live/` and are never modified or committed. The
gallery builder creates metadata-free WebP files in `.gallery-build/` and a
small Lektor data bag in `sps20/databags/photos-2026.json`.

## Build the gallery assets

```console
uv run --group photos python scripts/photos/build_gallery.py
```

The output is split by day because GitHub releases support at most 1,000
assets. The 2026 gallery contains two variants per photo:

- `photos-2026-thursday`: 626 assets
- `photos-2026-friday`: 416 assets

Review the generated files and the local website before publishing anything.

## Create and upload the releases

The following commands create public GitHub releases. Run them only after the
generated gallery has been reviewed.

```console
gh release create photos-2026-thursday \
  --title "Swiss Python Summit 2026 photos — Thursday" \
  --notes "Photos: kurzschluss photography gmbh"

gh release upload photos-2026-thursday .gallery-build/thursday/*

gh release create photos-2026-friday \
  --title "Swiss Python Summit 2026 photos — Friday" \
  --notes "Photos: kurzschluss photography gmbh"

gh release upload photos-2026-friday .gallery-build/friday/*
```

If a release already exists, omit its `gh release create` command. Re-running
the builder without `--force` reuses current output files whose source has not
changed.
