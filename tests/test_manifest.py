import json

from dataforge.observability.manifest import write_manifest


def test_manifest_is_written_as_stable_json(tmp_path):
    manifest = {
        "run_id": "test-run",
        "status": "completed",
        "source_files": [{"path": "rides.csv", "sha256": "abc123"}],
        "row_counts": {"bronze": 3, "silver": 2, "quarantine": 1},
    }

    path = write_manifest(tmp_path, "test-run", manifest)

    assert path.relative_to(tmp_path).as_posix() == "runs/test-run.json"
    assert json.loads(path.read_text(encoding="utf-8")) == manifest
    assert not path.with_name(path.name + ".tmp").exists()
