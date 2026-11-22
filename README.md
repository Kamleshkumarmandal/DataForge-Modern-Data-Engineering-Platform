# DataForge

**Modern Data Engineering & Pipeline Observability Platform**

DataForge is a portfolio-grade batch data platform that moves raw source files through validated Bronze, cleaned Silver, and analytics-ready Gold layers. It is designed to demonstrate the practical work behind dependable analytics: ingestion, schema validation, data quality, transformations, storage, lineage, reproducibility, and operational visibility.

> **Project status:** the repository includes a runnable local batch pipeline and an optional Prefect orchestration layer. The current implementation focuses on CSV/JSONL ingestion, a mobility-trips sample dataset, Parquet storage, DuckDB analytics, quality checks, quarantine output, run manifests, Prefect flow/task tracking, task retries, and failure-attempt manifests. Cloud schedules, dbt models, PostgreSQL serving, API, and dashboard integration remain planned milestones.

## Why DataForge

DataForge is intentionally different from analytics and prediction applications in this portfolio. Its central deliverable is the data platform itself: repeatable pipelines that convert source records into trustworthy, traceable datasets.

## First release scope

- Discover and ingest CSV and newline-delimited JSON (JSONL) files.
- Preserve source records and source-file metadata in a Bronze layer.
- Validate required fields, timestamps, identifiers, duplicate keys, and trip duration.
- Separate rejected records into a quarantine dataset with explicit quality reasons.
- Normalize valid records into a Silver Parquet dataset.
- Build Gold daily station-level aggregates.
- Publish the analytics tables into a local DuckDB database.
- Write a machine-readable run manifest with source hashes, row counts, quality outcomes, and output paths.
- Run the pipeline from a CLI and test its data contracts.
- Optionally orchestrate runs with Prefect flow/task tracking, retries, logs, and failed-attempt manifests.

## Architecture

```text
CSV / JSONL source files
          |
          v
     File discovery
          |
          v
      BRONZE LAYER
  Raw records + source metadata
          |
          v
   Schema & quality checks
       /          \
      v            v
   QUARANTINE   valid records
                   |
                   v
             SILVER LAYER
         Normalized Parquet data
                   |
                   v
             GOLD LAYER
       Daily station-level metrics
                   |
          +--------+--------+
          |                 |
          v                 v
      DuckDB tables     Run manifest
          |
          v
   Downstream analytics
```

## Technology

| Area | Technology |
|---|---|
| Language | Python 3.11+ |
| Ingestion / transforms | pandas |
| Columnar storage | Apache Parquet / PyArrow |
| Analytical database | DuckDB |
| Pipeline entry point | Python CLI and optional Prefect flow |
| Tests | pytest |
| Quality automation | GitHub Actions |
| Orchestration | Prefect 3 (optional local flow; managed schedules planned) |
| Next-stage transformations | dbt Core with DuckDB (planned) |
| Serving layer | FastAPI and PostgreSQL (planned) |
| User interface | React + TypeScript (planned) |
| Packaging / local environment | Docker Compose (planned) |

## Repository layout

```text
.
├── dataforge/
│   ├── ingestion/       # Source discovery and file readers
│   ├── quality/         # Data quality rules and outcomes
│   ├── transforms/      # Bronze, Silver and Gold transformations
│   ├── storage/         # Parquet and DuckDB persistence
│   ├── observability/   # Run manifests and metadata
│   ├── pipeline.py      # Pipeline orchestration
│   └── cli.py           # Command-line interface
├── sample_data/
│   └── input/           # Small synthetic mobility-trip input files
├── tests/               # Unit and integration tests
├── docs/                # Architecture, methodology, setup and roadmap
├── .github/workflows/   # CI
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Quick start

Clone the repository:

```bash
git clone https://github.com/Kamleshkumarmandal/DataForge-Modern-Data-Engineering-Platform.git
cd DataForge-Modern-Data-Engineering-Platform
```

Create an environment and install dependencies:

**Windows PowerShell**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Run the sample pipeline directly:

```bash
python -m dataforge.cli run --input sample_data/input --output data
```

Run the same pipeline through Prefect, with a tracked flow run, task logs and automatic retries:

```bash
pip install -r requirements-orchestration.txt
python -m dataforge.orchestration.cli run --input sample_data/input --output data
```

The Prefect task retries twice (after 5 and 15 seconds) if an attempt fails. Each failed attempt writes a separate failure manifest under `data/runs/`. Local on-demand orchestration is implemented; cloud schedules and deployed workers are not yet included.

Inspect the generated folders:

- `data/bronze/` — ingested source rows and source metadata.
- `data/silver/` — validated and normalized rows.
- `data/gold/` — daily station-level aggregates.
- `data/quarantine/` — rejected records and quality reasons.
- `data/warehouse.duckdb` — local analytical database.
- `data/runs/` — JSON pipeline run manifests.

Run tests:

```bash
pytest -q
```

See [docs/SETUP.md](docs/SETUP.md) for complete setup instructions and [docs/ROADMAP.md](docs/ROADMAP.md) for planned milestones.

## Data quality and reliability

The initial data contract checks for required columns, missing trip identifiers, duplicate trip identifiers, invalid timestamps, missing station identifiers, and non-positive trip duration. Invalid rows are quarantined rather than silently discarded. Each run records file hashes and quality outcomes so a result can be traced to its inputs.

The included mobility-trip files are synthetic examples created for local development. They are not real ridership records and must not be represented as an external benchmark.

## Evaluation plan

The project will report measured ingestion rows/second, run duration, output file sizes, rejected-row rate, repeat-run behaviour, and DuckDB query latency. Measurements will be recorded with the machine and dataset details used. No performance figures are claimed until benchmark runs are completed.

## Development principles

- Make pipelines deterministic and rerunnable.
- Never silently discard invalid records.
- Keep source data, transformed data, and aggregate outputs separate.
- Store raw input data and generated artifacts locally; do not commit private or large data.
- Track lineage from generated outputs to source files and run identifiers.
- Keep credentials and deployment secrets out of Git.

## License

MIT. See [LICENSE](LICENSE).
