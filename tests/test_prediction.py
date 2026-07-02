from src.inference.predict import predict


def test_predict_returns_average_value() -> None:
    assert predict([1.0, 2.0, 3.0]) == 2.0
