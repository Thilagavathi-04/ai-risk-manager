# Architecture

## Overview

AI Risk Manager is a small full-stack ML product demo built around a FastAPI backend, Jinja templates for the web UI, SQLite persistence, and a scikit-learn training pipeline with MLflow artifact tracking.

## High-level architecture

```text
Browser
  │
  ▼
FastAPI app
  │
  ├── HTML routes (/dashboard, /transactions, /reviews, /settings)
  ├── JSON API (/api/v1/health, /api/v1/metrics, /api/v1/predict)
  └── service/repository layer
        │
        ├── SQLite repository
        ├── dashboard summary logic
        └── review/audit persistence

ML layer
  │
  ├── ingestion
  ├── validation
  ├── feature construction
  ├── multi-model training sweep
  ├── threshold selection
  └── artifact export

Artifacts tracked by MLflow
  │
  ├── risk_model.joblib
  ├── threshold.json
  ├── metadata.json
  ├── model_leaderboard.json
  └── MLflow run metadata under mlruns/
```

## Runtime components

### App layer

- `main.py` creates the FastAPI app and mounts the routers
- `routes/v1/` hosts page and API endpoints
- `templates/` contains the HTML views
- `static/` holds front-end assets

### Data layer

- SQLite is used for app persistence and review data
- `db/repositories/app_repository.py` owns transaction, review, audit, and settings state

### ML layer

- `ml_pipeline/data_ingestion.py` loads the dataset
- `ml_pipeline/data_validation.py` checks required fields and class balance
- `ml_pipeline/features.py` builds the feature set and temporal split
- `ml_pipeline/model_zoo.py` defines the candidate estimators and evaluation helpers
- `ml_pipeline/train.py` trains the ten-model sweep and selects the best production model
- `ml_pipeline/artifacts.py` loads saved artifacts and runtime metadata
- `ml_pipeline/predict.py` scores a transaction row and returns reasons

## Model selection flow

The training pipeline produces:

- ten tracked candidate models logged as nested MLflow runs
- a selected production model bundle
- a saved threshold
- a model metadata file with the leaderboard and selected run context

The app reads the active metadata and stores the selected model as the runtime model in use.

## Logging and observability

The app uses a central logger configured in `logging_config.py`. This is intended to keep application logs consistent across startup, ML runs, and the main request workflow.

## Design decisions

- Server-rendered HTML is preferred over a React SPA for speed and simplicity
- model metadata is sourced from artifacts and MLflow output rather than hard-coded UI values
- the app attempts to keep the product defensive and operationally explainable
