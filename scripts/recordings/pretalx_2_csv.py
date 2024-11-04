import pandas as pd
from pathlib import Path
import json
import re

FILE_DIR = Path("scripts/recordings/sps24")
assert FILE_DIR.exists(), "FILE_DIR does not exist"

CSV_PATH = FILE_DIR / "talks.csv"
PRETALX_SCHEDULE_PATH = FILE_DIR / "schedule.json"

CONF_SHORT = "SPS24"

def get_talks_data(schedule_path = PRETALX_SCHEDULE_PATH):
    schedule_data = json.loads(schedule_path.read_text())
    talks = []
    for day in schedule_data["schedule"]["conference"]["days"]:
        day_idx = day["index"]
        print(f"Processing day {day_idx}")
        room_name = next(iter(day["rooms"]))
        for talk in day["rooms"][room_name]:
            print(f"\tProcessing talks #{talk['id']}")
            names, bios = zip(*[(d["public_name"], d["biography"]) for d in talk["persons"]])
            talk_data = dict(
                day = day_idx,
                title = talk["title"],
                abstract = talk["abstract"],
                names = names,
                biographies = bios
            )
            talks.append(talk_data)
    return talks

def enrich(talks):
    for talk in talks:
        named_title = f'{", ".join(talk["names"])} - {talk["title"]}'
        talk["named_title"] = named_title
        talk["video_title"] = f"{named_title} - {CONF_SHORT}"
        filename = clean_filename(f"{CONF_SHORT}_{named_title}")
        talk["filename"] = filename
        # combinded_bio = 
    return talks

def clean_filename(filename, max_length=70):
    # Trim
    filename = filename.strip()

    # Replace all spaces with underscore
    filename = filename.replace(' ', '_')

    # Define allowed characters: letters, numbers, dashes, and underscores. Remove not allowed
    filename = re.sub(r'[^a-zA-Z0-9_-]', '', filename)

    # Truncate after n characters
    filename = filename[:min(len(filename),max_length)]

    # To lower
    filename = filename.lower()

    # print(filename)

    return filename

def main():
    data = get_talks_data()
    data = enrich(data)
    df = pd.DataFrame(data)
    df.to_csv(CSV_PATH)

if __name__ == "__main__":
    main()
