"""Read-only profiling for the raw Iris dataset."""

import pandas as pd

from src.config.settings import RAW_IRIS_PATH
from src.data.schema import FEATURE_COLUMNS, HUMAN_READABLE_TARGET_COLUMN


def profile_dataset(dataframe: pd.DataFrame) -> None:
    """Print a lightweight profile of the dataset."""
    print(f"Shape: {dataframe.shape}")
    print(f"Columns: {list(dataframe.columns)}")
    print("Dtypes:")
    print(dataframe.dtypes)
    print("Nulls by column:")
    print(dataframe.isna().sum())
    print(f"{HUMAN_READABLE_TARGET_COLUMN} distribution:")
    print(dataframe[HUMAN_READABLE_TARGET_COLUMN].value_counts(dropna=False))
    print("Feature summary:")
    print(dataframe[FEATURE_COLUMNS].describe())


def main() -> None:
    dataframe = pd.read_csv(RAW_IRIS_PATH)
    profile_dataset(dataframe)


if __name__ == "__main__":
    main()
