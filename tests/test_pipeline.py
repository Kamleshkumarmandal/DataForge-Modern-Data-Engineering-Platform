import json
from pathlib import Path

import duckdb

from dataforge.pipeline import run_pipeline


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sample_pipeline_writes_layers_warehouse_and_manifest(tmp_path: Path):
    output_dir = tmp_path / "data"
    result = run_pipeline(REPO_ROOT / "sample_data" / "input", output_dir)

    assert result["status"] == "completed"
    assert result["row_counts"] == {
        "bronze": 11,
        "silver": 8,
        "quarantine": 3,
        "gold": 6,
    }
    assert len(result["source_files"]) == 2
    assert len(result["source_files"][0]["sha256"]) == 64

    for relative_path in result["outputs"].values():
        assert (output_dir / relative_path).exists()

    manifest_path = output_dir / result["manifest_path"]
    on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert on_disk["run_id"] == result["run_id"]
    assert on_disk["data_quality"]["rejected_rows"] == 3

    connection = duckdb.connect(str(output_dir / "warehouse.duckdb"), read_only=True)
    try:
        silver_count = connection.execute("SELECT COUNT(*) FROM silver_trips").fetchone()[0]
        gold_count = connection.execute(
            "SELECT COUNT(*) FROM gold_daily_station_metrics"
        ).fetchone()[0]
    finally:
        connection.close()

    assert silver_count == 8
    assert gold_count == 6


def test_pipeline_fails_for_empty_input_directory(tmp_path: Path):
    input_dir = tmp_path / "empty"
    input_dir.mkdir()
    try:
        run_pipeline(input_dir, tmp_path / "out")
    except FileNotFoundError as exc:
        assert "No CSV, JSONL or NDJSON" in str(exc)
    else:
        raise AssertionError("Expected empty input directory to fail.")
