import pandas as pd
from pathlib import Path
import json
import re
import shutil

FILE_DIR = Path("scripts/recordings/sps24")
assert FILE_DIR.exists(), "FILE_DIR does not exist"

CSV_PATH = FILE_DIR / "talks.csv"


CONF_SHORT = "SPS24"
CONF_YEAR = "2024"

OUTPUT_FOLDER = Path("scripts/recordings/out")

def get_data(csv_path, filter_type=["Talk", "Keynote"]):
    df = pd.read_csv(csv_path)
    df = df[df['type'].isin(filter_type)]
    df = df.reset_index()
    return df

def create_file_structure(df: pd.DataFrame):
    # if OUTPUT_FOLDER.exists():
    #     shutil.rmtree(OUTPUT_FOLDER)
    OUTPUT_FOLDER.mkdir(exist_ok=False)
    for i, row in df.iterrows():
        filename = Path(OUTPUT_FOLDER / row.filename)
        filename.mkdir()
        content = filename / "contents.lr"
        content.write_text(create_content(i, row))
        slide = filename / f"{filename}.lr"
        slide.write_text("type: slides")

def create_content(i, row):
    text = f'''
_model: recording
---
title: {row.title}
---
ordering: {i}
---
speaker: {row.names_combined}
---
video_url: {row.video_url}
---
year: {CONF_YEAR}
'''
    return text



def main():
    df = get_data(CSV_PATH)
    create_file_structure(df)

if __name__ == "__main__":
    main()
