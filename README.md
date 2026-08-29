# AI Risk Manager

AI Risk Manager is a defensive merchant-risk workflow for payment transactions. It helps assess whether a payment is likely legitimate or risky, surfaces the main factors behind that decision, and supports a review workflow for potentially risky transactions.

## High-level project view

The project combines three layers:

- Web app layer: FastAPI + Jinja2 server-rendered dashboard and transaction review screens
- ML layer: training, evaluation, and inference for a fraud-risk model
- Data layer: SQLite-backed persistence, artifact loading, and experiment tracking

The MVP is intentionally defense-only and product-focused. It is designed to demonstrate a merchant risk workflow without exposing attack guidance or unsafe bypass content.

## What the app includes

- Dashboard home page with summary stats
- Transaction queue and transaction detail pages
- Review queue and reviewer outcome submission flow
- Evaluation page with model metrics and threshold/cost overview
- Audit log and settings pages
- REST health and metrics endpoints

## Tech stack

- Python 3.12
- FastAPI
- Jinja2 templates
- `uv` for environment management
- scikit-learn for model training and evaluation
- MLflow for experiment tracking
- KaggleHub PaySim1 dataset for the demo workflow

## Repository layout

- [main.py](main.py): app entry point and FastAPI factory
- [routes](routes): HTTP routes for pages and API endpoints
- [db](db): SQLite-backed repository layer
- [models](models): Pydantic models for app data
- [ml_pipeline](ml_pipeline): training, feature, evaluation, and inference logic
- [notebooks](notebooks): experiment notebook(s)
- [templates](templates): UI pages
- [docs](docs): product and model documentation
- [tests](tests): app-level smoke tests

## Run the app

From the project root:

```bash
uv sync --python 3.12
uv run ai-risk-manager
```

Then open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/transactions
- http://127.0.0.1:8000/reviews

## Run the ML workflow

```bash
uv run python -m ml_pipeline
```

This runs the pipeline entry point and writes model artifacts used by the app.

## Dataset note

The demo uses the KaggleHub PaySim1 dataset, specifically the file `PS_20174392719_1491204439457_log.csv`.

This is a synthetic fraud simulation dataset for experimentation and product demo work. It should not be treated as real production merchant or payment data.

## Testing

Run the full validation suite:

```bash
uv run pytest
```

For a focused app and end-to-end module validation pass:

```bash
uv run pytest tests/test_app.py tests/test_full_application.py -q
```

## Model selection and rationale

The active model is the boosted tree pipeline saved to the MLflow run artifacts and loaded from the runtime artifact bundle. It is preferred over the logistic baseline because it produces better PR-AUC and lower expected review cost while handling non-linear transaction risk patterns more effectively.

See [docs/model.md](docs/model.md) for the full model rationale and artifact provenance.

## Notes

This project is a working MVP oriented toward the PRD, with an emphasis on a defensible payment-risk workflow and a review-driven merchant experience. The application includes a logging layer, SQLite-backed repository persistence, a CSV validation workflow in the settings UI, and module-level validation coverage for the core flow.
