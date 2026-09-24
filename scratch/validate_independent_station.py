"""
SkyBlend AI — Independent Ground-Station Validation Script (Kolkata / Alipore WMO 42807)

Validates the frozen SkyBlend Phase 6 production model and constituent NWP members
(ECMWF IFS, NOAA GFS, DWD ICON, Simple Average, Historical Weighted) against
independent ground-truth station observations.

Station: WMO 42807 (Kolkata / Alipore)
Coordinates: 22.5333° N, 88.3333° E
Target Periods:
  1. Pre-Monsoon Test Set: 2024-04-07T01:00:00Z to 2024-05-31T23:00:00Z (1,319 hours)
  2. July External Holdout: 2024-07-24T18:00:00Z to 2024-07-28T23:00:00Z (102 hours)

Authoritative Invariants:
  - Phase 6 production models remain frozen.
  - Zero retraining or tuning against station observations.
  - Strictly research / post-hoc independent validation layer.
"""

import sys
import os
import io
import gzip
import urllib.request
import ssl
from pathlib import Path
from typing import Dict, Tuple, Any

import pandas as pd
import numpy as np

# Ensure root directory is on PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.blending.ml_blender import AdaptiveMLBlender
from src.blending.baselines import (
    split_data_chronologically,
    pivot_aligned_dataset,
    compute_simple_ensemble,
    compute_historical_weighted_ensemble
)
from src.blending.evaluation import calculate_continuous_metrics, calculate_categorical_metrics

STATION_ID = "42807"
STATION_NAME = "Kolkata / Alipore"
STATION_LAT = 22.5333
STATION_LON = 88.3333
STATION_ELEVATION_M = 5.0

EXTERNAL_DIR = ROOT_DIR / "data" / "external" / "station_validation"
OBSERVATION_FILE = EXTERNAL_DIR / "kolkata_alipore_42807_hourly.csv"
METEOSTAT_URL = "https://bulk.meteostat.net/v2/hourly/42807.csv.gz"
PHASE6_MODEL_DIR = ROOT_DIR / "models" / "expanded_full_year"


def acquire_station_observations() -> pd.DataFrame:
    """
    Acquires and caches standardized station observations for WMO 42807.
    Converts timestamps to UTC ISO 8601 strings and validates rainfall units (mm/h).
    """
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    if OBSERVATION_FILE.exists():
        print(f"[1/4] Loading cached station observations from: {OBSERVATION_FILE}")
        df_clean = pd.read_csv(OBSERVATION_FILE)
    else:
        print(f"[1/4] Fetching independent ground-station observations from Meteostat/NOAA archive ({METEOSTAT_URL})...")
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(METEOSTAT_URL, headers={"User-Agent": "SkyBlend-Station-Validation/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            gz_data = resp.read()
        
        columns = [
            "date", "hour", "temp", "dwpt", "rhum", "prcp", "snow",
            "wdir", "wspd", "wpgt", "pres", "tsun", "coco"
        ]
        df_raw = pd.read_csv(io.BytesIO(gz_data), compression="gzip", header=None, names=columns)
        
        # Filter to 2024
        df_raw["year"] = df_raw["date"].str[:4].astype(int)
        df_2024 = df_raw[df_raw["year"] == 2024].copy()
        
        # Build UTC timestamp
        df_2024["valid_time"] = df_2024["date"] + "T" + df_2024["hour"].astype(str).str.zfill(2) + ":00:00Z"
        df_2024["station_id"] = STATION_ID
        df_2024["station_name"] = STATION_NAME
        df_2024["latitude"] = STATION_LAT
        df_2024["longitude"] = STATION_LON
        df_2024["elevation_m"] = STATION_ELEVATION_M
        df_2024["observed_rainfall_mm_h"] = df_2024["prcp"]
        
        df_clean = df_2024[[
            "station_id", "station_name", "latitude", "longitude", "elevation_m",
            "valid_time", "observed_rainfall_mm_h", "temp", "rhum", "pres", "wspd"
        ]].copy()
        
        df_clean.to_csv(OBSERVATION_FILE, index=False)
        print(f"      Cached {len(df_clean)} cleaned hourly observations to {OBSERVATION_FILE}")

    return df_clean


def evaluate_forecast_set(
    df_forecasts: pd.DataFrame,
    df_obs: pd.DataFrame,
    blender: AdaptiveMLBlender,
    period_title: str
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Matches forecasts to station observations on valid_time and calculates
    continuous, threshold (1.0 mm/h, 7.5 mm/h), and heavy-event statistics.
    """
    print(f"\n{'='*80}")
    print(f"VALIDATION TARGET: {period_title}")
    print(f"{'='*80}")
    
    merged = pd.merge(
        df_forecasts,
        df_obs[["valid_time", "observed_rainfall_mm_h"]],
        on="valid_time",
        how="inner"
    )
    n_instances = len(merged)
    n_unique_hours = merged["valid_time"].nunique()
    print(f"Matched Forecast Instances: {n_instances:,d}")
    print(f"Unique Matched Hourly Timestamps: {n_unique_hours:,d}")
    
    y_station = merged["observed_rainfall_mm_h"].values
    y_era5 = merged["reference_precipitation"].values
    
    # Compute member forecasts and ensembles
    f_ecmwf = merged["ECMWF_IFS_precip"].values
    f_gfs = merged["NOAA_GFS_precip"].values
    f_icon = merged["DWD_ICON_precip"].values
    f_simple = compute_simple_ensemble(merged)
    f_hist, _ = compute_historical_weighted_ensemble(merged)
    f_skyblend, _, _ = blender.predict_weights(merged)
    
    approaches = {
        "ECMWF IFS": f_ecmwf,
        "NOAA GFS": f_gfs,
        "DWD ICON": f_icon,
        "Simple Average": f_simple,
        "Historical Weighted": f_hist,
        "SkyBlend AI (Phase 6 Frozen)": f_skyblend,
    }
    
    results = []
    for name, f_vals in approaches.items():
        c_met = calculate_continuous_metrics(y_station, f_vals)
        cat_1 = calculate_categorical_metrics(y_station, f_vals, threshold=1.0)
        cat_75 = calculate_categorical_metrics(y_station, f_vals, threshold=7.5)
        
        # Heavy rain statistics (Observed >= 7.5 mm/h)
        heavy_mask = y_station >= 7.5
        hvy_mae = float(np.mean(np.abs(f_vals[heavy_mask] - y_station[heavy_mask]))) if heavy_mask.any() else 0.0
        hvy_bias = float(np.mean(f_vals[heavy_mask] - y_station[heavy_mask])) if heavy_mask.any() else 0.0
        obs_heavy_n = int(heavy_mask.sum())
        pred_heavy_n = int((f_vals >= 7.5).sum())
        
        results.append({
            "Approach": name,
            "MAE": c_met["MAE"],
            "RMSE": c_met["RMSE"],
            "Bias": c_met["Bias"],
            "Pearson_r": c_met["Pearson_r"],
            "POD_1.0": cat_1["POD"],
            "FAR_1.0": cat_1["FAR"],
            "CSI_1.0": cat_1["CSI"],
            "POD_7.5": cat_75["POD"],
            "FAR_7.5": cat_75["FAR"],
            "CSI_7.5": cat_75["CSI"],
            "Heavy_MAE": round(hvy_mae, 4),
            "Heavy_Bias": round(hvy_bias, 4),
            "Pred_Heavy_Count": pred_heavy_n,
            "Obs_Heavy_Count": obs_heavy_n
        })
        
    df_metrics = pd.DataFrame(results)
    
    # ERA5 vs Station ground truth reference comparison
    c_era5 = calculate_continuous_metrics(y_station, y_era5)
    cat_era5_1 = calculate_categorical_metrics(y_station, y_era5, threshold=1.0)
    cat_era5_75 = calculate_categorical_metrics(y_station, y_era5, threshold=7.5)
    era5_stats = {
        "Continuous": c_era5,
        "Cat_1.0": cat_era5_1,
        "Cat_7.5": cat_era5_75
    }
    
    print("\n[Continuous & Contingency Verification Matrix]:")
    print(df_metrics[[
        "Approach", "MAE", "RMSE", "Bias", "Pearson_r", "POD_1.0", "FAR_1.0", "CSI_1.0", "POD_7.5", "FAR_7.5", "CSI_7.5"
    ]].to_string(index=False))
    
    print("\n[Heavy-Event Contingency Breakdown (>= 7.5 mm/h)]:")
    print(df_metrics[[
        "Approach", "Obs_Heavy_Count", "Pred_Heavy_Count", "Heavy_MAE", "Heavy_Bias", "POD_7.5", "FAR_7.5", "CSI_7.5"
    ]].to_string(index=False))
    
    print(f"\n[Reference Comparison: ERA5 Reanalysis vs Station 42807 Ground Truth]:")
    print(f"  Continuous: MAE={c_era5['MAE']} mm/h | RMSE={c_era5['RMSE']} mm/h | Bias={c_era5['Bias']} mm/h | Pearson r={c_era5['Pearson_r']}")
    print(f"  Thresh 1.0: POD={cat_era5_1['POD']} | FAR={cat_era5_1['FAR']} | CSI={cat_era5_1['CSI']}")
    print(f"  Thresh 7.5: POD={cat_era5_75['POD']} | FAR={cat_era5_75['FAR']} | CSI={cat_era5_75['CSI']}")
    
    return df_metrics, era5_stats


def main():
    print("=" * 80)
    print("SKYBLEND AI — INDEPENDENT STATION VALIDATION (KOLKATA / ALIPORE 42807)")
    print("=" * 80)
    
    # 1. Acquire observations
    df_obs = acquire_station_observations()
    
    # 2. Load frozen Phase 6 model
    print(f"[2/4] Loading frozen Phase 6 blender from {PHASE6_MODEL_DIR}...")
    blender = AdaptiveMLBlender(epsilon=1e-4, random_state=42, peak_lift_alpha=0.35, rain_threshold=2.0)
    blender.load(PHASE6_MODEL_DIR)
    
    # 3. Load feature datasets
    print("[3/4] Preparing test datasets...")
    exp_features_path = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_ml_features_2023_06_to_2024_05.csv"
    df_exp = pd.read_csv(exp_features_path)
    _, _, df_test, test_dates = split_data_chronologically(df_exp)
    df_test_wide = pivot_aligned_dataset(df_test)
    kol_pm = df_test_wide[df_test_wide["location_id"] == "kolkata"].copy()
    
    july_features_path = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_ml_features.csv"
    df_july = pd.read_csv(july_features_path)
    _, _, df_july_test, july_dates = split_data_chronologically(df_july)
    df_july_test_wide = pivot_aligned_dataset(df_july_test)
    kol_july = df_july_test_wide[df_july_test_wide["location_id"] == "kolkata"].copy()
    
    # 4. Execute validation
    print("[4/4] Executing independent station validation across target periods...")
    pm_metrics, pm_era5 = evaluate_forecast_set(
        kol_pm, df_obs, blender,
        "PRE-MONSOON BENCHMARK TEST SPLIT (2024-04-07 to 2024-05-31)"
    )
    
    july_metrics, july_era5 = evaluate_forecast_set(
        kol_july, df_obs, blender,
        "JULY 2024 MONSOON TEST HOLDOUT (2024-07-24 to 2024-07-28)"
    )
    
    print("\n" + "=" * 80)
    print("INDEPENDENT STATION VALIDATION COMPLETED SUCCESSFULLY.")
    print("=" * 80)


if __name__ == "__main__":
    main()
