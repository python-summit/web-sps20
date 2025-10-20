import pandas as pd
from pathlib import Path
import json
import re
import shutil

# START Change these two
CONF_YEAR_SLUG = "25"
# END

BASE_DIR = Path(f"scripts/recordings/sps{CONF_YEAR_SLUG}")
CONF_SHORT = f"SPS{CONF_YEAR_SLUG}"
CONF_YEAR = f"20{CONF_YEAR_SLUG}"
CSV_PATH = BASE_DIR / "talks.csv"

assert BASE_DIR.exists(), "BASE_DIR does not exist"
assert CSV_PATH.exists(), "CSV_PATH not found"


def get_data(csv_path, filter_type=["Talk", "Keynote", "Lightning Talks (9x5min)"]):
    df = pd.read_csv(csv_path)
    df = df[df['type'].isin(filter_type)]
    df = df.reset_index()
    return df

def create_file_structure(df: pd.DataFrame):
    out_dir = BASE_DIR / "content"
    out_dir.mkdir(exist_ok=False) # Warn user if it exists
    for i, row in df.iterrows():
        filename = Path(out_dir / row.filename)
        filename.mkdir()
        content = filename / "contents.lr"
        content.write_text(create_content(row))
        slide = filename / f"{filename.name}.pdf.lr"
        slide.write_text("type: slides")

def create_content(row):
    text = f'''
_model: recording
---
title: {row.title}
---
ordering: {row.talk_idx}
---
speaker: {row.names_combined}
---
video_url: {row.video_url if row.video_url != "<VIDEO_URL>" else ""}
---
year: {CONF_YEAR} - Day {row.day}
'''
    return text



def main():
    df = get_data(CSV_PATH)
    create_file_structure(df)

if __name__ == "__main__":
    main()
