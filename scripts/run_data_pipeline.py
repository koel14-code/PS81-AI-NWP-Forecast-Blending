from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.data.pipeline import DataPipeline


def main():
    parser = argparse.ArgumentParser(description="Run the PS81 rainfall data pipeline.")
    parser.add_argument("--input", type=str, default=None, help="CSV path containing forecast samples")
    parser.add_argument("--reference", type=str, default=None, help="Reference grid CSV path")
    parser.add_argument("--output-dir", type=str, default="data/processed", help="Processed output directory")
    args = parser.parse_args()

    if not args.input or not args.reference:
        raise SystemExit("Both --input and --reference are required for the pipeline run.")

    csv_input = pd.read_csv(args.input)
    reference = pd.read_csv(args.reference)
    pipeline = DataPipeline(data_dir=args.output_dir)
    result = pipeline.run(csv_input, reference, model_names=[col for col in csv_input.columns if col not in {"time", "lat", "lon"}])
    print(f"Processed rows: {len(result)}")
    print(f"Saved to: {Path(args.output_dir) / 'aligned_forecasts.csv'}")


if __name__ == "__main__":
    main()
