"""Model evaluation helpers."""

from sklearn.metrics import accuracy_score


def evaluate_model(model, X_test, y_test) -> dict[str, float]:
    """Evaluate a trained classifier on the test split."""
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    return {"accuracy": float(accuracy)}
