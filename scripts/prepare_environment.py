"""
SkyBlend AI — Environment Preparation & Authentic Pipeline Orchestrator.
PS81 AI-NWP Forecast Blending System.

Ensures that all authentic data sources and trained model weights are in place:
1. Rainfall Pipeline:
   - Raw Dataset: Open-Meteo & ERA5 for 6 Indian Metros (scripts/build_multilocation_dataset.py)
   - Feature Engineering: 12 spatial, temporal, error, & ensemble features (scripts/build_features.py)
   - Model Training: Candidate F AdaptiveMLBlender for ECMWF, GFS, ICON (scripts/train_and_evaluate_expanded_model.py)
2. Wind Pipeline:
   - Raw Dataset & Reference: Open-Meteo & ERA5 (scripts/build_multilocation_wind_dataset.py)
   - Operational Inputs: 72h 6-city demonstration inputs (scripts/build_operational_wind_inputs.py)
3. Temperature Pipeline:
   - Raw Dataset: Open-Meteo 2m temperature for 6 Metros (scripts/build_multilocation_temperature_dataset.py)
   - Model Training: TemperatureBlender trained on WMO 42807 observations (scripts/train_and_evaluate_temperature.py)
"""

import sys
import time
import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "processed"
EXPANDED_MODEL_DIR = ROOT_DIR / "models" / "expanded_full_year"
TEMP_MODEL_DIR = ROOT_DIR / "models" / "temperature"

# Expected core data and model artifacts
RAINFALL_RAW = DATA_DIR / "multilocation_rainfall_training_dataset_2023_06_to_2024_05.csv"
RAINFALL_FEATURES = DATA_DIR / "multilocation_rainfall_ml_features_2023_06_to_2024_05.csv"
RAINFALL_MODELS = [
    EXPANDED_MODEL_DIR / "adaptive_blender_ECMWF_IFS.joblib",
    EXPANDED_MODEL_DIR / "adaptive_blender_NOAA_GFS.joblib",
    EXPANDED_MODEL_DIR / "adaptive_blender_DWD_ICON.joblib",
]
RAINFALL_PERF = DATA_DIR / "model_performance_test.csv"

WIND_RAW = DATA_DIR / "multilocation_wind_training_dataset_2023_06_to_2024_05.csv"
WIND_INPUTS = DATA_DIR / "multilocation_wind_forecast_inputs.csv"

TEMP_RAW = DATA_DIR / "phase8a_multilocation_training_dataset_2023_06_to_2024_05.csv"
TEMP_MODELS = [
    TEMP_MODEL_DIR / "temperature_blender_ECMWF_IFS.joblib",
    TEMP_MODEL_DIR / "temperature_blender_NOAA_GFS.joblib",
    TEMP_MODEL_DIR / "temperature_blender_DWD_ICON.joblib",
]
TEMP_INPUTS = DATA_DIR / "multilocation_temperature_forecast_inputs.csv"
TEMP_PERF = DATA_DIR / "temperature_test_performance.csv"


def run_step(description: str, script_name: str, args: list = None):
    """Executes a pipeline script using current Python interpreter with logging."""
    print("\n" + "=" * 80)
    print(f"--> {description}")
    print(f"    Running: {sys.executable} scripts/{script_name} {' '.join(args or [])}")
    print("=" * 80)
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / script_name)]
    if args:
        cmd.extend(args)

    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    elapsed = time.time() - t0

    if res.returncode != 0:
        print(f"\n[ERROR] Pipeline step failed ({script_name}, exit code {res.returncode}) after {elapsed:.1f}s")
        sys.exit(res.returncode)
    print(f"\n[SUCCESS] Completed {description} in {elapsed:.1f}s")


def are_rainfall_models_ready() -> bool:
    return all(p.exists() and p.stat().st_size > 0 for p in RAINFALL_MODELS) and RAINFALL_PERF.exists()


def are_temperature_models_ready() -> bool:
    return all(p.exists() and p.stat().st_size > 0 for p in TEMP_MODELS) and TEMP_INPUTS.exists() and TEMP_PERF.exists()


def check_all_ready() -> bool:
    """Returns True if all authentic datasets and model weights exist."""
    checks = [
        RAINFALL_RAW.exists(),
        RAINFALL_FEATURES.exists(),
        are_rainfall_models_ready(),
        WIND_RAW.exists(),
        WIND_INPUTS.exists(),
        TEMP_RAW.exists(),
        are_temperature_models_ready(),
    ]
    return all(checks)


def main():
    parser = argparse.ArgumentParser(description="Prepare SkyBlend AI environment and execute original pipelines.")
    parser.add_argument("--force", action="store_true", help="Force rebuild all datasets and retrain all models from scratch.")
    parser.add_argument("--train", action="store_true", help="Force retrain all model weights using existing feature datasets.")
    parser.add_argument("--check-only", action="store_true", help="Only verify whether all datasets and models are present.")
    args = parser.parse_args()

    # Pre-flight check
    if args.check_only:
        if check_all_ready():
            print("[OK] All authentic datasets and model weights are verified.")
            sys.exit(0)
        else:
            print("[WARN] Some datasets or model weights are missing.")
            sys.exit(1)

    if not args.force and not args.train and check_all_ready():
        print("[OK] All authentic datasets, model weights, and operational inputs are verified.")
        return

    print("=" * 80)
    print("SkyBlend AI — Original System Initialization & Training Pipeline")
    print("=" * 80)
    print("Authentic data sourcing: Open-Meteo Historical Forecast API & ECMWF ERA5 Reanalysis")
    print("Study locations: Kolkata, Delhi, Mumbai, Chennai, Bengaluru, Guwahati")
    print("Study duration: 1 Full Year (2023-06-01 to 2024-05-31, 8,784 hourly timestamps)")

    # 1. Rainfall Pipeline
    need_rainfall_raw = args.force or not RAINFALL_RAW.exists()
    if need_rainfall_raw:
        run_step(
            "Fetching Authentic Open-Meteo & ERA5 Rainfall Data (1 Full Year, 6 Metros)",
            "build_multilocation_dataset.py",
            ["--start-date", "2023-06-01", "--end-date", "2024-05-31"],
        )

    need_rainfall_features = args.force or need_rainfall_raw or not RAINFALL_FEATURES.exists()
    if need_rainfall_features:
        run_step(
            "Engineering Rainfall ML Features (12 Spatial, Temporal, & Uncertainty Predictors)",
            "build_features.py",
            [
                "--input-file", str(RAINFALL_RAW),
                "--output-file", str(RAINFALL_FEATURES),
            ],
        )

    need_rainfall_train = args.force or args.train or need_rainfall_features or not are_rainfall_models_ready()
    if need_rainfall_train:
        run_step(
            "Training Candidate F Rainfall ML Blender (ECMWF, GFS, ICON + Early Stopping)",
            "train_and_evaluate_expanded_model.py",
        )

    # 2. Wind Pipeline
    need_wind_raw = args.force or not WIND_RAW.exists()
    if need_wind_raw:
        run_step(
            "Fetching Authentic Open-Meteo & ERA5 Wind Data (1 Full Year, 6 Metros)",
            "build_multilocation_wind_dataset.py",
        )

    need_wind_inputs = args.force or need_wind_raw or not WIND_INPUTS.exists()
    if need_wind_inputs:
        run_step(
            "Generating 72h Multi-Location Operational Wind Forecast Inputs",
            "build_operational_wind_inputs.py",
        )

    # 3. Temperature Pipeline
    need_temp_raw = args.force or not TEMP_RAW.exists()
    if need_temp_raw:
        run_step(
            "Fetching Authentic Open-Meteo Temperature Data (1 Full Year, 6 Metros)",
            "build_multilocation_temperature_dataset.py",
        )

    need_temp_train = args.force or args.train or need_temp_raw or not are_temperature_models_ready()
    if need_temp_train:
        run_step(
            "Training TemperatureBlender on Ground Observations (WMO 42807) & Generating Inputs",
            "train_and_evaluate_temperature.py",
        )

    print("\n" + "=" * 80)
    print("[OK] All authentic datasets, trained model weights, and inputs are ready!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
