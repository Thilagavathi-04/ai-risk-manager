from __future__ import annotations

from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from ml_pipeline.data_ingestion import load_raw_data
from ml_pipeline.features import add_target, feature_columns, temporal_split


def evaluate(model_path: Path, threshold: float) -> dict[str, float]:
    raw_frame = load_raw_data()
    frame = add_target(raw_frame)
    split = temporal_split(frame)
    model = joblib.load(model_path)
    features = feature_columns(frame)
    X_test = split.test[features]
    y_test = split.test["label"]
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= threshold).astype(int)
    metrics = {
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "pr_auc": average_precision_score(y_test, probabilities),
        "roc_auc": roc_auc_score(y_test, probabilities),
    }
    confusion_matrix(y_test, predictions)
    mlflow.log_metrics(metrics)
    return metrics
