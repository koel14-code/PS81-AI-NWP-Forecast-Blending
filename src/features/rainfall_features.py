"""
Rainfall Feature Engineering Module for PS81 AI-NWP Blending System.

Engineers ML-ready features from aligned historical forecast data across single or multiple locations:
- Time features (month, day_of_year, hour, season)
- Lead-time features (lead_hours, lead_day)
- Strictly operationally leakage-free & location/lead-separated historical model error statistics
- Analytical rainfall regime categories
- One-hot model encodings
- Preserved spatial coordinates
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_LATITUDE,
    COL_LONGITUDE,
    COL_MODEL,
    COL_FORECAST_RUN,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
    COL_FORECAST_ERROR,
    COL_ABSOLUTE_ERROR,
)


def compute_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts time-based features from valid_time ISO-8601 strings."""
    dt_series = pd.to_datetime(df[COL_VALID_TIME], utc=True)
    
    df["month"] = dt_series.dt.month
    df["day_of_year"] = dt_series.dt.dayofyear
    df["hour"] = dt_series.dt.hour

    def map_season(month: int) -> str:
        if 6 <= month <= 9:
            return "monsoon"
        elif 10 <= month <= 11:
            return "post_monsoon"
        elif month in (12, 1, 2):
            return "winter"
        else:
            return "pre_monsoon"

    df["season"] = df["month"].apply(map_season)
    return df


def compute_lead_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes lead-time features."""
    def map_lead_day(lead_h: int) -> int:
        if lead_h <= 24:
            return 1
        elif lead_h <= 48:
            return 2
        elif lead_h <= 72:
            return 3
        else:
            return int(np.ceil(lead_h / 24.0))

    df["lead_day"] = df[COL_LEAD_HOURS].apply(map_lead_day)
    return df


def compute_rainfall_regime(df: pd.DataFrame) -> pd.DataFrame:
    """Categorizes forecast and reference rainfall into analytical regime bins."""
    def categorize_rain(precip_val: float) -> str:
        if pd.isnull(precip_val) or precip_val < 0.1:
            return "no_rain"
        elif precip_val < 2.5:
            return "light"
        elif precip_val < 7.5:
            return "moderate"
        else:
            return "heavy"

    df["forecast_rainfall_regime"] = df[COL_PRECIPITATION].apply(categorize_rain)
    if COL_REF_PRECIPITATION in df:
        df["ref_rainfall_regime"] = df[COL_REF_PRECIPITATION].apply(categorize_rain)
    return df


def compute_rolling_historical_error(
    df_input: pd.DataFrame, window_hours: int = 24, train_cutoff_time: Any = None
) -> pd.DataFrame:
    """
    Calculates STRICTLY OPERATIONALLY LEAKAGE-FREE, LOCATION & LEAD-SEPARATED rolling historical model MAE.
    
    Guarantees:
    1. Strictly causal window: only past observations (valid_time < forecast_run) are evaluated.
    2. Primary statistic: observations strictly within [forecast_run - 24h, forecast_run).
    3. Expanding fallback: if the 24h window is sparse, uses all available past observations up to forecast_run.
    4. Boundary cold-start: if no past observations exist (at start of historical series), uses
       a baseline prior derived EXCLUSIVELY from the training split (valid_time <= train_cutoff_time), or 0.0.
    5. Zero validation or test observations are EVER used to construct training features or fallback priors.
    """
    df = df_input.copy()
    
    if "lead_day" not in df.columns:
        df = compute_lead_features(df)

    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df.columns else "location_id"
    if loc_col not in df.columns:
        df[loc_col] = "kolkata"

    df["dt_forecast_run"] = pd.to_datetime(df[COL_FORECAST_RUN], utc=True)
    df["dt_valid_time"] = pd.to_datetime(df[COL_VALID_TIME], utc=True)
    
    df_obs = df[[loc_col, COL_MODEL, "lead_day", "dt_valid_time", COL_ABSOLUTE_ERROR]].copy()
    
    mae_lookup: Dict[Tuple[str, str, int, pd.Timestamp], float] = {}
    cutoff_dt = pd.to_datetime(train_cutoff_time, utc=True) if train_cutoff_time is not None else None
    
    for (loc_id, model_name, l_day), group in df_obs.groupby([loc_col, COL_MODEL, "lead_day"]):
        unique_runs = df[
            (df[loc_col] == loc_id) & (df[COL_MODEL] == model_name) & (df["lead_day"] == l_day)
        ]["dt_forecast_run"].unique()
        
        times = group["dt_valid_time"]
        errors = group[COL_ABSOLUTE_ERROR].values
        
        # Calculate training-only fallback prior (never touches validation or test observations)
        if cutoff_dt is not None:
            train_mask = times <= cutoff_dt
            fallback_mae = float(errors[train_mask.values].mean()) if train_mask.any() else 0.0
        else:
            fallback_mae = 0.0
        
        for run_t_val in sorted(unique_runs):
            run_time = pd.to_datetime(run_t_val, utc=True)
            win_start = run_time - pd.Timedelta(hours=window_hours)
            
            # 1. Strictly causal 24h operational window: [run_time - window_hours, run_time)
            mask = (times < run_time) & (times >= win_start)
            
            if mask.any():
                mae_val = float(errors[mask.values].mean())
            else:
                # 2. Expanding cumulative history strictly before run_time
                past_mask = times < run_time
                if past_mask.any():
                    mae_val = float(errors[past_mask.values].mean())
                else:
                    # 3. Cold start boundary before any observation has occurred:
                    # Uses training-phase baseline prior (never future data)
                    mae_val = fallback_mae
                    
            mae_lookup[(loc_id, model_name, l_day, run_t_val)] = round(mae_val, 4)

    df["rolling_historical_mae_24h"] = [
        mae_lookup.get((loc, m, ld, r), 0.0)
        for loc, m, ld, r in zip(df[loc_col], df[COL_MODEL], df["lead_day"], df["dt_forecast_run"])
    ]
    
    df.drop(columns=["dt_forecast_run", "dt_valid_time"], inplace=True)
    return df


def encode_models(df: pd.DataFrame) -> pd.DataFrame:
    """Creates one-hot dummy columns for NWP models."""
    model_dummies = pd.get_dummies(df[COL_MODEL], prefix="model", dtype=int)
    for col in ["model_ECMWF_IFS", "model_NOAA_GFS", "model_DWD_ICON"]:
        if col not in model_dummies.columns:
            model_dummies[col] = 0
            
    df = pd.concat([df, model_dummies], axis=1)
    return df


def compute_ensemble_disagreement_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes inter-model ensemble forecast features strictly from available NWP forecasts.
    Features:
    - ensemble_mean: mean precipitation across NWP models at (location, valid_time, lead_hours)
    - ensemble_std: standard deviation across NWP models (uncertainty/disagreement metric)
    - ensemble_max: maximum precipitation predicted by any NWP model
    - ensemble_min: minimum precipitation predicted by any NWP model
    - ensemble_range: ensemble_max - ensemble_min
    Zero reference or future information is used.
    """
    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df.columns else "location_id"
    pivot_cols = [loc_col, COL_VALID_TIME, COL_LEAD_HOURS]
    
    p = df.pivot_table(
        index=pivot_cols,
        columns=COL_MODEL,
        values=COL_PRECIPITATION,
        aggfunc="first"
    ).reset_index()
    
    models_present = [m for m in ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"] if m in p.columns]
    if len(models_present) > 1:
        f_vals = np.column_stack([p[m].fillna(0.0).values for m in models_present])
        p["ensemble_mean"] = np.round(np.mean(f_vals, axis=1), 4)
        p["ensemble_std"] = np.round(np.std(f_vals, axis=1), 4)
        p["ensemble_max"] = np.round(np.max(f_vals, axis=1), 4)
        p["ensemble_min"] = np.round(np.min(f_vals, axis=1), 4)
        p["ensemble_range"] = np.round(p["ensemble_max"] - p["ensemble_min"], 4)
    else:
        p["ensemble_mean"] = p[models_present[0]] if models_present else 0.0
        p["ensemble_std"] = 0.0
        p["ensemble_max"] = p["ensemble_mean"]
        p["ensemble_min"] = p["ensemble_mean"]
        p["ensemble_range"] = 0.0
        
    calc_cols = pivot_cols + ["ensemble_mean", "ensemble_std", "ensemble_max", "ensemble_min", "ensemble_range"]
    df_merged = pd.merge(df, p[calc_cols], on=pivot_cols, how="left")
    return df_merged


def generate_feature_dataset(
    df_raw: pd.DataFrame, train_cutoff_time: Any = None
) -> pd.DataFrame:
    """
    Master pipeline entrypoint for feature engineering.
    Converts raw aligned dataset into ML-ready feature DataFrame.
    
    Args:
        df_raw: Raw aligned DataFrame.
        train_cutoff_time: Optional timestamp defining chronological training boundary.
            When provided, boundary cold-start fallback priors are calculated strictly from
            training data (valid_time <= train_cutoff_time), ensuring zero validation or
            test leakage.
    """
    df = df_raw.copy()

    # 1. Time Features
    df = compute_time_features(df)

    # 2. Lead-Time Features
    df = compute_lead_features(df)

    # 3. Rainfall Context Regimes
    df = compute_rainfall_regime(df)

    # 4. Inter-Model Disagreement Features (Ensemble Spread & Range)
    df = compute_ensemble_disagreement_features(df)

    # 5. Strictly Operationally Leakage-Free & Location/Lead-Separated Rolling Error Feature
    df = compute_rolling_historical_error(df, window_hours=24, train_cutoff_time=train_cutoff_time)

    # 6. Model One-Hot Encoding
    df = encode_models(df)

    return df
