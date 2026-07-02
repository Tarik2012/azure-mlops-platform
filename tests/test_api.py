from fastapi.testclient import TestClient
import pytest

from src.api.main import app
from src.config.settings import settings
from src.data.schema import TARGET_NAMES


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "azure-mlops-platform-api",
    }


def test_model_info_endpoint_returns_metadata() -> None:
    response = client.get("/model-info")

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_name"] == "iris_random_forest"
    assert payload["model_version"] == "0.1.0"
    assert payload["model_path"]
    assert isinstance(payload["model_exists"], bool)


def test_predict_endpoint_returns_prediction() -> None:
    if not settings.MODEL_PATH.exists():
        pytest.skip("Model artifact not available. Run the local pipeline first.")

    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["prediction"], int)
    assert payload["prediction_label"] in TARGET_NAMES
    assert payload["model_name"] == "iris_random_forest"
    assert payload["model_version"] == "0.1.0"
