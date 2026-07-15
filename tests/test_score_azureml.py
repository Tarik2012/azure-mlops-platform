"""Tests for the Azure ML online endpoint scoring entrypoint."""

from __future__ import annotations

import json

import joblib
import pytest
from sklearn.dummy import DummyClassifier

from src.inference import score_azureml


@pytest.fixture
def initialized_score(tmp_path, monkeypatch):
    model = DummyClassifier(strategy="constant", constant=0)
    model.fit(
        [[5.1, 3.5, 1.4, 0.2], [6.7, 3.1, 4.7, 1.5]],
        [0, 1],
    )
    joblib.dump(model, tmp_path / "model.joblib")
    monkeypatch.setenv("AZUREML_MODEL_DIR", str(tmp_path))

    score_azureml.init()
    return score_azureml


def test_run_accepts_data_records(initialized_score) -> None:
    result = initialized_score.run(
        json.dumps(
            {
                "data": [
                    [5.1, 3.5, 1.4, 0.2],
                    [6.7, 3.1, 4.7, 1.5],
                ]
            }
        )
    )

    assert result == {"predictions": [0, 0]}


def test_run_accepts_named_iris_record(initialized_score) -> None:
    result = initialized_score.run(
        {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        }
    )

    assert result == {"predictions": [0]}


def test_run_rejects_missing_features(initialized_score) -> None:
    with pytest.raises(ValueError, match="missing: petal_width"):
        initialized_score.run(
            {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
            }
        )


def test_run_rejects_invalid_json(initialized_score) -> None:
    with pytest.raises(ValueError, match="not valid JSON"):
        initialized_score.run("not-json")
