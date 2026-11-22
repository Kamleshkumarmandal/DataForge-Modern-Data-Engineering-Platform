"""Atomic Parquet writes and DuckDB publishing."""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def write_parquet(frame: pd.DataFrame, path: str | Path) -> Path:
    """Write a Parquet file via a temporary sibling, then atomically replace it."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        frame.to_parquet(temporary, index=False, engine="pyarrow")
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination


def publish_warehouse(
    silver_rows: pd.DataFrame,
    gold_rows: pd.DataFrame,
    database_path: str | Path,
) -> Path:
    """Publish validated Silver and Gold DataFrames into local DuckDB tables."""
    destination = Path(database_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(destination))
    try:
        connection.register("_dataforge_silver_input", silver_rows)
        connection.register("_dataforge_gold_input", gold_rows)
        connection.execute(
            "CREATE OR REPLACE TABLE silver_trips AS SELECT * FROM _dataforge_silver_input"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE gold_daily_station_metrics AS "
            "SELECT * FROM _dataforge_gold_input"
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dataforge_metadata (
                key VARCHAR PRIMARY KEY,
                value VARCHAR NOT NULL
            )
            """
        )
        connection.execute(
            "INSERT OR REPLACE INTO dataforge_metadata VALUES "
            "('warehouse_schema_version', '1')"
        )
    finally:
        connection.close()
    return destination
