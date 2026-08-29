import json
from pathlib import Path

import joblib
import pandas as pd
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from db.repositories.app_repository import SQLiteAppRepository
from logging_config import configure_logging
from main import create_app
from ml_pipeline.data_validation import validate_dataset
from ml_pipeline.features import add_target, feature_columns, temporal_split
from ml_pipeline.predict import predict_row
from ml_pipeline.preprocessing import build_preprocessor


def _sample_transaction_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "step": 1,
                "type": "CASH_OUT",
                "amount": 1000,
                "nameOrig": "A",
                "oldbalanceOrg": 2000,
                "newbalanceOrig": 1000,
                "nameDest": "B",
                "oldbalanceDest": 0,
                "newbalanceDest": 1000,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            },
            {
                "step": 2,
                "type": "TRANSFER",
                "amount": 8000,
                "nameOrig": "C",
                "oldbalanceOrg": 5000,
                "newbalanceOrig": 500,
                "nameDest": "D",
                "oldbalanceDest": 100,
                "newbalanceDest": 8200,
                "isFraud": 1,
                "isFlaggedFraud": 0,
            },
            {
                "step": 3,
                "type": "PAYMENT",
                "amount": 2500,
                "nameOrig": "E",
                "oldbalanceOrg": 5000,
                "newbalanceOrig": 2500,
                "nameDest": "F",
                "oldbalanceDest": 1000,
                "newbalanceDest": 3500,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            },
            {
                "step": 4,
                "type": "CASH_IN",
                "amount": 1500,
                "nameOrig": "G",
                "oldbalanceOrg": 3000,
                "newbalanceOrig": 4500,
                "nameDest": "H",
                "oldbalanceDest": 2000,
                "newbalanceDest": 3500,
                "isFraud": 1,
                "isFlaggedFraud": 0,
            },
            {
                "step": 5,
                "type": "DEBIT",
                "amount": 1200,
                "nameOrig": "I",
                "oldbalanceOrg": 4000,
                "newbalanceOrig": 2800,
                "nameDest": "J",
                "oldbalanceDest": 1000,
                "newbalanceDest": 2200,
                "isFraud": 0,
                "isFlaggedFraud": 0,
            },
            {
                "step": 6,
                "type": "TRANSFER",
                "amount": 9100,
                "nameOrig": "K",
                "oldbalanceOrg": 6000,
                "newbalanceOrig": 1200,
                "nameDest": "L",
                "oldbalanceDest": 400,
                "newbalanceDest": 9500,
                "isFraud": 1,
                "isFlaggedFraud": 0,
            },
        ]
    )


def test_configure_logging_sets_up_handlers() -> None:
    logger = configure_logging()
    assert logger.name == "ai_risk_manager"
    assert logger.level == 20
    assert any(handler.__class__.__name__ == "StreamHandler" for handler in logger.handlers)


def test_dataset_validation_and_feature_split() -> None:
    frame = _sample_transaction_frame()
    validate_dataset(frame)

    annotated = add_target(frame)
    split = temporal_split(annotated)
    assert set(split.train.columns) == set(annotated.columns)
    assert len(split.test) > 0
    assert feature_columns(annotated)


def test_preprocessor_and_predict_pipeline() -> None:
    frame = _sample_transaction_frame()
    features = feature_columns(frame)
    train_data = frame.iloc[:4].copy()

    numeric_columns = ["amount", "step", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    categorical_columns = [column for column in features if column not in numeric_columns]
    preprocessor = build_preprocessor(numeric_columns, categorical_columns)
    X_train = train_data[features]
    y_train = train_data["isFraud"].astype(int)
    transformed = preprocessor.fit_transform(X_train)
    assert transformed.shape[0] == len(X_train)

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])
    model.fit(X_train, y_train)

    temp_dir = Path("/tmp/ai_risk_manager_tests")
    temp_dir.mkdir(exist_ok=True)
    model_path = temp_dir / "test_model.joblib"
    threshold_path = temp_dir / "test_threshold.json"
    joblib.dump(model, model_path)
    threshold_path.write_text(json.dumps({"threshold": 0.5}), encoding="utf-8")

    payload = pd.DataFrame({
        "step": [6],
        "type": ["TRANSFER"],
        "amount": [9100],
        "nameOrig": ["K"],
        "oldbalanceOrg": [6000],
        "newbalanceOrig": [1200],
        "nameDest": ["L"],
        "oldbalanceDest": [400],
        "newbalanceDest": [9500],
    })
    risk_score = float(model.predict_proba(payload)[:, 1][0])
    assert 0.0 <= risk_score <= 1.0
    assert predict_row(model_path, threshold_path, payload).risk_level in {"LOW", "MEDIUM", "HIGH"}


def test_sqlite_repository_persists_review_updates(tmp_path: Path) -> None:
    db_path = tmp_path / "repo.db"
    repo = SQLiteAppRepository(db_path)
    repo.record_review("TX1001", "Confirm risky")
    transaction = repo.get_transaction("TX1001")
    assert transaction.review_status == "Confirm risky"
    assert repo.list_reviews()[0].status == "Confirm risky"


def test_app_routes_and_health() -> None:
    client = TestClient(create_app())
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    metrics = client.get("/api/v1/metrics")
    assert metrics.status_code == 200
    assert metrics.json()["transactions"] == 12482

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "ai-risk-manager" in dashboard.text.lower()

    review_response = client.post(
        "/reviews/TX1001",
        data={"reviewer_outcome": "Confirm risky"},
    )
    assert review_response.status_code == 200
    assert "Confirm risky" in review_response.text
