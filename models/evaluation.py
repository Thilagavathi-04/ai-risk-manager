from pydantic import BaseModel


class EvaluationMetric(BaseModel):
    label: str
    value: str


class ConfusionMatrixCell(BaseModel):
    row: str
    column: str
    value: str


class ThresholdCostPoint(BaseModel):
    threshold: str
    cost: str


class ModelComparisonRow(BaseModel):
    model_name: str
    precision: str
    recall: str
    f1: str
    pr_auc: str
    expected_cost: str
    is_selected: bool = False
