"""
Train and Evaluate Expanded SkyBlend AI (Full-Year 2023-06 to 2024-05).

Executes:
1. Chronological splitting of expanded dataset:
   - TRAIN (70%): 2023-06-01 to 2024-02-12 (Monsoon, Post-monsoon, Early Winter)
   - VALIDATION (15%): 2024-02-12 to 2024-04-07 (Late Winter, Early Pre-monsoon)
   - TEST (15%): 2024-04-07 to 2024-05-31 (Peak Pre-monsoon Convective Season)
2. Retraining Candidate F Adaptive Blender with Validation Early Stopping.
   - 12 features (spatial, temporal, NWP precipitation, rolling causal error, ensemble disagreement spread)
   - Convective peak preservation (alpha=0.35, threshold=2.0 mm/h)
   - Saved to models/expanded_full_year/
3. Verification on Untouched Pre-Monsoon TEST Set (2024-04-07 to 2024-05-31).
4. Out-of-Period Generalization Verification on July 2024 Holdout (2024-07-24 to 2024-07-28).
5. Comprehensive comparison against raw NWP (ECMWF, GFS, ICON, Simple Average) and Phase 2/3 baseline.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.blending.baselines import (
    split_data_chronologically,
    pivot_aligned_dataset,
    compute_simple_ensemble,
    compute_historical_weighted_ensemble,
)
from src.blending.ml_blender import AdaptiveMLBlender, FEATURE_COLS, MODEL_NAMES
from src.blending.evaluation import calculate_continuous_metrics, calculate_categorical_metrics
from src.data.schema import COL_LOCATION_ID, COL_VALID_TIME


def compute_comprehensive_metrics(y_true: np.ndarray, y_pred: np.ndarray, approach_name: str) -> dict:
    """Computes overall continuous, categorical, regime breakdowns, and heavy-event counts."""
    c_met = calculate_continuous_metrics(y_true, y_pred)
    cat_met = calculate_categorical_metrics(y_true, y_pred, threshold=1.0)

    # Regime masks
    no_rain_mask = y_true < 0.1
    light_mask = (y_true >= 0.1) & (y_true < 2.5)
    mod_mask = (y_true >= 2.5) & (y_true < 7.5)
    heavy_mask = y_true >= 7.5

    def get_regime_stats(mask):
        if not mask.any():
            return 0.0, 0.0, 0.0
        errs = y_pred[mask] - y_true[mask]
        mae = float(np.mean(np.abs(errs)))
        rmse = float(np.sqrt(np.mean(errs ** 2)))
        bias = float(np.mean(errs))
        return round(mae, 4), round(rmse, 4), round(bias, 4)

    no_mae, _, _ = get_regime_stats(no_rain_mask)
    lt_mae, _, _ = get_regime_stats(light_mask)
    mod_mae, _, mod_bias = get_regime_stats(mod_mask)
    hvy_mae, _, hvy_bias = get_regime_stats(heavy_mask)

    total_n = len(y_true)
    obs_heavy = int(heavy_mask.sum())
    pred_heavy = int((y_pred >= 7.5).sum())
    freq_heavy = round(pred_heavy / total_n, 5) if total_n > 0 else 0.0

    return {
        "Approach": approach_name,
        "MAE": c_met["MAE"],
        "RMSE": c_met["RMSE"],
        "Bias": c_met["Bias"],
        "Pearson_r": c_met["Pearson_r"],
        "POD_1.0": cat_met["POD"],
        "FAR_1.0": cat_met["FAR"],
        "CSI_1.0": cat_met["CSI"],
        "NoRain_MAE": no_mae,
        "Light_MAE": lt_mae,
        "Mod_MAE": mod_mae,
        "Mod_Bias": mod_bias,
        "Heavy_MAE": hvy_mae,
        "Heavy_Bias": hvy_bias,
        "Obs_Heavy": obs_heavy,
        "Pred_Heavy": pred_heavy,
        "Pred_Heavy_Freq": freq_heavy,
    }


def main():
    print("=" * 90)
    print("SKYBLEND AI (PS81) — EXPANDED FULL-YEAR RETRAINING & EVALUATION PIPELINE")
    print("=" * 90)

    expanded_features_path = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_ml_features_2023_06_to_2024_05.csv"
    july_features_path = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_ml_features.csv"

    if not expanded_features_path.exists():
        print(f"Error: Expanded features file not found at {expanded_features_path}")
        sys.exit(1)

    print(f"Loading expanded features dataset: {expanded_features_path} ...")
    df_exp = pd.read_csv(expanded_features_path)
    print(f"  - Loaded {len(df_exp):,d} records.")

    # 1. Chronological Splitting (70% Train, 15% Validation, 15% Test)
    df_train, df_val, df_test, date_ranges = split_data_chronologically(df_exp)

    print("\nChronological Split Ranges:")
    print(f"  - TRAIN Split      (70%): {len(df_train):,d} rows | {date_ranges['train'][0]} to {date_ranges['train'][1]}")
    print(f"  - VALIDATION Split (15%): {len(df_val):,d} rows | {date_ranges['validation'][0]} to {date_ranges['validation'][1]}")
    print(f"  - TEST Split       (15%): {len(df_test):,d} rows | {date_ranges['test'][0]} to {date_ranges['test'][1]}")

    # 2. Retrain Candidate F with Early Stopping on Chronological Validation Split
    print("\nTraining Candidate F on Full-Year Train Set with Validation Early Stopping...")
    model_dir = ROOT_DIR / "models" / "expanded_full_year"
    model_dir.mkdir(parents=True, exist_ok=True)

    blender = AdaptiveMLBlender(
        epsilon=1e-4,
        random_state=42,
        peak_lift_alpha=0.35,
        rain_threshold=2.0,
    )
    blender.fit(df_train, df_val_long=df_val)
    blender.save(model_dir)

    for m_name, model_obj in blender.models.items():
        print(f"  - {m_name:12s} boosting trees stopped at iteration: {model_obj.n_iter_}")

    # -------------------------------------------------------------
    # 3. EVALUATION ON UNTOUCHED EXPANDED PRE-MONSOON TEST SET
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("EVALUATION 1: UNTOUCHED EXPANDED TEST SET (April 7 to May 31, 2024 — Peak Pre-Monsoon)")
    print("=" * 90)

    df_test_wide = pivot_aligned_dataset(df_test)
    y_test_true = df_test_wide["reference_precipitation"].values

    f_ecmwf_test = df_test_wide["ECMWF_IFS_precip"].values
    f_gfs_test = df_test_wide["NOAA_GFS_precip"].values
    f_icon_test = df_test_wide["DWD_ICON_precip"].values
    f_simple_test = compute_simple_ensemble(df_test_wide)
    f_hist_test, _ = compute_historical_weighted_ensemble(df_test_wide)
    f_ml_test, weights_test, _ = blender.predict_weights(df_test_wide)

    test_approaches = {
        "1. ECMWF_IFS": f_ecmwf_test,
        "2. NOAA_GFS": f_gfs_test,
        "3. DWD_ICON": f_icon_test,
        "4. Simple_Average": f_simple_test,
        "5. Historical_Weighted": f_hist_test,
        "6. SkyBlend (Retrained Candidate F)": f_ml_test,
    }

    test_results = [
        compute_comprehensive_metrics(y_test_true, f_vals, app_name)
        for app_name, f_vals in test_approaches.items()
    ]
    df_test_results = pd.DataFrame(test_results)
    
    print("\nOVERALL METRICS (PRE-MONSOON TEST SET):")
    print(df_test_results[["Approach", "MAE", "RMSE", "Bias", "Pearson_r", "POD_1.0", "FAR_1.0", "CSI_1.0"]].to_string(index=False))

    print("\nREGIME & HEAVY EVENT PERFORMANCE (PRE-MONSOON TEST SET):")
    print(df_test_results[["Approach", "NoRain_MAE", "Light_MAE", "Mod_MAE", "Heavy_MAE", "Heavy_Bias", "Obs_Heavy", "Pred_Heavy", "Pred_Heavy_Freq"]].to_string(index=False))

    # -------------------------------------------------------------
    # 4. OUT-OF-PERIOD GENERALIZATION ON JULY 2024 HOLDOUT
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("EVALUATION 2: OUT-OF-PERIOD GENERALIZATION ON JULY 2024 HOLDOUT (MONSOON)")
    print("=" * 90)

    if july_features_path.exists():
        df_july = pd.read_csv(july_features_path)
        # Evaluate on the July test split (July 24-28, 2024)
        _, _, df_july_test, july_dates = split_data_chronologically(df_july)
        df_july_test_wide = pivot_aligned_dataset(df_july_test)
        y_july_true = df_july_test_wide["reference_precipitation"].values

        f_ecmwf_july = df_july_test_wide["ECMWF_IFS_precip"].values
        f_gfs_july = df_july_test_wide["NOAA_GFS_precip"].values
        f_icon_july = df_july_test_wide["DWD_ICON_precip"].values
        f_simple_july = compute_simple_ensemble(df_july_test_wide)
        f_hist_july, _ = compute_historical_weighted_ensemble(df_july_test_wide)
        f_ml_july, weights_july, _ = blender.predict_weights(df_july_test_wide)

        july_approaches = {
            "1. ECMWF_IFS": f_ecmwf_july,
            "2. NOAA_GFS": f_gfs_july,
            "3. DWD_ICON": f_icon_july,
            "4. Simple_Average": f_simple_july,
            "5. Historical_Weighted": f_hist_july,
            "6. SkyBlend (Retrained Full-Year)": f_ml_july,
        }

        july_results = [
            compute_comprehensive_metrics(y_july_true, f_vals, app_name)
            for app_name, f_vals in july_approaches.items()
        ]
        df_july_results = pd.DataFrame(july_results)

        print("\nOVERALL METRICS (JULY 2024 TEST HOLDOUT):")
        print(df_july_results[["Approach", "MAE", "RMSE", "Bias", "Pearson_r", "POD_1.0", "FAR_1.0", "CSI_1.0"]].to_string(index=False))

        print("\nREGIME & HEAVY EVENT PERFORMANCE (JULY 2024 TEST HOLDOUT):")
        print(df_july_results[["Approach", "NoRain_MAE", "Light_MAE", "Mod_MAE", "Heavy_MAE", "Heavy_Bias", "Obs_Heavy", "Pred_Heavy", "Pred_Heavy_Freq"]].to_string(index=False))

        # Save artifacts
        out_dir = ROOT_DIR / "data" / "processed"
        df_test_results.to_csv(out_dir / "expanded_test_performance.csv", index=False)
        df_test_results.to_csv(out_dir / "model_performance_test.csv", index=False)
        df_july_results.to_csv(out_dir / "july_holdout_performance.csv", index=False)
        print(f"\nSaved evaluation artifacts to: {out_dir}")

    print("=" * 90)


if __name__ == "__main__":
    main()
