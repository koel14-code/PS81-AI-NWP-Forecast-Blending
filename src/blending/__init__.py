"""
PS81 Forecast Blending Engine Package.

Modules:
- baselines: Chronological data splitting, dataset pivoting, simple average & historical error weighting.
- ml_blender: Adaptive ML error-prediction models & normalized weight generation.
- evaluation: Continuous (MAE, RMSE, Bias, Correlation) & Categorical (POD, FAR, CSI) metrics.
"""

from src.blending.baselines import (
    split_data_chronologically,
    pivot_aligned_dataset,
    compute_simple_ensemble,
    compute_historical_weighted_ensemble,
)
from src.blending.ml_blender import AdaptiveMLBlender
from src.blending.evaluation import (
    calculate_continuous_metrics,
    calculate_categorical_metrics,
)

__all__ = [
    "split_data_chronologically",
    "pivot_aligned_dataset",
    "compute_simple_ensemble",
    "compute_historical_weighted_ensemble",
    "AdaptiveMLBlender",
    "calculate_continuous_metrics",
    "calculate_categorical_metrics",
]
