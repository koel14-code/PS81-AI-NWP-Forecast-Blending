"""
Central Configuration Module for AI-NWP Forecast Blending System (PS81).

Provides environment configuration loading, file path management,
regional bounding boxes, model constants, and feature specifications.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base Project Directory
BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class PathConfig:
    """Configures project directory paths."""
    base_dir: Path = BASE_DIR
    raw_data_dir: Path = Path(os.getenv("DATA_RAW_DIR", BASE_DIR / "data" / "raw"))
    processed_data_dir: Path = Path(os.getenv("DATA_PROCESSED_DIR", BASE_DIR / "data" / "processed"))
    model_checkpoint_dir: Path = Path(os.getenv("MODEL_CHECKPOINT_DIR", BASE_DIR / "models_checkpoints"))

    def __post_init__(self):
        """Ensure critical local directories exist."""
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.model_checkpoint_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class BoundingBox:
    """Geographic Bounding Box definition (Latitude/Longitude boundaries)."""
    min_lat: float = float(os.getenv("REGION_MIN_LAT", 6.0))
    max_lat: float = float(os.getenv("REGION_MAX_LAT", 38.0))
    min_lon: float = float(os.getenv("REGION_MIN_LON", 68.0))
    max_lon: float = float(os.getenv("REGION_MAX_LON", 98.0))

    @property
    def bounds_tuple(self) -> Tuple[float, float, float, float]:
        """Returns (min_lat, max_lat, min_lon, max_lon)."""
        return (self.min_lat, self.max_lat, self.min_lon, self.max_lon)


@dataclass
class ModelConfig:
    """Target NWP models and blending parameters."""
    target_parameter: str = os.getenv("TARGET_PARAMETER", "rainfall")
    supported_nwp_models: List[str] = field(default_factory=lambda: ["GFS", "NCUM", "ECMWF", "IMD_GFS"])
    lead_times_hours: List[int] = field(
        default_factory=lambda: [
            int(x.strip()) for x in os.getenv("DEFAULT_LEAD_TIMES", "24,48,72,120").split(",")
        ]
    )
    spatial_resolution_deg: float = 0.25  # Standard grid size in degrees


@dataclass
class AppConfig:
    """Root Application Configuration Container."""
    env: str = os.getenv("ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    paths: PathConfig = field(default_factory=PathConfig)
    region: BoundingBox = field(default_factory=BoundingBox)
    model: ModelConfig = field(default_factory=ModelConfig)


# Global configuration instance
config = AppConfig()
