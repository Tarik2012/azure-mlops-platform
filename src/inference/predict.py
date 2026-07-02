"""Prediction helpers."""


def predict(features: list[float]) -> float:
    """Return a deterministic placeholder prediction."""
    if not features:
        return 0.0
    return float(sum(features) / len(features))
