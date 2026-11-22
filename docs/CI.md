# Continuous integration

GitHub Actions runs the DataForge test workflow on pushes to `main` and pull requests targeting `main`.

The workflow:
1. Checks out the repository.
2. Sets up Python 3.11.
3. Installs the project and development dependencies.
4. Compiles the `dataforge` package and tests.
5. Runs the complete pytest suite.

Run the same checks locally:

```bash
pip install -r requirements-dev.txt
pip install -e .
python -m compileall -q dataforge tests
pytest -q
```

The integration test executes the supplied sample inputs and verifies Bronze/Silver/Gold Parquet outputs, quarantine counts, the JSON run manifest and DuckDB table contents.
