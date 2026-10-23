"""Scrape the Wikipedia snapshot that matches the course's 2020 sample."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAGE_URL = "https://en.wikipedia.org/w/index.php?oldid=987426997"
SNAPSHOT = ROOT / "data/raw/wikipedia_falcon_launch_history_2020.html"
OUT = ROOT / "data/raw/wikipedia_launch_history.csv"
START = pd.Timestamp("2010-06-04", tz="UTC")
END = pd.Timestamp("2020-11-05 23:59:59", tz="UTC")


def clean_header(value) -> str:
    if isinstance(value, tuple):
        value = " ".join(str(part) for part in value if str(part) != "nan")
    return re.sub(r"\s+", " ", str(value)).strip()


def scrape_tables() -> pd.DataFrame:
    """Read historical launch tables and retain dated launches in the lab era."""
    source = SNAPSHOT if SNAPSHOT.exists() else PAGE_URL
    tables = pd.read_html(source)
    matches = []
    for table in tables:
        table = table.copy()
        table.columns = [clean_header(c) for c in table.columns]
        lookup = {c.lower(): c for c in table.columns}
        flight_col = next((v for k, v in lookup.items() if k.startswith("flight no")), None)
        date_col = next((v for k, v in lookup.items() if "date and time" in k), None)
        if not flight_col or not date_col:
            continue

        frame = table.rename(columns={flight_col: "FlightNumber", date_col: "DateText"})
        frame["DateText"] = frame["DateText"].astype(str).str.replace(r"\[\d+\]", "", regex=True).str.strip()
        frame["DateUTC"] = pd.to_datetime(frame["DateText"], format="mixed", utc=True, errors="coerce")
        frame["FlightNumber"] = pd.to_numeric(frame["FlightNumber"], errors="coerce")
        frame = frame.dropna(subset=["FlightNumber", "DateUTC"])
        frame = frame[frame["DateUTC"].between(START, END)]
        if not frame.empty:
            matches.append(frame)

    if not matches:
        raise RuntimeError("No dated launch-history rows matched the historical course window")
    result = pd.concat(matches, ignore_index=True, sort=False)
    result["FlightNumber"] = result["FlightNumber"].astype(int)
    result = result.sort_values(["FlightNumber", "DateUTC"]).drop_duplicates("FlightNumber", keep="first")
    result["SourceRevision"] = "Wikipedia revision 987426997 (2020-11-06)"
    return result.reset_index(drop=True)


def main() -> None:
    frame = scrape_tables()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT, index=False)
    print(f"Historical launches scraped: {len(frame)}")
    print(f"Date range: {frame['DateUTC'].min()} to {frame['DateUTC'].max()}")
    print(f"Saved: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
