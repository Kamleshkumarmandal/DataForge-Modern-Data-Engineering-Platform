from pathlib import Path

from prefect.testing.utilities import prefect_test_harness

from dataforge.orchestration.flows import dataforge_batch_flow, execute_batch_pipeline


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_prefect_flow_executes_the_batch_pipeline(tmp_path: Path):
    with prefect_test_harness():
        result = dataforge_batch_flow(
            str(REPO_ROOT / "sample_data" / "input"),
            str(tmp_path / "flow-output"),
        )

    assert result["status"] == "completed"
    assert result["row_counts"]["bronze"] == 11
    assert result["row_counts"]["silver"] == 8
    assert result["row_counts"]["quarantine"] == 3


def test_prefect_task_declares_retries():
    assert execute_batch_pipeline.retries == 2
    assert execute_batch_pipeline.retry_delay_seconds == [5, 15]
