"""Local training entrypoint with MLflow tracking."""

import joblib
import mlflow
from sklearn.ensemble import RandomForestClassifier

from src.config.settings import settings
from src.training.data_loader import load_training_data
from src.training.evaluate import evaluate_model


def train_model() -> None:
    """Train a simple RandomForest model on the Iris dataset."""
    n_estimators = 100
    random_state = 42
    test_size = 0.2
    model_path = settings.MODEL_PATH

    model_path.parent.mkdir(parents=True, exist_ok=True)
    settings.MLFLOW_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    settings.MLFLOW_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    experiment = mlflow.get_experiment_by_name(settings.MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        mlflow.create_experiment(
            name=settings.MLFLOW_EXPERIMENT_NAME,
            artifact_location=settings.MLFLOW_ARTIFACTS_URI,
        )
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)

    X_train, X_test, y_train, y_test, target_names = load_training_data()

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
    )

    with mlflow.start_run() as run:
        model.fit(X_train, y_train)

        metrics = evaluate_model(model, X_test, y_test)

        joblib.dump(model, model_path)

        mlflow.log_params(
            {
                "n_estimators": n_estimators,
                "random_state": random_state,
                "test_size": test_size,
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_param("target_names", ",".join(target_names))
        mlflow.log_artifact(str(model_path), artifact_path="model")

        print(f"accuracy: {metrics['accuracy']:.4f}")
        print(f"model_path: {model_path}")
        print(f"mlflow_run_id: {run.info.run_id}")


if __name__ == "__main__":
    train_model()
