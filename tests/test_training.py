from pathlib import Path

from src.config.settings import settings
from src.data import ingest, preprocess
from src.data.schema import FEATURE_COLUMNS, TARGET_COLUMN, TARGET_NAMES
from src.training.data_loader import load_training_data


def test_load_training_data_returns_expected_splits(tmp_path, monkeypatch) -> None:
    raw_path = tmp_path / "data" / "raw" / "iris.csv"
    processed_path = tmp_path / "data" / "processed" / "iris_processed.csv"

    monkeypatch.setattr(ingest, "RAW_IRIS_PATH", raw_path)
    monkeypatch.setattr(preprocess, "RAW_IRIS_PATH", raw_path)
    monkeypatch.setattr(preprocess, "PROCESSED_IRIS_PATH", processed_path)
    monkeypatch.setattr(settings, "PROCESSED_IRIS_PATH", processed_path)

    if not processed_path.exists():
        ingest.save_raw_dataset(raw_path)
        preprocess.preprocess_dataset()

    X_train, X_test, y_train, y_test, target_names = load_training_data()

    assert not X_train.empty
    assert not X_test.empty
    assert list(X_train.columns) == FEATURE_COLUMNS
    assert list(X_test.columns) == FEATURE_COLUMNS
    assert not y_train.empty
    assert not y_test.empty
    assert target_names == TARGET_NAMES


def test_model_path_points_to_expected_location() -> None:
    assert settings.MODEL_PATH == settings.PROJECT_ROOT / Path("models/iris_model.joblib")
