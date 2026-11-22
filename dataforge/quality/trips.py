"""Data contract and row-level validation for the mobility-trip example."""
from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = (
    "trip_id",
    "started_at",
    "ended_at",
    "start_station_id",
    "end_station_id",
    "member_type",
)

ALLOWED_MEMBER_TYPES = {"member", "casual"}


def validate_trips(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    """Split source rows into valid and quarantined sets with explicit issue reasons.

    Missing required columns are a file/schema error and raise ValueError. Row-level
    problems are quarantined, never silently dropped.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    if frame.empty:
        empty = frame.copy()
        empty["quality_issues"] = pd.Series(dtype="string")
        return empty.copy(), empty.copy(), {"input_rows": 0, "valid_rows": 0, "rejected_rows": 0, "rejection_reasons": {}}

    data = frame.copy().reset_index(drop=True)
    issues: dict[object, list[str]] = {index: [] for index in data.index}

    text_columns = ("trip_id", "start_station_id", "end_station_id", "member_type")
    for column in text_columns:
        values = data[column].astype("string").str.strip()
        missing_mask = values.isna() | values.eq("")
        for index in data.index[missing_mask]:
            issues[index].append(f"missing_{column}")

    trip_ids = data["trip_id"].astype("string").str.strip()
    duplicate_mask = trip_ids.notna() & trip_ids.ne("") & trip_ids.duplicated(keep="first")
    for index in data.index[duplicate_mask]:
        issues[index].append("duplicate_trip_id")

    started = pd.to_datetime(data["started_at"], utc=True, errors="coerce")
    ended = pd.to_datetime(data["ended_at"], utc=True, errors="coerce")
    for index in data.index[started.isna()]:
        issues[index].append("invalid_started_at")
    for index in data.index[ended.isna()]:
        issues[index].append("invalid_ended_at")

    duration = (ended - started).dt.total_seconds()
    for index in data.index[duration.notna() & duration.le(0)]:
        issues[index].append("non_positive_duration")

    member_types = data["member_type"].astype("string").str.strip().str.lower()
    unsupported = member_types.notna() & member_types.ne("") & ~member_types.isin(ALLOWED_MEMBER_TYPES)
    for index in data.index[unsupported]:
        issues[index].append("unsupported_member_type")

    data["started_at"] = started
    data["ended_at"] = ended
    data["duration_seconds"] = duration
    data["member_type"] = member_types
    data["quality_issues"] = [";".join(issues[index]) for index in data.index]

    rejected_mask = data["quality_issues"].ne("")
    valid = data.loc[~rejected_mask].copy().reset_index(drop=True)
    rejected = data.loc[rejected_mask].copy().reset_index(drop=True)

    reason_counts: dict[str, int] = {}
    for reasons in rejected["quality_issues"]:
        for reason in reasons.split(";"):
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    summary = {
        "input_rows": int(len(data)),
        "valid_rows": int(len(valid)),
        "rejected_rows": int(len(rejected)),
        "rejection_reasons": dict(sorted(reason_counts.items())),
    }
    return valid, rejected, summary
