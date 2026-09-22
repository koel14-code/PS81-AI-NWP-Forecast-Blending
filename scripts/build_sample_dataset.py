"""
Build Sample Dataset Script.

Executes the PS81 Data Ingestion and Alignment Pipeline for a target location
(default: Kolkata, Lat=22.57, Lon=88.36) over a specified date range.

Outputs aligned multi-model forecast data alongside ERA5 reanalysis reference data to:
data/processed/aligned_rainfall_sample.csv
"""

import os
import sys
from pathlib import Path

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.data.sources import LocationConfig
from src.data.fetch_forecasts import fetch_nwp_forecasts
from src.data.fetch_reference import fetch_era5_reference
from src.data.alignment import align_forecasts_and_reference


def main():
    print("=" * 70)
    print("PS81 AI-NWP Forecast Blending System - Data Pipeline Runner")
    print("=" * 70)

    # 1. Target Location (Kolkata)
    location = LocationConfig(name="Kolkata", latitude=22.57, longitude=88.36)
    
    # 2. Historical Sample Date Range (72 hours of hourly data)
    start_date = "2024-07-15"
    end_date = "2024-07-17"
    
    # 3. Lead time horizons (Day-1 lead 1h-24h, Day-2 lead 25h-48h)
    lead_horizons = [0, 1]

    print(f"Target Location : {location.name} (Lat={location.latitude}, Lon={location.longitude})")
    print(f"Date Window     : {start_date} to {end_date} (UTC)")
    print(f"Lead Horizons   : {lead_horizons} (Day 1 & Day 2 initializations)")
    print("-" * 70)

    # 4. Fetch Forecasts
    print("Fetching multi-model forecasts (ECMWF IFS, NOAA GFS, DWD ICON)...")
    forecasts = fetch_nwp_forecasts(location, start_date, end_date)
    for model_name, records in forecasts.items():
        print(f"  - {model_name}: {len(records)} records fetched.")

    # 5. Fetch ERA5 Reference
    print("Fetching ERA5 reanalysis/reference precipitation data...")
    era5_records = fetch_era5_reference(location, start_date, end_date)
    print(f"  - ERA5 Reference: {len(era5_records)} records fetched.")

    # 6. Align Datasets & Run Data Quality Checks
    print("Aligning forecast and reference datasets by valid_time, location, and lead_hours...")
    aligned_df, quality_report = align_forecasts_and_reference(
        forecasts, era5_records, lead_time_horizons=lead_horizons
    )

    # 7. Save Processed Sample Dataset
    output_dir = ROOT_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "aligned_rainfall_sample.csv"
    
    aligned_df.to_csv(output_file, index=False)
    print(f"\nSaved aligned sample dataset to: {output_file}")

    # 8. Print Data Quality Report & Pipeline Summary
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION SUMMARY & DATA QUALITY REPORT")
    print("=" * 70)
    print(f"Total Rows Returned  : {len(aligned_df)}")
    print(f"Total Columns        : {len(aligned_df.columns)} ({list(aligned_df.columns)})")
    print(f"Date Range (UTC)     : {aligned_df['valid_time'].min()} to {aligned_df['valid_time'].max()}")
    print(f"Models Present       : {sorted(aligned_df['model'].unique().tolist())}")
    print(f"Lead Hours Present   : {sorted(aligned_df['lead_hours'].unique().tolist())}")
    print(f"Missing Values Count : {quality_report.missing_value_count}")
    print(f"Duplicate Count      : {quality_report.duplicate_count}")
    print(f"Quality Check Pass   : {quality_report.is_valid}")
    
    if quality_report.issues:
        print("\nData Quality Notes:")
        for issue in quality_report.issues:
            print(f"  - {issue}")

    print("\nFirst 5 Rows of Aligned Dataset:")
    print("-" * 70)
    print(aligned_df.head().to_string(index=False))
    print("=" * 70)


if __name__ == "__main__":
    main()
