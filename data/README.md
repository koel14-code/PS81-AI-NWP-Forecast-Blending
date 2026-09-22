# Data Directory Documentation

This directory manages all input datasets used by the **Hybrid AI–NWP Multi-Model Forecast Blending System**.

> **Note**: Raw and processed weather datasets are **git-ignored** to keep the repository lightweight. Do NOT commit large GRIB2, NetCDF (`.nc`), or CSV data files to Git.

---

## Folder Organization

### `data/raw/`
Contains raw, unmodified forecast output files and observational ground-truth datasets downloaded from meteorological providers.

**Expected Contents**:
- **NWP Model Outputs**:
  - `gfs/`: Global Forecast System (GFS) gridded outputs (`.grib2` / `.nc`).
  - `ncum/`: NCMRWF Unified Model outputs (`.nc`).
  - `ecmwf/`: ECMWF HRES / Ensemble forecasts (`.nc` / `.grib2`).
  - `imd_gfs/`: IMD GFS high-resolution operational forecasts.
- **Observations / Ground Truth**:
  - `imd_obs/`: IMD gridded daily rainfall datasets (`.grd` / `.nc`).
  - `gpm/`: NASA Global Precipitation Measurement IMERG satellite rainfall estimates (`.nc4`).

### `data/processed/`
Contains cleaned, spatial-temporally aligned, and standardized datasets produced by the data processing pipeline (`src/data/`).

**Expected Contents**:
- Standardized NetCDF (`.nc`) files matching uniform spatial grids (e.g., 0.25° x 0.25° over India).
- Merged multi-model feature matrices containing past forecast skills, lead times, spatial coordinates, and observational targets.

---

## Sourcing & Dataset Preparation Instructions

1. Obtain official NWP model datasets and observational rainfall files from approved sources (e.g., IMD, NCMRWF, NOAA, ECMWF).
2. Place raw files under `data/raw/` in appropriate subdirectories.
3. Run the data preprocessing script (to be developed in `src/data/`) to generate aligned files in `data/processed/`.
4. Ensure no real or sensitive data files are staged for commit before pushing changes (`git status`).
