"""
Evaluate Adaptive Blender & Baselines Script (Multi-Location & Single-Location Support).

Evaluates individual models, simple ensemble, historical error weighting, and adaptive ML weighting
on the untouched chronological TEST dataset across multiple locations.

Outputs:
- data/processed/multilocation_adaptive_weights_test.csv (and adaptive_weights_test.csv)
- data/processed/model_weight_map_summary.csv
- data/processed/model_performance_test.csv
- reports/ (PNG visualization plots)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root directory to python import path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.blending.baselines import (
    split_data_chronologically,
    pivot_aligned_dataset,
    compute_simple_ensemble,
    compute_historical_weighted_ensemble,
)
from src.blending.ml_blender import AdaptiveMLBlender
from src.blending.evaluation import (
    calculate_continuous_metrics,
    calculate_categorical_metrics,
)
from src.data.schema import COL_LOCATION_ID


def generate_reports_and_plots(
    df_test_wide: pd.DataFrame,
    ml_weights_df: pd.DataFrame,
    results_df: pd.DataFrame,
    lead_results_df: pd.DataFrame,
    loc_results_df: pd.DataFrame,
    reports_dir: Path,
):
    """Generates PNG evaluation plots in reports/ directory."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Plot 1: Forecast Comparison Time Series for Sample Location (reports/forecast_comparison.png)
    plt.figure(figsize=(14, 6))
    sample_loc = df_test_wide["location_id"].iloc[0]
    sample_df = df_test_wide[df_test_wide["location_id"] == sample_loc].iloc[:72]
    
    plt.plot(sample_df["valid_time"], sample_df["reference_precipitation"], label="ERA5 Reference", color="black", linewidth=2.5, linestyle="--")
    plt.plot(sample_df["valid_time"], sample_df["ECMWF_IFS_precip"], label="ECMWF IFS", alpha=0.7)
    plt.plot(sample_df["valid_time"], sample_df["NOAA_GFS_precip"], label="NOAA GFS", alpha=0.7)
    plt.plot(sample_df["valid_time"], sample_df["DWD_ICON_precip"], label="DWD ICON", alpha=0.7)
    plt.plot(sample_df["valid_time"], sample_df["adaptive_ml_blend"], label="Adaptive ML Blend", color="crimson", linewidth=2.0)

    plt.title(f"Rainfall Forecast Comparison vs ERA5 Reference ({sample_loc.capitalize()} - Test Sample)", fontsize=14, fontweight="bold")
    plt.xlabel("Valid Time (UTC)", fontsize=12)
    plt.ylabel("Precipitation (mm/h)", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    plt.savefig(reports_dir / "forecast_comparison.png", dpi=300)
    plt.close()

    # 2. Plot 2: Model Weights Evolution / Stacked Area (reports/model_weights.png)
    plt.figure(figsize=(12, 5))
    sample_weights = ml_weights_df.iloc[:200]
    times = range(len(sample_weights))
    plt.stackplot(
        times,
        sample_weights["w_ECMWF_IFS"],
        sample_weights["w_NOAA_GFS"],
        sample_weights["w_DWD_ICON"],
        labels=["ECMWF IFS Weight", "NOAA GFS Weight", "DWD ICON Weight"],
        colors=["#1f77b4", "#ff7f0e", "#2ca02c"],
        alpha=0.8,
    )
    plt.title("Adaptive ML Weight Allocation Over Test Predictions", fontsize=14, fontweight="bold")
    plt.xlabel("Test Prediction Sequence Index", fontsize=12)
    plt.ylabel("Normalized Weight (Sum = 1.0)", fontsize=12)
    plt.ylim(0, 1.0)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    plt.savefig(reports_dir / "model_weights.png", dpi=300)
    plt.close()

    # 3. Plot 3: Error by Lead Time (reports/error_by_lead_time.png)
    plt.figure(figsize=(10, 6))
    chart_df = lead_results_df.melt(id_vars=["Lead_Horizon", "Approach"], value_vars=["MAE", "RMSE"], var_name="Metric", value_name="Value")
    sns.barplot(data=chart_df, x="Lead_Horizon", y="Value", hue="Approach", palette="viridis")
    plt.title("Forecast MAE & RMSE by Lead-Time Horizon (Test Period)", fontsize=14, fontweight="bold")
    plt.xlabel("Lead-Time Horizon", fontsize=12)
    plt.ylabel("Error (mm/h)", fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", frameon=True)
    plt.tight_layout()
    plt.savefig(reports_dir / "error_by_lead_time.png", dpi=300)
    plt.close()


def main():
    print("=" * 80)
    print("PS81 AI-NWP Forecast Blending System - Multi-Location Test Evaluation Pipeline")
    print("=" * 80)

    output_dir = ROOT_DIR / "data" / "processed"
    model_dir = ROOT_DIR / "models"
    
    multi_file = output_dir / "multilocation_rainfall_ml_features.csv"
    single_file = output_dir / "rainfall_ml_features.csv"

    if multi_file.exists():
        input_file = multi_file
    elif single_file.exists():
        input_file = single_file
    else:
        print("Error: Input ML features dataset not found in data/processed/")
        sys.exit(1)

    df_features = pd.read_csv(input_file)

    # 1. Chronological Data Splitting
    df_train, df_val, df_test, date_ranges = split_data_chronologically(df_features)

    print("Data Chronological Split Ranges:")
    print(f"  - TRAIN      : {date_ranges['train'][0]} to {date_ranges['train'][1]}")
    print(f"  - VALIDATION : {date_ranges['validation'][0]} to {date_ranges['validation'][1]}")
    print(f"  - TEST       : {date_ranges['test'][0]} to {date_ranges['test'][1]}")

    # Pivot TEST set into wide format
    df_test_wide = pivot_aligned_dataset(df_test)
    y_true = df_test_wide["reference_precipitation"].values

    # 2. Evaluate Baseline Approaches on TEST set
    f_ecmwf = df_test_wide["ECMWF_IFS_precip"].values
    f_gfs = df_test_wide["NOAA_GFS_precip"].values
    f_icon = df_test_wide["DWD_ICON_precip"].values
    f_simple = compute_simple_ensemble(df_test_wide)
    f_hist, hist_weights = compute_historical_weighted_ensemble(df_test_wide)

    # 3. Predict Adaptive ML Weights
    blender = AdaptiveMLBlender()
    blender.load(model_dir)
    f_ml, ml_weights_df, pred_errs_df = blender.predict_weights(df_test_wide)

    df_test_wide["adaptive_ml_blend"] = f_ml
    df_test_wide["simple_blend"] = f_simple
    df_test_wide["hist_blend"] = f_hist

    # 4. Verify Weight Normalization Sum == 1.0
    weight_sums = ml_weights_df.sum(axis=1).values
    weight_sum_diff = np.abs(weight_sums - 1.0).max()
    print(f"\nAdaptive Weight Normalization Check (Max |Sum - 1.0|): {weight_sum_diff:.7f}")
    if weight_sum_diff > 1e-5:
        print("Warning: Adaptive weights do not sum to 1.0 within numerical tolerance!")
    else:
        print("Weight Verification: PASSED (Sum = 1.000000 across all test predictions).")

    # 5. Save Test Adaptive Weights CSV
    weights_export_df = pd.DataFrame({
        "location_id": df_test_wide["location_id"],
        "latitude": df_test_wide["latitude"],
        "longitude": df_test_wide["longitude"],
        "valid_time": df_test_wide["valid_time"],
        "lead_hours": df_test_wide["lead_hours"],
        "ECMWF_IFS_weight": ml_weights_df["w_ECMWF_IFS"].round(4),
        "NOAA_GFS_weight": ml_weights_df["w_NOAA_GFS"].round(4),
        "DWD_ICON_weight": ml_weights_df["w_DWD_ICON"].round(4),
        "blended_precipitation": np.round(f_ml, 4),
        "reference_precipitation": df_test_wide["reference_precipitation"],
    })
    
    weights_csv_multi = output_dir / "multilocation_adaptive_weights_test.csv"
    weights_csv_single = output_dir / "adaptive_weights_test.csv"
    weights_export_df.to_csv(weights_csv_multi, index=False)
    weights_export_df.to_csv(weights_csv_single, index=False)
    print(f"\nSaved test adaptive weights to: {weights_csv_multi}")

    # 6. Save Model Weight Map Summary CSV (data/processed/model_weight_map_summary.csv)
    df_test_wide["lead_day"] = pd.cut(df_test_wide["lead_hours"], bins=[0, 24, 48, 72], labels=[1, 2, 3])
    df_test_wide["w_ECMWF_IFS"] = ml_weights_df["w_ECMWF_IFS"]
    df_test_wide["w_NOAA_GFS"] = ml_weights_df["w_NOAA_GFS"]
    df_test_wide["w_DWD_ICON"] = ml_weights_df["w_DWD_ICON"]

    weight_map_rows = []
    loc_col = COL_LOCATION_ID if COL_LOCATION_ID in df_test_wide.columns else "location_id"

    for (loc_id, l_day), group in df_test_wide.groupby([loc_col, "lead_day"], observed=True):
        lat = group["latitude"].iloc[0]
        lon = group["longitude"].iloc[0]
        m_ecmwf = group["w_ECMWF_IFS"].mean()
        m_gfs = group["w_NOAA_GFS"].mean()
        m_icon = group["w_DWD_ICON"].mean()

        # Determine dominant model by highest mean weight
        w_dict = {"ECMWF_IFS": m_ecmwf, "NOAA_GFS": m_gfs, "DWD_ICON": m_icon}
        dominant = max(w_dict, key=w_dict.get)

        weight_map_rows.append({
            "location_id": loc_id,
            "latitude": lat,
            "longitude": lon,
            "lead_day": int(l_day),
            "mean_ECMWF_IFS_weight": round(m_ecmwf, 4),
            "mean_NOAA_GFS_weight": round(m_gfs, 4),
            "mean_DWD_ICON_weight": round(m_icon, 4),
            "dominant_model": dominant,
        })

    weight_map_df = pd.DataFrame(weight_map_rows)
    weight_map_csv = output_dir / "model_weight_map_summary.csv"
    weight_map_df.to_csv(weight_map_csv, index=False)
    print(f"Saved model weight map summary to: {weight_map_csv}")

    # 7. Compute Overall Continuous & Categorical Metrics
    approaches = {
        "ECMWF_IFS": f_ecmwf,
        "NOAA_GFS": f_gfs,
        "DWD_ICON": f_icon,
        "Simple_Average": f_simple,
        "Historical_Weighted": f_hist,
        "Adaptive_ML_Blend": f_ml,
    }

    thresh = 1.0  # Project analytical heavy rain threshold
    metrics_list = []

    for app_name, f_vals in approaches.items():
        c_met = calculate_continuous_metrics(y_true, f_vals)
        cat_met = calculate_categorical_metrics(y_true, f_vals, threshold=thresh)
        row = {"Approach": app_name, **c_met, **cat_met}
        metrics_list.append(row)

    results_df = pd.DataFrame(metrics_list)
    perf_csv = output_dir / "model_performance_test.csv"
    results_df.to_csv(perf_csv, index=False)
    print(f"Saved test performance metrics to: {perf_csv}")

    # 8. Compute Lead Horizon Breakdown Metrics
    lead_metrics_list = []
    for h_label, group in df_test_wide.groupby("lead_day", observed=True):
        y_grp = group["reference_precipitation"].values
        app_grp = {
            "ECMWF_IFS": group["ECMWF_IFS_precip"].values,
            "NOAA_GFS": group["NOAA_GFS_precip"].values,
            "DWD_ICON": group["DWD_ICON_precip"].values,
            "Simple_Average": compute_simple_ensemble(group),
            "Historical_Weighted": compute_historical_weighted_ensemble(group)[0],
            "Adaptive_ML_Blend": group["adaptive_ml_blend"].values,
        }
        for app_name, f_vals in app_grp.items():
            c_met = calculate_continuous_metrics(y_grp, f_vals)
            lead_metrics_list.append({"Lead_Horizon": f"Day {h_label}", "Approach": app_name, **c_met})

    lead_results_df = pd.DataFrame(lead_metrics_list)

    # 9. Compute Location-Level Breakdown Metrics
    loc_metrics_list = []
    for loc_id, group in df_test_wide.groupby(loc_col):
        y_grp = group["reference_precipitation"].values
        app_grp = {
            "ECMWF_IFS": group["ECMWF_IFS_precip"].values,
            "NOAA_GFS": group["NOAA_GFS_precip"].values,
            "DWD_ICON": group["DWD_ICON_precip"].values,
            "Simple_Average": compute_simple_ensemble(group),
            "Historical_Weighted": compute_historical_weighted_ensemble(group)[0],
            "Adaptive_ML_Blend": group["adaptive_ml_blend"].values,
        }
        for app_name, f_vals in app_grp.items():
            c_met = calculate_continuous_metrics(y_grp, f_vals)
            loc_metrics_list.append({"location_id": loc_id, "Approach": app_name, **c_met})

    loc_results_df = pd.DataFrame(loc_metrics_list)

    # 10. Generate Evaluation Plots
    reports_dir = ROOT_DIR / "reports"
    generate_reports_and_plots(df_test_wide, ml_weights_df, results_df, lead_results_df, loc_results_df, reports_dir)
    print(f"Generated evaluation plots in: {reports_dir}")

    # 11. Print Final Terminal Reports
    print("\n" + "=" * 80)
    print("OVERALL TEST EVALUATION METRICS (COMBINED MULTI-LOCATION TEST SET)")
    print("=" * 80)
    print(results_df.to_string(index=False))

    print("\n" + "=" * 80)
    print("LOCATION-LEVEL ADAPTIVE ML BLEND METRICS")
    print("=" * 80)
    ml_loc_df = loc_results_df[loc_results_df["Approach"] == "Adaptive_ML_Blend"]
    print(ml_loc_df.to_string(index=False))

    print("\n" + "=" * 80)
    print("AVERAGE ADAPTIVE MODEL WEIGHTS BY LOCATION")
    print("=" * 80)
    loc_weights = df_test_wide.groupby(loc_col)[["w_ECMWF_IFS", "w_NOAA_GFS", "w_DWD_ICON"]].mean()
    print(loc_weights.round(4).to_string())

    print("\n" + "=" * 80)
    print("AVERAGE ADAPTIVE MODEL WEIGHTS BY LEAD DAY")
    print("=" * 80)
    lead_weights = df_test_wide.groupby("lead_day", observed=True)[["w_ECMWF_IFS", "w_NOAA_GFS", "w_DWD_ICON"]].mean()
    print(lead_weights.round(4).to_string())

    print("\n" + "=" * 80)
    print("MODEL WEIGHT MAP SUMMARY PREVIEW")
    print("=" * 80)
    print(weight_map_df.head(10).to_string(index=False))

    print("\n" + "=" * 80)
    print("SCIENTIFIC LIMITATION NOTICE")
    print("=" * 80)
    print("  'This multi-location MVP demonstrates geographic variation in model reliability using six")
    print("   selected locations. It does not establish nationwide forecast superiority. Broader validation")
    print("   requires substantially more locations, seasons, and years.'")
    print("=" * 80)


if __name__ == "__main__":
    main()
