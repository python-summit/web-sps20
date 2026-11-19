# Automating YouTube uploads and playlists

## Goal

Until now, the conference recordings were uploaded to our YouTube channel and sorted into playlists by hand.
We want to automate this. Questions:

1. Can we upload videos to the channel and create playlists via the API?
2. What is a Google Cloud project, and how hard is it to set up?
3. Is there a simple API key or token instead?
4. What is the most reasonable way to upload ~30 videos once per year, create 2 playlists, and alter metadata (title, description, license, tags etc.)?

Short answers:
1. Yes, the YouTube Data API v3 supports all of it.
2. A free container for API credentials and quota. Setup is a few clicks (see below).
3. No. Writes need OAuth 2.0 as the channel owner. API keys are read-only.
4. A small local Python script driven by a CSV/JSON, run once a year (see "Recommended approach").

## Feasibility

The YouTube Data API v3 supports uploading videos, creating playlists, adding videos to playlists and editing metadata.

| Task | Method | Quota cost |
|---|---|---|
| Upload video | `videos.insert` (resumable) | separate bucket, 100 calls/day |
| Create playlist | `playlists.insert` | 50 |
| Add video to playlist | `playlistItems.insert` | 50 |
| List playlists | `playlists.list` | 1 |
| Edit metadata | `videos.update` | 50 |
| Set thumbnail | `thumbnails.set` | 50 |

Default quota: 10,000 units/day (resets at midnight Pacific Time) plus 100 `videos.insert` calls/day.
Roughly 30 uploads, 30 playlist inserts (1,500 units) and several metadata updates per year fit easily.

## Authentication

- An API key only grants read access to public data. It cannot upload or edit.
- Writes require OAuth 2.0 as the channel owner. Service accounts do not work with YouTube channels.
- Scopes: `youtube.upload` for uploads. Playlists and `videos.update` need `https://www.googleapis.com/auth/youtube`.
- The first run opens a browser for consent and caches a refresh token (`token.json`). Later runs are unattended.

## Google Cloud project

A free container holding API settings, credentials and quota. Nothing is billed or hosted.
Setup:
1. Create a project in the Cloud Console.
2. Enable "YouTube Data API v3".
3. Configure the OAuth consent screen and set it to "Production" (in "Testing" mode, refresh tokens expire after 7 days).
4. Create an OAuth client ID of type "Desktop app" and download `client_secrets.json`.

Do not commit `client_secrets.json` or `token.json`.

## Recommended approach (~30 videos/year, 2 playlists)

A small Python script using `google-api-python-client`, `google-auth-oauthlib` and `google-auth-httplib2`, run locally once a year:

1. Read a CSV/JSON with one row per talk: file path, title, description, tags, playlist.
2. `videos.insert` with resumable upload, `privacyStatus=private`, and `status.license` set to `youtube` or `creativeCommon`.
3. Create the 2 playlists once (`playlists.insert`) and reuse them later (`playlists.list`).
4. `playlistItems.insert` for each uploaded video.
5. Store the returned video IDs in a file for later edits.
6. Change metadata later with `videos.update` using those IDs.
7. Review and set visibility to public in YouTube Studio.

Official sample script: https://developers.google.com/youtube/v3/guides/uploading_a_video

## Pitfalls

- Uploads from unverified API projects are locked to private since July 2020. Publishing as public/unlisted requires the YouTube API Services compliance audit. Workaround: upload private, then flip visibility in Studio. This is from prior knowledge and was not re-verified against current docs.
- `videos.update` replaces the whole `snippet`. Always send title, description, tags and categoryId together, otherwise omitted fields are wiped.
- New or unverified channels can hit `uploadLimitExceeded`. Phone-verify the channel.

## Existing tools

- YouTube Studio supports bulk metadata editing in the UI.
- `youtube-upload` (https://github.com/tokland/youtube-upload) is a command-line uploader. Correction: I earlier called it "CSV-driven", which I could not verify and is probably wrong. It appears to be a per-video CLI, and I could not check its maintenance status or whether it still works with the current OAuth flow. Treat it as unverified.
- The official API script is the more maintainable choice, and it can read the existing `talks.csv` workflow.

## Sources

- https://developers.google.com/youtube/v3/guides/uploading_a_video
- https://developers.google.com/youtube/v3/determine_quota_cost
- https://support.google.com/youtube/contact/yt_api_form (audit form)
