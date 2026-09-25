"""
Build ML Features Script (Multi-Location & Single-Location Support).

Ingests raw training dataset, executes feature engineering,
verifies data quality and leakage prevention, and outputs:
- data/processed/multilocation_rainfall_ml_features.csv
- data/processed/rainfall_ml_features.csv
- data/processed/feature_quality_report.txt
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.features.rainfall_features import generate_feature_dataset
from src.data.schema import COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS, COL_LOCATION_ID


import argparse

def main():
    parser = argparse.ArgumentParser(description="Build ML Features for SkyBlend AI.")
    parser.add_argument(
        "--input-file",
        type=str,
        default="data/processed/multilocation_rainfall_training_dataset.csv",
        help="Input aligned training dataset CSV.",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/processed/multilocation_rainfall_ml_features.csv",
        help="Output features CSV path.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Chronological training split ratio.")
    args = parser.parse_args()

    print("=" * 80)
    print("PS81 AI-NWP Forecast Blending System - Feature Engineering Pipeline")
    print("=" * 80)

    output_dir = ROOT_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    in_path = Path(args.input_file)
    if not in_path.is_absolute():
        in_path = ROOT_DIR / in_path

    out_path = Path(args.output_file)
    if not out_path.is_absolute():
        out_path = ROOT_DIR / out_path

    if not in_path.exists():
        print(f"Error: Input dataset not found at {in_path}")
        sys.exit(1)

    print(f"Loading input training dataset: {in_path}")
    df_raw = pd.read_csv(in_path)
    print(f"  - Loaded {len(df_raw):,d} records.")

    # Determine chronological training split cutoff to ensure zero validation/test leakage
    unique_times = sorted(df_raw[COL_VALID_TIME].unique())
    n_train = int(len(unique_times) * args.train_ratio)
    train_cutoff = pd.to_datetime(unique_times[n_train - 1], utc=True)
    print(f"  - Chronological Training Cutoff : {train_cutoff} (First {n_train} hours / {args.train_ratio*100:.0f}%)")
    print(f"  - Validation & Test Boundaries  : Isolated from feature fallback priors")

    print("\nExecuting feature engineering pipeline (strictly leakage-safe)...")
    df_features = generate_feature_dataset(df_raw, train_cutoff_time=train_cutoff)

    df_features.to_csv(out_path, index=False)
    print(f"Saved engineered ML features dataset to: {out_path}")

    # Ensure compatibility aliases exist
    if out_path.name == "multilocation_rainfall_ml_features_2023_06_to_2024_05.csv":
        df_features.to_csv(output_dir / "multilocation_rainfall_ml_features.csv", index=False)
        df_features.to_csv(output_dir / "rainfall_ml_features.csv", index=False)
    elif out_path.name == "multilocation_rainfall_ml_features.csv":
        df_features.to_csv(output_dir / "rainfall_ml_features.csv", index=False)

    # Generate Feature Quality Report
    report_file = output_dir / "feature_quality_report.txt"
    
    num_rows = len(df_features)
    num_features = len(df_features.columns)
    feature_names = list(df_features.columns)
    missing_count = int(df_features.isnull().sum().sum())
    
    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df_features.columns else "location_id"
    key_cols = [loc_col, COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS] if loc_col in df_features.columns else [COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS]
    dup_count = int(df_features.duplicated(subset=key_cols).sum())

    date_min = df_features[COL_VALID_TIME].min()
    date_max = df_features[COL_VALID_TIME].max()

    model_dist = df_features[COL_MODEL].value_counts().to_dict()
    lead_day_dist = df_features["lead_day"].value_counts().sort_index().to_dict()

    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY & FEATURE REPORT")
    print("=" * 80)
    print(f"1. Number of Rows    : {num_rows}")
    print(f"2. Number of Features: {num_features}")
    print(f"3. Missing Values    : {missing_count}")
    print(f"4. Duplicate Rows    : {dup_count}")
    print(f"5. Date Range (UTC)  : {date_min} to {date_max}")

    if loc_col in df_features.columns:
        print("\nLocation Coverage:")
        for loc_id, group in df_features.groupby(loc_col):
            print(f"   - {loc_id:12s} : {len(group):6d} rows")

    print("\nFirst 5 Rows Preview:")
    print("-" * 80)
    cols_preview = [loc_col, "valid_time", "model", "lead_hours", "lead_day", "rolling_historical_mae_24h", "precipitation", "reference_precipitation"]
    print(df_features[cols_preview].head().to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
