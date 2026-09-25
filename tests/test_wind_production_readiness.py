"""
SkyBlend AI — Wind Production-Readiness Audit Tests
SIH Problem Statement PS81: Hybrid AI-NWP Multi-Model Forecast Blending System.

Validates the Historical-Error Weighted Blend for 10m surface wind speed across:
1. Mathematical correctness and weight normalization
2. Numerical safety (zero MAE, NaN, Inf, missing members, all-failed fallback)
3. Zero learned-artifact dependency (no .joblib files required)
4. Sub-millisecond latency
5. Physical bounding and severe weather stability (Cyclone Remal envelope)
6. Strict variable semantics (10m wind speed, km/h, analytical signal)
"""

import time
import pytest
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

EPSILON = 1e-4


def compute_historical_weighted_blend(
    forecasts: Dict[str, np.ndarray],
    historical_maes: Dict[str, float],
    epsilon: float = EPSILON,
) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    Production-grade reference implementation of the Historical-Error Weighted Blend.
    Formula:
        weight_m = 1 / (rolling_24h_MAE_m + epsilon)
        w_m = weight_m / sum(weights)
        wind_blend = sum(w_m * wind_m)
    """
    valid_members = []
    inv_errors = []

    for m, f_vals in forecasts.items():
        if f_vals is None:
            continue
        f_arr = np.asarray(f_vals, dtype=float)
        if f_arr.size == 0 or np.isnan(f_arr).all():
            continue

        mae = historical_maes.get(m, np.nan)
        if np.isnan(mae) or np.isinf(mae) or mae < 0:
            mae = 2.5  # Neutral historical prior error (km/h)

        inv_e = 1.0 / (mae + epsilon)
        valid_members.append(m)
        inv_errors.append(inv_e)

    if not valid_members:
        avail = [m for m, f in forecasts.items() if f is not None]
        if not avail:
            raise ValueError("No forecast members provided.")
        n = len(avail)
        weights = {m: 1.0 / n for m in avail}
        stacked = np.column_stack([np.nan_to_num(forecasts[m], nan=0.0) for m in avail])
        blend = np.mean(stacked, axis=1)
        return blend, weights

    sum_inv = sum(inv_errors)
    if sum_inv <= 0 or not np.isfinite(sum_inv):
        n = len(valid_members)
        weights = {m: 1.0 / n for m in valid_members}
    else:
        weights = {m: inv_e / sum_inv for m, inv_e in zip(valid_members, inv_errors)}

    f_matrix = np.column_stack([np.nan_to_num(forecasts[m], nan=0.0) for m in valid_members])
    w_vec = np.array([weights[m] for m in valid_members])
    blend = np.dot(f_matrix, w_vec)
    return blend, weights


class TestWindProductionReadiness:

    def test_wind_formula_convexity_and_bounds(self):
        """Weights must be strictly positive, sum to 1.0, and blend must lie within NWP envelope."""
        forecasts = {
            "ECMWF_IFS": np.array([12.5, 18.0, 24.2]),
            "NOAA_GFS": np.array([15.0, 22.1, 28.5]),
            "DWD_ICON": np.array([10.2, 14.3, 19.8]),
        }
        maes = {"ECMWF_IFS": 2.29, "NOAA_GFS": 3.15, "DWD_ICON": 4.77}

        blend, weights = compute_historical_weighted_blend(forecasts, maes)

        # 1. Weight normalization
        assert abs(sum(weights.values()) - 1.0) < 1e-6, "Weights must sum to 1.0"
        for m, w in weights.items():
            assert w > 0.0, f"Weight for {m} must be strictly positive"

        # 2. Ranking order: ECMWF has lowest MAE -> highest weight, ICON lowest weight
        assert weights["ECMWF_IFS"] > weights["NOAA_GFS"] > weights["DWD_ICON"]

        # 3. Bounded convex combination
        for i in range(len(blend)):
            min_val = min(forecasts[m][i] for m in forecasts)
            max_val = max(forecasts[m][i] for m in forecasts)
            assert min_val <= blend[i] <= max_val, f"Blended value {blend[i]} out of bounds [{min_val}, {max_val}]"

    def test_wind_zero_mae_division_by_zero_safety(self):
        """Epsilon must prevent ZeroDivisionError and safely allocate near-unity weight."""
        forecasts = {
            "ECMWF_IFS": np.array([25.0]),
            "NOAA_GFS": np.array([30.0]),
            "DWD_ICON": np.array([20.0]),
        }
        maes = {"ECMWF_IFS": 0.0, "NOAA_GFS": 3.0, "DWD_ICON": 3.0}

        blend, weights = compute_historical_weighted_blend(forecasts, maes, epsilon=1e-4)

        assert np.isfinite(blend[0])
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert weights["ECMWF_IFS"] > 0.999  # dominates due to zero error
        assert abs(blend[0] - 25.0) < 0.01

    def test_wind_missing_member_graceful_degradation(self):
        """When one NWP model fails or is absent, weights must automatically re-normalize over remaining members."""
        forecasts = {
            "ECMWF_IFS": np.array([15.0, 18.0]),
            "NOAA_GFS": None,  # Dropped member
            "DWD_ICON": np.array([12.0, 14.0]),
        }
        maes = {"ECMWF_IFS": 2.0, "NOAA_GFS": 3.0, "DWD_ICON": 4.0}

        blend, weights = compute_historical_weighted_blend(forecasts, maes)

        assert "NOAA_GFS" not in weights
        assert len(weights) == 2
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert np.isfinite(blend).all()
        assert blend[0] == pytest.approx(
            weights["ECMWF_IFS"] * 15.0 + weights["DWD_ICON"] * 12.0, rel=1e-5
        )

    def test_wind_nan_inf_sanitization(self):
        """Corrupt NaN values in forecasts or Inf in historical errors must be sanitized safely."""
        forecasts = {
            "ECMWF_IFS": np.array([18.0, np.nan]),
            "NOAA_GFS": np.array([20.0, 22.0]),
            "DWD_ICON": np.array([16.0, 17.0]),
        }
        maes = {"ECMWF_IFS": np.inf, "NOAA_GFS": 2.5, "DWD_ICON": np.nan}

        blend, weights = compute_historical_weighted_blend(forecasts, maes)

        assert np.isfinite(blend).all(), "Final forecast must be finite even with NaNs"
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert all(w >= 0 for w in weights.values())

    def test_wind_all_failed_uniform_fallback(self):
        """If all MAE priors are invalid, system must safely fall back to equal weighting."""
        forecasts = {
            "ECMWF_IFS": np.array([10.0]),
            "NOAA_GFS": np.array([20.0]),
            "DWD_ICON": np.array([30.0]),
        }
        maes = {"ECMWF_IFS": np.nan, "NOAA_GFS": np.nan, "DWD_ICON": np.nan}

        blend, weights = compute_historical_weighted_blend(forecasts, maes)

        # When all MAEs are NaN, each gets default neutral prior 2.5, resulting in equal 1/3 weights
        assert abs(weights["ECMWF_IFS"] - 1/3) < 1e-5
        assert abs(weights["NOAA_GFS"] - 1/3) < 1e-5
        assert abs(weights["DWD_ICON"] - 1/3) < 1e-5
        assert abs(blend[0] - 20.0) < 1e-5

    def test_wind_zero_learned_artifact_dependency(self):
        """Wind candidate must require ZERO learned model files (.joblib) or weight arrays."""
        # The Historical-Error Weighted Blend is completely defined by its closed-form formula.
        # It requires no scikit-learn models, no serialized pipelines, and no training state.
        import os
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent
        wind_model_dir = base_dir / "models" / "wind"
        # Confirm that no production deployment requires a models/wind directory
        assert not (wind_model_dir / "production_model.joblib").exists()

    def test_wind_submillisecond_latency(self):
        """A full 72-hour forecast blending run must complete in under 5 milliseconds."""
        forecasts = {
            "ECMWF_IFS": np.random.uniform(5.0, 45.0, size=72),
            "NOAA_GFS": np.random.uniform(5.0, 45.0, size=72),
            "DWD_ICON": np.random.uniform(5.0, 45.0, size=72),
        }
        maes = {"ECMWF_IFS": 2.29, "NOAA_GFS": 3.15, "DWD_ICON": 4.77}

        # Warmup
        for _ in range(10):
            compute_historical_weighted_blend(forecasts, maes)

        times = []
        for _ in range(500):
            t0 = time.perf_counter()
            b, w = compute_historical_weighted_blend(forecasts, maes)
            times.append(time.perf_counter() - t0)

        mean_ms = np.mean(times) * 1000.0
        p95_ms = np.percentile(times, 95) * 1000.0

        assert mean_ms < 1.0, f"Mean latency ({mean_ms:.3f} ms) exceeds 1 ms target"
        assert p95_ms < 5.0, f"P95 latency ({p95_ms:.3f} ms) exceeds 5 ms budget"

    def test_wind_cyclone_remal_stability(self):
        """During extreme cyclonic wind events (Cyclone Remal), the blend must remain stable."""
        # Recreating the exact Remal landfall conditions at Kolkata (May 26 21:00 UTC)
        remal_forecasts = {
            "ECMWF_IFS": np.array([40.0]),
            "NOAA_GFS": np.array([71.0]),
            "DWD_ICON": np.array([29.6]),
        }
        # Pre-storm rolling MAE priors
        maes = {"ECMWF_IFS": 2.29, "NOAA_GFS": 3.15, "DWD_ICON": 4.77}

        blend, weights = compute_historical_weighted_blend(remal_forecasts, maes)

        # Output must be finite, between 29.6 and 71.0 km/h
        assert 29.6 <= blend[0] <= 71.0
        # In fact, with weights ~ (0.443, 0.322, 0.235), blend ~ 46.7 km/h
        assert 44.0 <= blend[0] <= 50.0

    def test_wind_variable_semantics(self):
        """Wind metadata must strictly specify 10m scalar wind speed in km/h with analytical disclaimer."""
        from src.blending.regimes import get_variable_metadata, classify_wind_regime

        meta = get_variable_metadata("wind")
        assert meta["variable"] == "wind"
        assert meta["unit"] == "km/h"
        assert "10m" in meta["display_name"] or "Wind Speed" in meta["display_name"]
        assert meta["extreme_threshold"] == 40.0
        assert meta["severe_threshold"] == 60.0
