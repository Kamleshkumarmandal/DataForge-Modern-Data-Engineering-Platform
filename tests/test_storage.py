import duckdb
import pandas as pd

from dataforge.storage.warehouse import publish_warehouse, write_parquet


def test_parquet_write_and_duckdb_publish(tmp_path):
    silver = pd.DataFrame({"trip_id": ["a", "b"], "duration_seconds": [30.0, 45.0]})
    gold = pd.DataFrame({"trip_count": [2]})

    parquet_path = write_parquet(silver, tmp_path / "silver" / "trips.parquet")
    database_path = publish_warehouse(silver, gold, tmp_path / "warehouse.duckdb")

    assert parquet_path.exists()
    assert pd.read_parquet(parquet_path).equals(silver)
    assert database_path.exists()

    connection = duckdb.connect(str(database_path), read_only=True)
    try:
        count = connection.execute("SELECT COUNT(*) FROM silver_trips").fetchone()[0]
    finally:
        connection.close()
    assert count == 2
