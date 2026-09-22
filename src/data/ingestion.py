from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import xarray as xr


class NWPDataLoader:
    """Minimal loader abstraction for multiple NWP model sources."""

    def __init__(self, model_names: Sequence[str] | None = None):
        self.model_names = list(model_names or [])

    def load(self, model_name: str):
        return {"model": model_name, "data": []}

    def read_csv(self, source: str | Path | pd.DataFrame):
        """Read a CSV file or accept an in-memory dataframe."""
        if isinstance(source, pd.DataFrame):
            return source.copy()
        return pd.read_csv(source)

    def read_netcdf(self, source: str | Path | xr.Dataset):
        """Read a NetCDF dataset and return an xarray.Dataset."""
        if isinstance(source, xr.Dataset):
            return source
        return xr.open_dataset(source)

    def to_dataframe(self, ds: xr.Dataset, value_name: str | None = None, model_name: str | None = None):
        """Convert an xarray Dataset into a tidy DataFrame."""
        if value_name is None:
            value_name = next(iter(ds.data_vars.keys()))

        df = ds[[value_name]].to_dataframe().reset_index()
        if model_name is not None and model_name not in df.columns:
            df[model_name] = df[value_name]
        return df

    def __iter__(self):
        return iter(self.model_names)
