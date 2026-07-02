"""Prediction helpers backed by the trained Iris model."""

from __future__ import annotations

from typing import Any
import warnings

import joblib

from src.config.settings import settings
from src.data.schema import FEATURE_COLUMNS, TARGET_NAMES


def load_trained_model() -> Any:
    """Load the trained model artifact from disk."""
    if not settings.MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model file not found. Run python scripts/run_local_pipeline.py first."
        )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Setting the shape on a NumPy array has been deprecated.*",
            category=DeprecationWarning,
        )
        return joblib.load(settings.MODEL_PATH)


def get_prediction_label(prediction: int) -> str:
    """Map a numeric class prediction to a human-readable Iris label."""
    prediction_index = int(prediction)
    if prediction_index < 0 or prediction_index >= len(TARGET_NAMES):
        raise ValueError(f"Unsupported prediction value: {prediction_index}")
    return TARGET_NAMES[prediction_index]


def predict_single(features: list[float]) -> dict[str, int | str]:
    """Run inference for a single Iris feature vector."""
    if len(features) != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Expected exactly {len(FEATURE_COLUMNS)} features: {FEATURE_COLUMNS}"
        )

    model = load_trained_model()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names.*",
            category=UserWarning,
        )
        prediction = int(model.predict([features])[0])

    return {
        "prediction": prediction,
        "prediction_label": get_prediction_label(prediction),
    }


def predict(features: list[float]) -> int:
    """Backward-compatible numeric prediction helper used by the API layer."""
    return int(predict_single(features)["prediction"])


if __name__ == "__main__":
    features = [5.1, 3.5, 1.4, 0.2]
    prediction_result = predict_single(features)

    print(f"features: {features}")
    print(f"prediction: {prediction_result['prediction']}")
    print(f"prediction_label: {prediction_result['prediction_label']}")
