"""
Data Schema and Quality Validation Definitions for PS81 Data Pipeline.

Defines expected column names, data types, value constraints,
and quality check report structures for multi-location aligned rainfall datasets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


# Standard Column Names for Aligned & Training Datasets
COL_LOCATION_ID = "location_id"
COL_VALID_TIME = "valid_time"
COL_LATITUDE = "latitude"
COL_LONGITUDE = "longitude"
COL_MODEL = "model"
COL_FORECAST_RUN = "forecast_run"
COL_LEAD_HOURS = "lead_hours"
COL_PRECIPITATION = "precipitation"
COL_REF_PRECIPITATION = "reference_precipitation"
COL_FORECAST_ERROR = "forecast_error"
COL_ABSOLUTE_ERROR = "absolute_error"

REQUIRED_COLUMNS = [
    COL_LOCATION_ID,
    COL_VALID_TIME,
    COL_LATITUDE,
    COL_LONGITUDE,
    COL_MODEL,
    COL_FORECAST_RUN,
    COL_LEAD_HOURS,
    COL_PRECIPITATION,
    COL_REF_PRECIPITATION,
    COL_FORECAST_ERROR,
    COL_ABSOLUTE_ERROR,
]


@dataclass
class DataQualityReport:
    """Holds summary statistics of dataset quality checks."""
    total_records: int = 0
    duplicate_count: int = 0
    missing_value_count: int = 0
    invalid_timestamp_count: int = 0
    negative_precipitation_count: int = 0
    inconsistent_lead_time_count: int = 0
    unaligned_reference_count: int = 0
    is_valid: bool = True
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Returns quality report as dictionary."""
        return {
            "total_records": self.total_records,
            "duplicate_count": self.duplicate_count,
            "missing_value_count": self.missing_value_count,
            "invalid_timestamp_count": self.invalid_timestamp_count,
            "negative_precipitation_count": self.negative_precipitation_count,
            "inconsistent_lead_time_count": self.inconsistent_lead_time_count,
            "unaligned_reference_count": self.unaligned_reference_count,
            "is_valid": self.is_valid,
            "issues": self.issues,
        }
