import json

from dataforge.orchestration.flows import _write_failure_manifest


def test_failed_attempt_writes_failure_manifest(tmp_path):
    path = _write_failure_manifest(
        tmp_path,
        "input-files",
        ValueError("sample failure"),
    )
    manifest = json.loads(path.read_text(encoding="utf-8"))

    assert manifest["status"] == "failed"
    assert manifest["error"]["type"] == "ValueError"
    assert manifest["error"]["message"] == "sample failure"
    assert path.parent.name == "runs"
