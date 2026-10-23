"""Collect and normalize the archived SpaceX API response used by IBM's lab."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/API_call_spacex_api.json"
OUT = ROOT / "data/processed/api_launches_normalized.csv"
STATIC_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json"
)


def collect_static_course_json() -> list[dict]:
    """Read the saved course response, downloading it when absent."""
    if RAW.exists():
        payload = RAW.read_bytes()
    else:
        req = Request(STATIC_URL, headers={"User-Agent": "IBM-capstone-project/1.0"})
        with urlopen(req, timeout=30) as response:
            payload = response.read()
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_bytes(payload)
    records = json.loads(payload)
    if not isinstance(records, list):
        raise ValueError("Expected the archived API response to be a JSON list")
    return records


def normalize_records(records: list[dict]) -> pd.DataFrame:
    """Flatten the fields used in the collection lab, retaining nested data."""
    rows = []
    for launch in records:
        cores = launch.get("cores") or []
        core = cores[0] if cores else {}
        rows.append({
            "flight_number": launch.get("flight_number"),
            "name": launch.get("name"),
            "date_utc": launch.get("date_utc"),
            "upcoming": launch.get("upcoming"),
            "launch_success": launch.get("success"),
            "rocket_id": launch.get("rocket"),
            "launchpad_id": launch.get("launchpad"),
            "payload_ids": json.dumps(launch.get("payloads") or []),
            "core_id": core.get("core"),
            "core_flight": core.get("flight"),
            "gridfins": core.get("gridfins"),
            "legs": core.get("legs"),
            "reused": core.get("reused"),
            "landing_attempt": core.get("landing_attempt"),
            "landing_success": core.get("landing_success"),
            "landing_type": core.get("landing_type"),
            "landingpad_id": core.get("landpad"),
            "failures_json": json.dumps(launch.get("failures") or []),
        })
    frame = pd.DataFrame(rows).sort_values("flight_number", na_position="last")
    return frame.reset_index(drop=True)


def main() -> None:
    records = collect_static_course_json()
    frame = normalize_records(records)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(f"Raw API records: {len(records)}")
    print(f"Normalized rows/columns: {frame.shape[0]} x {frame.shape[1]}")
    print(f"Saved: {RAW.relative_to(ROOT)}")
    print(f"Saved: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
