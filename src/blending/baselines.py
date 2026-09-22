"""
Data Splitting & Baseline Ensemble Models Module for PS81 Blending Engine.

Provides:
- Chronological Train / Validation / Test data splitting (multi-location aware).
- Dataset pivoting for multi-model alignment.
- Simple Equal-Weighted Ensemble baseline.
- Leakage-safe Historical-Error Weighted Ensemble baseline.
"""

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_MODEL,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
)


def split_data_chronologically(
    df: pd.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Tuple[str, str]]]:
    """
    Performs a strictly chronological split based on unique valid_time timestamps
    to prevent temporal data leakage across all locations.
    """
    unique_times = sorted(df[COL_VALID_TIME].unique())
    n_total = len(unique_times)

    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)

    train_times = unique_times[:n_train]
    val_times = unique_times[n_train : n_train + n_val]
    test_times = unique_times[n_train + n_val :]

    df_train = df[df[COL_VALID_TIME].isin(train_times)].copy()
    df_val = df[df[COL_VALID_TIME].isin(val_times)].copy()
    df_test = df[df[COL_VALID_TIME].isin(test_times)].copy()

    date_ranges = {
        "train": (train_times[0], train_times[-1]),
        "validation": (val_times[0], val_times[-1]),
        "test": (test_times[0], test_times[-1]),
    }

    return df_train, df_val, df_test, date_ranges


def pivot_aligned_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots long-format multi-model dataframe into wide format indexed by
    (location_id, valid_time, lead_hours, latitude, longitude) with separate columns per model.
    """
    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df.columns else "location_id"
    if loc_col not in df.columns:
        df[loc_col] = "kolkata"

    pivot_cols = [loc_col, COL_VALID_TIME, "latitude", "longitude", COL_LEAD_HOURS]

    df_precip = df.pivot_table(
        index=pivot_cols,
        columns=COL_MODEL,
        values=COL_PRECIPITATION,
        aggfunc="first"
    ).reset_index()

    df_precip.rename(
        columns={
            "ECMWF_IFS": "ECMWF_IFS_precip",
            "NOAA_GFS": "NOAA_GFS_precip",
            "DWD_ICON": "DWD_ICON_precip",
        },
        inplace=True,
    )

    df_rolling = df.pivot_table(
        index=pivot_cols,
        columns=COL_MODEL,
        values="rolling_historical_mae_24h",
        aggfunc="first"
    ).reset_index()

    df_rolling.rename(
        columns={
            "ECMWF_IFS": "ECMWF_IFS_rolling_mae",
            "NOAA_GFS": "NOAA_GFS_rolling_mae",
            "DWD_ICON": "DWD_ICON_rolling_mae",
        },
        inplace=True,
    )

    meta_cols = [
        loc_col, COL_VALID_TIME, "latitude", "longitude", COL_LEAD_HOURS,
        COL_REF_PRECIPITATION, "month", "day_of_year", "hour", "season", "lead_day"
    ]
    df_meta = df[meta_cols].drop_duplicates(subset=[loc_col, COL_VALID_TIME, COL_LEAD_HOURS])

    df_wide = pd.merge(df_precip, df_rolling, on=pivot_cols, how="inner")
    df_wide = pd.merge(df_wide, df_meta, on=pivot_cols, how="inner")

    return df_wide.sort_values(by=[loc_col, COL_VALID_TIME, COL_LEAD_HOURS]).reset_index(drop=True)


def compute_simple_ensemble(df_wide: pd.DataFrame) -> np.ndarray:
    """Computes Simple Equal-Weight Ensemble: (ECMWF + GFS + ICON) / 3."""
    f_ecmwf = df_wide["ECMWF_IFS_precip"].values
    f_gfs = df_wide["NOAA_GFS_precip"].values
    f_icon = df_wide["DWD_ICON_precip"].values

    return (f_ecmwf + f_gfs + f_icon) / 3.0


def compute_historical_weighted_ensemble(
    df_wide: pd.DataFrame, epsilon: float = 1e-4
) -> Tuple[np.ndarray, pd.DataFrame]:
    """Computes Leakage-Safe Historical-Error Weighted Ensemble."""
    mae_ecmwf = df_wide["ECMWF_IFS_rolling_mae"].values
    mae_gfs = df_wide["NOAA_GFS_rolling_mae"].values
    mae_icon = df_wide["DWD_ICON_rolling_mae"].values

    rel_ecmwf = 1.0 / (mae_ecmwf + epsilon)
    rel_gfs = 1.0 / (mae_gfs + epsilon)
    rel_icon = 1.0 / (mae_icon + epsilon)

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

    return blended, weights_df
