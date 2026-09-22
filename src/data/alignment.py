"""
Dataset Alignment & Data Quality Validation Module.

Aligns multi-model NWP forecast time series with ERA5 reanalysis/reference values
on location_id, valid_time, latitude, longitude, model, and lead_hours.
Computes derived forecast_error and absolute_error, executes quality checks,
and produces standardized tabular datasets.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
import pandas as pd

from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_LATITUDE,
    COL_LONGITUDE,
    COL_MODEL,
    COL_FORECAST_RUN,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
    COL_FORECAST_ERROR,
    COL_ABSOLUTE_ERROR,
    REQUIRED_COLUMNS,
    DataQualityReport,
)


def align_forecasts_and_reference(
    forecasts_dict: Dict[str, List[Dict[str, Any]]],
    reference_records: List[Dict[str, Any]],
    lead_time_horizons: List[int] = None,
) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Aligns NWP forecast records with ERA5 reference precipitation data across locations.
    """
    quality_report = DataQualityReport()

    if lead_time_horizons is None:
        lead_time_horizons = [0, 1, 2]  # Default: Day 1 (1-24h), Day 2 (25-48h), Day 3 (49-72h)

    # Convert ERA5 reference records to lookup dictionary by (location_id, valid_time)
    ref_lookup: Dict[Tuple[str, str], float] = {}
    for ref in reference_records:
        loc_id = ref.get(COL_LOCATION_ID, "kolkata")
        vt = ref.get(COL_VALID_TIME)
        val = ref.get(COL_REF_PRECIPITATION)
        if vt is not None:
            ref_lookup[(loc_id, vt)] = val

    aligned_rows = []

    for model_name, records in forecasts_dict.items():
        for rec in records:
            loc_id = rec.get(COL_LOCATION_ID, "kolkata")
            vt_str = rec.get(COL_VALID_TIME)
            lat = rec.get(COL_LATITUDE)
            lon = rec.get(COL_LONGITUDE)
            precip = rec.get(COL_PRECIPITATION)

            if not vt_str:
                quality_report.invalid_timestamp_count += 1
                continue

            try:
                dt_valid = datetime.fromisoformat(vt_str.replace("Z", "+00:00"))
            except ValueError:
                quality_report.invalid_timestamp_count += 1
                continue

            for horizon_days in lead_time_horizons:
                if dt_valid.hour == 0:
                    base_run_date = dt_valid.date() - timedelta(days=1 + horizon_days)
                    lead_h = 24 + (horizon_days * 24)
                else:
                    base_run_date = dt_valid.date() - timedelta(days=horizon_days)
                    lead_h = dt_valid.hour + (horizon_days * 24)

                dt_run = datetime(base_run_date.year, base_run_date.month, base_run_date.day, 0, 0, 0, tzinfo=timezone.utc)

                # Look up corresponding ERA5 reference precipitation for this location and valid_time
                ref_precip = ref_lookup.get((loc_id, vt_str))

                if precip is not None and ref_precip is not None:
                    forecast_err = round(precip - ref_precip, 4)
                    abs_err = round(abs(forecast_err), 4)
                else:
                    forecast_err = None
                    abs_err = None

                aligned_rows.append({
                    COL_LOCATION_ID: loc_id,
                    COL_VALID_TIME: vt_str,
                    COL_LATITUDE: float(lat),
                    COL_LONGITUDE: float(lon),
                    COL_MODEL: model_name,
                    COL_FORECAST_RUN: dt_run.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    COL_LEAD_HOURS: lead_h,
                    COL_PRECIPITATION: precip,
                    COL_REF_PRECIPITATION: ref_precip,
                    COL_FORECAST_ERROR: forecast_err,
                    COL_ABSOLUTE_ERROR: abs_err,
                })

    df = pd.DataFrame(aligned_rows)
    if df.empty:
        quality_report.is_valid = False
        quality_report.issues.append("Aligned dataset is empty.")
        return df, quality_report

    df = df[REQUIRED_COLUMNS]
    df, quality_report = run_data_quality_checks(df, quality_report)

    return df, quality_report


def run_data_quality_checks(
    df: pd.DataFrame, report: DataQualityReport
) -> Tuple[pd.DataFrame, DataQualityReport]:
    """
    Executes automated data-quality checks on the aligned DataFrame:
    - Duplicates
    - Missing values
    - Negative precipitation
    - Inconsistent lead times
    - Model/Reference alignment gaps
    """
    report.total_records = len(df)

    key_cols = [COL_LOCATION_ID, COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS]
    dup_mask = df.duplicated(subset=key_cols, keep="first")
    report.duplicate_count = int(dup_mask.sum())
    if report.duplicate_count > 0:
        report.issues.append(f"Found {report.duplicate_count} duplicate records. Deduplicating...")
        df = df.drop_duplicates(subset=key_cols, keep="first")

    missing_count = df.isnull().sum().sum()
    report.missing_value_count = int(missing_count)
    if report.missing_value_count > 0:
        report.issues.append(f"Found {report.missing_value_count} missing values across columns.")

    neg_forecast = (df[COL_PRECIPITATION] < 0.0).sum() if COL_PRECIPITATION in df else 0
    neg_ref = (df[COL_REF_PRECIPITATION] < 0.0).sum() if COL_REF_PRECIPITATION in df else 0
    report.negative_precipitation_count = int(neg_forecast + neg_ref)
    if report.negative_precipitation_count > 0:
        report.issues.append(f"Found {report.negative_precipitation_count} negative precipitation values.")

    inconsistent_lead = (df[COL_LEAD_HOURS] < 1).sum()
    report.inconsistent_lead_time_count = int(inconsistent_lead)
    if report.inconsistent_lead_time_count > 0:
        report.issues.append(f"Found {report.inconsistent_lead_time_count} non-positive lead times.")

    unaligned_ref = df[COL_REF_PRECIPITATION].isnull().sum()
    report.unaligned_reference_count = int(unaligned_ref)
    if report.unaligned_reference_count > 0:
        report.issues.append(f"Found {report.unaligned_reference_count} records lacking ERA5 reference alignment.")

    report.is_valid = (
        report.duplicate_count == 0
        and report.missing_value_count == 0
        and report.negative_precipitation_count == 0
        and report.inconsistent_lead_time_count == 0
        and report.unaligned_reference_count == 0
    )

    return df, report
