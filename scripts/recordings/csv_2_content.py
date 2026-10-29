import pandas as pd
from pathlib import Path
import json
import re
import shutil

# START Change these:
CONF_YEAR_SLUG = "26"
# END

BASE_DIR = Path(f"scripts/recordings/sps{CONF_YEAR_SLUG}")
CONF_SHORT = f"SPS{CONF_YEAR_SLUG}"
CONF_YEAR = f"20{CONF_YEAR_SLUG}"
CSV_PATH = BASE_DIR / "talks.csv"
PDF_DIR = BASE_DIR / "slides"

assert BASE_DIR.exists(), "BASE_DIR does not exist"
assert CSV_PATH.exists(), "CSV_PATH not found"


def get_data(csv_path, filter_type=["Talk", "Keynote", "Lightning Talks"]):
    df = pd.read_csv(csv_path)
    df = df[df['type'].isin(filter_type)]
    df = df.reset_index()
    return df

def create_file_structure(df: pd.DataFrame, pdf_dir: Path | None = None):
    out_dir = BASE_DIR / "content"
    out_dir.mkdir(exist_ok=False) # Warn user if it exists
    for i, row in df.iterrows():
        foldername = Path(out_dir / row.filename)
        foldername.mkdir()
        content = foldername / "contents.lr"
        content.write_text(create_content(row))
        slide = foldername / f"{foldername.name}.pdf.lr"
        slide.write_text("type: slides")
        if pdf_dir:
            pdf_path = pdf_dir / f"{row.filename}.pdf"
            if pdf_path.exists():
                shutil.copy(pdf_path, foldername / f"{row.filename}.pdf")
            else:
                print(f"Warning: PDF not found for {row.filename}")


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
    create_file_structure(df, pdf_dir=PDF_DIR)

if __name__ == "__main__":
    main()
