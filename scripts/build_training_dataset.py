"""
Build Historical Training Dataset Script.

Generates a multi-week historical dataset for weather forecast error analysis and ML training
using ECMWF IFS, NOAA GFS, DWD ICON, and ERA5 reanalysis reference data.

Output File:
data/processed/rainfall_training_dataset.csv
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.data.sources import LocationConfig
from src.data.fetch_forecasts import fetch_nwp_forecasts
from src.data.fetch_reference import fetch_era5_reference
from src.data.alignment import align_forecasts_and_reference
from src.data.schema import (
    COL_VALID_TIME,
    COL_MODEL,
    COL_FORECAST_RUN,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
    COL_ABSOLUTE_ERROR,
)


def main():
    print("=" * 75)
    print("PS81 AI-NWP Forecast Blending System - Historical Training Dataset Builder")
    print("=" * 75)

    # 1. Location (Kolkata)
    location = LocationConfig(name="Kolkata", latitude=22.57, longitude=88.36)

    # 2. Historical Period (4 full weeks during Indian monsoon season)
    start_date = "2024-07-01"
    end_date = "2024-07-28"

    # 3. Target Lead Time Groups: 24h (Day 1), 48h (Day 2), 72h (Day 3)
    lead_horizons = [0, 1, 2]

    print(f"Target Location   : {location.name} (Lat={location.latitude}, Lon={location.longitude})")
    print(f"Historical Period : {start_date} to {end_date} UTC (4 Weeks)")
    print(f"Lead-Time Groups  : Day 1 (1-24h), Day 2 (25-48h), Day 3 (49-72h)")
    print("-" * 75)

    # 4. Fetch Multi-Model Forecasts
    print("Fetching historical multi-model forecasts (ECMWF IFS, NOAA GFS, DWD ICON)...")
    try:
        forecasts = fetch_nwp_forecasts(location, start_date, end_date)
        for model_name, records in forecasts.items():
            print(f"  - {model_name}: {len(records)} hourly records fetched.")
    except Exception as err:
        print(f"API Error fetching forecast data: {err}")
        sys.exit(1)

    # 5. Fetch ERA5 Reference
    print("Fetching ERA5 reanalysis/reference precipitation data...")
    try:
        era5_records = fetch_era5_reference(location, start_date, end_date)
        print(f"  - ERA5 Reference: {len(era5_records)} hourly records fetched.")
    except Exception as err:
        print(f"API Error fetching ERA5 reference data: {err}")
        sys.exit(1)

    # 6. Align Datasets & Calculate Errors
    print("Aligning datasets and computing forecast & absolute errors...")
    aligned_df, quality_report = align_forecasts_and_reference(
        forecasts, era5_records, lead_time_horizons=lead_horizons
    )

    # 7. Save Dataset
    output_dir = ROOT_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "rainfall_training_dataset.csv"
    
    aligned_df.to_csv(output_file, index=False)
    print(f"\nSaved historical training dataset to: {output_file}")

    # 8. Compute Real Baseline Forecast Error Statistics
    print("\n" + "=" * 75)
    print("DATASET METRICS & BASELINE FORECAST ERROR SUMMARY")
    print("=" * 75)
    print(f"Total Rows Returned  : {len(aligned_df)}")
    print(f"Total Columns        : {len(aligned_df.columns)}")
    print(f"Date Range (UTC)     : {aligned_df[COL_VALID_TIME].min()} to {aligned_df[COL_VALID_TIME].max()}")
    print(f"Models Present       : {sorted(aligned_df[COL_MODEL].unique().tolist())}")
    print(f"Lead Hours Range     : {aligned_df[COL_LEAD_HOURS].min()}h to {aligned_df[COL_LEAD_HOURS].max()}h")
    print(f"Missing Values Count : {quality_report.missing_value_count}")
    print(f"Duplicate Row Count  : {quality_report.duplicate_count}")

    # Coverage Details
    print("\n1. Rows Per Model:")
    model_counts = aligned_df[COL_MODEL].value_counts()
    for m, c in model_counts.items():
        print(f"   - {m:12s} : {c:5d} rows")

    print("\n2. Rows Per Lead-Time Horizon Group:")
    aligned_df["horizon_group"] = pd.cut(
        aligned_df[COL_LEAD_HOURS],
        bins=[0, 24, 48, 72],
        labels=["Day 1 (1-24h)", "Day 2 (25-48h)", "Day 3 (49-72h)"]
    )
    horizon_counts = aligned_df["horizon_group"].value_counts().sort_index()
    for h_label, count in horizon_counts.items():
        print(f"   - {h_label:15s} : {count:5d} rows")

    # Baseline MAE by Model (Calculated directly from downloaded real data)
    print("\n3. Baseline Mean Absolute Error (MAE) by Model (mm/h):")
    mae_by_model = aligned_df.groupby(COL_MODEL)[COL_ABSOLUTE_ERROR].mean()
    for model_name, mae_val in mae_by_model.items():
        print(f"   - {model_name:12s} : {mae_val:.4f} mm/h")

    # Baseline MAE by Lead Horizon Group
    print("\n4. Baseline Mean Absolute Error (MAE) by Lead Horizon Group (mm/h):")
    mae_by_horizon = aligned_df.groupby("horizon_group", observed=True)[COL_ABSOLUTE_ERROR].mean()
    for h_label, mae_val in mae_by_horizon.items():
        print(f"   - {h_label:15s} : {mae_val:.4f} mm/h")

    print("\nFirst 5 Rows of Aligned Training Dataset:")
    print("-" * 75)
    cols_to_show = [COL_VALID_TIME, COL_MODEL, COL_FORECAST_RUN, COL_LEAD_HOURS, COL_PRECIPITATION, COL_REF_PRECIPITATION, COL_ABSOLUTE_ERROR]
    print(aligned_df[cols_to_show].head().to_string(index=False))
    print("=" * 75)


if __name__ == "__main__":
    main()
