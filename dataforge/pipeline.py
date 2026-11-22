"""End-to-end batch pipeline for the DataForge mobility-trip example."""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from dataforge.ingestion.readers import discover_sources, read_source
from dataforge.observability.manifest import write_manifest
from dataforge.quality.trips import validate_trips
from dataforge.storage.warehouse import publish_warehouse, write_parquet
from dataforge.transforms.layers import build_gold, build_silver


def run_pipeline(input_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Run ingestion, quality, Bronze/Silver/Gold, DuckDB and manifest steps."""
    input_root = Path(input_dir).resolve()
    output_root = Path(output_dir).resolve()
    started_wall = datetime.now(timezone.utc)
    started_clock = time.perf_counter()
    run_id = uuid.uuid4().hex[:12]

    sources = discover_sources(input_root)
    if not sources:
        raise FileNotFoundError(
            f"No CSV, JSONL or NDJSON input files found in {input_root}"
        )

    ingested_at = pd.Timestamp(started_wall)
    bronze_frames: list[pd.DataFrame] = []
    source_manifest: list[dict[str, Any]] = []

    for source in sources:
        frame = read_source(source)
        relative_path = source.path.relative_to(input_root).as_posix()
        frame = frame.copy()
        # Keep contract fields as source text in Bronze so CSV and JSONL files
        # have compatible Arrow types. Typed timestamps are created at the
        # Silver quality/normalization boundary.
        for column in (
            "trip_id",
            "started_at",
            "ended_at",
            "start_station_id",
            "end_station_id",
            "member_type",
        ):
            if column in frame:
                frame[column] = frame[column].astype("string")
        frame["source_file"] = relative_path
        frame["source_sha256"] = source.sha256
        frame["source_row_number"] = range(1, len(frame) + 1)
        frame["ingested_at_utc"] = ingested_at
        bronze_frames.append(frame)
        source_manifest.append(
            {
                "path": relative_path,
                "format": source.format,
                "sha256": source.sha256,
                "size_bytes": source.size_bytes,
                "rows_read": int(len(frame)),
            }
        )

    bronze = pd.concat(bronze_frames, ignore_index=True, sort=False)
    valid, rejected, quality_summary = validate_trips(bronze)
    silver = build_silver(valid)
    gold = build_gold(silver)

    bronze_path = write_parquet(bronze, output_root / "bronze" / "trips.parquet")
    silver_path = write_parquet(silver, output_root / "silver" / "trips.parquet")
    gold_path = write_parquet(
        gold, output_root / "gold" / "daily_station_metrics.parquet"
    )
    quarantine_path = write_parquet(
        rejected, output_root / "quarantine" / "rejected_trips.parquet"
    )
    warehouse_path = publish_warehouse(
        silver, gold, output_root / "warehouse.duckdb"
    )

    finished_wall = datetime.now(timezone.utc)
    duration_seconds = round(time.perf_counter() - started_clock, 6)
    output_paths = {
        "bronze": str(bronze_path.relative_to(output_root)),
        "silver": str(silver_path.relative_to(output_root)),
        "gold": str(gold_path.relative_to(output_root)),
        "quarantine": str(quarantine_path.relative_to(output_root)),
        "warehouse": str(warehouse_path.relative_to(output_root)),
    }
    manifest: dict[str, Any] = {
        "platform": "DataForge",
        "manifest_schema_version": 1,
        "run_id": run_id,
        "status": "completed",
        "started_at_utc": started_wall.isoformat(),
        "finished_at_utc": finished_wall.isoformat(),
        "duration_seconds": duration_seconds,
        "input_directory": str(input_root),
        "output_directory": str(output_root),
        "source_files": source_manifest,
        "row_counts": {
            "bronze": int(len(bronze)),
            "silver": int(len(silver)),
            "quarantine": int(len(rejected)),
            "gold": int(len(gold)),
        },
        "data_quality": quality_summary,
        "outputs": output_paths,
    }
    manifest["manifest_path"] = f"runs/{run_id}.json"
    write_manifest(output_root, run_id, manifest)
    return manifest
