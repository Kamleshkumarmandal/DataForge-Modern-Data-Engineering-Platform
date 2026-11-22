# Prefect scheduled deployment

DataForge includes a version-controlled Prefect deployment definition in the repository root. It describes a daily mobility batch deployment that uses a **process work pool** and pulls the public GitHub repository when a scheduled run starts.

The schedule is deliberately **inactive by default**. Creating the deployment does not activate recurring runs. Enable it explicitly after confirming the worker, input data and output storage are configured.

## What this deployment does

- Runs `dataforge/orchestration/flows.py:dataforge_batch_flow`.
- Uses the existing sample input directory `sample_data/input`.
- Writes scheduled outputs to `data/scheduled/`.
- Requests a daily run at 06:00 in `Asia/Kolkata`.
- Uses the `dataforge-process-pool` work pool and the `default` queue.
- Pulls the public `main` branch and installs dependencies from `requirements-orchestration.txt` at run time.
- Leaves the recurring schedule inactive until explicitly enabled.

Prefect schedules create scheduled flow runs; a worker is separately responsible for executing them. See the [Prefect schedule documentation](https://docs.prefect.io/v3/concepts/schedules) and [deployment configuration guide](https://docs.prefect.io/v3/how-to-guides/deployments/).

## Prerequisites

- Python 3.11 or newer.
- Git installed on the machine that will run the worker.
- A Prefect Cloud account, or a reachable self-hosted Prefect server.
- This public GitHub repository available to the worker.
- A machine that remains online while scheduled work should execute.

## 1. Install orchestration dependencies

From the repository root:

```bash
pip install -r requirements-orchestration.txt
```

## 2. Connect to Prefect Cloud

For the simplest hosted scheduler, sign in to Prefect Cloud:

```bash
prefect cloud login
```

Follow the browser prompts and select the intended workspace. Do not commit API keys or paste them into source files. If using a self-hosted server instead, configure `PREFECT_API_URL` according to your server setup.

## 3. Create the process work pool

Create the work pool once:

```bash
prefect work-pool create --type process dataforge-process-pool
```

If the pool already exists, keep using it rather than recreating it.

## 4. Register the deployment

Run from the repository root:

```bash
prefect deploy --name dataforge-daily-batch
```

Prefect reads `prefect.yaml`, registers the deployment, and stores its inactive schedule. The schedule is configured for 06:00 daily in India Standard Time (Asia/Kolkata), but it will not create recurring runs until activated.

## 5. Start a worker

On the machine that should execute the pipeline, start:

```bash
prefect worker start --pool dataforge-process-pool
```

Keep this process running. A deployment schedule can create a run even when no worker is available, but the run will wait in the work pool until a worker polls and executes it.

The process worker runs code on the machine where it is started. The generated Parquet files, DuckDB database and run manifests are written to that machine's local `data/scheduled/` directory. They are not automatically uploaded to cloud object storage or a database. Use a persistent worker host and back up the output directory if you need durable outputs.

## 6. Test the deployment before enabling the schedule

In Prefect Cloud, open the `dataforge-daily-batch` deployment and trigger a manual run. Confirm that:
- The flow and task complete successfully.
- The worker logs show the source files and row counts.
- `data/scheduled/bronze/`, `silver/`, `gold/`, `quarantine/`, `warehouse.duckdb`, and `runs/` are created on the worker host.

Only after a successful manual run should you activate the daily schedule in the Prefect UI. You can also edit `active: false` to `active: true` in `prefect.yaml` and redeploy, but do not activate both methods independently.

## Operational notes

- The sample source records are synthetic portfolio fixtures. The same deployment will process the repository's sample data until the input parameter is changed to a mounted, persistent data directory.
- The scheduled example is a full-refresh batch run, not a live data connector or CDC pipeline.
- A process worker is not a serverless service. It needs an always-on host to execute scheduled jobs.
- The schedule does not guarantee execution if the worker is offline.
- The schedule is inactive by default to avoid surprise recurring jobs or unnecessary compute.
