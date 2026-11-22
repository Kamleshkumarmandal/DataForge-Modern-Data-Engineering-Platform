"""Prefect flow and task wrappers around the DataForge batch pipeline."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prefect import flow, task
from prefect.logging import get_run_logger

from dataforge.observability.manifest import write_manifest
from dataforge.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def _write_failure_manifest(
    output_dir: str | Path,
    input_dir: str | Path,
    error: Exception,
) -> Path:
    """Record a failed orchestration attempt without hiding the original error."""
    failed_at = datetime.now(timezone.utc)
    failure_id = f"failed-{uuid.uuid4().hex[:12]}"
    manifest: dict[str, Any] = {
        "platform": "DataForge",
        "manifest_schema_version": 1,
        "run_id": failure_id,
        "status": "failed",
        "failed_at_utc": failed_at.isoformat(),
        "input_directory": str(Path(input_dir).resolve()),
        "output_directory": str(Path(output_dir).resolve()),
        "error": {
            "type": type(error).__name__,
            "message": str(error),
        },
        "note": "This manifest records a failed Prefect task attempt.",
    }
    return write_manifest(output_dir, failure_id, manifest)


@task(
    name="execute-dataforge-batch-pipeline",
    description="Run the existing Bronze/Silver/Gold batch pipeline.",
    retries=2,
    retry_delay_seconds=[5, 15],
    log_prints=True,
    tags={"dataforge", "batch", "bronze-silver-gold"},
)
def execute_batch_pipeline(input_dir: str, output_dir: str) -> dict[str, Any]:
    """Execute the batch pipeline as an observable Prefect task.

    The task is retried up to two times by Prefect. Each failed attempt is
    recorded in the output run-manifest folder before the exception is raised
    so the Prefect engine can mark the task attempt as failed and retry it.
    """
    task_logger = get_run_logger()
    task_logger.info("Starting DataForge pipeline: input=%s output=%s", input_dir, output_dir)
    try:
        result = run_pipeline(input_dir, output_dir)
    except Exception as exc:
        try:
            failure_path = _write_failure_manifest(output_dir, input_dir, exc)
            task_logger.exception("DataForge attempt failed; manifest written to %s", failure_path)
        except Exception:
            task_logger.exception("DataForge attempt failed and its failure manifest could not be written")
        raise

    counts = result.get("row_counts", {})
    task_logger.info(
        "DataForge pipeline completed: run_id=%s rows=%s",
        result.get("run_id"),
        counts,
    )
    return result


@flow(
    name="dataforge-batch-pipeline",
    description=(
        "Orchestrate DataForge ingestion, quality validation, Bronze/Silver/Gold "
        "transforms, Parquet outputs and DuckDB publishing."
    ),
    log_prints=True,
)
def dataforge_batch_flow(input_dir: str, output_dir: str) -> dict[str, Any]:
    """Run one observable DataForge batch pipeline flow."""
    flow_logger = get_run_logger()
    flow_logger.info("Submitting the DataForge batch pipeline task")
    return execute_batch_pipeline(input_dir, output_dir)
