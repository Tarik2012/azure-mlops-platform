"""Project data contract for the Iris dataset."""

FEATURE_COLUMNS = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]

TARGET_COLUMN = "target"
HUMAN_READABLE_TARGET_COLUMN = "target_name"

EXPECTED_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN, HUMAN_READABLE_TARGET_COLUMN]

EXPECTED_DTYPES = {
    "sepal_length": "numeric",
    "sepal_width": "numeric",
    "petal_length": "numeric",
    "petal_width": "numeric",
    TARGET_COLUMN: "integer",
    HUMAN_READABLE_TARGET_COLUMN: "string/object",
}

TARGET_NAMES = ["setosa", "versicolor", "virginica"]
VALID_TARGET_VALUES = list(range(len(TARGET_NAMES)))
