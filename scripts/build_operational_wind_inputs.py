"""
Builds data/processed/multilocation_wind_forecast_inputs.csv for operational demonstration.
Follows the exact conventions of multilocation_temperature_forecast_inputs.csv:
- 6 cities: Kolkata, Delhi, Mumbai, Chennai, Bengaluru, Guwahati
- 72 forecast lead hours per city (432 rows)
- Target run: 2024-05-28T00:00:00Z (valid_time 2024-05-28T01:00:00Z to 2024-05-31T00:00:00Z)
- Features: ECMWF_IFS_wind, NOAA_GFS_wind, DWD_ICON_wind, reference_wind (all km/h)
- Weights: Historical-Error Weighted Blend using pre-forecast 24h errors (May 27, 2024)
"""

from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
SRC_WIND_FILE = DATA_DIR / "multilocation_wind_training_dataset_2023_06_to_2024_05.csv"
OUT_FILE = DATA_DIR / "multilocation_wind_forecast_inputs.csv"

def build_wind_forecast_inputs():
    print(f"Loading wind training dataset from {SRC_WIND_FILE}...")
    df = pd.read_csv(SRC_WIND_FILE)

    target_start = "2024-05-28T01:00:00Z"
    target_end = "2024-05-31T00:00:00Z"

    sub = df[(df["valid_time"] >= target_start) & (df["valid_time"] <= target_end)].copy()
    print(f"Filtered {len(sub)} rows for operational demonstration window [{target_start} to {target_end}].")

    # Pivot NWP models
    piv = sub.pivot(
        index=["location_id", "latitude", "longitude", "valid_time"],
        columns="model",
        values="wind_speed_10m_kmh"
    ).reset_index()

    ref_sub = sub[["location_id", "valid_time", "reference_wind_speed_10m_kmh"]].drop_duplicates()
    piv = piv.merge(ref_sub, on=["location_id", "valid_time"], how="left")

    piv.rename(columns={
        "ECMWF_IFS": "ECMWF_IFS_wind",
        "NOAA_GFS": "NOAA_GFS_wind",
        "DWD_ICON": "DWD_ICON_wind",
        "reference_wind_speed_10m_kmh": "reference_wind"
    }, inplace=True)

    # Sort deterministically
    piv["dt"] = pd.to_datetime(piv["valid_time"])
    piv.sort_values(["location_id", "dt"], inplace=True)
    piv.reset_index(drop=True, inplace=True)

    # Add temporal metadata
    piv["lead_hours"] = piv.groupby("location_id").cumcount() + 1
    piv["lead_day"] = ((piv["lead_hours"] - 1) // 24) + 1
    piv["hour"] = piv["dt"].dt.hour
    piv["month"] = piv["dt"].dt.month
    piv["day_of_year"] = piv["dt"].dt.dayofyear

    # Compute pre-forecast rolling 24h MAEs strictly prior to 2024-05-28 00:00:00Z
    prior_df = df[(df["valid_time"] >= "2024-05-27T00:00:00Z") & (df["valid_time"] < "2024-05-28T00:00:00Z")]
    eps = 1e-4
    fallback_priors = {"ECMWF_IFS": 2.29, "NOAA_GFS": 3.15, "DWD_ICON": 4.77}

    city_weights = {}
    print("\nComputing pre-forecast 24h causal weights per city:")
    for loc in piv["location_id"].unique():
        loc_prior = prior_df[prior_df["location_id"] == loc]
        loc_maes = {}
        for m in ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]:
            m_df = loc_prior[loc_prior["model"] == m]
            if len(m_df) >= 12:
                loc_maes[m] = float(np.mean(np.abs(m_df["wind_speed_10m_kmh"] - m_df["reference_wind_speed_10m_kmh"])))
            else:
                loc_maes[m] = fallback_priors[m]

        inv_errs = {m: 1.0 / (loc_maes[m] + eps) for m in loc_maes}
        sum_inv = sum(inv_errs.values())
        city_weights[loc] = {m: inv_errs[m] / sum_inv for m in inv_errs}
        print(f"  {loc:<10}: EC={city_weights[loc]['ECMWF_IFS']:.4f}, GFS={city_weights[loc]['NOAA_GFS']:.4f}, ICON={city_weights[loc]['DWD_ICON']:.4f}")

    piv["w_ECMWF_IFS"] = piv["location_id"].map(lambda loc: city_weights[loc]["ECMWF_IFS"])
    piv["w_NOAA_GFS"] = piv["location_id"].map(lambda loc: city_weights[loc]["NOAA_GFS"])
    piv["w_DWD_ICON"] = piv["location_id"].map(lambda loc: city_weights[loc]["DWD_ICON"])

    # Compute Historical-Weighted blend
    piv["blended_wind"] = (
        piv["w_ECMWF_IFS"] * piv["ECMWF_IFS_wind"] +
        piv["w_NOAA_GFS"] * piv["NOAA_GFS_wind"] +
        piv["w_DWD_ICON"] * piv["DWD_ICON_wind"]
    ).round(2)

    # Reorder columns to align with temperature forecast inputs
    cols = [
        "location_id", "valid_time", "latitude", "longitude", "lead_hours",
        "DWD_ICON_wind", "ECMWF_IFS_wind", "NOAA_GFS_wind", "reference_wind",
        "dt", "hour", "month", "day_of_year", "lead_day",
        "blended_wind", "w_ECMWF_IFS", "w_NOAA_GFS", "w_DWD_ICON"
    ]
    piv = piv[cols]

    print(f"\nSaving {len(piv)} rows to {OUT_FILE}...")
    piv.to_csv(OUT_FILE, index=False)
    print("Done. Verification:")
    print(f"  Shape: {piv.shape}")
    print(f"  Null counts: {piv.isnull().sum().sum()}")
    print(f"  Locations: {list(piv['location_id'].unique())}")
    print(f"  Lead hours: {piv['lead_hours'].min()} to {piv['lead_hours'].max()}")
    print(f"  Lead days: {list(piv['lead_day'].unique())}")

if __name__ == "__main__":
    build_wind_forecast_inputs()
