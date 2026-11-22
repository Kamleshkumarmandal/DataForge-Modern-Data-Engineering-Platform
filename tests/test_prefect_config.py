from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_prefect_deployment_config_is_opt_in_and_points_to_existing_flow():
    config = yaml.safe_load((REPO_ROOT / "prefect.yaml").read_text(encoding="utf-8"))

    assert config["name"] == "dataforge"
    assert len(config["deployments"]) == 1
    deployment = config["deployments"][0]
    assert deployment["name"] == "dataforge-daily-batch"
    assert deployment["entrypoint"] == "dataforge/orchestration/flows.py:dataforge_batch_flow"
    assert Path(REPO_ROOT / deployment["entrypoint"].split(":")[0]).exists()
    assert deployment["parameters"] == {
        "input_dir": "sample_data/input",
        "output_dir": "data/scheduled",
    }
    assert deployment["work_pool"]["name"] == "dataforge-process-pool"

    schedule = deployment["schedules"][0]
    assert schedule["cron"] == "0 6 * * *"
    assert schedule["timezone"] == "Asia/Kolkata"
    assert schedule["active"] is False


def test_prefect_pull_step_uses_public_repo_and_orchestration_requirements():
    config = yaml.safe_load((REPO_ROOT / "prefect.yaml").read_text(encoding="utf-8"))
    pull = config["pull"]

    assert pull[0]["prefect.deployments.steps.git_clone"]["branch"] == "main"
    assert pull[1]["prefect.deployments.steps.set_working_directory"]["directory"] == "{{ clone-step.directory }}"
    pip_step = pull[2]["prefect.deployments.steps.pip_install_requirements"]
    assert pip_step["requirements_file"] == "requirements-orchestration.txt"
    assert (REPO_ROOT / pip_step["requirements_file"]).exists()
