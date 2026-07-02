"""Ingest the raw Iris dataset into the project data directory."""

from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris

from src.config.settings import RAW_IRIS_PATH
from src.data.schema import (
    FEATURE_COLUMNS,
    HUMAN_READABLE_TARGET_COLUMN,
    TARGET_COLUMN,
    TARGET_NAMES,
)


def build_iris_dataframe() -> pd.DataFrame:
    """Load Iris from scikit-learn and normalize it to the project schema."""
    dataset = load_iris()
    dataframe = pd.DataFrame(dataset.data, columns=FEATURE_COLUMNS)
    dataframe[TARGET_COLUMN] = dataset.target.astype(int)
    dataframe[HUMAN_READABLE_TARGET_COLUMN] = dataframe[TARGET_COLUMN].map(
        dict(enumerate(TARGET_NAMES))
    )
    return dataframe


def save_raw_dataset(output_path: Path = RAW_IRIS_PATH) -> Path:
    """Persist the raw Iris dataset as CSV."""
    dataframe = build_iris_dataframe()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)

    print(f"Generated CSV path: {output_path}")
    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")

    return output_path


def main() -> None:
    save_raw_dataset()


if __name__ == "__main__":
    main()
