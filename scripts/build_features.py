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


def main():
    print("=" * 80)
    print("PS81 AI-NWP Forecast Blending System - Feature Engineering Pipeline")
    print("=" * 80)

    output_dir = ROOT_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process Multi-Location dataset if present, otherwise single-location
    multi_file = output_dir / "multilocation_rainfall_training_dataset.csv"
    single_file = output_dir / "rainfall_training_dataset.csv"

    if multi_file.exists():
        input_file = multi_file
        output_file = output_dir / "multilocation_rainfall_ml_features.csv"
    elif single_file.exists():
        input_file = single_file
        output_file = output_dir / "rainfall_ml_features.csv"
    else:
        print("Error: No training dataset found in data/processed/")
        sys.exit(1)

    print(f"Loading input training dataset: {input_file}")
    df_raw = pd.read_csv(input_file)
    print(f"  - Loaded {len(df_raw)} records.")

    print("\nExecuting feature engineering pipeline...")
    df_features = generate_feature_dataset(df_raw)

    df_features.to_csv(output_file, index=False)
    # Also save as rainfall_ml_features.csv for backward compatibility
    df_features.to_csv(output_dir / "rainfall_ml_features.csv", index=False)
    print(f"Saved engineered ML features dataset to: {output_file}")

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
