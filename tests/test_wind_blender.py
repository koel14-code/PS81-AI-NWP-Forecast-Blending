"""
SkyBlend AI — Unit Tests for Production Wind Blender
SIH Problem Statement PS81: Hybrid AI-NWP Multi-Model Forecast Blending System.

Validates HistoricalWeightedWindBlender:
1. Mathematical formula execution: w_m = 1 / (MAE_m + epsilon)
2. Normalized convex weighting (sum(w) = 1 within 1e-6)
3. Zero-MAE division-by-zero protection via epsilon = 1e-4
4. Graceful handling of missing members with dynamic re-normalization
5. Fallback priors (ECMWF: 2.29, GFS: 3.15, ICON: 4.77 km/h)
6. Finite output validation on operational data slices
7. Zero reference to research GBDT/Ridge models
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.blending.wind_blender import HistoricalWeightedWindBlender


@pytest.fixture
def wind_blender():
    return HistoricalWeightedWindBlender(epsilon=1e-4)


def test_wind_blender_formula_and_normalization(wind_blender):
    """Test inverse-MAE weighting and normalization."""
    # Custom historical errors
    maes = {"ECMWF_IFS": 2.0, "NOAA_GFS": 4.0, "DWD_ICON": 4.0}
    # inv: 1/2.0001 ~ 0.499975, 1/4.0001 ~ 0.249994, 1/4.0001 ~ 0.249994
    # sum ~ 0.999963 -> weights ~ 0.50, 0.25, 0.25
    weights = wind_blender.compute_weights(historical_maes=maes)
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert abs(weights["ECMWF_IFS"] - 0.50) < 1e-3
    assert abs(weights["NOAA_GFS"] - 0.25) < 1e-3
    assert abs(weights["DWD_ICON"] - 0.25) < 1e-3


def test_wind_blender_fallback_priors(wind_blender):
    """Test audited fallback priors when no runtime telemetry is provided."""
    weights = wind_blender.compute_weights()
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    # Fallback priors: ECMWF=2.29, GFS=3.15, ICON=4.77
    assert weights["ECMWF_IFS"] > weights["NOAA_GFS"] > weights["DWD_ICON"]
    # Check expected weight values
    e_ec = 1.0 / (2.29 + 1e-4)
    e_gfs = 1.0 / (3.15 + 1e-4)
    e_icon = 1.0 / (4.77 + 1e-4)
    tot = e_ec + e_gfs + e_icon
    assert abs(weights["ECMWF_IFS"] - (e_ec / tot)) < 1e-5
    assert abs(weights["NOAA_GFS"] - (e_gfs / tot)) < 1e-5
    assert abs(weights["DWD_ICON"] - (e_icon / tot)) < 1e-5


def test_wind_blender_zero_mae_handling(wind_blender):
    """Test zero-MAE safety via epsilon."""
    maes = {"ECMWF_IFS": 0.0, "NOAA_GFS": 3.0, "DWD_ICON": 4.0}
    weights = wind_blender.compute_weights(historical_maes=maes)
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert weights["ECMWF_IFS"] > 0.999
    assert np.isfinite(list(weights.values())).all()


def test_wind_blender_missing_member_renormalization(wind_blender):
    """Test dynamic re-normalization when one or two members are missing."""
    # Only 2 members available
    df = pd.DataFrame({
        "ECMWF_IFS": [15.0, 20.0],
        "NOAA_GFS": [18.0, 22.0],
    })
    blend, weights = wind_blender.blend_forecast(df)
    assert len(weights) == 2
    assert "DWD_ICON" not in weights
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert np.isfinite(blend).all()
    # Ensure blend = sum(w * m)
    expected_0 = weights["ECMWF_IFS"] * 15.0 + weights["NOAA_GFS"] * 18.0
    assert abs(blend[0] - expected_0) < 1e-5


def test_wind_blender_single_member_available(wind_blender):
    """Test single surviving member gets weight 1.0."""
    df = pd.DataFrame({
        "ECMWF_IFS": [25.0, 30.0],
    })
    blend, weights = wind_blender.blend_forecast(df)
    assert weights == {"ECMWF_IFS": 1.0}
    assert np.allclose(blend, [25.0, 30.0])


def test_wind_blender_operational_dataset_integrity():
    """Verify operational wind input file matches schema and has 432 rows."""
    input_file = Path("data/processed/multilocation_wind_forecast_inputs.csv")
    assert input_file.exists(), f"Operational wind file {input_file} missing"
    df = pd.read_csv(input_file)
    assert len(df) == 432
    assert set(df["location_id"].unique()) == {"kolkata", "delhi", "mumbai", "chennai", "guwahati", "bengaluru"}
    for col in ["ECMWF_IFS_wind", "NOAA_GFS_wind", "DWD_ICON_wind", "blended_wind", "lead_hours", "lead_day"]:
        assert col in df.columns
        assert df[col].isna().sum() == 0


def test_production_boundary_isolation():
    """Verify production wind blender has ZERO imports of research models."""
    import src.blending.wind_blender as wb
    source_code = Path(wb.__file__).read_text()
    assert "GradientBoosting" not in source_code
    assert "Ridge" not in source_code
    assert "import joblib" not in source_code
    assert "from joblib" not in source_code
    assert "Calib" not in source_code
    assert "regime_gate" not in source_code
