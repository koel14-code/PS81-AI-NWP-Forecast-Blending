from pathlib import Path

import numpy as np
import xarray as xr

from src.data.ingestion import NWPDataLoader


def test_read_netcdf_returns_dataset(tmp_path: Path):
    path = tmp_path / "sample.nc"
    ds = xr.Dataset(
        {
            "rainfall": (("time", "lat", "lon"), np.ones((2, 2, 2))),
            "gfs": (("time", "lat", "lon"), np.full((2, 2, 2), 2.0)),
        },
        coords={
            "time": [0, 1],
            "lat": [10.0, 11.0],
            "lon": [70.0, 71.0],
        },
    )
    ds.to_netcdf(path)

    loader = NWPDataLoader(model_names=["GFS", "ECMWF"])
    loaded = loader.read_netcdf(path)

    assert set(loaded.data_vars) == {"rainfall", "gfs"}
    assert loaded["rainfall"].shape == (2, 2, 2)
