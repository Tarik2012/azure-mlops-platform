"""Helpers for exposing model metadata to the API layer."""

from src.config.settings import settings


MODEL_NAME = "iris_random_forest"
MODEL_VERSION = "0.1.0"


def get_model_name() -> str:
    """Return the API-facing model name."""
    return MODEL_NAME


def get_model_version() -> str:
    """Return the API-facing model version."""
    return MODEL_VERSION


def get_model_path() -> str:
    """Return the configured local model artifact path."""
    return str(settings.MODEL_PATH)


def model_exists() -> bool:
    """Return whether the trained model artifact is available."""
    return settings.MODEL_PATH.exists()
