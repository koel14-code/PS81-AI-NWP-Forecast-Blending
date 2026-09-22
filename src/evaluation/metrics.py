from __future__ import annotations

import numpy as np


def rainfall_metrics(y_true, y_pred):
    """Compute basic continuous verification metrics for rainfall forecasts."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_true.shape != y_pred.shape:
        raise ValueError("y_true and y_pred must have the same shape.")

    errors = y_pred - y_true
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    mae = float(np.mean(np.abs(errors)))
    bias = float(np.mean(y_pred - y_true))
    return {"rmse": rmse, "mae": mae, "bias": bias}
