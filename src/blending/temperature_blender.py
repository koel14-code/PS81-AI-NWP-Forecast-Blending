"""
Temperature Blending Engine for SkyBlend AI.
SIH Problem Statement PS81: Multi-Variable Forecast Blending.

Implements continuous adaptive inverse-error reliability weighting for 2-meter surface temperature.
Unlike precipitation, temperature is a continuous thermal state variable; therefore,
it does NOT use zero-inflation thresholding or convective peak-lift.
"""

from typing import Dict, Tuple, List, Optional
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor

MODEL_NAMES = ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]

TEMP_FEATURE_COLS = [
    "lead_hours",
    "lead_day",
    "hour",
    "month",
    "day_of_year",
    "latitude",
    "longitude",
    "model_temp",
    "ensemble_mean",
    "ensemble_std",
    "ensemble_range",
]


class TemperatureBlender:
    """
    Adaptive Machine Learning Temperature Blender.
    Learns expected absolute forecast errors of individual NWP models for 2m temperature
    and computes dynamic reliability-weighted consensus forecasts.
    """

    def __init__(self, epsilon: float = 1e-4, random_state: int = 42):
        self.epsilon = epsilon
        self.random_state = random_state
        self.models: Dict[str, HistGradientBoostingRegressor] = {}
        self.is_fitted = False

    def fit(self, df_train_wide: pd.DataFrame, y_true: np.ndarray) -> "TemperatureBlender":
        """
        Trains error-prediction regressors for each NWP model on training set.
        Target is absolute error: |T_model - T_obs|.
        """
        f_models = np.column_stack([df_train_wide[f"{m}_temp"].values for m in MODEL_NAMES])
        ens_mean = np.mean(f_models, axis=1)
        ens_std = np.std(f_models, axis=1)
        ens_max = np.max(f_models, axis=1)
        ens_min = np.min(f_models, axis=1)
        ens_range = ens_max - ens_min

        for m in MODEL_NAMES:
            X = pd.DataFrame({
                "lead_hours": df_train_wide["lead_hours"],
                "lead_day": df_train_wide["lead_day"],
                "hour": df_train_wide["hour"],
                "month": df_train_wide["month"],
                "day_of_year": df_train_wide["day_of_year"],
                "latitude": df_train_wide["latitude"],
                "longitude": df_train_wide["longitude"],
                "model_temp": df_train_wide[f"{m}_temp"],
                "ensemble_mean": ens_mean,
                "ensemble_std": ens_std,
                "ensemble_range": ens_range,
            })[TEMP_FEATURE_COLS]

            y_err = np.abs(df_train_wide[f"{m}_temp"].values - y_true)

            reg = HistGradientBoostingRegressor(
                max_iter=100,
                learning_rate=0.05,
                max_leaf_nodes=31,
                random_state=self.random_state,
            )
            reg.fit(X, y_err)
            self.models[m] = reg

        self.is_fitted = True
        return self

    def predict_weights(
        self, df_wide: pd.DataFrame
    ) -> Tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
        """
        Computes dynamic reliability weights and blended temperature forecast.
        """
        f_ecmwf = df_wide["ECMWF_IFS_temp"].values
        f_gfs = df_wide["NOAA_GFS_temp"].values
        f_icon = df_wide["DWD_ICON_temp"].values
        f_models = np.column_stack([f_ecmwf, f_gfs, f_icon])

        ens_mean = np.mean(f_models, axis=1)
        ens_std = np.std(f_models, axis=1)
        ens_max = np.max(f_models, axis=1)
        ens_min = np.min(f_models, axis=1)
        ens_range = ens_max - ens_min

        pred_errors = {}
        for m in MODEL_NAMES:
            if self.is_fitted and m in self.models:
                X = pd.DataFrame({
                    "lead_hours": df_wide["lead_hours"],
                    "lead_day": df_wide["lead_day"],
                    "hour": df_wide["hour"],
                    "month": df_wide["month"],
                    "day_of_year": df_wide["day_of_year"],
                    "latitude": df_wide["latitude"],
                    "longitude": df_wide["longitude"],
                    "model_temp": df_wide[f"{m}_temp"],
                    "ensemble_mean": ens_mean,
                    "ensemble_std": ens_std,
                    "ensemble_range": ens_range,
                })[TEMP_FEATURE_COLS]
                raw_err = self.models[m].predict(X)
                pred_errors[m] = np.clip(raw_err, a_min=0.1, a_max=None)
            else:
                # Disagreement-based fallback prior when unfitted
                pred_errors[m] = np.abs(df_wide[f"{m}_temp"].values - ens_mean) + 0.5

        pred_errors_df = pd.DataFrame(pred_errors)

        rel_ecmwf = 1.0 / (pred_errors_df["ECMWF_IFS"].values + self.epsilon)
        rel_gfs = 1.0 / (pred_errors_df["NOAA_GFS"].values + self.epsilon)
        rel_icon = 1.0 / (pred_errors_df["DWD_ICON"].values + self.epsilon)
        sum_rel = rel_ecmwf + rel_gfs + rel_icon

        w_ecmwf = rel_ecmwf / sum_rel
        w_gfs = rel_gfs / sum_rel
        w_icon = rel_icon / sum_rel

        # Continuous thermal consensus blend (no peak lift)
        blended = (w_ecmwf * f_ecmwf) + (w_gfs * f_gfs) + (w_icon * f_icon)

        weights_df = pd.DataFrame({
            "w_ECMWF_IFS": w_ecmwf,
            "w_NOAA_GFS": w_gfs,
            "w_DWD_ICON": w_icon,
        })

        return np.round(blended, 2), weights_df, pred_errors_df

    def save(self, model_dir: Path):
        """Saves temperature error models to model_dir."""
        model_dir.mkdir(parents=True, exist_ok=True)
        for m_name, reg in self.models.items():
            joblib.dump(reg, model_dir / f"temperature_blender_{m_name}.joblib")

    def load(self, model_dir: Path):
        """Loads temperature error models from model_dir."""
        for m_name in MODEL_NAMES:
            filepath = model_dir / f"temperature_blender_{m_name}.joblib"
            if filepath.exists():
                self.models[m_name] = joblib.load(filepath)
            else:
                raise FileNotFoundError(f"Temperature model artifact not found at {filepath}")
        self.is_fitted = True
