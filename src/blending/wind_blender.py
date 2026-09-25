"""
Historical-Error Weighted Wind Blender for SkyBlend AI.
SIH Problem Statement PS81: Multi-Variable Forecast Blending.

Implements the audited research-stage Historical-Error Weighted Blend for 10m surface wind speed (km/h):
    weight_m = 1 / (rolling_24h_MAE_m + epsilon)
    w_m = weight_m / sum(weights)
    wind_blend = sum(w_m * wind_m)

Zero learned model serialized files required. Transparent, deterministic, and strictly causal.
"""

from typing import Dict, Tuple, List, Optional, Union
import numpy as np
import pandas as pd

MODEL_NAMES = ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]
DEFAULT_FALLBACK_PRIORS = {
    "ECMWF_IFS": 2.29,  # Pre-monsoon / full-year training split MAE (km/h)
    "NOAA_GFS": 3.15,
    "DWD_ICON": 4.77,
}


class HistoricalWeightedWindBlender:
    """
    Transparent Historical-Error Weighted Wind Blender.
    Dynamically combines multi-model NWP 10m scalar wind speed forecasts
    using inverse historical mean absolute error weighting.
    """

    def __init__(
        self,
        epsilon: float = 1e-4,
        fallback_priors: Optional[Dict[str, float]] = None,
    ):
        self.epsilon = float(epsilon)
        self.fallback_priors = (
            dict(fallback_priors) if fallback_priors is not None else dict(DEFAULT_FALLBACK_PRIORS)
        )

    def compute_weights(
        self,
        error_priors: Optional[Dict[str, float]] = None,
        available_members: Optional[List[str]] = None,
        historical_maes: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Computes normalized weights from error priors with complete numerical safety:
        - Filters out unavailable or non-finite members.
        - Clamps negative MAEs to zero.
        - Handles zero MAE safely via epsilon (allocates near-100% weight).
        - Handles missing members by dynamically re-normalizing remaining members.
        - Falls back to uniform weighting (1/N) if all error priors are invalid.
        - Guarantees non-negative weights and sum(weights) == 1.0 within floating tolerance.
        """
        if error_priors is None and historical_maes is not None:
            error_priors = historical_maes

        members = list(available_members) if available_members is not None else list(MODEL_NAMES)
        if not members:
            raise ValueError("No forecast members specified.")

        priors = dict(self.fallback_priors)
        if error_priors:
            for m, val in error_priors.items():
                if m in members and val is not None:
                    try:
                        f_val = float(val)
                        if np.isfinite(f_val) and f_val >= 0:
                            priors[m] = f_val
                    except (ValueError, TypeError):
                        pass

        # Calculate inverse errors for available members
        inv_errors = {}
        for m in members:
            mae = priors.get(m, self.fallback_priors.get(m, 2.5))
            if not np.isfinite(mae) or mae < 0:
                mae = 2.5
            inv_errors[m] = 1.0 / (mae + self.epsilon)

        sum_inv = sum(inv_errors.values())
        if sum_inv <= 0 or not np.isfinite(sum_inv):
            # Safe uniform fallback
            n = len(members)
            return {m: 1.0 / n for m in members}

        weights = {m: inv_errors[m] / sum_inv for m in members}
        return weights

    def predict(
        self,
        forecasts: Dict[str, np.ndarray],
        error_priors: Optional[Dict[str, float]] = None,
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Blends forecast arrays from a dictionary of members:
            forecasts = {"ECMWF_IFS": array, "NOAA_GFS": array, "DWD_ICON": array}
        Returns:
            (blended_wind_array, weights_dict)
        """
        valid_members = []
        for m, arr in forecasts.items():
            if arr is not None:
                np_arr = np.asarray(arr, dtype=float)
                if np_arr.size > 0 and not np.isnan(np_arr).all():
                    valid_members.append(m)

        if not valid_members:
            # Fallback if everything is None
            avail = [m for m, arr in forecasts.items() if arr is not None]
            if not avail:
                raise ValueError("No forecast arrays provided.")
            n = len(avail)
            w_fallback = {m: 1.0 / n for m in avail}
            stacked = np.column_stack([np.nan_to_num(forecasts[m], nan=0.0) for m in avail])
            return np.mean(stacked, axis=1), w_fallback

        weights = self.compute_weights(error_priors=error_priors, available_members=valid_members)

        # Assemble matrix and apply linear combination
        first_len = len(np.asarray(forecasts[valid_members[0]]))
        f_matrix = np.column_stack([
            np.nan_to_num(np.asarray(forecasts[m], dtype=float), nan=0.0)
            for m in valid_members
        ])
        w_vec = np.array([weights[m] for m in valid_members])
        blend = np.dot(f_matrix, w_vec)
        # Wind speed cannot physically be negative
        blend = np.maximum(blend, 0.0)

        return blend, weights

    def predict_df(
        self,
        df_wide: pd.DataFrame,
        error_priors: Optional[Dict[str, float]] = None,
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Blends forecast columns from a wide pandas DataFrame.
        Accepts columns named '{MODEL}_wind' or '{MODEL}'.
        Returns:
            (blended_wind_array, weights_dataframe)
        """
        forecasts = {}
        for m in MODEL_NAMES:
            if f"{m}_wind" in df_wide.columns:
                forecasts[m] = df_wide[f"{m}_wind"].values
            elif m in df_wide.columns:
                forecasts[m] = df_wide[m].values
            else:
                forecasts[m] = None

        blend, weights = self.predict(forecasts, error_priors=error_priors)

        # Build weights DataFrame
        n_rows = len(df_wide)
        weights_dict = {f"w_{m}": np.full(n_rows, weights.get(m, 0.0)) for m in MODEL_NAMES}
        weights_df = pd.DataFrame(weights_dict, index=df_wide.index)

        return blend, weights_df

    def blend_forecast(
        self,
        df_or_dict: Union[pd.DataFrame, Dict[str, np.ndarray]],
        error_priors: Optional[Dict[str, float]] = None,
        historical_maes: Optional[Dict[str, float]] = None,
    ) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Convenience wrapper supporting DataFrame or Dict inputs.
        Returns: (blended_wind_array, weights_dict)
        """
        if error_priors is None and historical_maes is not None:
            error_priors = historical_maes
        if isinstance(df_or_dict, pd.DataFrame):
            blend, weights_df = self.predict_df(df_or_dict, error_priors=error_priors)
            weights_dict = {
                col.replace("w_", ""): float(weights_df[col].iloc[0])
                for col in weights_df.columns
                if float(weights_df[col].iloc[0]) > 0
            }
            return blend, weights_dict
        return self.predict(df_or_dict, error_priors=error_priors)
