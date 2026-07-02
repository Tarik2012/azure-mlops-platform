"""Preprocess the raw Iris dataset into the training-ready dataset."""

import pandas as pd

from src.config.settings import PROCESSED_IRIS_PATH, RAW_IRIS_PATH
from src.data.schema import FEATURE_COLUMNS, TARGET_COLUMN
from src.data.validate import validate_dataframe


def preprocess_dataset() -> None:
    dataframe = pd.read_csv(RAW_IRIS_PATH)
    validate_dataframe(dataframe)

    processed_dataframe = dataframe[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()
    PROCESSED_IRIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    processed_dataframe.to_csv(PROCESSED_IRIS_PATH, index=False)

    print(f"Processed CSV path: {PROCESSED_IRIS_PATH}")
    print(f"Rows: {len(processed_dataframe)}")
    print(f"Columns: {len(processed_dataframe.columns)}")


def main() -> None:
    preprocess_dataset()


if __name__ == "__main__":
    main()
