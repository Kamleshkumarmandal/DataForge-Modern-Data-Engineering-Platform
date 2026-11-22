"""Command-line interface for DataForge."""
from __future__ import annotations

import argparse
import json
import logging
import sys

from dataforge.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataforge",
        description="Run a local Bronze/Silver/Gold mobility-trip data pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Ingest, validate and transform source files.")
    run_parser.add_argument("--input", required=True, help="Directory containing CSV/JSONL files.")
    run_parser.add_argument("--output", required=True, help="Directory for generated data layers.")
    run_parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: WARNING).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        manifest = run_pipeline(args.input, args.output)
    except (FileNotFoundError, NotADirectoryError, ValueError, OSError) as exc:
        print(f"DataForge pipeline failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
