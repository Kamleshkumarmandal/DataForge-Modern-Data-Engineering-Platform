"""Bronze-to-Silver normalization and Silver-to-Gold aggregations."""
from __future__ import annotations

import pandas as pd


SILVER_COLUMNS = (
    "trip_id",
    "started_at",
    "ended_at",
    "trip_date",
    "duration_seconds",
    "start_station_id",
    "end_station_id",
    "member_type",
    "source_file",
    "source_sha256",
    "source_row_number",
    "ingested_at_utc",
)


def build_silver(valid_rows: pd.DataFrame) -> pd.DataFrame:
    """Normalize valid rows into the canonical Silver trip schema."""
    frame = valid_rows.copy()
    if frame.empty:
        return pd.DataFrame(
            {
                "trip_id": pd.Series(dtype="string"),
                "started_at": pd.Series(dtype="datetime64[ns, UTC]"),
                "ended_at": pd.Series(dtype="datetime64[ns, UTC]"),
                "trip_date": pd.Series(dtype="object"),
                "duration_seconds": pd.Series(dtype="float64"),
                "start_station_id": pd.Series(dtype="string"),
                "end_station_id": pd.Series(dtype="string"),
                "member_type": pd.Series(dtype="string"),
                "source_file": pd.Series(dtype="string"),
                "source_sha256": pd.Series(dtype="string"),
                "source_row_number": pd.Series(dtype="int64"),
                "ingested_at_utc": pd.Series(dtype="datetime64[ns, UTC]"),
            }
        )

    frame["trip_id"] = frame["trip_id"].astype("string").str.strip()
    frame["start_station_id"] = frame["start_station_id"].astype("string").str.strip()
    frame["end_station_id"] = frame["end_station_id"].astype("string").str.strip()
    frame["member_type"] = frame["member_type"].astype("string").str.strip().str.lower()
    frame["trip_date"] = frame["started_at"].dt.date
    frame["duration_seconds"] = frame["duration_seconds"].astype("float64")

    for column in ("source_file", "source_sha256"):
        if column not in frame:
            frame[column] = pd.Series([""] * len(frame), dtype="string")
        frame[column] = frame[column].astype("string")
    if "source_row_number" not in frame:
        frame["source_row_number"] = range(1, len(frame) + 1)
    frame["source_row_number"] = frame["source_row_number"].astype("int64")
    if "ingested_at_utc" not in frame:
        frame["ingested_at_utc"] = pd.Timestamp.now(tz="UTC")
    frame["ingested_at_utc"] = pd.to_datetime(frame["ingested_at_utc"], utc=True)

    return frame.loc[:, list(SILVER_COLUMNS)].sort_values(
        ["started_at", "trip_id"], kind="stable"
    ).reset_index(drop=True)


def build_gold(silver_rows: pd.DataFrame) -> pd.DataFrame:
    """Create daily start-station aggregates for analytics consumers."""
    columns = [
        "trip_date",
        "start_station_id",
        "trip_count",
        "avg_duration_seconds",
        "member_trip_count",
        "casual_trip_count",
        "unique_end_station_count",
    ]
    if silver_rows.empty:
        return pd.DataFrame(
            {
                "trip_date": pd.Series(dtype="object"),
                "start_station_id": pd.Series(dtype="string"),
                "trip_count": pd.Series(dtype="int64"),
                "avg_duration_seconds": pd.Series(dtype="float64"),
                "member_trip_count": pd.Series(dtype="int64"),
                "casual_trip_count": pd.Series(dtype="int64"),
                "unique_end_station_count": pd.Series(dtype="int64"),
            }
        )

    grouped = silver_rows.groupby(["trip_date", "start_station_id"], dropna=False)
    gold = grouped.agg(
        trip_count=("trip_id", "count"),
        avg_duration_seconds=("duration_seconds", "mean"),
        unique_end_station_count=("end_station_id", "nunique"),
    ).reset_index()
    member = grouped["member_type"].apply(lambda values: int(values.eq("member").sum())).rename("member_trip_count")
    casual = grouped["member_type"].apply(lambda values: int(values.eq("casual").sum())).rename("casual_trip_count")
    gold = gold.merge(member.reset_index(), on=["trip_date", "start_station_id"])
    gold = gold.merge(casual.reset_index(), on=["trip_date", "start_station_id"])
    gold["trip_count"] = gold["trip_count"].astype("int64")
    gold["member_trip_count"] = gold["member_trip_count"].astype("int64")
    gold["casual_trip_count"] = gold["casual_trip_count"].astype("int64")
    gold["unique_end_station_count"] = gold["unique_end_station_count"].astype("int64")
    return gold.loc[:, columns].sort_values(
        ["trip_date", "start_station_id"], kind="stable"
    ).reset_index(drop=True)
