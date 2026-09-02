# Setup and Run Guide

## Requirements

- Python 3.12
- uv
- local project environment

## Installation

From the project root:

```bash
uv sync --python 3.12
```

## Run the app

```bash
uv run ai-risk-manager
```

Then browse:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/transactions
- http://127.0.0.1:8000/reviews
- http://127.0.0.1:8000/settings

## Run the ML training pipeline

```bash
uv run python -m ml_pipeline
```

This step trains the ten-model sweep, logs metrics and artifacts under `mlruns/`, and saves the selected production model bundle in `artifacts/`.

## Run the MLflow UI

From the repository root:

```bash
uv run mlflow ui --backend-store-uri mlruns
```

If you start the UI from `frontend/`, point it back to the repo-root store:

```bash
uv run mlflow ui --backend-store-uri ../mlruns
```

The selected production run logs summary metrics on the parent run, while the per-model sweeps appear as nested runs.

## Run tests

```bash
uv run pytest -q
```

## Frequently used checks

- app smoke: `uv run pytest tests/test_app.py -q`
- full validation: `uv run pytest -q`

## Notes

- This project depends on the PaySim1 dataset and local MLflow artifact tracking.
- The app is intended for demo and review workflows, not for production fraud decisioning in a live financial environment.
