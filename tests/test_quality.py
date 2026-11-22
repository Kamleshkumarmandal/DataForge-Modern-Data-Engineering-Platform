import pandas as pd
import pytest

from dataforge.quality.trips import validate_trips


def make_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["t-1", "2025-01-01T08:00:00Z", "2025-01-01T08:10:00Z", "A", "B", "member"],
            ["t-2", "bad-time", "2025-01-01T08:15:00Z", "A", "C", "casual"],
            ["t-3", "2025-01-01T09:00:00Z", "2025-01-01T08:55:00Z", "B", "A", "member"],
            ["t-1", "2025-01-01T10:00:00Z", "2025-01-01T10:10:00Z", "A", "B", "member"],
            ["t-5", "2025-01-01T11:00:00Z", "2025-01-01T11:10:00Z", "", "B", "member"],
        ],
        columns=["trip_id", "started_at", "ended_at", "start_station_id", "end_station_id", "member_type"],
    )


def test_validation_quarantines_invalid_rows_with_reasons():
    valid, rejected, summary = validate_trips(make_rows())

    assert len(valid) == 1
    assert len(rejected) == 4
    assert summary["input_rows"] == 5
    assert summary["valid_rows"] == 1
    assert summary["rejected_rows"] == 4
    reasons = set(";".join(rejected["quality_issues"]).split(";"))
    assert {"invalid_started_at", "non_positive_duration", "duplicate_trip_id", "missing_start_station_id"} <= reasons


def test_validation_rejects_missing_schema_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_trips(pd.DataFrame({"trip_id": ["only-id"]}))


def test_empty_frame_is_supported():
    frame = make_rows().iloc[:0]
    valid, rejected, summary = validate_trips(frame)
    assert valid.empty and rejected.empty
    assert summary["input_rows"] == 0
