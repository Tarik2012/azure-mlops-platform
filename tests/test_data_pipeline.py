from pathlib import Path

import pandas as pd

from src.data import ingest, preprocess, validate
from src.data.schema import FEATURE_COLUMNS, TARGET_COLUMN


def test_data_pipeline_generates_and_validates_expected_files(
    tmp_path, monkeypatch
) -> None:
    raw_path = tmp_path / "data" / "raw" / "iris.csv"
    processed_path = tmp_path / "data" / "processed" / "iris_processed.csv"

    monkeypatch.setattr(ingest, "RAW_IRIS_PATH", raw_path)
    monkeypatch.setattr(validate, "RAW_IRIS_PATH", raw_path)
    monkeypatch.setattr(preprocess, "RAW_IRIS_PATH", raw_path)
    monkeypatch.setattr(preprocess, "PROCESSED_IRIS_PATH", processed_path)

    generated_path = ingest.save_raw_dataset(raw_path)

    assert generated_path == raw_path
    assert raw_path.exists()

    validate.validate_raw_dataset()

    preprocess.preprocess_dataset()

    assert processed_path.exists()

    processed_dataframe = pd.read_csv(processed_path)
    assert list(processed_dataframe.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
