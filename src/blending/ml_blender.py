"""
Adaptive ML Forecast Blending Engine for PS81.

Learns model reliability and expected absolute forecast errors using
contextual predictor features (lead time, seasonality, historical skill, latitude, longitude).

Transforms predicted model errors into normalized blending weights:
    reliability_i = 1 / (predicted_error_i + epsilon)
    weight_i = reliability_i / sum(reliability)
    F_blended = sum(weight_i * F_i)
"""

from typing import Dict, Tuple, List, Any
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingRegressor

from src.data.schema import COL_MODEL, COL_ABSOLUTE_ERROR


MODEL_NAMES = ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]

# Allowed Predictor Features (Explicit Location Context + Zero Target Leakage)
FEATURE_COLS = [
    "lead_hours",
    "lead_day",
    "month",
    "day_of_year",
    "hour",
    "latitude",
    "longitude",
    "precipitation",
    "rolling_historical_mae_24h",
]


class AdaptiveMLBlender:
    """
    Adaptive Machine Learning Blending Engine.
    Trains one error-prediction model per NWP source to predict expected absolute error.
    """

    def __init__(self, epsilon: float = 1e-4, random_state: int = 42):
        self.epsilon = epsilon
        self.random_state = random_state
        self.models: Dict[str, HistGradientBoostingRegressor] = {}
        self.is_fitted = False

    def _prepare_model_dataset(
        self, df_long: pd.DataFrame, model_name: str
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Filters long-format dataframe for a single model and extracts X, y."""
        df_sub = df_long[df_long[COL_MODEL] == model_name].copy()
        
        X = df_sub[FEATURE_COLS]
        y = df_sub[COL_ABSOLUTE_ERROR].values
        
        return X, y

    def fit(self, df_train_long: pd.DataFrame) -> "AdaptiveMLBlender":
        """
        Trains error-prediction regressors for each NWP model on training set.
        """
        for model_name in MODEL_NAMES:
            X_train, y_train = self._prepare_model_dataset(df_train_long, model_name)
            
            regressor = HistGradientBoostingRegressor(
                max_iter=150,
                learning_rate=0.05,
                max_leaf_nodes=31,
                random_state=self.random_state,
            )
            regressor.fit(X_train, y_train)
            self.models[model_name] = regressor

        self.is_fitted = True
        return self

    def predict_weights(self, df_wide: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
        """
        Predicts expected absolute errors for each model, converts to reliabilities,
        and normalizes into non-negative weights summing to 1.0.

        Args:
            df_wide: Aligned dataset in wide format.

        Returns:
            Tuple of (blended_forecast_array, weights_df, predicted_errors_df)
        """
        if not self.is_fitted:
            raise RuntimeError("AdaptiveMLBlender must be fitted before calling predict_weights().")

        pred_errors = {}

        for model_name in MODEL_NAMES:
            X_infer = pd.DataFrame({
                "lead_hours": df_wide["lead_hours"],
                "lead_day": df_wide["lead_day"],
                "month": df_wide["month"],
                "day_of_year": df_wide["day_of_year"],
                "hour": df_wide["hour"],
                "latitude": df_wide["latitude"],
                "longitude": df_wide["longitude"],
                "precipitation": df_wide[f"{model_name}_precip"],
                "rolling_historical_mae_24h": df_wide[f"{model_name}_rolling_mae"],
            })[FEATURE_COLS]

            raw_pred_err = self.models[model_name].predict(X_infer)
            pred_errors[model_name] = np.clip(raw_pred_err, a_min=0.0, a_max=None)

        pred_errors_df = pd.DataFrame(pred_errors)

        rel_ecmwf = 1.0 / (pred_errors_df["ECMWF_IFS"].values + self.epsilon)
        rel_gfs = 1.0 / (pred_errors_df["NOAA_GFS"].values + self.epsilon)
        rel_icon = 1.0 / (pred_errors_df["DWD_ICON"].values + self.epsilon)

        sum_rel = rel_ecmwf + rel_gfs + rel_icon

        w_ecmwf = rel_ecmwf / sum_rel
        w_gfs = rel_gfs / sum_rel
        w_icon = rel_icon / sum_rel

        f_ecmwf = df_wide["ECMWF_IFS_precip"].values
        f_gfs = df_wide["NOAA_GFS_precip"].values
        f_icon = df_wide["DWD_ICON_precip"].values

        blended = (w_ecmwf * f_ecmwf) + (w_gfs * f_gfs) + (w_icon * f_icon)

        weights_df = pd.DataFrame({
            "w_ECMWF_IFS": w_ecmwf,
            "w_NOAA_GFS": w_gfs,
            "w_DWD_ICON": w_icon,
        })

        return blended, weights_df, pred_errors_df

    def save(self, model_dir: Path):
        """Saves trained model artifacts to specified directory."""
        model_dir.mkdir(parents=True, exist_ok=True)
        for model_name, reg in self.models.items():
            joblib.dump(reg, model_dir / f"adaptive_blender_{model_name}.joblib")

    def load(self, model_dir: Path):
        """Loads trained model artifacts from specified directory."""
        for model_name in MODEL_NAMES:
            filepath = model_dir / f"adaptive_blender_{model_name}.joblib"
            if not filepath.exists():
                raise FileNotFoundError(f"Model artifact not found at: {filepath}")
            self.models[model_name] = joblib.load(filepath)
        self.is_fitted = True
