"""
Forecast Data Fetcher Module.

Retrieves historical gridded precipitation forecasts for target NWP models
(ECMWF IFS, NOAA GFS, DWD ICON) for a specified location and date range.
"""

import urllib.request
import json
from typing import Dict, List, Any
from datetime import datetime, timezone

from src.data.sources import LocationConfig, SUPPORTED_SOURCES, DataSourceMeta


def fetch_nwp_forecasts(
    location: LocationConfig,
    start_date: str,
    end_date: str,
    models: List[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetches raw forecast records from configured NWP model endpoints.

    Args:
        location: LocationConfig instance (location_id, latitude, longitude, name).
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        models: List of model keys to fetch (defaults to ECMWF_IFS, NOAA_GFS, DWD_ICON).

    Returns:
        Dictionary mapping model key to list of raw hourly forecast observations.
    """
    if models is None:
        models = ["ECMWF_IFS", "NOAA_GFS", "DWD_ICON"]

    model_codes = [SUPPORTED_SOURCES[m].model_code for m in models if m in SUPPORTED_SOURCES]
    models_str = ",".join(model_codes)

    url = (
        f"https://historical-forecast-api.open-meteo.com/v1/forecast?"
        f"latitude={location.latitude}&longitude={location.longitude}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=precipitation&models={models_str}&timezone=UTC"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "PS81-Forecast-Pipeline/1.0"})
    
    raw_json = None
    last_err = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw_json = json.loads(response.read().decode("utf-8"))
                break
        except Exception as err:
            last_err = err
            if attempt < 3:
                import time
                time.sleep(2 * attempt)
            else:
                raise RuntimeError(f"Failed to fetch forecast data for {location.name} after 3 attempts ({url}): {last_err}") from last_err

    hourly_data = raw_json.get("hourly", {})
    timestamps = hourly_data.get("time", [])

    results: Dict[str, List[Dict[str, Any]]] = {}

    for model_key in models:
        meta = SUPPORTED_SOURCES.get(model_key)
        if not meta:
            continue

        var_name = meta.variable_name
        precip_series = hourly_data.get(var_name, hourly_data.get("precipitation", []))

        model_records = []
        for ts_str, val in zip(timestamps, precip_series):
            dt_utc = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
            iso_utc = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            model_records.append({
                "location_id": location.location_id,
                "valid_time": iso_utc,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "model": model_key,
                "precipitation": float(val) if val is not None else None,
            })

        results[model_key] = model_records

    return results
