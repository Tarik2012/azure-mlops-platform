"""Validation for the raw Iris dataset against the project data contract."""

from typing import Iterable

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_object_dtype, is_string_dtype

from src.config.settings import RAW_IRIS_PATH
from src.data.schema import (
    EXPECTED_COLUMNS,
    FEATURE_COLUMNS,
    HUMAN_READABLE_TARGET_COLUMN,
    TARGET_COLUMN,
    TARGET_NAMES,
    VALID_TARGET_VALUES,
)


def _format_columns(columns: Iterable[str]) -> str:
    return ", ".join(columns)


def validate_dataframe(dataframe: pd.DataFrame) -> None:
    """Validate a dataframe against the project data contract."""
    if dataframe.empty:
        raise ValueError("Dataset must contain at least 1 row.")

    missing_columns = [column for column in EXPECTED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {_format_columns(missing_columns)}"
        )

    extra_columns = [column for column in dataframe.columns if column not in EXPECTED_COLUMNS]
    if extra_columns:
        print(f"Warning: unexpected extra columns detected: {_format_columns(extra_columns)}")

    null_counts = dataframe[EXPECTED_COLUMNS].isna().sum()
    columns_with_nulls = [column for column, count in null_counts.items() if count > 0]
    if columns_with_nulls:
        raise ValueError(f"Null values detected in columns: {_format_columns(columns_with_nulls)}")

    for feature_column in FEATURE_COLUMNS:
        if not is_numeric_dtype(dataframe[feature_column]):
            raise ValueError(f"Feature column '{feature_column}' must be numeric.")

    if not is_numeric_dtype(dataframe[TARGET_COLUMN]):
        raise ValueError(f"Target column '{TARGET_COLUMN}' must be numeric.")

    if not (dataframe[TARGET_COLUMN] % 1 == 0).all():
        raise ValueError(f"Target column '{TARGET_COLUMN}' must contain integer values only.")

    if not (is_string_dtype(dataframe[HUMAN_READABLE_TARGET_COLUMN]) or is_object_dtype(dataframe[HUMAN_READABLE_TARGET_COLUMN])):
        raise ValueError(
            f"Human-readable target column '{HUMAN_READABLE_TARGET_COLUMN}' must be string/object."
        )

    invalid_target_values = sorted(
        set(dataframe[TARGET_COLUMN].astype(int).tolist()) - set(VALID_TARGET_VALUES)
    )
    if invalid_target_values:
        raise ValueError(
            f"Invalid target values found: {invalid_target_values}. "
            f"Allowed values: {VALID_TARGET_VALUES}"
        )

    valid_target_names = set(TARGET_NAMES)
    invalid_target_names = sorted(
        set(dataframe[HUMAN_READABLE_TARGET_COLUMN].astype(str).tolist()) - valid_target_names
    )
    if invalid_target_names:
        raise ValueError(
            f"Invalid target_name values found: {invalid_target_names}. "
            f"Allowed values: {TARGET_NAMES}"
        )


def validate_raw_dataset() -> None:
    dataframe = pd.read_csv(RAW_IRIS_PATH)
    validate_dataframe(dataframe)
    print("Data validation passed")


def main() -> None:
    validate_raw_dataset()


if __name__ == "__main__":
    main()
