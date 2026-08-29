from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud",
}


def validate_dataset(frame: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    if frame.empty:
        raise ValueError("Dataset is empty")
    if frame["isFraud"].nunique() < 2:
        raise ValueError("Target requires both classes")
