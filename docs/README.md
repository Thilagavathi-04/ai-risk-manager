# AI Risk Manager Documentation

This folder contains the working project documentation for the AI Risk Manager application.

## Contents

- [prd.md](prd.md) — product requirements, user goals, scope, and acceptance criteria
- [architecture.md](architecture.md) — system layout, modules, ML pipeline, and runtime flow
- [design.md](design.md) — UI/UX direction, dashboard patterns, and visual system
- [model.md](model.md) — active model, metadata, and rationale for the chosen model
- [setup.md](setup.md) — environment setup, local run instructions, and validation commands

## Project summary

AI Risk Manager is a defensive transaction-risk dashboard built with FastAPI, Jinja2, SQLite, and scikit-learn. It models fraud-like risk on payment transactions and supports a human review flow for suspicious values.

The application is designed for a merchant-risk demo workflow:

- score a transaction
- explain the risk reason
- compare model performance
- inspect the active model metadata
- perform review decisions and audit the outcome

## Quick start

From the repository root:

```bash
uv sync --python 3.12
uv run ai-risk-manager
```

Then open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/transactions
- http://127.0.0.1:8000/settings

## ML pipeline

```bash
uv run python -m ml_pipeline
```

This trains the model and stores the artifact bundle used by the app.

## Validation

```bash
uv run pytest -q
```

## Important note

The project is intentionally framed as a defensive merchant-risk decision-support system and not as a general-purpose fraud evasion or attack tool.
