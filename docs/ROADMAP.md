# DataForge roadmap

## Milestone 1 — Reproducible batch core
- [x] Public GitHub repository and project overview.
- [x] CSV, JSONL and NDJSON source discovery.
- [x] SHA-256 source-file lineage.
- [x] Bronze ingestion layer.
- [x] Required-column and row-level quality checks.
- [x] Quarantine output with reason codes.
- [x] Silver normalized trip layer.
- [x] Gold daily station aggregates.
- [x] Parquet outputs and DuckDB tables.
- [x] JSON run manifests.
- [x] Synthetic sample data and end-to-end tests.
- [ ] Verify GitHub Actions on the latest commit.

## Milestone 2 — Production-shaped orchestration
- [ ] Add typed configuration and environment-based settings.
- [x] Introduce a Prefect batch flow and observable pipeline task.
- [x] Add task retries and per-attempt failure manifests.
- [x] Add version-controlled Prefect deployment configuration with an inactive daily schedule.
- [ ] Register the deployment in Prefect Cloud and validate a manual scheduled-deployment run.
- [ ] Run a persistent worker and explicitly enable recurring scheduling.
- [ ] Add managed run history and richer operational metrics.
- [ ] Add richer pipeline run history and structured operational metrics.
- [ ] Add structured logs and operational metrics.
- [ ] Add idempotent incremental ingestion checkpoints.

## Milestone 3 — Analytics engineering
- [ ] Add dbt Core project using DuckDB.
- [ ] Move Gold models into versioned SQL models.
- [ ] Add dbt schema tests and documentation.
- [ ] Add source freshness and model lineage.

## Milestone 4 — Serving and application
- [ ] Add FastAPI endpoints for runs, datasets and data-quality outcomes.
- [ ] Add PostgreSQL metadata / serving integration.
- [ ] Add React pipeline monitoring dashboard.
- [ ] Add authentication and access controls before shared deployment.

## Milestone 5 — Portfolio release
- [ ] Add a reproducible benchmark suite.
- [ ] Capture architecture and pipeline screenshots.
- [ ] Publish measured throughput and query metrics.
- [ ] Add Docker Compose for the complete local stack.
- [ ] Add deployment and troubleshooting guides.
- [ ] Tag a versioned release.

Checked items describe repository components already added. Planned items are not yet implemented and should not be presented as completed resume achievements.
