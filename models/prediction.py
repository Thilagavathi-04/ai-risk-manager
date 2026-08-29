from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    step: int = Field(ge=0)
    transaction_type: str = Field(alias="type")
    amount: float = Field(gt=0)
    oldbalanceOrg: float = Field(ge=0)
    newbalanceOrig: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)
    newbalanceDest: float = Field(ge=0)


class PredictionResponse(BaseModel):
    risk_score: float
    risk_level: str
    recommended_action: str
    threshold: float
    model_version: str
    reasons: list[str]
