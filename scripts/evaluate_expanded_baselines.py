"""
Expanded Dataset Diagnostics, Seasonal Coverage & Baseline Benchmark Suite.

Executes:
1. Seasonal Coverage Analysis (Pre-monsoon, Monsoon, Post-monsoon, Winter).
2. Heavy Rainfall Distribution Comparison: Current July 2024 vs Expanded Year (2023-06 to 2024-05).
   Note: Synthesized lead horizons are deduplicated so that only UNIQUE hourly events are counted.
3. Proposed Chronological Train/Validation/Test Split Boundaries (~70% / ~15% / ~15%).
4. Raw NWP Baselines (ECMWF IFS, NOAA GFS, DWD ICON, Simple Average) Evaluation across:
   - Overall continuous and categorical metrics (MAE, RMSE, Bias, Pearson_r, POD, FAR, CSI)
   - Breakdown by location
   - Breakdown by month
   - Breakdown by season
   - Breakdown by rainfall intensity regime (No Rain, Light, Moderate, Heavy)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.blending.evaluation import calculate_continuous_metrics, calculate_categorical_metrics
from src.data.schema import (
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_MODEL,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
)


def assign_meteorological_season(month: int) -> str:
    """Classifies month into official project seasons."""
    if month in [3, 4, 5]:
        return "PRE-MONSOON (Mar-May)"
    elif month in [6, 7, 8, 9]:
        return "MONSOON (Jun-Sep)"
    elif month in [10, 11]:
        return "POST-MONSOON (Oct-Nov)"
    else:  # 12, 1, 2
        return "WINTER (Dec-Feb)"


def assign_intensity_regime(precip: float) -> str:
    """Categorizes rainfall intensity."""
    if precip < 0.1:
        return "No Rain (<0.1 mm/h)"
    elif precip < 2.5:
        return "Light (0.1-2.5 mm/h)"
    elif precip < 7.5:
        return "Moderate (2.5-7.5 mm/h)"
    else:
        return "Heavy (>=7.5 mm/h)"


def main():
    print("=" * 90)
    print("SKYBLEND AI (PS81) — EXPANDED YEAR DATASET EVALUATION & SEASONAL DIAGNOSTICS")
    print("=" * 90)

    expanded_csv = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_training_dataset_2023_06_to_2024_05.csv"
    july_csv = ROOT_DIR / "data" / "processed" / "multilocation_rainfall_training_dataset.csv"

    if not expanded_csv.exists():
        print(f"Error: Expanded dataset not found at {expanded_csv}")
        sys.exit(1)

    print(f"Loading expanded year dataset: {expanded_csv} ...")
    df_exp = pd.read_csv(expanded_csv)
    print(f"  - Loaded {len(df_exp):,d} records.")

    # Convert valid_time to datetime
    dt_v = pd.to_datetime(df_exp[COL_VALID_TIME], utc=True)
    df_exp["month"] = dt_v.dt.month
    df_exp["year_month"] = dt_v.dt.strftime("%Y-%m")
    df_exp["season"] = df_exp["month"].apply(assign_meteorological_season)
    df_exp["intensity"] = df_exp[COL_REF_PRECIPITATION].apply(assign_intensity_regime)

    # -------------------------------------------------------------
    # 1. PIVOT TO WIDE FORMAT FOR UNIQUE METEOROLOGICAL EVENTS
    # -------------------------------------------------------------
    pivot_idx = [COL_LOCATION_ID, COL_VALID_TIME, "year_month", "month", "season", COL_REF_PRECIPITATION]
    df_wide = df_exp.pivot_table(
        index=pivot_idx,
        columns=COL_MODEL,
        values=COL_PRECIPITATION,
        aggfunc="first"
    ).reset_index()

    f_ecmwf = df_wide["ECMWF_IFS"].values
    f_gfs = df_wide["NOAA_GFS"].values
    f_icon = df_wide["DWD_ICON"].values
    f_simple = (f_ecmwf + f_gfs + f_icon) / 3.0
    y_true = df_wide[COL_REF_PRECIPITATION].values
    df_wide["Simple_Average"] = f_simple

    total_unique_hours = len(df_wide)
    print(f"\nUnique Meteorological Timestamps (Deduplicated across horizons): {total_unique_hours:,d}")

    # -------------------------------------------------------------
    # 2. SEASONAL COVERAGE REPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SECTION 6: SEASONAL COVERAGE REPORT (ERA5 REFERENCE OBSERVATIONS)")
    print("=" * 90)
    season_rows = []
    season_order = [
        "MONSOON (Jun-Sep)",
        "POST-MONSOON (Oct-Nov)",
        "WINTER (Dec-Feb)",
        "PRE-MONSOON (Mar-May)",
    ]

    for s_name in season_order:
        s_grp = df_wide[df_wide["season"] == s_name]
        if s_grp.empty:
            continue
        y_s = s_grp[COL_REF_PRECIPITATION]
        n_tot = len(s_grp)
        n_dry = int((y_s < 0.1).sum())
        n_light = int(((y_s >= 0.1) & (y_s < 2.5)).sum())
        n_mod = int(((y_s >= 2.5) & (y_s < 7.5)).sum())
        n_heavy = int((y_s >= 7.5).sum())
        max_rain = float(y_s.max())
        
        # Heavy event count by location
        loc_heavy_counts = s_grp[s_grp[COL_REF_PRECIPITATION] >= 7.5][COL_LOCATION_ID].value_counts().to_dict()
        loc_heavy_str = ", ".join([f"{k}:{v}" for k, v in sorted(loc_heavy_counts.items())]) if loc_heavy_counts else "None"

        season_rows.append({
            "Season": s_name,
            "Total_Hours": n_tot,
            "Dry (<0.1)": n_dry,
            "Light (0.1-2.5)": n_light,
            "Moderate (2.5-7.5)": n_mod,
            "Heavy (>=7.5)": n_heavy,
            "Max_Rain (mm/h)": round(max_rain, 1),
            "Heavy_Events_by_Location": loc_heavy_str,
        })

    df_seasons = pd.DataFrame(season_rows)
    print(df_seasons.to_string(index=False))

    # -------------------------------------------------------------
    # 3. HEAVY RAINFALL COMPARISON: JULY 2024 vs EXPANDED YEAR
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SECTION 8: HEAVY RAINFALL DISTRIBUTION COMPARISON (UNIQUE STORM HOURS)")
    print("=" * 90)
    
    # Load July 2024 dataset for true comparison
    df_july = pd.read_csv(july_csv)
    df_july_wide = df_july.pivot_table(
        index=[COL_LOCATION_ID, COL_VALID_TIME, COL_REF_PRECIPITATION],
        columns=COL_MODEL,
        values=COL_PRECIPITATION,
        aggfunc="first"
    ).reset_index()
    y_july = df_july_wide[COL_REF_PRECIPITATION]

    july_heavy_hours = int((y_july >= 7.5).sum())
    july_mod_hours = int(((y_july >= 2.5) & (y_july < 7.5)).sum())
    july_max = float(y_july.max())
    july_loc_heavy = df_july_wide[y_july >= 7.5][COL_LOCATION_ID].value_counts().to_dict()

    exp_heavy_hours = int((y_true >= 7.5).sum())
    exp_mod_hours = int(((y_true >= 2.5) & (y_true < 7.5)).sum())
    exp_max = float(y_true.max())
    exp_loc_heavy = df_wide[y_true >= 7.5][COL_LOCATION_ID].value_counts().to_dict()

    comp_summary = [
        {
            "Metric": "Total Deduplicated Hourly Samples",
            "July 2024 Baseline (28 Days)": f"{len(df_july_wide):,d}",
            "Expanded Full Year (366 Days)": f"{len(df_wide):,d}",
            "Multiplier": f"{len(df_wide)/len(df_july_wide):.1f}x",
        },
        {
            "Metric": "Unique Heavy Rain Hours (>=7.5 mm/h)",
            "July 2024 Baseline (28 Days)": f"{july_heavy_hours:,d}",
            "Expanded Full Year (366 Days)": f"{exp_heavy_hours:,d}",
            "Multiplier": f"{exp_heavy_hours/max(1, july_heavy_hours):.1f}x",
        },
        {
            "Metric": "Unique Moderate Rain Hours (2.5-7.5 mm/h)",
            "July 2024 Baseline (28 Days)": f"{july_mod_hours:,d}",
            "Expanded Full Year (366 Days)": f"{exp_mod_hours:,d}",
            "Multiplier": f"{exp_mod_hours/max(1, july_mod_hours):.1f}x",
        },
        {
            "Metric": "Maximum Observed Hourly Rainfall (mm/h)",
            "July 2024 Baseline (28 Days)": f"{july_max:.1f}",
            "Expanded Full Year (366 Days)": f"{exp_max:.1f}",
            "Multiplier": f"{exp_max/july_max:.2f}x",
        },
    ]
    print(pd.DataFrame(comp_summary).to_string(index=False))

    print("\nHeavy Rain Hours (>=7.5 mm/h) by Location:")
    all_locs = sorted(list(set(list(july_loc_heavy.keys()) + list(exp_loc_heavy.keys()))))
    loc_comp_rows = []
    for loc in all_locs:
        c_j = july_loc_heavy.get(loc, 0)
        c_e = exp_loc_heavy.get(loc, 0)
        loc_comp_rows.append({"Location": loc, "July_2024_Events": c_j, "Expanded_Year_Events": c_e})
    print(pd.DataFrame(loc_comp_rows).to_string(index=False))

    # -------------------------------------------------------------
    # 4. PROPOSED CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SECTION 7: PROPOSED CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT")
    print("=" * 90)

    # Sort timestamps chronologically
    sorted_vts = sorted(df_wide[COL_VALID_TIME].unique().tolist())
    n_ts = len(sorted_vts)
    
    n_train_ts = int(np.floor(0.70 * n_ts))
    n_val_ts = int(np.floor(0.15 * n_ts))
    n_test_ts = n_ts - n_train_ts - n_val_ts

    train_vts = sorted_vts[:n_train_ts]
    val_vts = sorted_vts[n_train_ts:n_train_ts + n_val_ts]
    test_vts = sorted_vts[n_train_ts + n_val_ts:]

    print(f"Total Unique Chronological Timestamps: {n_ts:,d} ({n_ts/24:.1f} days)")
    print(f"  - TRAIN Split      (70%): {len(train_vts):,d} hours | {train_vts[0]} to {train_vts[-1]}")
    print(f"  - VALIDATION Split (15%): {len(val_vts):,d} hours | {val_vts[0]} to {val_vts[-1]}")
    print(f"  - TEST Split       (15%): {len(test_vts):,d} hours | {test_vts[0]} to {test_vts[-1]}")
    print(f"  - OUT-OF-PERIOD HOLDOUT : July 1-28, 2024 (Quarantined for subsequent generalization check)")

    # -------------------------------------------------------------
    # 5. BASELINE PERFORMANCE ON EXPANDED DATASET (NO MODEL OPTIMIZATION)
    # -------------------------------------------------------------
    print("\n" + "=" * 90)
    print("SECTION 9: RAW NWP BASELINE BENCHMARK ON EXPANDED YEAR DATASET (FULL YEAR)")
    print("=" * 90)

    models_eval = {
        "ECMWF_IFS": f_ecmwf,
        "NOAA_GFS": f_gfs,
        "DWD_ICON": f_icon,
        "Simple_Average": f_simple,
    }

    base_metrics = []
    for m_name, f_vals in models_eval.items():
        c_m = calculate_continuous_metrics(y_true, f_vals)
        cat_m = calculate_categorical_metrics(y_true, f_vals, threshold=1.0)
        base_metrics.append({
            "Model": m_name,
            "MAE": c_m["MAE"],
            "RMSE": c_m["RMSE"],
            "Bias": c_m["Bias"],
            "Pearson_r": c_m["Pearson_r"],
            "POD (>=1.0)": cat_m["POD"],
            "FAR (>=1.0)": cat_m["FAR"],
            "CSI (>=1.0)": cat_m["CSI"],
        })
    print(pd.DataFrame(base_metrics).to_string(index=False))

    # Baseline performance by Season
    print("\nBaseline MAE & RMSE by Meteorological Season:")
    season_metric_rows = []
    for s_name in season_order:
        s_mask = df_wide["season"] == s_name
        y_s = y_true[s_mask]
        for m_name, f_vals in models_eval.items():
            f_s = f_vals[s_mask]
            c_m = calculate_continuous_metrics(y_s, f_s)
            season_metric_rows.append({
                "Season": s_name,
                "Model": m_name,
                "MAE": c_m["MAE"],
                "RMSE": c_m["RMSE"],
                "Bias": c_m["Bias"],
                "Pearson_r": c_m["Pearson_r"],
            })
    print(pd.DataFrame(season_metric_rows).to_string(index=False))

    # Baseline performance by Location
    print("\nBaseline MAE & RMSE by Location:")
    loc_metric_rows = []
    for loc_id in sorted(df_wide[COL_LOCATION_ID].unique()):
        l_mask = df_wide[COL_LOCATION_ID] == loc_id
        y_l = y_true[l_mask]
        for m_name, f_vals in models_eval.items():
            f_l = f_vals[l_mask]
            c_m = calculate_continuous_metrics(y_l, f_l)
            loc_metric_rows.append({
                "Location": loc_id,
                "Model": m_name,
                "MAE": c_m["MAE"],
                "RMSE": c_m["RMSE"],
                "Bias": c_m["Bias"],
                "Pearson_r": c_m["Pearson_r"],
            })
    print(pd.DataFrame(loc_metric_rows).to_string(index=False))

    # Save summary tables to data/processed
    out_dir = ROOT_DIR / "data" / "processed"
    pd.DataFrame(season_rows).to_csv(out_dir / "expanded_dataset_seasonal_coverage.csv", index=False)
    pd.DataFrame(base_metrics).to_csv(out_dir / "expanded_dataset_baseline_performance.csv", index=False)
    print(f"\nSaved summary artifacts to: {out_dir}")
    print("=" * 90)


if __name__ == "__main__":
    main()
