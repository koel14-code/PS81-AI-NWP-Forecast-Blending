"""
Data Sources Configuration and API Metadata for Weather Models.

Defines target models (ECMWF IFS, NOAA GFS, DWD ICON), ERA5 reference,
and multi-location metadata. Designed so latitude/longitude and date ranges
are fully configurable.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class LocationConfig:
    """Configurable target location coordinates and ID."""
    location_id: str = "kolkata"
    name: str = "Kolkata"
    latitude: float = 22.57
    longitude: float = 88.36


# Demonstration Locations for Multi-Location MVP
DEMO_LOCATIONS: Dict[str, LocationConfig] = {
    "kolkata": LocationConfig(location_id="kolkata", name="Kolkata", latitude=22.57, longitude=88.36),
    "delhi": LocationConfig(location_id="delhi", name="Delhi", latitude=28.61, longitude=77.21),
    "mumbai": LocationConfig(location_id="mumbai", name="Mumbai", latitude=19.08, longitude=72.88),
    "chennai": LocationConfig(location_id="chennai", name="Chennai", latitude=13.08, longitude=80.27),
    "guwahati": LocationConfig(location_id="guwahati", name="Guwahati", latitude=26.14, longitude=91.74),
    "bengaluru": LocationConfig(location_id="bengaluru", name="Bengaluru", latitude=12.97, longitude=77.59),
}


@dataclass
class DataSourceMeta:
    """Metadata representation for an NWP model or reference dataset."""
    display_name: str
    model_code: str
    variable_name: str
    api_endpoint: str
    is_reference: bool = False


# Supported Weather Forecast Models & Reference Sources
SUPPORTED_SOURCES: Dict[str, DataSourceMeta] = {
    "ECMWF_IFS": DataSourceMeta(
        display_name="ECMWF IFS",
        model_code="ecmwf_ifs04",
        variable_name="precipitation_ecmwf_ifs04",
        api_endpoint="https://historical-forecast-api.open-meteo.com/v1/forecast",
        is_reference=False,
    ),
    "NOAA_GFS": DataSourceMeta(
        display_name="NOAA GFS",
        model_code="gfs_seamless",
        variable_name="precipitation_gfs_seamless",
        api_endpoint="https://historical-forecast-api.open-meteo.com/v1/forecast",
        is_reference=False,
    ),
    "DWD_ICON": DataSourceMeta(
        display_name="DWD ICON",
        model_code="icon_seamless",
        variable_name="precipitation_icon_seamless",
        api_endpoint="https://historical-forecast-api.open-meteo.com/v1/forecast",
        is_reference=False,
    ),
    "ERA5": DataSourceMeta(
        display_name="ERA5 Reanalysis/Reference",
        model_code="era5",
        variable_name="precipitation",
        api_endpoint="https://archive-api.open-meteo.com/v1/archive",
        is_reference=True,
    ),
}
