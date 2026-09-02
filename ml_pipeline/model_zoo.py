from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from imblearn.ensemble import BalancedRandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier


FALSE_POSITIVE_COST = 20.0
FALSE_NEGATIVE_COST = 500.0
MANUAL_REVIEW_COST = 10.0


@dataclass(frozen=True)
class ModelSpec:
    model_name: str
    model_family: str
    builder: Callable[[pd.Series], BaseEstimator]


@dataclass(frozen=True)
class SplitMetrics:
    precision: float
    recall: float
    f1: float
    pr_auc: float
    roc_auc: float
    expected_cost: float


@dataclass(frozen=True)
class CandidateResult:
    model_name: str
    model_family: str
    threshold: float
    validation: SplitMetrics
    test: SplitMetrics
    mlflow_run_id: str
    mlflow_run_name: str
    artifact_path: str
    is_selected: bool = False

    def to_metadata(self) -> dict[str, object]:
        return {
            "model_name": self.model_name,
            "model_family": self.model_family,
            "threshold": round(self.threshold, 6),
            "mlflow_run_id": self.mlflow_run_id,
            "mlflow_run_name": self.mlflow_run_name,
            "artifact_path": self.artifact_path,
            "is_selected": self.is_selected,
            "validation": {
                "precision": round(self.validation.precision, 4),
                "recall": round(self.validation.recall, 4),
                "f1": round(self.validation.f1, 4),
                "pr_auc": round(self.validation.pr_auc, 4),
                "roc_auc": round(self.validation.roc_auc, 4),
                "expected_cost": round(self.validation.expected_cost, 2),
            },
            "test": {
                "precision": round(self.test.precision, 4),
                "recall": round(self.test.recall, 4),
                "f1": round(self.test.f1, 4),
                "pr_auc": round(self.test.pr_auc, 4),
                "roc_auc": round(self.test.roc_auc, 4),
                "expected_cost": round(self.test.expected_cost, 2),
            },
        }


class IsolationForestRiskAdapter(BaseEstimator, ClassifierMixin):
    def __init__(self, contamination: float, random_state: int = 42) -> None:
        self.contamination = contamination
        self.random_state = random_state
        self.estimator = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=300,
            max_samples="auto",
        )
        self.score_min_: float | None = None
        self.score_max_: float | None = None

    def fit(self, X, y=None):
        self.estimator.fit(X)
        return self

    def calibrate(self, X) -> "IsolationForestRiskAdapter":
        risk_scores = self._raw_scores(X)
        self.score_min_ = float(np.min(risk_scores))
        self.score_max_ = float(np.max(risk_scores))
        return self

    def _raw_scores(self, X) -> np.ndarray:
        return -self.estimator.decision_function(X)

    def _risk_probabilities(self, X) -> np.ndarray:
        risk_scores = self._raw_scores(X)
        if self.score_min_ is None or self.score_max_ is None:
            self.score_min_ = float(np.min(risk_scores))
            self.score_max_ = float(np.max(risk_scores))

        score_range = self.score_max_ - self.score_min_
        if score_range <= 0:
            return np.full(len(risk_scores), 0.5, dtype=float)
        return np.clip((risk_scores - self.score_min_) / score_range, 0.0, 1.0)

    def predict_proba(self, X):
        probabilities = self._risk_probabilities(X)
        return np.column_stack([1.0 - probabilities, probabilities])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def _class_imbalance_weight(labels: pd.Series) -> float:
    positive = max(1, int(labels.sum()))
    negative = max(1, int(len(labels) - labels.sum()))
    return negative / positive


def _contamination_rate(labels: pd.Series) -> float:
    ratio = float(labels.mean()) if len(labels) else 0.01
    return max(0.01, min(0.2, ratio if ratio > 0 else 0.01))


def build_model_specs() -> list[ModelSpec]:
    return [
        ModelSpec(
            model_name="XGBoost",
            model_family="XGBClassifier",
            builder=lambda y: XGBClassifier(
                n_estimators=120,
                learning_rate=0.05,
                max_depth=5,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_lambda=1.0,
                random_state=42,
                eval_metric="logloss",
                tree_method="hist",
                scale_pos_weight=_class_imbalance_weight(y),
            ),
        ),
        ModelSpec(
            model_name="LightGBM",
            model_family="LGBMClassifier",
            builder=lambda y: LGBMClassifier(
                n_estimators=120,
                learning_rate=0.05,
                num_leaves=24,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                class_weight="balanced",
                verbose=-1,
            ),
        ),
        ModelSpec(
            model_name="CatBoost",
            model_family="CatBoostClassifier",
            builder=lambda y: CatBoostClassifier(
                iterations=120,
                learning_rate=0.05,
                depth=5,
                loss_function="Logloss",
                random_seed=42,
                verbose=False,
                auto_class_weights="Balanced",
            ),
        ),
        ModelSpec(
            model_name="HistGradientBoosting",
            model_family="HistGradientBoostingClassifier",
            builder=lambda y: HistGradientBoostingClassifier(
                max_depth=5,
                learning_rate=0.08,
                max_iter=120,
                random_state=42,
            ),
        ),
        ModelSpec(
            model_name="Random Forest",
            model_family="RandomForestClassifier",
            builder=lambda y: RandomForestClassifier(
                n_estimators=120,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced_subsample",
            ),
        ),
        ModelSpec(
            model_name="Extra Trees",
            model_family="ExtraTreesClassifier",
            builder=lambda y: ExtraTreesClassifier(
                n_estimators=120,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced",
            ),
        ),
        ModelSpec(
            model_name="Balanced Random Forest",
            model_family="BalancedRandomForestClassifier",
            builder=lambda y: BalancedRandomForestClassifier(
                n_estimators=120,
                random_state=42,
                n_jobs=-1,
                replacement=False,
            ),
        ),
        ModelSpec(
            model_name="Logistic Regression",
            model_family="LogisticRegression",
            builder=lambda y: LogisticRegression(
                max_iter=1500,
                class_weight="balanced",
                solver="lbfgs",
            ),
        ),
        ModelSpec(
            model_name="MLP Neural Network",
            model_family="MLPClassifier",
            builder=lambda y: MLPClassifier(
                hidden_layer_sizes=(48, 24),
                activation="relu",
                alpha=0.0005,
                learning_rate_init=0.0015,
                max_iter=160,
                early_stopping=True,
                random_state=42,
            ),
        ),
        ModelSpec(
            model_name="Isolation Forest",
            model_family="IsolationForest",
            builder=lambda y: IsolationForestRiskAdapter(
                contamination=_contamination_rate(y),
                random_state=42,
            ),
        ),
    ]


def build_candidate_model(spec: ModelSpec, train_labels: pd.Series) -> BaseEstimator:
    return spec.builder(train_labels)


def predict_positive_probabilities(model: BaseEstimator, features) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.asarray(model.predict_proba(features))[:, 1]
    if hasattr(model, "decision_function"):
        raw_scores = np.asarray(model.decision_function(features), dtype=float)
        return 1.0 / (1.0 + np.exp(-raw_scores))
    if hasattr(model, "score_samples"):
        raw_scores = np.asarray(model.score_samples(features), dtype=float)
        return 1.0 / (1.0 + np.exp(-raw_scores))
    raise AttributeError("Model does not expose a supported probability or scoring method")


def evaluate_predictions(y_true, probabilities, threshold: float) -> SplitMetrics:
    predictions = (np.asarray(probabilities) >= threshold).astype(int)
    y_true_array = np.asarray(y_true).astype(int)
    precision = precision_score(y_true_array, predictions, zero_division=0)
    recall = recall_score(y_true_array, predictions, zero_division=0)
    f1 = f1_score(y_true_array, predictions, zero_division=0)
    pr_auc = average_precision_score(y_true_array, probabilities)
    roc_auc = roc_auc_score(y_true_array, probabilities)
    false_positives = int(((predictions == 1) & (y_true_array == 0)).sum())
    false_negatives = int(((predictions == 0) & (y_true_array == 1)).sum())
    predicted_positive = int((predictions == 1).sum())
    expected_cost = (
        false_positives * FALSE_POSITIVE_COST
        + false_negatives * FALSE_NEGATIVE_COST
        + predicted_positive * MANUAL_REVIEW_COST
    )
    return SplitMetrics(
        precision=precision,
        recall=recall,
        f1=f1,
        pr_auc=pr_auc,
        roc_auc=roc_auc,
        expected_cost=expected_cost,
    )


def select_threshold(y_true, probabilities) -> tuple[float, float]:
    best_threshold = 0.5
    best_cost = float("inf")
    for threshold in np.linspace(0.05, 0.95, 91):
        metrics = evaluate_predictions(y_true, probabilities, float(threshold))
        if metrics.expected_cost < best_cost - 1e-9:
            best_threshold = float(threshold)
            best_cost = metrics.expected_cost
    return best_threshold, best_cost


def calibrate_isolation_forest(model: BaseEstimator, validation_features) -> BaseEstimator:
    if isinstance(model, IsolationForestRiskAdapter):
        model.calibrate(validation_features)
    return model


def leaderboard_row(result: CandidateResult) -> dict[str, object]:
    return {
        "model_name": result.model_name,
        "model_family": result.model_family,
        "mlflow_run_id": result.mlflow_run_id,
        "threshold": round(result.threshold, 6),
        "validation_precision": f"{result.validation.precision:.1%}",
        "validation_recall": f"{result.validation.recall:.1%}",
        "validation_f1": f"{result.validation.f1:.1%}",
        "validation_pr_auc": f"{result.validation.pr_auc:.1%}",
        "validation_roc_auc": f"{result.validation.roc_auc:.1%}",
        "validation_expected_cost": f"₹{result.validation.expected_cost:,.0f}",
        "test_precision": f"{result.test.precision:.1%}",
        "test_recall": f"{result.test.recall:.1%}",
        "test_f1": f"{result.test.f1:.1%}",
        "test_pr_auc": f"{result.test.pr_auc:.1%}",
        "test_roc_auc": f"{result.test.roc_auc:.1%}",
        "test_expected_cost": f"₹{result.test.expected_cost:,.0f}",
        "artifact_path": result.artifact_path,
        "is_selected": result.is_selected,
    }