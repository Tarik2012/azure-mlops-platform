"""Portable Iris training entrypoint for local and Azure ML command jobs."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import mlflow
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

MODEL_FILENAME = "model.joblib"


def _configure_local_tracking(output_dir: Path) -> None:
    """Use SQLite locally while preserving Azure ML's injected tracking URI."""
    current_uri = mlflow.get_tracking_uri()
    if current_uri.startswith("file:") or current_uri in {"mlruns", "./mlruns"}:
        database_path = (output_dir.parent / "mlflow.db").resolve().as_posix()
        mlflow.set_tracking_uri(f"sqlite:///{database_path}")


def train_model(
    model_output: str | Path,
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict[str, float]:
    """Train and track an Iris classifier, returning its evaluation metrics."""
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be greater than 0 and less than 1")

    output_dir = Path(model_output)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / MODEL_FILENAME
    _configure_local_tracking(output_dir)

    dataset = load_iris(as_frame=True)
    features = dataset.data
    target = dataset.target
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )

    n_estimators = 100
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
    )

    with mlflow.start_run(run_name="iris-random-forest") as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "f1_macro": float(f1_score(y_test, predictions, average="macro")),
        }

        joblib.dump(model, model_path)

        mlflow.log_params(
            {
                "dataset": "sklearn.datasets.load_iris",
                "model_type": type(model).__name__,
                "n_estimators": n_estimators,
                "random_state": random_state,
                "test_size": test_size,
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(model_path), artifact_path="model")

        print(f"accuracy: {metrics['accuracy']:.4f}")
        print(f"f1_macro: {metrics['f1_macro']:.4f}")
        print(f"model_path: {model_path}")
        print(f"mlflow_run_id: {run.info.run_id}")

    return metrics


def parse_args() -> argparse.Namespace:
    """Parse command-line options for local or Azure ML execution."""
    parser = argparse.ArgumentParser(description="Train an Iris model with MLflow")
    parser.add_argument(
        "--model-output",
        type=Path,
        required=True,
        help="Directory in which to write the trained model artifact.",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    """Run training from CLI arguments."""
    args = parse_args()
    train_model(
        model_output=args.model_output,
        test_size=args.test_size,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
