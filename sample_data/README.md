# Sample data

The files in `input/` are small synthetic mobility-trip fixtures created for development and automated tests. They are not real passenger, customer or transit records and must not be represented as a public benchmark.

The fixture set intentionally includes both accepted and rejected rows:
- valid CSV and JSONL records,
- a malformed start timestamp,
- a trip whose end precedes its start,
- a trip ID duplicated across source files.

This allows a local pipeline run to demonstrate source discovery, lineage, validation, quarantine, Bronze/Silver/Gold outputs and DuckDB publishing without downloading external data.
