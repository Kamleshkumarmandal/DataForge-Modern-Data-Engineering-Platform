# DataForge local setup

## Requirements

- Python 3.11 or newer.
- Git.
- Windows PowerShell, macOS Terminal or Linux shell.
- Internet access for installing Python packages.

## 1. Clone

```bash
git clone https://github.com/Kamleshkumarmandal/DataForge-Modern-Data-Engineering-Platform.git
cd DataForge-Modern-Data-Engineering-Platform
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install project and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 3. Run the sample pipeline

From the repository root:

```bash
python -m dataforge.cli run --input sample_data/input --output data
```

On success, the CLI prints a JSON summary containing the run ID, source file checksums, row counts, data-quality results and output paths.

## 4. Explore the output

```text
data/
├── bronze/trips.parquet
├── silver/trips.parquet
├── gold/daily_station_metrics.parquet
├── quarantine/rejected_trips.parquet
├── warehouse.duckdb
└── runs/<run-id>.json
```

Use Python to inspect Parquet:

```python
import pandas as pd

silver = pd.read_parquet("data/silver/trips.parquet")
gold = pd.read_parquet("data/gold/daily_station_metrics.parquet")
print(silver.head())
print(gold.head())
```

Query DuckDB:

```python
import duckdb

with duckdb.connect("data/warehouse.duckdb", read_only=True) as connection:
    print(connection.sql("SELECT * FROM gold_daily_station_metrics").df())
```

## 5. Run tests

```bash
pytest -q
```

Compile the package:

```bash
python -m compileall -q dataforge tests
```

## 6. Run your own files

Create a folder containing CSV, JSONL or NDJSON files that follow the mobility-trip contract in [METHODOLOGY.md](METHODOLOGY.md), then pass that folder to `--input`.

```bash
python -m dataforge.cli run --input path/to/my/files --output path/to/output
```

The first version expects one consistent trip schema across source files. Files missing required columns fail the run. Invalid rows are quarantined with quality reason codes.

## Generated data

The `data/` output directory is excluded from Git. Never commit private, regulated, or large source datasets, credentials, or generated warehouse databases.
