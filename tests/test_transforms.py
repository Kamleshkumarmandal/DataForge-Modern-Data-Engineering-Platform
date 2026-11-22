import pandas as pd

from dataforge.transforms.layers import build_gold, build_silver


def test_silver_normalizes_types_and_adds_trip_date():
    source = pd.DataFrame(
        [{
            "trip_id": " t-1 ",
            "started_at": pd.Timestamp("2025-01-01T08:00:00Z"),
            "ended_at": pd.Timestamp("2025-01-01T08:10:00Z"),
            "duration_seconds": 600.0,
            "start_station_id": " A ",
            "end_station_id": " B ",
            "member_type": " Member ",
            "source_file": "trips.csv",
            "source_sha256": "abc",
            "source_row_number": 1,
            "ingested_at_utc": pd.Timestamp("2025-01-02T00:00:00Z"),
        }]
    )
    silver = build_silver(source)
    assert silver.loc[0, "trip_id"] == "t-1"
    assert silver.loc[0, "start_station_id"] == "A"
    assert silver.loc[0, "member_type"] == "member"
    assert str(silver.loc[0, "trip_date"]) == "2025-01-01"


def test_gold_builds_station_day_aggregates():
    source = pd.DataFrame(
        [
            {"trip_id":"1","trip_date":pd.to_datetime("2025-01-01").date(),"start_station_id":"A","end_station_id":"B","duration_seconds":600.0,"member_type":"member"},
            {"trip_id":"2","trip_date":pd.to_datetime("2025-01-01").date(),"start_station_id":"A","end_station_id":"C","duration_seconds":900.0,"member_type":"casual"},
        ]
    )
    gold = build_gold(source)
    row = gold.iloc[0]
    assert row["trip_count"] == 2
    assert row["avg_duration_seconds"] == 750.0
    assert row["member_trip_count"] == 1
    assert row["casual_trip_count"] == 1
    assert row["unique_end_station_count"] == 2
