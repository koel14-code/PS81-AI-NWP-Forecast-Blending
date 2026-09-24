"""
Data Quality Audit & Integrity Verification Suite for SkyBlend AI Datasets.

Audits:
- Number of unique locations
- Number of unique models
- Number of forecast runs
- Number of valid timestamps
- Temporal coverage and date range
- Lead-hour distribution & missing lead horizons
- Record counts per model and location
- Missing values / nulls
- Duplicate (location_id, model, forecast_run, valid_time) keys
- Impossible negative lead times
- Reference precipitation coverage
- Forecast precipitation coverage

Exits with code 1 if critical integrity checks fail, or code 0 if all checks pass.
Usage:
    python scripts/audit_forecast_dataset.py [--input path/to/dataset.csv]
"""

import sys
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_MODEL,
    COL_FORECAST_RUN,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
)


def run_audit(file_path: Path) -> bool:
    print("=" * 85)
    print(f"SKYBLEND AI — DATA QUALITY & INTEGRITY AUDIT")
    print(f"Target File: {file_path}")
    print("=" * 85)

    if not file_path.exists():
        print(f"[FATAL ERROR]: Dataset file does not exist: {file_path}")
        return False

    df = pd.read_csv(file_path)
    total_records = len(df)
    print(f"Total Rows Loaded: {total_records:,}")

    critical_failures = []
    warnings = []

    # 1. Location Coverage
    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df.columns else "location_id"
    if loc_col not in df.columns:
        critical_failures.append(f"Missing primary location identifier column '{loc_col}'.")
        unique_locs = []
    else:
        unique_locs = df[loc_col].unique().tolist()
        print(f"\n1. Locations ({len(unique_locs)} total): {', '.join(sorted(unique_locs))}")
        loc_counts = df[loc_col].value_counts().to_dict()
        for loc, count in sorted(loc_counts.items()):
            print(f"   - {loc:12s} : {count:6,d} records ({count/total_records*100:5.1f}%)")

    # 2. Model Coverage
    if COL_MODEL not in df.columns:
        critical_failures.append(f"Missing model column '{COL_MODEL}'.")
        unique_models = []
    else:
        unique_models = df[COL_MODEL].unique().tolist()
        print(f"\n2. NWP Models ({len(unique_models)} total): {', '.join(sorted(unique_models))}")
        model_counts = df[COL_MODEL].value_counts().to_dict()
        for m, count in sorted(model_counts.items()):
            print(f"   - {m:12s} : {count:6,d} records ({count/total_records*100:5.1f}%)")

    # 3. Temporal Coverage & Date Ranges
    if COL_VALID_TIME not in df.columns:
        critical_failures.append(f"Missing valid time column '{COL_VALID_TIME}'.")
        n_valid = 0
    else:
        dt_valids = pd.to_datetime(df[COL_VALID_TIME], utc=True)
        min_vt = dt_valids.min()
        max_vt = dt_valids.max()
        n_valid = df[COL_VALID_TIME].nunique()
        print(f"\n3. Valid Timestamp Coverage:")
        print(f"   - Unique Valid Timestamps : {n_valid:,}")
        print(f"   - Date Range (UTC)        : {min_vt.strftime('%Y-%m-%d %H:%M:%S UTC')} to {max_vt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   - Duration Span           : {(max_vt - min_vt).days} days, {(max_vt - min_vt).seconds // 3600} hours")

    # 4. Forecast Run Coverage
    if COL_FORECAST_RUN not in df.columns:
        warnings.append(f"Column '{COL_FORECAST_RUN}' not present in dataset.")
        n_runs = 0
    else:
        dt_runs = pd.to_datetime(df[COL_FORECAST_RUN], utc=True)
        n_runs = df[COL_FORECAST_RUN].nunique()
        print(f"\n4. Forecast Runs:")
        print(f"   - Unique Initialization Runs : {n_runs:,}")
        print(f"   - Run Date Range (UTC)       : {dt_runs.min().strftime('%Y-%m-%d %H:%M:%S UTC')} to {dt_runs.max().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # 5. Lead-Time Distribution & Horizons
    if COL_LEAD_HOURS not in df.columns:
        critical_failures.append(f"Missing lead hours column '{COL_LEAD_HOURS}'.")
    else:
        lead_series = df[COL_LEAD_HOURS]
        print(f"\n5. Lead-Time Distribution:")
        print(f"   - Lead Hours Min / Max : {lead_series.min():.0f}h / {lead_series.max():.0f}h")
        print(f"   - Unique Lead Horizons : {sorted(lead_series.unique().tolist())}")
        
        # Check negative lead times
        neg_leads = (lead_series < 0).sum()
        if neg_leads > 0:
            critical_failures.append(f"Found {neg_leads} records with impossible negative lead hours.")
        else:
            print("   - Negative Lead Hours  : 0 (PASSED)")

        # Check lead horizons (Day 1: 1-24h, Day 2: 25-48h, Day 3: 49-72h)
        day1_count = ((lead_series >= 1) & (lead_series <= 24)).sum()
        day2_count = ((lead_series >= 25) & (lead_series <= 48)).sum()
        day3_count = ((lead_series >= 49) & (lead_series <= 72)).sum()
        print(f"   - Day 1 Horizon (1-24h)  : {day1_count:6,d} rows ({day1_count/total_records*100:5.1f}%)")
        print(f"   - Day 2 Horizon (25-48h) : {day2_count:6,d} rows ({day2_count/total_records*100:5.1f}%)")
        print(f"   - Day 3 Horizon (49-72h) : {day3_count:6,d} rows ({day3_count/total_records*100:5.1f}%)")

        if day1_count == 0 or day2_count == 0 or day3_count == 0:
            warnings.append("One or more standard lead horizons (Day 1, 2, 3) has zero records.")

    # 6. Duplicate Primary Key Integrity Check
    primary_keys = [loc_col, COL_MODEL, COL_FORECAST_RUN, COL_VALID_TIME]
    available_keys = [k for k in primary_keys if k in df.columns]
    if len(available_keys) == len(primary_keys):
        dup_count = df.duplicated(subset=available_keys).sum()
        print(f"\n6. Duplicate Key Verification on {available_keys}:")
        if dup_count > 0:
            critical_failures.append(f"Found {dup_count} duplicate records on primary keys {available_keys}.")
            print(f"   - Duplicates Found : {dup_count} [FAILED]")
        else:
            print("   - Duplicates Found : 0 (PASSED)")

    # 7. Missing Values & Coverage Audit
    print(f"\n7. Data Completeness & Coverage:")
    null_counts = df.isnull().sum()
    has_nulls = False
    for col, count in null_counts.items():
        if count > 0:
            has_nulls = True
            print(f"   - [WARN] Column '{col}' has {count:,} nulls ({count/total_records*100:.2f}%)")
            if col in [COL_PRECIPITATION, COL_REF_PRECIPITATION, COL_VALID_TIME, loc_col, COL_MODEL]:
                critical_failures.append(f"Critical column '{col}' contains {count} missing/null values.")
    if not has_nulls:
        print("   - Null Values across all columns : 0 (PASSED - 100% complete)")

    # Reference Coverage
    ref_col = COL_REF_PRECIPITATION if COL_REF_PRECIPITATION in df.columns else "reference_precipitation"
    if ref_col in df.columns:
        valid_ref = df[ref_col].notnull().sum()
        print(f"   - Reference (ERA5) Coverage      : {valid_ref:,} / {total_records:,} ({valid_ref/total_records*100:.1f}%)")
    
    # Forecast Coverage
    precip_col = COL_PRECIPITATION if COL_PRECIPITATION in df.columns else "precipitation"
    if precip_col in df.columns:
        valid_fcst = df[precip_col].notnull().sum()
        print(f"   - Forecast Coverage              : {valid_fcst:,} / {total_records:,} ({valid_fcst/total_records*100:.1f}%)")

    # 8. Genuine Lead-Time Integrity Diagnostic
    print(f"\n8. Lead-Time Generation & Source Authenticity Diagnostic:")
    if COL_FORECAST_RUN in df.columns and COL_VALID_TIME in df.columns and COL_LEAD_HOURS in df.columns:
        computed_diff_hours = (pd.to_datetime(df[COL_VALID_TIME], utc=True) - pd.to_datetime(df[COL_FORECAST_RUN], utc=True)).dt.total_seconds() / 3600.0
        mismatch_count = (np.abs(computed_diff_hours - df[COL_LEAD_HOURS]) > 1e-4).sum()
        if mismatch_count > 0:
            critical_failures.append(f"Found {mismatch_count} rows where lead_hours != (valid_time - forecast_run).")
            print(f"   - Mathematical Consistency (valid_time - forecast_run == lead_hours) : [FAILED] ({mismatch_count} mismatches)")
        else:
            print("   - Mathematical Consistency (valid_time - forecast_run == lead_hours) : PASSED")

        # Check whether precipitation is identical across horizons for the same valid time
        sample_check = df.groupby([loc_col, COL_MODEL, COL_VALID_TIME])[precip_col].nunique()
        identical_pct = (sample_check == 1).mean() * 100.0
        print(f"   - Precipitation Invariance across Lead Horizons: {identical_pct:.1f}% of timestamps have identical values across Day 1/2/3.")
        if identical_pct > 90.0:
            warnings.append(
                "DATA LIMITATION: Forecast values are identical across lead horizons for the same valid timestamp. "
                "The source is a seamless forecast series rather than independently archived model runs."
            )

    print("\n" + "=" * 85)
    print("AUDIT SUMMARY & CONCLUSION:")
    print("=" * 85)

    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  [WARN] {w}")

    if critical_failures:
        print(f"\nCRITICAL INTEGRITY FAILURES ({len(critical_failures)}):")
        for f in critical_failures:
            print(f"  [FAIL] {f}")
        print("\nAudit Status: FAILED (Critical integrity errors found)")
        return False

    print("\nAudit Status: PASSED (Zero critical failures)")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit NWP forecast dataset for PS81 SkyBlend AI.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(ROOT_DIR / "data" / "processed" / "multilocation_rainfall_training_dataset.csv"),
        help="Path to CSV dataset to audit.",
    )
    args = parser.parse_args()
    success = run_audit(Path(args.input))
    sys.exit(0 if success else 1)
