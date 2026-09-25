"""
Build Multi-Location Training Dataset Script.

Executes the PS81 Data Ingestion and Alignment Pipeline across 6 demonstration locations:
1. Kolkata (22.57, 88.36)
2. Delhi (28.61, 77.21)
3. Mumbai (19.08, 72.88)
4. Chennai (13.08, 80.27)
5. Guwahati (26.14, 91.74)
6. Bengaluru (12.97, 77.59)

Period: July 1, 2024 through July 28, 2024 (4 weeks UTC).

Outputs:
- data/processed/multilocation_rainfall_training_dataset.csv
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.data.sources import DEMO_LOCATIONS
from src.data.fetch_forecasts import fetch_nwp_forecasts
from src.data.fetch_reference import fetch_era5_reference
from src.data.alignment import align_forecasts_and_reference
from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_MODEL,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
    COL_ABSOLUTE_ERROR,
)


import argparse

def main():
    parser = argparse.ArgumentParser(description="Build Multi-Location Training Dataset for SkyBlend AI.")
    parser.add_argument("--start-date", type=str, default="2023-06-01", help="Start date (YYYY-MM-DD), UTC.")
    parser.add_argument("--end-date", type=str, default="2024-05-31", help="End date (YYYY-MM-DD), UTC.")
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/processed/multilocation_rainfall_training_dataset_2023_06_to_2024_05.csv",
        help="Target output CSV file path.",
    )
    args = parser.parse_args()

    print("=" * 80)
    print("PS81 AI-NWP Forecast Blending System - Multi-Location Dataset Builder")
    print("=" * 80)

    start_date = args.start_date
    end_date = args.end_date
    lead_horizons = [0, 1, 2]

    out_path = Path(args.output_file)
    if not out_path.is_absolute():
        out_path = ROOT_DIR / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_aligned_dfs = []

    print(f"Target Locations  : {len(DEMO_LOCATIONS)} ({', '.join(DEMO_LOCATIONS.keys())})")
    print(f"Historical Period : {start_date} to {end_date} UTC")
    print(f"Lead-Time Groups  : Day 1 (1-24h), Day 2 (25-48h), Day 3 (49-72h)")
    print(f"Target Output     : {out_path}")
    print("-" * 80)

    for loc_id, loc_cfg in DEMO_LOCATIONS.items():
        print(f"\nProcessing Location: {loc_cfg.name:12s} (Lat={loc_cfg.latitude:.2f}, Lon={loc_cfg.longitude:.2f})...")
        
        # 1. Fetch Forecasts
        forecasts = fetch_nwp_forecasts(loc_cfg, start_date, end_date)
        
        # 2. Fetch ERA5 Reference
        era5_recs = fetch_era5_reference(loc_cfg, start_date, end_date)
        
        # 3. Align Location Dataset
        loc_df, q_rep = align_forecasts_and_reference(forecasts, era5_recs, lead_time_horizons=lead_horizons)
        
        print(f"  - Rows Returned : {len(loc_df):5d} | Date Range: {loc_df[COL_VALID_TIME].min()} to {loc_df[COL_VALID_TIME].max()}")
        print(f"  - Missing Values: {q_rep.missing_value_count} | Duplicates: {q_rep.duplicate_count}")
        
        all_aligned_dfs.append(loc_df)

    # Combine all multi-location dataframes
    combined_df = pd.concat(all_aligned_dfs, ignore_index=True)
    combined_df.to_csv(out_path, index=False)
    print(f"\nSaved combined multi-location training dataset to: {out_path}")

    # Print Comprehensive Pre-Training Validation Report
    print("\n" + "=" * 80)
    print("MULTI-LOCATION PRE-TRAINING DATASET VALIDATION REPORT")
    print("=" * 80)
    print(f"Total Combined Rows  : {len(combined_df)}")
    print(f"Total Columns        : {len(combined_df.columns)} ({list(combined_df.columns)})")
    print(f"Date Range (UTC)     : {combined_df[COL_VALID_TIME].min()} to {combined_df[COL_VALID_TIME].max()}")
    print(f"Missing Values Count : {combined_df.isnull().sum().sum()}")
    print(f"Duplicate Rows Count : {combined_df.duplicated(subset=['location_id', 'valid_time', 'model', 'lead_hours']).sum()}")

    print("\n1. Coverage per Location:")
    for loc_id, group in combined_df.groupby(COL_LOCATION_ID):
        print(f"   - {loc_id:12s} : {len(group):6d} rows | Range: {group[COL_VALID_TIME].min()} to {group[COL_VALID_TIME].max()}")

    print("\n2. Coverage per Model:")
    for m_name, group in combined_df.groupby(COL_MODEL):
        print(f"   - {m_name:12s} : {len(group):6d} rows")

    print("\n3. Coverage per Lead-Time Horizon Group:")
    combined_df["lead_day"] = pd.cut(combined_df[COL_LEAD_HOURS], bins=[0, 24, 48, 72], labels=["Day 1 (1-24h)", "Day 2 (25-48h)", "Day 3 (49-72h)"])
    for h_label, group in combined_df.groupby("lead_day", observed=True):
        print(f"   - {h_label:15s} : {len(group):6d} rows")

    print("=" * 80)


if __name__ == "__main__":
    main()
