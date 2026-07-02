"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel


class IrisPredictionRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class IrisPredictionResponse(BaseModel):
    prediction: int
    prediction_label: str
    model_name: str
    model_version: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    model_path: str
    model_exists: bool


class HealthResponse(BaseModel):
    status: str
    service: str
