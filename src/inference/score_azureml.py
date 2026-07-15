"""Azure ML managed online endpoint scoring entrypoint."""

from __future__ import annotations

import json
import os
from numbers import Real
from pathlib import Path
from typing import Any

import joblib

FEATURE_NAMES = (
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
)
MODEL_FILENAME = "model.joblib"

_model: Any | None = None


def init() -> None:
    """Load the registered model once when the inference container starts."""
    global _model

    model_dir = os.getenv("AZUREML_MODEL_DIR")
    if not model_dir:
        raise RuntimeError("AZUREML_MODEL_DIR is not set")

    model_path = Path(model_dir) / MODEL_FILENAME
    if not model_path.is_file():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")

    try:
        _model = joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to load model artifact: {model_path}") from exc


def _parse_payload(raw_data: Any) -> dict[str, Any]:
    if isinstance(raw_data, bytes):
        raw_data = raw_data.decode("utf-8")

    if isinstance(raw_data, str):
        try:
            raw_data = json.loads(raw_data)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Request body is not valid JSON: {exc.msg}") from exc

    if not isinstance(raw_data, dict):
        raise ValueError("Request body must be a JSON object")

    return raw_data


def _validate_record(record: Any) -> list[float]:
    if not isinstance(record, (list, tuple)):
        raise ValueError("Each data record must be an array of four numbers")
    if len(record) != len(FEATURE_NAMES):
        raise ValueError(
            f"Each data record must contain exactly {len(FEATURE_NAMES)} values"
        )
    if any(not isinstance(value, Real) or isinstance(value, bool) for value in record):
        raise ValueError("All Iris feature values must be numbers")
    return [float(value) for value in record]


def _extract_records(payload: dict[str, Any]) -> list[list[float]]:
    if "data" in payload:
        data = payload["data"]
        if not isinstance(data, list) or not data:
            raise ValueError("The 'data' field must be a non-empty array of records")
        return [_validate_record(record) for record in data]

    missing = [name for name in FEATURE_NAMES if name not in payload]
    if missing:
        raise ValueError(
            "Request must contain either 'data' or all Iris features; "
            f"missing: {', '.join(missing)}"
        )

    return [_validate_record([payload[name] for name in FEATURE_NAMES])]


def _json_value(value: Any) -> Any:
    """Convert NumPy scalar-like predictions to standard Python values."""
    return value.item() if hasattr(value, "item") else value


def run(raw_data: Any) -> dict[str, list[Any]]:
    """Validate an inference request and return JSON-serializable predictions."""
    if _model is None:
        raise RuntimeError("Model is not initialized; init() must complete before run()")

    payload = _parse_payload(raw_data)
    records = _extract_records(payload)

    try:
        predictions = _model.predict(records)
    except Exception as exc:
        raise RuntimeError("Model prediction failed") from exc

    return {"predictions": [_json_value(value) for value in predictions]}
