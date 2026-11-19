# Photo gallery workflow

Photo galleries are separated by year:

- `/photos/` is the automatically generated archive page.
- `/photos/<year>/` is one self-contained gallery.
- `scripts/photos/galleries/<year>.json` configures its source folders,
  release tags, credit and output paths.
- `sps20/databags/photos-<year>.json` is the generated image manifest.

Source photos remain outside Git. They are never modified by the builder.

## Upload photos from a folder on your drive

The workflow has three parts: prepare the photos, upload the generated images
to GitHub releases, then publish the website's gallery manifest. The builder
automates image preparation; it does not create releases or upload files.

Run all commands below from the root of this repository.

### 1. Check the tools and source folder

You need `uv`, the GitHub CLI (`gh`), and permission to create releases in
`python-summit/web-sps20`. Sign in to GitHub if you have not already:

```sh
gh auth login
```

For the existing 2026 configuration, your photo folder should look like this:

```text
/Volumes/My Drive/Summit Photos/
├── Donnerstag/
│   ├── KSP_0001.jpg
│   └── KSP_0002.jpg
└── Freitag/
    ├── KSP_0101.jpg
    └── KSP_0102.jpg
```

Replace `/Volumes/My Drive/Summit Photos` in the next command with the path to
your own folder. Keep the quotes when the path contains spaces. Pass the parent
folder containing `Donnerstag` and `Freitag`, not one of the day folders.

The day folder names come from `days[].source` in
`scripts/photos/galleries/2026.json`. Change those values if your folders have
different names. The builder reads files directly inside each day folder; it
does not search subfolders.

By default, only filenames starting with `KSP_` are included. Supported formats
are JPG, JPEG, PNG, TIF and TIFF (including uppercase extensions). Set
`filename_prefix` to `""` in the configuration to include every supported image.
Within each day, filenames must have unique stems: `photo.jpg` and `photo.png`
would produce the same output names.

### 2. Generate the web images

```sh
uv run --group photos python scripts/photos/build_gallery.py \
  --config scripts/photos/galleries/2026.json \
  --source "/Volumes/My Drive/Summit Photos"
```

The source photos stay on your drive and are not modified or committed to Git.
The command creates:

- `.gallery-build/2026/thursday/`: generated Thursday images.
- `.gallery-build/2026/friday/`: generated Friday images.
- `sps20/databags/photos-2026.json`: the website manifest with image URLs.

Each photo becomes **two release assets**: a thumbnail up to 640 px and a large
image up to 2400 px, both metadata-free WebP files. For example, 300 photos
produce 600 assets. This is expected for the current gallery design. Uploading
only a ZIP will not work: the gallery loads each image through its own URL.

The command prints the photo count, asset count and total size for each day.
Check those counts and open a few generated images before uploading.
Re-running the builder reuses current files unless `--force` is provided.
It does not remove old output files when photos are removed from the source;
review the staging folders before uploading a changed selection.

### 3. Create a release for each day

The release tags must match the configuration and generated manifest exactly.
First check which releases exist:

```sh
gh release list --repo python-summit/web-sps20
```

Run each creation command only if that release is missing. The previous 2026
photo releases were deleted; do not assume they still exist. Creating a release
makes it public in this public repository.

```sh
gh release create photos-2026-thursday \
  --repo python-summit/web-sps20 \
  --title "Swiss Python Summit 2026 photos — Thursday" \
  --notes "Photo: kurzschuss photography gmbh — https://www.instagram.com/kurzschuss_photo/"

gh release create photos-2026-friday \
  --repo python-summit/web-sps20 \
  --title "Swiss Python Summit 2026 photos — Friday" \
  --notes "Photo: kurzschuss photography gmbh — https://www.instagram.com/kurzschuss_photo/"
```

These commands can reuse existing Git tags. If a tag does not exist, GitHub CLI
creates it from the repository's default branch. The original photos do not
need to be in the tagged commit.

### 4. Upload the generated images

Upload the WebP files from the staging folders, rather than the original JPGs
on your drive. The commands below send files in batches of up to 50 and preserve
filenames containing spaces:

```sh
find .gallery-build/2026/thursday -type f -name '*.webp' -print0 | \
  xargs -0 -n 50 gh release upload photos-2026-thursday \
    --repo python-summit/web-sps20

find .gallery-build/2026/friday -type f -name '*.webp' -print0 | \
  xargs -0 -n 50 gh release upload photos-2026-friday \
    --repo python-summit/web-sps20
```

If an upload is interrupted, inspect the release and upload the missing files.
To repeat a whole upload, add `--clobber` to `gh release upload`; this replaces
any existing assets with matching names, so only use it when you intend to
replace those images.

### 5. Preview and publish the gallery

```sh
make serve
```

Open <http://localhost:5000/photos/2026/>. Check both days, thumbnails, and the
large images opened by clicking a photo. Images load from GitHub, so this check
requires the uploads to be complete.

Commit the generated `sps20/databags/photos-2026.json` and any intentional
configuration or gallery page changes through the usual branch and pull request
workflow. The `.gallery-build/` directory is ignored and should not be committed.
The website deploys when the changes reach `main`.

## Add another year

1. Copy `scripts/photos/galleries/2026.json` to the new year and update:
   `year`, `source`, `output`, `manifest`, the photo credit and every day.
2. Arrange your drive folder to match `days[].source`, or update those values
   to match your folders. Set `filename_prefix` to match your image filenames.
3. Run the builder with the new configuration file and `--source` pointing at
   your drive folder, as shown above.
4. Create `sps20/content/photos/<year>/contents.lr` using the
   `photo-gallery` model and point `gallery_bag` at `photos-<year>`.
5. Create one release per configured day and upload the generated WebP files
   from the corresponding staging folder, using the new tags and year.
6. Review the local `/photos/<year>/` page, then commit and publish the manifest,
   configuration and gallery page.

The archive at `/photos/` reads its child galleries automatically. No index
template or JavaScript changes are needed for another year.
