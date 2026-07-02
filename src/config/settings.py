"""Application settings."""

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


def _resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return BASE_DIR / path


@dataclass(slots=True)
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "mlops-azure-fastapi-demo")
    PROJECT_ROOT: Path = BASE_DIR
    MODEL_DIR: Path = _resolve_project_path(os.getenv("MODEL_DIR", "models"))
    MODEL_PATH: Path = _resolve_project_path(
        os.getenv("MODEL_PATH", "models/iris_model.joblib")
    )
    MLFLOW_EXPERIMENT_NAME: str = os.getenv(
        "MLFLOW_EXPERIMENT_NAME",
        "iris-local-training",
    )
    MLFLOW_DB_PATH: Path = _resolve_project_path(
        os.getenv("MLFLOW_DB_PATH", "mlflow.db")
    )
    MLFLOW_ARTIFACTS_DIR: Path = _resolve_project_path(
        os.getenv("MLFLOW_ARTIFACTS_DIR", "mlartifacts")
    )
    RAW_DATA_DIR: Path = _resolve_project_path(os.getenv("RAW_DATA_DIR", "data/raw"))
    PROCESSED_DATA_DIR: Path = _resolve_project_path(
        os.getenv("PROCESSED_DATA_DIR", "data/processed")
    )
    RAW_IRIS_PATH: Path = _resolve_project_path(
        os.getenv("RAW_IRIS_PATH", "data/raw/iris.csv")
    )
    PROCESSED_IRIS_PATH: Path = _resolve_project_path(
        os.getenv("PROCESSED_IRIS_PATH", "data/processed/iris_processed.csv")
    )

    @property
    def MLFLOW_TRACKING_URI(self) -> str:
        return f"sqlite:///{self.MLFLOW_DB_PATH.resolve().as_posix()}"

    @property
    def MLFLOW_ARTIFACTS_URI(self) -> str:
        return self.MLFLOW_ARTIFACTS_DIR.resolve().as_uri()


settings = Settings()

# Backward-compatible module-level aliases for data pipeline modules.
RAW_DATA_DIR = settings.RAW_DATA_DIR
PROCESSED_DATA_DIR = settings.PROCESSED_DATA_DIR
RAW_IRIS_PATH = settings.RAW_IRIS_PATH
PROCESSED_IRIS_PATH = settings.PROCESSED_IRIS_PATH
