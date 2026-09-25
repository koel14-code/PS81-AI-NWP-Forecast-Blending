"""
PS81 Feature Engineering Package.

Exports feature generation modules for time features, lead-time features,
leakage-free rolling historical model errors, rainfall regime categorization,
and one-hot model encodings.
"""

from src.features.rainfall_features import (
    compute_time_features,
    compute_lead_features,
    compute_rainfall_regime,
    compute_rolling_historical_error,
    encode_models,
    generate_feature_dataset,
)

__all__ = [
    "compute_time_features",
    "compute_lead_features",
    "compute_rainfall_regime",
    "compute_rolling_historical_error",
    "encode_models",
    "generate_feature_dataset",
]
