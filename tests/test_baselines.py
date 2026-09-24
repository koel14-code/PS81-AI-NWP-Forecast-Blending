import pandas as pd

from src.blending.baselines import (
    compute_simple_ensemble,
    compute_historical_weighted_ensemble,
)

def test_simple_ensemble():
    df = pd.DataFrame({
        "ECMWF_IFS_precip": [10.0],
        "NOAA_GFS_precip": [20.0],
        "DWD_ICON_precip": [30.0],
    })

    result = compute_simple_ensemble(df)

    assert result[0] == 20.0

def test_historical_weighted_ensemble():
    df = pd.DataFrame({
        "ECMWF_IFS_precip": [10.0],
        "NOAA_GFS_precip": [20.0],
        "DWD_ICON_precip": [30.0],
        "ECMWF_IFS_rolling_mae": [1.0],
        "NOAA_GFS_rolling_mae": [2.0],
        "DWD_ICON_rolling_mae": [4.0],
    })

    result = compute_historical_weighted_ensemble(df)

    blended_forecast = result[0]
    weights = result[1]

    assert len(blended_forecast) == 1
    assert abs(weights.sum(axis=1).iloc[0] - 1.0) < 1e-6