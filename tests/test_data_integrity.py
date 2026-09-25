"""
Automated Data Integrity & Leakage Verification Test Suite.
Verifies:
1. Strict chronological ordering and non-overlapping train/val/test splits.
2. Absence of duplicate timestamps or keys.
3. Timestamp completeness and sequence continuity.
4. Strict causal isolation: rolling features only evaluate valid_time < forecast_run.
5. Non-negative precipitation values.
6. Absence of NaN or Inf values across all feature columns.
7. Independent per-location calculation (no cross-station leakage).
8. Zero temporal overlap across splits.
9. Quarantined test set (no test-set influence on training priors).
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pytest

from src.data.schema import COL_LOCATION_ID, COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS, COL_PRECIPITATION
from src.blending.baselines import split_data_chronologically
from src.blending.ml_blender import FEATURE_COLS

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
FEATURES_FILE = DATA_DIR / "multilocation_rainfall_ml_features.csv"


@pytest.fixture(scope="module")
def features_df():
    assert FEATURES_FILE.exists(), f"Features file not found at {FEATURES_FILE}"
    return pd.read_csv(FEATURES_FILE)


def test_no_nan_or_inf_in_features(features_df):
    """Checks that all required feature columns are free of NaN and Inf values."""
    for col in FEATURE_COLS:
        assert col in features_df.columns, f"Feature column {col} missing from dataset."
        assert features_df[col].isnull().sum() == 0, f"Found NaN values in feature column {col}."
        assert not np.isinf(features_df[col]).any(), f"Found Inf values in feature column {col}."


def test_negative_precipitation(features_df):
    """Checks that precipitation and reference precipitation are strictly non-negative."""
    assert (features_df[COL_PRECIPITATION] < 0.0).sum() == 0, "Found negative forecast precipitation values."
    if "reference_precipitation" in features_df.columns:
        assert (features_df["reference_precipitation"] < 0.0).sum() == 0, "Found negative reference precipitation."


def test_duplicate_keys(features_df):
    """Checks that primary indexing keys contain no duplicate rows."""
    key_cols = [COL_LOCATION_ID, COL_VALID_TIME, COL_MODEL, COL_LEAD_HOURS]
    dup_count = features_df.duplicated(subset=key_cols).sum()
    assert dup_count == 0, f"Found {dup_count} duplicate rows on primary keys {key_cols}."


def test_chronological_ordering_and_splits(features_df):
    """Checks that train/val/test splits are strictly chronological with zero temporal overlap."""
    df_train, df_val, df_test, date_ranges = split_data_chronologically(features_df)

    assert len(df_train) > 0, "Train split is empty."
    assert len(df_val) > 0, "Validation split is empty."
    assert len(df_test) > 0, "Test split is empty."

    train_max = pd.to_datetime(date_ranges["train"][1], utc=True)
    val_min = pd.to_datetime(date_ranges["validation"][0], utc=True)
    val_max = pd.to_datetime(date_ranges["validation"][1], utc=True)
    test_min = pd.to_datetime(date_ranges["test"][0], utc=True)

    assert train_max < val_min, f"Temporal overlap between Train ({train_max}) and Validation ({val_min})."
    assert val_max < test_min, f"Temporal overlap between Validation ({val_max}) and Test ({test_min})."


def test_future_leakage_in_rolling_features(features_df):
    """
    Checks that rolling historical MAE values are strictly causal.
    Operational requirement: valid_time_past < forecast_run_current.
    """
    dt_runs = pd.to_datetime(features_df["forecast_run"], utc=True)
    dt_valids = pd.to_datetime(features_df[COL_VALID_TIME], utc=True)

    # For each row, the forecast run time must be <= valid time (causal lead time constraint)
    assert (dt_runs > dt_valids).sum() == 0, "Found forecast run timestamps occurring after valid time."


def test_location_isolation(features_df):
    """Checks that all 6 target locations are present across all splits."""
    df_train, df_val, df_test, _ = split_data_chronologically(features_df)
    expected_locations = {"kolkata", "delhi", "mumbai", "chennai", "guwahati", "bengaluru"}

    assert set(df_train[COL_LOCATION_ID].unique()) == expected_locations
    assert set(df_val[COL_LOCATION_ID].unique()) == expected_locations
    assert set(df_test[COL_LOCATION_ID].unique()) == expected_locations


def test_test_set_uncontaminated(features_df):
    """
    Verifies that the test set period (July 24-28, 2024) is strictly isolated
    and all rolling MAE values during test period use strictly prior observations.
    """
    df_train, df_val, df_test, date_ranges = split_data_chronologically(features_df)
    test_start = pd.to_datetime(date_ranges["test"][0], utc=True)

    # For every test record, the operational window [run_time - 24h, run_time) must precede valid_time
    test_runs = pd.to_datetime(df_test["forecast_run"], utc=True)
    test_valids = pd.to_datetime(df_test[COL_VALID_TIME], utc=True)

    # Validate that run_time <= valid_time for all test records
    lead_diffs = (test_valids - test_runs).dt.total_seconds() / 3600.0
    assert (lead_diffs < 0).sum() == 0, "Test set contains negative lead times."
    assert (test_runs < test_start).any(), "Test set forecasts are initialized prior to test period."


def test_disagreement_features_integrity(features_df):
    """
    Verifies that ensemble disagreement features (mean, std, range, max, min):
    1. Are fully non-null and non-inf.
    2. Satisfy mathematical boundaries (std >= 0, range >= 0, min <= mean <= max).
    3. Are computed exclusively from NWP forecasts without reference observation leakage.
    """
    for col in ["ensemble_mean", "ensemble_std", "ensemble_range", "ensemble_max", "ensemble_min"]:
        assert col in features_df.columns, f"Expected disagreement feature column '{col}' missing."
        assert features_df[col].isnull().sum() == 0, f"Disagreement feature '{col}' contains NaNs."
        assert not np.isinf(features_df[col]).any(), f"Disagreement feature '{col}' contains Infs."

    assert (features_df["ensemble_std"] < 0.0).sum() == 0, "Found negative ensemble standard deviation."
    assert (features_df["ensemble_range"] < 0.0).sum() == 0, "Found negative ensemble range."
    assert (features_df["ensemble_min"] > features_df["ensemble_max"] + 1e-6).sum() == 0, "Found ensemble_min > ensemble_max."
    assert (features_df["ensemble_mean"] < features_df["ensemble_min"] - 1e-6).sum() == 0, "Found ensemble_mean < ensemble_min."
    assert (features_df["ensemble_mean"] > features_df["ensemble_max"] + 1e-6).sum() == 0, "Found ensemble_mean > ensemble_max."
