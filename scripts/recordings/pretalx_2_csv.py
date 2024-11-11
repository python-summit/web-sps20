import pandas as pd
from pathlib import Path
import json
import re
from datetime import datetime

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
            names, bios = zip(*[(d["public_name"], d["biography"] if d["biography"] else "") for d in talk["persons"]])
            talk_data = dict(
                day = day_idx,
                date = talk["date"],
                title = talk["title"],
                type = talk["type"],
                names_raw = names,
                biographies_raw = bios,
                abstract = talk["abstract"],
            )
            talks.append(talk_data)
    return talks

def timestring(timestamp):
    dt = datetime.fromisoformat(timestamp)
    local_dt = dt.astimezone()
    
    # Add suffix for day (st, nd, rd, th)
    day = local_dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    return local_dt.strftime(f"%B {day}{suffix}, %Y")

def enrich(talks):
    for talk in talks:
        names = ", ".join(talk["names_raw"])
        talk["names_combined"] = names
        named_title = f'{names} - {talk["title"]}'
        talk["named_title"] = named_title
        talk["video_title"] = f"{named_title} - {CONF_SHORT}"
        filename = clean_filename(f"{CONF_SHORT}_{named_title}")
        talk["filename"] = filename
        talk["video_url"] = "<TODO>"
        talk["biographies_combined"] = "\n\n".join(talk["biographies_raw"])
        talk["date_str"] = talk["date"]
        # Title and Description for youtube
        talk["video_text"] = f'{talk["names_combined"]} – {talk["title"]} – {CONF_SHORT}'
        talk["video_text"] = f'''Talk recorded at the Swiss Python Summit on {timestring(talk["date"])}.

Licensed as Creative Commons Attribution 4.0 International.

---------
Abstract:

{talk["abstract"]}

---------------------
About the speaker(s):

{talk["biographies_combined"]}
'''
    return talks

def clean_filename(filename, max_length=70):
    # Trim
    filename = filename.strip()

    # Replace all spaces with underscore
    filename = filename.replace(' ', '_')

    # Replace umlaut and french accents
    umlaut_map = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ç': 'c',
        'î': 'i', 'ï': 'i', 'í': 'i',
        'ô': 'o',
        'ù': 'u', 'û': 'u'
    }
    for umlaut, replacement in umlaut_map.items():
        filename = filename.replace(umlaut, replacement)

    # Define allowed characters: letters, numbers, dashes, and underscores. Remove not allowed
    new_filename = []
    for c in filename:
        if re.match(r'[a-zA-Z0-9_-]', c):
            new_filename.append(c)
        else:
            print(f"Warning: Deleted char '{c}' in filename '{filename}'")
    filename = ''.join(new_filename)

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
    short_csv_path = CSV_PATH.parent / (CSV_PATH.stem + "_notext" + CSV_PATH.suffix)
    # print(short_csv_path)
    # drop multiline texts
    df.drop(["abstract","biographies_raw", "biographies_combined", "video_text"], axis=1).to_csv(short_csv_path)

if __name__ == "__main__":
    main()
    print("*** Script end ***")
