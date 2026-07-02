"""API route definitions."""

from fastapi import APIRouter

from src.api.model_loader import get_model_version
from src.api.schemas import HealthResponse, PredictionRequest, PredictionResponse
from src.inference.predict import predict


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse()


@router.post("/predict", response_model=PredictionResponse, tags=["inference"])
def predict_route(payload: PredictionRequest) -> PredictionResponse:
    prediction = predict(payload.features)
    return PredictionResponse(
        prediction=prediction,
        model_version=get_model_version(),
    )
