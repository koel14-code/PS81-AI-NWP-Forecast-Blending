"""
Meteorological Verification & Skill Metrics Module for PS81 Blending Engine.

Computes continuous metrics (MAE, RMSE, Bias, Pearson Correlation) and
categorical contingency metrics (POD, FAR, CSI) for precipitation evaluation.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def calculate_continuous_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes continuous error and correlation metrics.

    Args:
        y_true: Ground truth / reference values (ERA5 precipitation in mm/h).
        y_pred: Forecast / blended precipitation values (mm/h).

    Returns:
        Dict with keys: MAE, RMSE, Bias, Pearson_r
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    errors = y_pred - y_true
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    bias = float(np.mean(errors))

    # Pearson correlation coefficient
    if len(y_true) > 1 and np.std(y_true) > 1e-8 and np.std(y_pred) > 1e-8:
        r_val, _ = pearsonr(y_true, y_pred)
        corr = float(r_val) if not np.isnan(r_val) else 0.0
    else:
        corr = 0.0

    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "Bias": round(bias, 4),
        "Pearson_r": round(corr, 4),
    }


def calculate_categorical_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, threshold: float = 1.0
) -> Dict[str, float]:
    """
    Computes 2x2 contingency table metrics for a specified rainfall threshold.

    Project Analytical Thresholds (e.g. >= 1.0 mm/h):
    - Hits (a): y_true >= threshold and y_pred >= threshold
    - False Alarms (b): y_true < threshold and y_pred >= threshold
    - Misses (c): y_true >= threshold and y_pred < threshold
    - Correct Negatives (d): y_true < threshold and y_pred < threshold

    Metrics:
    - POD (Probability of Detection) = a / (a + c)
    - FAR (False Alarm Ratio)        = b / (a + b)
    - CSI (Critical Success Index)   = a / (a + b + c)

    Returns:
        Dict with keys: POD, FAR, CSI
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    obs_event = y_true >= threshold
    fcst_event = y_pred >= threshold

    a = np.sum(obs_event & fcst_event)  # Hits
    b = np.sum((~obs_event) & fcst_event)  # False Alarms
    c = np.sum(obs_event & (~fcst_event))  # Misses

    pod = float(a / (a + c)) if (a + c) > 0 else 0.0
    far = float(b / (a + b)) if (a + b) > 0 else 0.0
    csi = float(a / (a + b + c)) if (a + b + c) > 0 else 0.0

    return {
        "POD": round(pod, 4),
        "FAR": round(far, 4),
        "CSI": round(csi, 4),
    }
