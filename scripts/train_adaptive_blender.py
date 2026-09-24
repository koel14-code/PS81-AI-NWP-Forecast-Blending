"""
Train Adaptive Forecast Blender Script (Multi-Location Support).

Ingests data/processed/multilocation_rainfall_ml_features.csv (or rainfall_ml_features.csv),
performs chronological data splitting (70% Train, 15% Validation, 15% Test), trains error-prediction
models per NWP source across locations, and saves model binaries to models/.
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.blending.baselines import split_data_chronologically, pivot_aligned_dataset
from src.blending.ml_blender import AdaptiveMLBlender
from src.blending.evaluation import calculate_continuous_metrics, calculate_categorical_metrics
from src.data.schema import COL_LOCATION_ID


def main():
    print("=" * 80)
    print("PS81 AI-NWP Forecast Blending System - Multi-Location Model Training Pipeline")
    print("=" * 80)

    output_dir = ROOT_DIR / "data" / "processed"
    multi_file = output_dir / "multilocation_rainfall_ml_features.csv"
    single_file = output_dir / "rainfall_ml_features.csv"

    if multi_file.exists():
        input_file = multi_file
    elif single_file.exists():
        input_file = single_file
    else:
        print("Error: Input ML features dataset not found in data/processed/")
        sys.exit(1)

    print(f"Loading input ML features dataset: {input_file}")
    df_features = pd.read_csv(input_file)
    print(f"  - Loaded {len(df_features)} records.")

    # 1. Chronological Data Splitting (70% Train, 15% Val, 15% Test)
    print("\nPerforming chronological data split (70% Train, 15% Val, 15% Test)...")
    df_train, df_val, df_test, date_ranges = split_data_chronologically(df_features)

    print(f"  - TRAIN Split      : {len(df_train):6d} rows | Range: {date_ranges['train'][0]} to {date_ranges['train'][1]}")
    print(f"  - VALIDATION Split : {len(df_val):6d} rows | Range: {date_ranges['validation'][0]} to {date_ranges['validation'][1]}")
    print(f"  - TEST Split       : {len(df_test):6d} rows | Range: {date_ranges['test'][0]} to {date_ranges['test'][1]}")
    print("  - NOTE: TEST set is strictly quarantined for final unbiased evaluation.")

    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df_train.columns else "location_id"
    if loc_col in df_train.columns:
        print(f"\nLocation Coverage in TRAIN set ({df_train[loc_col].nunique()} locations):")
        for loc_id, grp in df_train.groupby(loc_col):
            print(f"   - {loc_id:12s} : {len(grp):5d} rows")

    # 2. Train Adaptive ML Blender using Validation Split for Early Stopping
    print("\nTraining Multi-Location Adaptive ML Error Predictors with Validation Early Stopping...")
    blender = AdaptiveMLBlender(random_state=42)
    blender.fit(df_train, df_val_long=df_val)

    # 3. Model Validation Performance Assessment
    print("\nEvaluating Model on Held-Out Chronological VALIDATION Set...")
    df_val_wide = pivot_aligned_dataset(df_val)
    f_val_ml, _, _ = blender.predict_weights(df_val_wide)
    y_val_true = df_val_wide["reference_precipitation"].values

    val_c_met = calculate_continuous_metrics(y_val_true, f_val_ml)
    val_cat_met = calculate_categorical_metrics(y_val_true, f_val_ml, threshold=1.0)
    print(f"  - Validation MAE   : {val_c_met['MAE']:.4f} mm/h")
    print(f"  - Validation RMSE  : {val_c_met['RMSE']:.4f} mm/h")
    print(f"  - Validation Bias  : {val_c_met['Bias']:.4f} mm/h")
    print(f"  - Validation Corr  : {val_c_met['Pearson_r']:.4f}")
    print(f"  - Validation POD   : {val_cat_met['POD']:.4f}")
    print(f"  - Validation FAR   : {val_cat_met['FAR']:.4f}")
    print(f"  - Validation CSI   : {val_cat_met['CSI']:.4f}")

    for m_name, model_obj in blender.models.items():
        print(f"  - {m_name:12s} boosting trees stopped at iteration: {model_obj.n_iter_}")

    # 4. Save Model Artifacts
    model_dir = ROOT_DIR / "models"
    blender.save(model_dir)
    print(f"\nSaved validated model binaries to: {model_dir}")
    print("  - adaptive_blender_ECMWF_IFS.joblib")
    print("  - adaptive_blender_NOAA_GFS.joblib")
    print("  - adaptive_blender_DWD_ICON.joblib")

    print("\nTraining pipeline completed reproducibly without test set contamination.")
    print("=" * 80)


if __name__ == "__main__":
    main()
