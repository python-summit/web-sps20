# Recordings Scripts

These script should help in the process of releasing the talk recordings on Youtube and on the website

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run the
commands below from the repository root. The optional `recordings` dependency group
provides pandas and is installed automatically by `uv run --group recordings`.

## Steps

1. Download Pretalx Schedule

**WARNING:** Download the `schedule.json` without being logged in or in private mode otherwise there will be personal data (e.g. email addresses) in the json and therefore public as this repo is public !!!!

2. Run `uv run --locked --group recordings python scripts/recordings/schedule_2_csv.py`

Upload video to Youtube with the provided metadata (title, description) from the CSV. Get the Youtube link and add it to the CSV

3. Run `uv run --locked --group recordings python scripts/recordings/csv_2_content.py`

Add link to the content files provided

4. Copy content files `sps20/content/recordings` to release it

Copy the slides pdf as well an name it accordingly TODO

5. For full playlist, add them to `sps20/databags/playlists.json`
