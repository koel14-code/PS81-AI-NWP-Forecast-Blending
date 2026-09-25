import numpy as np
import pandas as pd

from src.blending.ml_blender import AdaptiveMLBlender, MODEL_NAMES


def make_training_data():
    rows = []

    for model_name in MODEL_NAMES:
        for i in range(10):
            rows.append({
                "model": model_name,
                "lead_hours": float(i + 1),
                "lead_day": float((i + 1) / 24),
                "month": 7.0,
                "day_of_year": float(182 + i),
                "hour": float(i % 24),
                "latitude": 22.5,
                "longitude": 88.3,
                "precipitation": float(i + 1),
                "rolling_historical_mae_24h": float(i + 1) * 0.1,
                "ensemble_mean": float(i + 1),
                "ensemble_std": 0.5,
                "ensemble_range": 1.0,
                "absolute_error": float(i + 1) * 0.2,
            })

    return pd.DataFrame(rows)


def make_inference_data():
    return pd.DataFrame({
        "lead_hours": [1.0, 2.0],
        "lead_day": [1.0 / 24, 2.0 / 24],
        "month": [7.0, 7.0],
        "day_of_year": [182.0, 183.0],
        "hour": [1.0, 2.0],
        "latitude": [22.5, 22.5],
        "longitude": [88.3, 88.3],
        "ECMWF_IFS_precip": [10.0, 20.0],
        "NOAA_GFS_precip": [12.0, 18.0],
        "DWD_ICON_precip": [11.0, 19.0],
        "ECMWF_IFS_rolling_mae": [0.1, 0.2],
        "NOAA_GFS_rolling_mae": [0.2, 0.3],
        "DWD_ICON_rolling_mae": [0.3, 0.4],
    })


def test_ml_blender_fit():
    blender = AdaptiveMLBlender()
    blender.fit(make_training_data())

    assert blender.is_fitted is True
    assert set(blender.models.keys()) == set(MODEL_NAMES)


def test_ml_blender_weights():
    blender = AdaptiveMLBlender()
    blender.fit(make_training_data())

    blended, weights, predicted_errors = blender.predict_weights(
        make_inference_data()
    )

    assert len(blended) == 2
    assert weights.shape == (2, 3)
    assert predicted_errors.shape == (2, 3)

    assert (weights >= 0).all().all()
    assert (predicted_errors >= 0).all().all()

    weight_sums = weights.sum(axis=1)
    assert np.allclose(weight_sums, 1.0)