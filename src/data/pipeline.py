from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import config
from src.data.ingestion import NWPDataLoader
from src.data.preprocessing import align_to_reference, normalize_columns


class DataPipeline:
    """Minimal end-to-end data pipeline for rainfall forecast preparation."""

    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = Path(data_dir or config.paths.processed_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def run(self, raw_table: pd.DataFrame, reference_table: pd.DataFrame, model_names: list[str] | None = None):
        loader = NWPDataLoader(model_names=model_names or [])
        loaded = loader.read_csv(raw_table)
        normalized = normalize_columns(loaded)
        value_cols = [c for c in normalized.columns if c not in {"time", "lat", "lon"}]
        aligned = align_to_reference(normalized, reference_table, value_cols=value_cols)
        output_path = self.data_dir / "aligned_forecasts.csv"
        aligned.to_csv(output_path, index=False)
        return aligned

    def run_netcdf(self, path: str | Path, reference_table: pd.DataFrame, value_name: str | None = None, model_name: str | None = None):
        loader = NWPDataLoader(model_names=[model_name] if model_name else [])
        ds = loader.read_netcdf(path)
        df = loader.to_dataframe(ds, value_name=value_name, model_name=model_name)
        normalized = normalize_columns(df)
        value_cols = [c for c in normalized.columns if c not in {"time", "lat", "lon"}]
        aligned = align_to_reference(normalized, reference_table, value_cols=value_cols)
        output_path = self.data_dir / "aligned_netcdf_forecasts.csv"
        aligned.to_csv(output_path, index=False)
        return aligned
