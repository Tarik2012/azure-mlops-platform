from pathlib import Path

import mlflow

from src.training.train_azureml import MODEL_FILENAME, train_model


def test_train_model_creates_artifact_and_returns_metrics(tmp_path: Path) -> None:
    tracking_dir = tmp_path / "mlruns"
    model_output = tmp_path / "model-output"
    mlflow.set_tracking_uri(tracking_dir.resolve().as_uri())

    metrics = train_model(
        model_output=model_output,
        test_size=0.25,
        random_state=7,
    )

    model_path = model_output / MODEL_FILENAME
    assert model_path.is_file()
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1_macro"] <= 1.0
