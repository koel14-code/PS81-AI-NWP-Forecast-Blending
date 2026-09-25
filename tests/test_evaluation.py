import numpy as np

from src.blending.evaluation import (
    calculate_continuous_metrics,
    calculate_categorical_metrics,
)
def test_continuous_metrics():
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 3.0, 2.0])

    metrics = calculate_continuous_metrics(y_true, y_pred)

    assert abs(metrics["MAE"] - (2 / 3)) < 1e-4
    assert abs(metrics["RMSE"] - np.sqrt(2 / 3)) < 1e-4
    assert metrics["Bias"] == 0.0
def test_categorical_metrics():
    y_true = np.array([0.0, 2.0, 3.0, 0.0])
    y_pred = np.array([0.0, 1.5, 0.5, 2.0])

    metrics = calculate_categorical_metrics(
        y_true,
        y_pred,
        threshold=1.0,
    )

    assert metrics["POD"] == 0.5
    assert metrics["FAR"] == 0.5
    assert abs(metrics["CSI"] - (1 / 3)) < 1e-4