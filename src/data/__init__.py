"""
PS81 Data Ingestion, Retrieval, and Alignment Package.

Modules:
- sources: LocationConfig and model metadata configurations.
- fetch_forecasts: Retrieval of ECMWF IFS, NOAA GFS, and DWD ICON forecasts.
- fetch_reference: Retrieval of ERA5 reanalysis reference dataset.
- alignment: Alignment on valid_time, latitude, longitude, model, and lead_hours.
- schema: Standard schema column definitions and quality check structures.
"""

from src.data.sources import LocationConfig, SUPPORTED_SOURCES
from src.data.fetch_forecasts import fetch_nwp_forecasts
from src.data.fetch_reference import fetch_era5_reference
from src.data.alignment import align_forecasts_and_reference
from src.data.schema import REQUIRED_COLUMNS, DataQualityReport

__all__ = [
    "LocationConfig",
    "SUPPORTED_SOURCES",
    "fetch_nwp_forecasts",
    "fetch_era5_reference",
    "align_forecasts_and_reference",
    "REQUIRED_COLUMNS",
    "DataQualityReport",
]
