"""
Automated Data Integrity Tests for Wind Extension.
SkyBlend AI — SIH Problem Statement PS81.

Verifies:
1. Physical validity of ground station wind observations (non-negative, realistic speed range).
2. Completeness of Kolkata Alipore WMO 42807 wind speed series.
3. Mathematical equivalence of wind speed conversion: speed = sqrt(u^2 + v^2).
4. Unit conversion consistency (m/s to km/h).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
STATION_CSV = ROOT_DIR / "data" / "external" / "station_validation" / "kolkata_alipore_42807_hourly.csv"


@pytest.fixture(scope="module")
def station_df():
    assert STATION_CSV.exists(), f"Station CSV not found at {STATION_CSV}"
    df = pd.read_csv(STATION_CSV)
    df["valid_dt"] = pd.to_datetime(df["valid_time"], utc=True)
    return df


def test_station_wind_non_negative(station_df):
    """Wind speed observations must be strictly non-negative."""
    assert "wspd" in station_df.columns, "wspd column missing from station dataset."
    wspd = station_df["wspd"].dropna()
    assert (wspd < 0.0).sum() == 0, f"Found {(wspd < 0.0).sum()} negative wind speed values."


def test_station_wind_realistic_range(station_df):
    """Wind speed observations must fall within realistic tropospheric surface range (0 to 150 km/h)."""
    wspd = station_df["wspd"].dropna()
    assert wspd.min() >= 0.0, f"Minimum wind speed {wspd.min()} is below 0."
    assert wspd.max() <= 150.0, f"Maximum wind speed {wspd.max()} exceeds realistic limit."
    # Kolkata Cyclone Remal maximum is known to be ~57.2 km/h
    assert wspd.max() >= 40.0, f"Expected cyclonic wind peaks >= 40 km/h, got max {wspd.max()}."


def test_station_wind_completeness_pre_monsoon(station_df):
    """Wind speed records must have >= 99% completeness during pre-monsoon test period."""
    pm_mask = (station_df["valid_dt"] >= "2024-04-07T01:00:00Z") & (station_df["valid_dt"] <= "2024-05-31T23:00:00Z")
    df_pm = station_df[pm_mask]
    assert len(df_pm) == 1319, f"Expected 1,319 pre-monsoon hours, got {len(df_pm)}."
    completeness = df_pm["wspd"].notnull().sum() / len(df_pm)
    assert completeness >= 0.99, f"Pre-monsoon wind completeness is {completeness:.2%}, expected >= 99%."


def test_wind_vector_trigonometric_conversion():
    """Verifies that vector components u, v convert exactly to scalar speed s = sqrt(u^2 + v^2)."""
    speeds = np.array([5.0, 12.0, 25.0, 50.0])  # km/h
    directions = np.array([0.0, 90.0, 180.0, 270.0])  # degrees from North

    # Meteorological convention: direction from which wind blows
    rad = np.deg2rad(directions)
    u = -speeds * np.sin(rad)
    v = -speeds * np.cos(rad)

    reconstructed_speeds = np.sqrt(u**2 + v**2)
    np.testing.assert_allclose(reconstructed_speeds, speeds, rtol=1e-5)


def test_wind_speed_unit_conversion():
    """Verifies conversion between m/s and km/h: 1 m/s = 3.6 km/h."""
    speed_ms = 10.0
    speed_kmh = speed_ms * 3.6
    assert speed_kmh == 36.0
    assert speed_kmh / 3.6 == speed_ms


def test_multilocation_wind_dataset_structure_and_completeness():
    """Validates structure, row counts, and null-freedom of processed wind training dataset."""
    dataset_file = ROOT_DIR / "data" / "processed" / "multilocation_wind_training_dataset_2023_06_to_2024_05.csv"
    assert dataset_file.exists(), f"Processed wind dataset not found at {dataset_file}"
    df = pd.read_csv(dataset_file)

    # 6 locations * 3 models * 8,784 hours = 158,112 rows
    assert len(df) == 158112, f"Expected 158,112 rows, found {len(df)}"
    assert df["location_id"].nunique() == 6, f"Expected 6 locations, found {df['location_id'].nunique()}"
    assert df["model"].nunique() == 3, f"Expected 3 models, found {df['model'].nunique()}"
    assert df["valid_time"].nunique() == 8784, f"Expected 8,784 unique valid times, found {df['valid_time'].nunique()}"

    # Zero nulls
    assert df.isnull().sum().sum() == 0, f"Found nulls in dataset: {df.isnull().sum().to_dict()}"

    # Zero duplicates on primary composite key
    dups = df.duplicated(subset=["location_id", "valid_time", "model"]).sum()
    assert dups == 0, f"Found {dups} duplicate keys"

    # Physical validity
    assert (df["wind_speed_10m_kmh"] < 0.0).sum() == 0, "Negative forecast wind speeds detected"
    assert (df["reference_wind_speed_10m_kmh"] < 0.0).sum() == 0, "Negative reference wind speeds detected"
    assert df["wind_speed_10m_kmh"].max() <= 150.0, "Excessive forecast wind speed detected"


def test_multilocation_wind_reference_table():
    """Validates unique timestamp-level ERA5 reference table."""
    ref_file = ROOT_DIR / "data" / "processed" / "multilocation_wind_training_reference_2023_06_to_2024_05.csv"
    assert ref_file.exists(), f"Reference table not found at {ref_file}"
    df_ref = pd.read_csv(ref_file)

    # 6 locations * 8,784 hours = 52,704 rows
    assert len(df_ref) == 52704, f"Expected 52,704 rows, found {len(df_ref)}"
    assert df_ref["location_id"].nunique() == 6, f"Expected 6 locations, found {df_ref['location_id'].nunique()}"
    assert df_ref["valid_time"].nunique() == 8784, f"Expected 8,784 unique valid times, found {df_ref['valid_time'].nunique()}"
    assert df_ref.isnull().sum().sum() == 0, f"Found nulls in reference table: {df_ref.isnull().sum().to_dict()}"
    dups = df_ref.duplicated(subset=["location_id", "valid_time"]).sum()
    assert dups == 0, f"Found {dups} duplicate keys in reference table"


def test_kolkata_wind_station_alignment():
    """Validates Kolkata Alipore station wind alignment table."""
    kol_file = ROOT_DIR / "data" / "processed" / "kolkata_wind_station_alignment_2024.csv"
    assert kol_file.exists(), f"Kolkata station alignment not found at {kol_file}"
    df_kol = pd.read_csv(kol_file)

    assert len(df_kol) == 3648, f"Expected 3,648 matched station hours, found {len(df_kol)}"
    required_cols = ["valid_time", "ECMWF_IFS_wind_kmh", "NOAA_GFS_wind_kmh", "DWD_ICON_wind_kmh", "ERA5_wind_kmh", "station_wind_kmh"]
    for c in required_cols:
        assert c in df_kol.columns, f"Missing column {c} in station alignment table"
        assert df_kol[c].isnull().sum() == 0, f"Found nulls in column {c}"
