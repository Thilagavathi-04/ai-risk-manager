from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


DROP_COLUMNS = ["isFraud", "isFlaggedFraud", "nameOrig", "nameDest"]


@dataclass(frozen=True)
class FeatureSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def add_target(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["label"] = result["isFraud"].astype(int)
    return result


def temporal_split(frame: pd.DataFrame, train_ratio: float = 0.7, validation_ratio: float = 0.15) -> FeatureSplit:
    ordered = frame.sort_values(["step"]).reset_index(drop=True)
    train_end = int(len(ordered) * train_ratio)
    validation_end = int(len(ordered) * (train_ratio + validation_ratio))
    return FeatureSplit(
        train=ordered.iloc[:train_end].copy(),
        validation=ordered.iloc[train_end:validation_end].copy(),
        test=ordered.iloc[validation_end:].copy(),
    )


def feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column not in DROP_COLUMNS + ["label"]]
