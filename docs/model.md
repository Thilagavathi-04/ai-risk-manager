# Model documentation

## Active model

The live production decision model for the AI Risk Manager demo is the best-performing pipeline from the ten-model sweep stored as `risk_model.joblib` in the application artifact bundle. The model artifact is produced by the training pipeline in `ml_pipeline/train.py`, and the runtime app reads that bundle via `ml_pipeline/artifacts.py`.

For comprehensive technical specifications, hyperparameter tables, and pipeline diagrams, see [MODEL_DETAILS.md](file:///Thilaga/Projects/ai-risk-manager/MODEL_DETAILS.md).

## Why this model is selected

The app now compares ten candidate models on the same temporal split and promotes the winner by validation PR-AUC with expected cost as the tie-breaker. In the current sweep, LightGBM is selected as the production model.

The selection criteria still favor ranking and decision quality on the PaySim1 fraud task. That matters because fraud-risk scoring is a ranked prioritization problem: increasing PR-AUC and precision helps the reviewer focus on the most likely frauds while reducing expected review cost.

The sweep includes gradient-boosted trees, tree ensembles, linear baseline, MLP, and an anomaly detector so the production choice is based on measured evidence rather than a fixed default.

## Artifact provenance

The runtime metadata is loaded from the MLflow artifact metadata and the repo-root `mlruns/` store. The app surfaces the active model name, version, selected run name, selected threshold, and artifact URI directly in the Settings screen. The metadata contract is intentionally read from the actual artifact location rather than hard-coded UI values.

## Model family and version

- Model family: LightGBM
- Model version: ai-risk-manager-v2
- Experiment: ai-risk-manager-paysim1
- Run name: train_pipeline
- Decision threshold: derived from the validation sweep for the selected model

## Operational note

The model is a demonstration product model for defensive merchant-risk decision support. It is designed to rank suspicious payments and direct them into manual review, not to provide unsafe fraud evasion guidance or production-grade transaction policy logic.
