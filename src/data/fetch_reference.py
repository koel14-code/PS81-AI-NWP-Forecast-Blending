"""
Reference/Reanalysis Data Fetcher Module.

Retrieves ERA5 reanalysis/reference precipitation data for specified target location
and date range.
"""

import urllib.request
import json
from typing import List, Dict, Any
from datetime import datetime, timezone

from src.data.sources import LocationConfig, SUPPORTED_SOURCES


def fetch_era5_reference(
    location: LocationConfig,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    """
    Fetches ERA5 reanalysis/reference precipitation data.

    Args:
        location: LocationConfig instance (location_id, latitude, longitude).
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).

    Returns:
        List of reference observation dictionaries.
    """
    meta = SUPPORTED_SOURCES["ERA5"]
    url = (
        f"{meta.api_endpoint}?"
        f"latitude={location.latitude}&longitude={location.longitude}&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=precipitation&timezone=UTC"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "PS81-Forecast-Pipeline/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_json = json.loads(response.read().decode("utf-8"))
    except Exception as err:
        raise RuntimeError(f"Failed to fetch ERA5 reanalysis data for {location.name} ({url}): {err}") from err

    hourly_data = raw_json.get("hourly", {})
    timestamps = hourly_data.get("time", [])
    precip_series = hourly_data.get("precipitation", [])

    records = []
    for ts_str, val in zip(timestamps, precip_series):
        dt_utc = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
        iso_utc = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

        records.append({
            "location_id": location.location_id,
            "valid_time": iso_utc,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "reference_precipitation": float(val) if val is not None else None,
        })

    return records
