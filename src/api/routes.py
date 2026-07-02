"""API route definitions."""

from fastapi import APIRouter, HTTPException

from src.api.model_loader import (
    get_model_name,
    get_model_path,
    get_model_version,
    model_exists,
)
from src.api.schemas import (
    HealthResponse,
    IrisPredictionRequest,
    IrisPredictionResponse,
    ModelInfoResponse,
)
from src.inference.predict import predict_single


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="azure-mlops-platform-api",
    )


@router.get("/model-info", response_model=ModelInfoResponse, tags=["model"])
def get_model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        model_name=get_model_name(),
        model_version=get_model_version(),
        model_path=get_model_path(),
        model_exists=model_exists(),
    )


@router.post("/predict", response_model=IrisPredictionResponse, tags=["inference"])
def predict_route(payload: IrisPredictionRequest) -> IrisPredictionResponse:
    features = [
        payload.sepal_length,
        payload.sepal_width,
        payload.petal_length,
        payload.petal_width,
    ]

    try:
        prediction_result = predict_single(features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IrisPredictionResponse(
        prediction=prediction_result["prediction"],
        prediction_label=prediction_result["prediction_label"],
        model_name=get_model_name(),
        model_version=get_model_version(),
    )
