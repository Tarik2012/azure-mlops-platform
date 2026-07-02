import pytest

from src.config.settings import settings
from src.data.schema import TARGET_NAMES
from src.inference.predict import predict_single


def test_predict_single_returns_expected_payload() -> None:
    if not settings.MODEL_PATH.exists():
        pytest.skip("Model artifact not available. Run the local pipeline first.")

    prediction_result = predict_single([5.1, 3.5, 1.4, 0.2])

    assert isinstance(prediction_result, dict)
    assert isinstance(prediction_result["prediction"], int)
    assert prediction_result["prediction_label"] in TARGET_NAMES


@pytest.mark.parametrize(
    "features",
    [
        [5.1, 3.5, 1.4],
        [5.1, 3.5, 1.4, 0.2, 0.9],
    ],
)
def test_predict_single_validates_feature_count(features: list[float]) -> None:
    with pytest.raises(ValueError):
        predict_single(features)
