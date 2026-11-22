# DataForge architecture

## First-release components

### Ingestion
Discovers local CSV, JSONL and NDJSON source files in stable path order. Each file receives a SHA-256 checksum, byte size and source format record. The reader preserves incoming fields; source metadata is attached when records enter Bronze.

### Bronze
The Bronze layer preserves ingested source columns and adds:
- relative source file path,
- source-file SHA-256,
- one-based source row number,
- ingestion timestamp in UTC.

It is an auditable copy of what the reader returned, not a place for business transformations.

### Quality gate
The mobility-trip contract checks required columns, blank identifiers, duplicate trip IDs, timestamp parsing, positive trip duration and supported rider categories. Missing required schema columns fail the run. Invalid individual records are written to a quarantine Parquet file with semicolon-separated issue codes.

### Silver
Silver is the canonical, validated trip table. It standardizes identifiers and rider categories, parses timestamps as UTC, computes duration and derives the trip date. Source lineage metadata is retained.

### Gold
Gold contains daily aggregates grouped by trip date and start-station identifier:
- trip count,
- average trip duration,
- member and casual trip counts,
- number of distinct destination stations.

### Warehouse
DuckDB receives two queryable tables: `silver_trips` and `gold_daily_station_metrics`. Parquet remains the portable file-based storage format.

### Observability
A run manifest records run ID, status, start and finish timestamps, duration, source file hashes, row counts, data-quality outcomes and output paths.

## Processing flow

```text
Local CSV / JSONL files
          |
          v
   Discovery + SHA-256
          |
          v
        Bronze
          |
          v
     Quality gate -------> Quarantine
          |
          v
        Silver
          |
          v
         Gold
          |
     +----+-----+
     |          |
     v          v
   DuckDB    Run manifest
```

## Idempotency and reruns

Each run uses a unique run ID and rewrites the current layer files and DuckDB tables for the selected input directory. Previous run manifests are retained. This is a full-refresh batch prototype, not an incremental change-data-capture engine yet. Re-running the same input should reproduce the same data content, while run IDs and ingestion timestamps naturally differ.

## Planned extensions

Prefect orchestration, dbt-managed SQL models, PostgreSQL serving, an API, UI, source API connectors and incremental checkpoints are follow-up milestones. They are not represented as implemented capabilities in the current CLI.
