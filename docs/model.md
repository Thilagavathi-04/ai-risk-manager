# Model documentation

## Active model

The live production decision model for the AI Risk Manager demo is the boosted tree pipeline stored as `risk_model.joblib` in the application artifact bundle. The model artifact is produced by the training pipeline in `ml_pipeline/train.py`, and the runtime app reads that bundle via `ml_pipeline/artifacts.py`.

For comprehensive technical specifications, hyperparameter tables, and pipeline diagrams, see [MODEL_DETAILS.md](file:///Thilaga/Projects/ai-risk-manager/MODEL_DETAILS.md).

## Why this model is selected

The app uses the boosted tree over the logistic baseline because the boosted tree delivers materially better ranking and decision quality on the PaySim1 fraud task. In the current recorded evaluation:

- Boosted tree: Precision 91.2%, Recall 78.6%, F1 84.4%, PR-AUC 89.1%
- Logistic regression baseline: Precision 86.4%, Recall 72.1%, F1 78.7%, PR-AUC 83.0%

This matters because fraud-risk scoring is a ranked prioritization problem: increasing PR-AUC and precision helps the reviewer focus on the most likely frauds while reducing expected review cost. The boosted tree also captures nonlinear interactions among transaction amount, balances, and transfer patterns that the linear baseline tends to smooth over.

## Artifact provenance

The runtime metadata is loaded from the MLflow artifact metadata and the latest MLflow run stored under `mlruns/`. The app surfaces the active model name, version, run name, and artifact URI directly in the Settings screen. The metadata contract is intentionally read from the actual artifact location rather than hard-coded UI values.

## Model family and version

- Model family: HistGradientBoostingClassifier
- Model version: ai-risk-manager-v1
- Experiment: ai-risk-manager-paysim1
- Run name: train_pipeline
- Decision threshold: 0.72

## Operational note

The model is a demonstration product model for defensive merchant-risk decision support. It is designed to rank suspicious payments and direct them into manual review, not to provide unsafe fraud evasion guidance or production-grade transaction policy logic.
