"""
Master End-to-End Pipeline Runner for SkyBlend AI.

Executes the complete reproducible workflow:
1. Feature Engineering (strictly leakage-free with training cutoff).
2. Chronological Splitting & Model Training (with explicit validation early stopping).
3. Test Set Evaluation & Verification (metrics by location, lead time, and rain intensity).
4. Artifact Generation (joblib models, CSV weights, performance tables, and report plots).

Usage:
    python scripts/run_pipeline.py
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.build_features import main as run_build_features
from scripts.train_adaptive_blender import main as run_train_blender
from scripts.evaluate_blender import main as run_evaluate_blender


def main():
    t0 = time.time()
    print("=" * 85)
    print("SKYBLEND AI (PS81) — MASTER END-TO-END PIPELINE EXECUTION")
    print("=" * 85)

    print("\n>>> STEP 1/3: FEATURE ENGINEERING (LEAKAGE-SAFE)")
    print("-" * 85)
    run_build_features()

    print("\n>>> STEP 2/3: CHRONOLOGICAL TRAINING & VALIDATION SELECTION")
    print("-" * 85)
    run_train_blender()

    print("\n>>> STEP 3/3: FINAL HELD-OUT TEST EVALUATION & ARTIFACT GENERATION")
    print("-" * 85)
    run_evaluate_blender()

    elapsed = time.time() - t0
    print("\n" + "=" * 85)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f}s")
    print("All artifacts generated deterministically in data/processed/, models/, and reports/")
    print("=" * 85)


if __name__ == "__main__":
    main()
