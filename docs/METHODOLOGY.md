# Data contract and processing methodology

## Domain: synthetic mobility trips

The included CSV and JSONL files are synthetic development fixtures. Each record represents one trip.

Required fields:

| Field | Meaning | Rule |
|---|---|---|
| trip_id | Stable trip identifier | Required and unique |
| started_at | Trip start timestamp | Parseable timestamp |
| ended_at | Trip end timestamp | Parseable and later than start |
| start_station_id | Origin station identifier | Required |
| end_station_id | Destination station identifier | Required |
| member_type | Rider category | `member` or `casual` |

Additional source columns are preserved in Bronze but are not part of the canonical Silver table unless explicitly added to its data contract.

## Quality outcomes

Row-level quality issues are recorded using stable reason codes:

- `missing_trip_id`
- `missing_start_station_id`
- `missing_end_station_id`
- `missing_member_type`
- `duplicate_trip_id`
- `invalid_started_at`
- `invalid_ended_at`
- `non_positive_duration`
- `unsupported_member_type`

One rejected record can have multiple reason codes. A schema-level missing required column is treated as a source contract failure instead of quarantining every row.

## Layer definitions

- Bronze: ingested source values plus immutable source metadata for traceability.
- Silver: validated and normalized trip records with UTC timestamps, derived duration, trip date and source lineage.
- Gold: aggregate daily metrics by starting station.

## Gold metrics

The first Gold model groups by `trip_date` and `start_station_id`. It calculates trip count, average trip duration, member trip count, casual trip count and unique destination-station count.

These are examples of descriptive analytics and do not imply a causal or demand forecast.

## Reproducibility

Every input source is identified by a SHA-256 checksum. The manifest records source paths, checksums, file sizes, row counts, rejection reasons and output locations. The sample data is deterministic; pipeline run IDs and ingestion timestamps are generated at execution time.

## Benchmark methodology

Performance benchmarks are not included as pre-filled claims. Future benchmark runs should record:
- operating system and CPU / RAM,
- Python and dependency versions,
- number of source files and bytes,
- total input rows,
- run duration and rows per second,
- layer output sizes,
- DuckDB query and result details.

Use the same input files and environment for before/after comparisons.
