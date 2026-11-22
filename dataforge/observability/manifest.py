"""JSON run manifests for reproducibility and basic pipeline observability."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_manifest(output_dir: str | Path, run_id: str, manifest: dict[str, Any]) -> Path:
    destination = Path(output_dir) / "runs" / f"{run_id}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination
