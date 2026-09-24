"""
Weather Regime Context and Extreme Analytical Signal Classifier for SkyBlend AI.
SIH Problem Statement PS81: Weather Situation / Regime Awareness & Extreme Weather Guidance.

Derives lightweight, scientifically defensible operational forecast context and
analytical hazard signals for multi-variable weather forecasting.
"""

from typing import Dict, Any, List
import numpy as np


def classify_precipitation_regime(precip_mm: float, ensemble_std: float = 0.0) -> str:
    """
    Classifies rainfall forecast context based on rainfall intensity and model spread.
    """
    if ensemble_std >= 1.5 and precip_mm >= 1.0:
        return "High Model Disagreement"
    if precip_mm < 0.1:
        return "Dry (< 0.1 mm/h)"
    elif precip_mm < 2.5:
        return "Light Precipitation (0.1–2.5 mm/h)"
    elif precip_mm < 7.5:
        return "Moderate Precipitation (2.5–7.5 mm/h)"
    else:
        return "Heavy Precipitation (≥ 7.5 mm/h)"


def classify_temperature_regime(temp_c: float, ensemble_std: float = 0.0) -> str:
    """
    Classifies thermal forecast context based on 2m temperature and model spread.
    """
    if ensemble_std >= 2.0:
        return "High Model Disagreement (≥ 2.0°C Spread)"
    if temp_c < 20.0:
        return "Cool / Mild (< 20°C)"
    elif temp_c < 35.0:
        return "Moderate / Normal (20–35°C)"
    elif temp_c < 40.0:
        return "High Thermal Risk (35–40°C)"
    else:
        return "Extreme Heatwave Risk (≥ 40°C)"


def classify_wind_regime(wind_kmh: float = 0.0, ensemble_std: float = 0.0) -> str:
    """
    Classifies wind forecast context. Marked as unvalidated when telemetry is pending.
    """
    return "Telemetry Pending Ingestion"


def get_variable_metadata(variable: str) -> Dict[str, Any]:
    """Returns standardized metadata, units, and status for supported variables."""
    var_lower = variable.lower().strip()
    if var_lower in ["precipitation", "rain", "prcp"]:
        return {
            "variable": "precipitation",
            "display_name": "Precipitation",
            "unit": "mm/h",
            "status": "production_validated",
            "metric_label": "Peak Rainfall Intensity",
            "extreme_threshold": 1.0,
            "severe_threshold": 7.5,
            "extreme_label": "Heavy Rainfall Analytical Signal",
        }
    elif var_lower in ["temperature", "temp", "t2m"]:
        return {
            "variable": "temperature",
            "display_name": "2m Temperature",
            "unit": "°C",
            "status": "implemented_extension",
            "metric_label": "Maximum Temperature",
            "extreme_threshold": 38.0,
            "severe_threshold": 40.0,
            "extreme_label": "High Temperature / Heat Risk Signal",
        }
    elif var_lower in ["wind", "wind_speed", "wspd"]:
        return {
            "variable": "wind",
            "display_name": "10m Wind Speed",
            "unit": "km/h",
            "status": "unvalidated_pending_ingestion",
            "metric_label": "Maximum Wind Speed",
            "extreme_threshold": 40.0,
            "severe_threshold": 60.0,
            "extreme_label": "High Wind Speed Indicator",
        }
    else:
        return {
            "variable": var_lower,
            "display_name": var_lower.capitalize(),
            "unit": "N/A",
            "status": "unsupported",
            "metric_label": "Maximum Value",
            "extreme_threshold": 0.0,
            "severe_threshold": 0.0,
            "extreme_label": "Analytical Signal",
        }
