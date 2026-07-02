"""Training data loading helpers."""

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config.settings import settings
from src.data.schema import FEATURE_COLUMNS, TARGET_COLUMN, TARGET_NAMES


def load_training_data() -> tuple:
    """Load the processed training dataset and return a deterministic split."""
    if not settings.PROCESSED_IRIS_PATH.exists():
        raise FileNotFoundError(
            "Processed dataset not found. Run python -m src.data.preprocess first."
        )

    dataframe = pd.read_csv(settings.PROCESSED_IRIS_PATH)
    features = dataframe[FEATURE_COLUMNS]
    target = dataframe[TARGET_COLUMN]

    stratify_target = None
    if target.nunique() > 1 and target.value_counts().min() >= 2:
        stratify_target = target

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=stratify_target,
    )

    return X_train, X_test, y_train, y_test, TARGET_NAMES
