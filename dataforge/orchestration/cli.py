"""CLI entry point for running a DataForge pipeline through Prefect."""
from __future__ import annotations

import argparse
import json
import logging
import sys

from dataforge.orchestration.flows import dataforge_batch_flow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dataforge-orchestrate",
        description="Run a DataForge batch pipeline with Prefect observability and retries.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser(
        "run",
        help="Run one Bronze/Silver/Gold batch pipeline flow.",
    )
    run_parser.add_argument("--input", required=True, help="Directory containing CSV/JSONL files.")
    run_parser.add_argument("--output", required=True, help="Directory for generated data layers.")
    run_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Python log verbosity (default: INFO).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        result = dataforge_batch_flow(args.input, args.output)
    except Exception as exc:
        print(f"DataForge orchestration failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
