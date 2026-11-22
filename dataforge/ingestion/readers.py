"""Deterministic discovery and lightweight readers for CSV and JSONL sources."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


SUPPORTED_SUFFIXES = {".csv", ".jsonl", ".ndjson"}


@dataclass(frozen=True)
class SourceFile:
    path: Path
    format: str
    sha256: str
    size_bytes: int


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_sources(root: str | Path) -> list[SourceFile]:
    """Discover supported files recursively and return them in stable path order."""
    directory = Path(root)
    if not directory.exists():
        raise FileNotFoundError(f"Input directory does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(str(directory))

    paths = sorted(
        (path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES),
        key=lambda item: item.as_posix().lower(),
    )
    return [
        SourceFile(
            path=path,
            format=path.suffix.lower().lstrip("."),
            sha256=sha256_file(path),
            size_bytes=path.stat().st_size,
        )
        for path in paths
    ]


def read_source(source: SourceFile) -> pd.DataFrame:
    """Read a CSV or newline-delimited JSON source without silently changing headers."""
    if source.format == "csv":
        frame = pd.read_csv(source.path, encoding="utf-8-sig")
    elif source.format in {"jsonl", "ndjson"}:
        frame = pd.read_json(source.path, lines=True, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported source format: {source.format}")

    if frame.columns.duplicated().any():
        duplicates = frame.columns[frame.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names in {source.path.name}: {duplicates}")
    return frame
