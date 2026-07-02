"""Helpers for loading model artifacts."""

from pathlib import Path


MODELS_DIR = Path("models")
DEFAULT_MODEL_FILE = MODELS_DIR / "model.joblib"


def load_model_path() -> Path:
    """Return the default local model path."""
    return DEFAULT_MODEL_FILE


def get_model_version() -> str:
    """Return a placeholder model version."""
    return "dev"
