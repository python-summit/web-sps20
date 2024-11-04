import pandas as pd
from pathlib import Path
import json

FILE_DIR = Path("scripts/recordings/sps24")
assert FILE_DIR.exists(), "FILE_DIR does not exist"

CSV_PATH = FILE_DIR / "talks.csv"
PRETALX_SCHEDULE_PATH = FILE_DIR / "schedule.json"

def main():
    schedule_data = json.loads(PRETALX_SCHEDULE_PATH.read_text())

