"""
SkyBlend AI — Build Multi-Location Wind Telemetry Dataset (Wind Phase 1).
SIH Problem Statement PS81: Multi-Variable Blending (Wind).

Fetches genuine 10m scalar wind speed (km/h) for:
- 6 Demonstration Locations: Kolkata, Delhi, Mumbai, Chennai, Bengaluru, Guwahati
- 3 NWP Models: ECMWF IFS (ecmwf_ifs04), NOAA GFS (gfs_seamless), DWD ICON (icon_seamless)
- Reference: ERA5 Reanalysis (0.25° grid)
- Full-Year Study Period: 2023-06-01T00:00:00Z to 2024-05-31T23:00:00Z (8,784 hours)
- July Holdout: 2024-07-01 to 2024-07-28

Outputs:
1. data/processed/multilocation_wind_training_dataset_2023_06_to_2024_05.csv (158,112 rows)
2. data/processed/multilocation_wind_training_reference_2023_06_to_2024_05.csv (52,704 rows)
3. data/processed/multilocation_wind_training_dataset_july2024.csv (12,096 rows)
4. data/processed/kolkata_wind_station_alignment_2024.csv (matched station evaluation)
"""

import sys
import time
import urllib.request
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.data.sources import DEMO_LOCATIONS
from src.blending.evaluation import calculate_continuous_metrics

MODELS = ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]
MODEL_CODES = {
    "ECMWF_IFS": "ecmwf_ifs04",
    "NOAA_GFS": "gfs_seamless",
    "DWD_ICON": "icon_seamless",
}

STATION_FILE = ROOT_DIR / "data" / "external" / "station_validation" / "kolkata_alipore_42807_hourly.csv"
OUT_DIR = ROOT_DIR / "data" / "processed"


def fetch_nwp_wind(loc_cfg, start_date: str, end_date: str) -> dict:
    """Fetches wind_speed_10m for ECMWF, GFS, ICON in km/h from Open-Meteo."""
    models_str = ",".join([MODEL_CODES[m] for m in MODELS])
    url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast?"
        f"latitude={loc_cfg.latitude}&longitude={loc_cfg.longitude}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=wind_speed_10m&models={models_str}&timezone=UTC"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "SkyBlend-Wind-Pipeline/1.0"})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("hourly", {})
        except Exception as e:
            if attempt < 3:
                time.sleep(2 * attempt)
            else:
                raise RuntimeError(f"Failed to fetch NWP wind for {loc_cfg.name}: {e}") from e


def fetch_era5_wind(loc_cfg, start_date: str, end_date: str) -> dict:
    """Fetches ERA5 wind_speed_10m in km/h from Open-Meteo Archive API."""
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={loc_cfg.latitude}&longitude={loc_cfg.longitude}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=wind_speed_10m&timezone=UTC"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "SkyBlend-Wind-Pipeline/1.0"})
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("hourly", {})
        except Exception as e:
            if attempt < 3:
                time.sleep(2 * attempt)
            else:
                raise RuntimeError(f"Failed to fetch ERA5 wind for {loc_cfg.name}: {e}") from e


def build_wind_dataset_for_period(start_date: str, end_date: str, period_name: str):
    print("=" * 80)
    print(f"BUILDING WIND DATASET: {period_name} ({start_date} to {end_date})")
    print("=" * 80)

    dataset_rows = []
    reference_rows = []

    for loc_id, loc_cfg in DEMO_LOCATIONS.items():
        print(f"Fetching {loc_cfg.name} (Lat={loc_cfg.latitude}, Lon={loc_cfg.longitude})...", end=" ", flush=True)
        t0 = time.time()

        # 1. Fetch NWP
        nwp_hourly = fetch_nwp_wind(loc_cfg, start_date, end_date)
        time.sleep(0.5)

        # 2. Fetch ERA5
        era5_hourly = fetch_era5_wind(loc_cfg, start_date, end_date)
        time.sleep(0.5)

        timestamps = nwp_hourly.get("time", [])
        era5_speeds = era5_hourly.get("wind_speed_10m", [])
        era5_map = {ts: val for ts, val in zip(era5_hourly.get("time", []), era5_speeds)}

        for ts_str in timestamps:
            dt_utc = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
            iso_utc = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            ref_val = era5_map.get(ts_str)

            # Store unique timestamp-level reference
            reference_rows.append({
                "location_id": loc_id,
                "location_name": loc_cfg.name,
                "latitude": loc_cfg.latitude,
                "longitude": loc_cfg.longitude,
                "valid_time": iso_utc,
                "reference_wind_speed_10m_kmh": round(float(ref_val), 2) if ref_val is not None else None,
            })

            # Store multi-model rows
            for m in MODELS:
                m_code = MODEL_CODES[m]
                val = nwp_hourly.get(f"wind_speed_10m_{m_code}", [])[timestamps.index(ts_str)]
                dataset_rows.append({
                    "location_id": loc_id,
                    "location_name": loc_cfg.name,
                    "latitude": loc_cfg.latitude,
                    "longitude": loc_cfg.longitude,
                    "valid_time": iso_utc,
                    "model": m,
                    "wind_speed_10m_kmh": round(float(val), 2) if val is not None else None,
                    "reference_wind_speed_10m_kmh": round(float(ref_val), 2) if ref_val is not None else None,
                })

        print(f"Done ({len(timestamps)} hours in {time.time() - t0:.1f}s)")

    df_dataset = pd.DataFrame(dataset_rows)
    df_reference = pd.DataFrame(reference_rows)

    return df_dataset, df_reference


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Full Year (2023-06-01 to 2024-05-31)
    df_dataset, df_reference = build_wind_dataset_for_period("2023-06-01", "2024-05-31", "Full Year 2023-06 to 2024-05")

    out_dataset_file = OUT_DIR / "multilocation_wind_training_dataset_2023_06_to_2024_05.csv"
    out_ref_file = OUT_DIR / "multilocation_wind_training_reference_2023_06_to_2024_05.csv"

    df_dataset.to_csv(out_dataset_file, index=False)
    df_reference.to_csv(out_ref_file, index=False)
    print(f"\nSaved primary wind dataset: {out_dataset_file} ({len(df_dataset):,d} rows)")
    print(f"Saved primary reference table: {out_ref_file} ({len(df_reference):,d} rows)")

    # 2. July Holdout (2024-07-01 to 2024-07-28)
    df_july_dataset, _ = build_wind_dataset_for_period("2024-07-01", "2024-07-28", "July 2024 Holdout")
    out_july_file = OUT_DIR / "multilocation_wind_training_dataset_july2024.csv"
    df_july_dataset.to_csv(out_july_file, index=False)
    print(f"Saved July holdout dataset: {out_july_file} ({len(df_july_dataset):,d} rows)")

    # 3. Data Integrity & Completeness Validation
    print("\n" + "=" * 80)
    print("DATA INTEGRITY AUDIT (FULL-YEAR DATASET)")
    print("=" * 80)
    print(f"Expected Rows: 6 locations * 3 models * 8,784 hours = 158,112")
    print(f"Actual Rows  : {len(df_dataset):,d}")
    assert len(df_dataset) == 158112, f"Row count mismatch: {len(df_dataset)}"

    print(f"\nExpected Reference Rows: 6 locations * 8,784 hours = 52,704")
    print(f"Actual Reference Rows  : {len(df_reference):,d}")
    assert len(df_reference) == 52704, f"Reference row count mismatch: {len(df_reference)}"

    # Check nulls
    print("\nNull Counts:")
    for col in df_dataset.columns:
        null_c = df_dataset[col].isnull().sum()
        print(f"  - {col:32s}: {null_c}")
        assert null_c == 0, f"Found {null_c} nulls in {col}"

    # Check duplicates
    dups = df_dataset.duplicated(subset=["location_id", "valid_time", "model"]).sum()
    print(f"\nDuplicate Keys (location_id, valid_time, model): {dups}")
    assert dups == 0, f"Found {dups} duplicates"

    # Check range
    min_spd = df_dataset["wind_speed_10m_kmh"].min()
    max_spd = df_dataset["wind_speed_10m_kmh"].max()
    print(f"Wind speed range: {min_spd:.2f} .. {max_spd:.2f} km/h")
    assert min_spd >= 0.0, "Negative wind speed detected"
    assert max_spd <= 150.0, "Impossible hurricane wind speed detected"

    # 4. Chronological Splits & Baseline Model Skill
    print("\n" + "=" * 80)
    print("BASELINE NWP MODEL EVALUATION AGAINST ERA5 REFERENCE")
    print("=" * 80)

    df_dataset["valid_dt"] = pd.to_datetime(df_dataset["valid_time"], utc=True)
    splits = {
        "Full Year (2023-06 to 2024-05)": df_dataset,
        "Train (2023-06-01 to 2024-02-12 03:00)": df_dataset[(df_dataset["valid_dt"] >= "2023-06-01T00:00:00Z") & (df_dataset["valid_dt"] <= "2024-02-12T03:00:00Z")],
        "Validation (2024-02-12 04:00 to 2024-04-07 00:00)": df_dataset[(df_dataset["valid_dt"] >= "2024-02-12T04:00:00Z") & (df_dataset["valid_dt"] <= "2024-04-07T00:00:00Z")],
        "Pre-Monsoon Test (2024-04-07 01:00 to 2024-05-31 23:00)": df_dataset[(df_dataset["valid_dt"] >= "2024-04-07T01:00:00Z") & (df_dataset["valid_dt"] <= "2024-05-31T23:00:00Z")],
    }

    # Add July holdout window (2024-07-24 18:00 to 2024-07-28 23:00)
    df_july_dataset["valid_dt"] = pd.to_datetime(df_july_dataset["valid_time"], utc=True)
    july_window = df_july_dataset[(df_july_dataset["valid_dt"] >= "2024-07-24T18:00:00Z") & (df_july_dataset["valid_dt"] <= "2024-07-28T23:00:00Z")]
    splits["July External Holdout (2024-07-24 18:00 to 2024-07-28 23:00)"] = july_window

    baseline_stats = []
    for split_name, split_df in splits.items():
        print(f"\n--- Split: {split_name} ({len(split_df):,d} rows) ---")
        for m in MODELS:
            sub = split_df[split_df["model"] == m]
            y_pred = sub["wind_speed_10m_kmh"].values
            y_true = sub["reference_wind_speed_10m_kmh"].values
            m_metrics = calculate_continuous_metrics(y_true, y_pred)
            baseline_stats.append({
                "Split": split_name,
                "Model": m,
                "Rows": len(sub),
                "MAE": m_metrics["MAE"],
                "RMSE": m_metrics["RMSE"],
                "Bias": m_metrics["Bias"],
                "Pearson_r": m_metrics["Pearson_r"],
            })
            print(f"  {m:12s}: MAE={m_metrics['MAE']:.3f} km/h | RMSE={m_metrics['RMSE']:.3f} | Bias={m_metrics['Bias']:+.3f} | r={m_metrics['Pearson_r']:.3f}")

    # 5. Wind Regime Analytical Breakdown (Full Year)
    print("\n" + "=" * 80)
    print("ANALYTICAL WIND REGIME DISTRIBUTION (Full Year, ERA5 Reference)")
    print("=" * 80)
    ref_speeds = df_reference["reference_wind_speed_10m_kmh"].values
    regimes = [
        ("Calm / Light Breeze (< 12 km/h, Beaufort 0-2)", ref_speeds < 12.0),
        ("Moderate Breeze (12 - 28 km/h, Beaufort 3-4)", (ref_speeds >= 12.0) & (ref_speeds < 29.0)),
        ("Strong Wind (29 - 49 km/h, Beaufort 5-6)", (ref_speeds >= 29.0) & (ref_speeds < 50.0)),
        ("High Wind / Near Gale+ (>= 50 km/h, Beaufort 7+)", ref_speeds >= 50.0),
    ]
    for r_name, r_mask in regimes:
        cnt = r_mask.sum()
        pct = cnt / len(ref_speeds) * 100.0
        print(f"  {r_name:55s}: {cnt:5d} hours ({pct:5.2f}%)")

    # 6. Kolkata Ground Station Alignment (WMO 42807)
    print("\n" + "=" * 80)
    print("KOLKATA INDEPENDENT STATION ALIGNMENT (WMO 42807)")
    print("=" * 80)
    kol_forecasts = df_dataset[df_dataset["location_id"] == "kolkata"].pivot(
        index="valid_time", columns="model", values="wind_speed_10m_kmh"
    ).reset_index()
    kol_forecasts.rename(columns={
        "ECMWF_IFS": "ECMWF_IFS_wind_kmh",
        "NOAA_GFS": "NOAA_GFS_wind_kmh",
        "DWD_ICON": "DWD_ICON_wind_kmh",
    }, inplace=True)

    kol_ref = df_reference[df_reference["location_id"] == "kolkata"][["valid_time", "reference_wind_speed_10m_kmh"]]
    kol_ref.rename(columns={"reference_wind_speed_10m_kmh": "ERA5_wind_kmh"}, inplace=True)

    df_stn = pd.read_csv(STATION_FILE)
    stn_wind = df_stn[["valid_time", "wspd"]].rename(columns={"wspd": "station_wind_kmh"}).dropna(subset=["station_wind_kmh"])

    kol_aligned = pd.merge(kol_forecasts, kol_ref, on="valid_time", how="inner")
    kol_aligned = pd.merge(kol_aligned, stn_wind, on="valid_time", how="inner")

    out_kolkata_file = OUT_DIR / "kolkata_wind_station_alignment_2024.csv"
    kol_aligned.to_csv(out_kolkata_file, index=False)
    print(f"Matched Kolkata station hours: {len(kol_aligned):,d} rows")
    print(f"Saved station alignment CSV: {out_kolkata_file}")

    # Station skill
    print("\nKolkata Station Evaluation (Out-of-Sample Ground Truth):")
    y_stn = kol_aligned["station_wind_kmh"].values
    for m in ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]:
        y_fc = kol_aligned[f"{m}_wind_kmh"].values
        met = calculate_continuous_metrics(y_stn, y_fc)
        print(f"  {m:12s} vs Station: MAE={met['MAE']:.3f} km/h | RMSE={met['RMSE']:.3f} | Bias={met['Bias']:+.3f} | r={met['Pearson_r']:.3f}")
    met_era = calculate_continuous_metrics(y_stn, kol_aligned["ERA5_wind_kmh"].values)
    print(f"  {'ERA5':12s} vs Station: MAE={met_era['MAE']:.3f} km/h | RMSE={met_era['RMSE']:.3f} | Bias={met_era['Bias']:+.3f} | r={met_era['Pearson_r']:.3f}")

    # 7. Cyclone Remal Diagnostic (2024-05-26 to 2024-05-27)
    print("\n" + "=" * 80)
    print("CYCLONE REMAL HIGH-WIND DIAGNOSTIC (2024-05-26 to 2024-05-27)")
    print("=" * 80)
    remal_df = kol_aligned[(kol_aligned["valid_time"] >= "2024-05-26T00:00:00Z") & (kol_aligned["valid_time"] <= "2024-05-27T23:00:00Z")]

    stn_max = remal_df["station_wind_kmh"].max()
    stn_time = remal_df.loc[remal_df["station_wind_kmh"].idxmax(), "valid_time"]
    ec_max = remal_df["ECMWF_IFS_wind_kmh"].max()
    ec_time = remal_df.loc[remal_df["ECMWF_IFS_wind_kmh"].idxmax(), "valid_time"]
    gf_max = remal_df["NOAA_GFS_wind_kmh"].max()
    gf_time = remal_df.loc[remal_df["NOAA_GFS_wind_kmh"].idxmax(), "valid_time"]
    ic_max = remal_df["DWD_ICON_wind_kmh"].max()
    ic_time = remal_df.loc[remal_df["DWD_ICON_wind_kmh"].idxmax(), "valid_time"]
    era_max = remal_df["ERA5_wind_kmh"].max()
    era_time = remal_df.loc[remal_df["ERA5_wind_kmh"].idxmax(), "valid_time"]

    print(f"  Station Max Wind : {stn_max:5.1f} km/h (at {stn_time})")
    print(f"  ECMWF Max Wind   : {ec_max:5.1f} km/h (at {ec_time})")
    print(f"  NOAA GFS Max Wind: {gf_max:5.1f} km/h (at {gf_time})")
    print(f"  DWD ICON Max Wind: {ic_max:5.1f} km/h (at {ic_time})")
    print(f"  ERA5 Max Wind    : {era_max:5.1f} km/h (at {era_time})")


if __name__ == "__main__":
    main()
