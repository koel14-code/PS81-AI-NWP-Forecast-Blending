# Historical Rainfall Training Dataset Specification

## 1. Overview & Goal

This document specifies the **Historical Rainfall Training Dataset** (`data/processed/rainfall_training_dataset.csv`) generated for SIH Problem Statement PS81 (**Hybrid AI–NWP Multi-Model Forecast Blending System**).

The dataset aggregates multi-week historical precipitation forecasts from three major global Numerical Weather Prediction (NWP) models (ECMWF IFS, NOAA GFS, DWD ICON) and aligns them with ERA5 reanalysis reference data across multiple forecast initialization run cycles.

---

## 2. Dataset Metadata

- **Historical Period**: July 1, 2024 to July 28, 2024 (4 full weeks, peak Indian monsoon season).
- **Target Location**: Kolkata region (`Latitude = 22.57° N`, `Longitude = 88.36° E`).
- **Primary Variable**: Hourly Precipitation / Rainfall (`mm/h`).
- **Total Records**: `6,048` aligned hourly forecast observations (2,016 rows per NWP model).
- **Lead Time Horizons**: 1 hour to 72 hours (Day 1: 1–24h, Day 2: 25–48h, Day 3: 49–72h).

---

## 3. Data Sources

1. **ECMWF IFS** (European Centre for Medium-Range Weather Forecasts)
2. **NOAA GFS** (National Oceanic and Atmospheric Administration)
3. **DWD ICON** (Deutscher Wetterdienst)
4. **ERA5 Reanalysis** (ECMWF 5th Generation Atmospheric Reanalysis Reference)

---

## 4. Dataset Schema

The generated dataset (`data/processed/rainfall_training_dataset.csv`) contains 10 standardized columns:

| Column Name | Data Type | Units / Format | Description |
| :--- | :--- | :--- | :--- |
| `valid_time` | String (ISO-8601) | `YYYY-MM-DDTHH:MM:SSZ` | Forecast target valid timestamp in UTC |
| `latitude` | Float | Degrees | Target location latitude coordinate (22.57) |
| `longitude` | Float | Degrees | Target location longitude coordinate (88.36) |
| `model` | String | Categorical | NWP model source (`ECMWF_IFS`, `NOAA_GFS`, `DWD_ICON`) |
| `forecast_run` | String (ISO-8601) | `YYYY-MM-DDTHH:MM:SSZ` | Operational initialization run timestamp (00:00 UTC cycle) |
| `lead_hours` | Integer | Hours | Forecast lead time horizon ($t_{\text{valid}} - t_{\text{run}}$, 1h to 72h) |
| `precipitation` | Float | mm/h | Model forecast hourly precipitation |
| `reference_precipitation` | Float | mm/h | ERA5 reanalysis reference hourly precipitation |
| `forecast_error` | Float | mm/h | Derived error ($P_{\text{forecast}} - P_{\text{reference}}$) |
| `absolute_error` | Float | mm/h | Absolute forecast error ($|P_{\text{forecast}} - P_{\text{reference}}|$) |

---

## 5. Forecast Error Formulations

For each aligned observation $i$:
1. **Forecast Error ($E_i$)**:
   $$E_i = P_{\text{forecast}, i} - P_{\text{reference}, i}$$
2. **Absolute Error ($|E_i|$)**:
   $$|E_i| = \left| P_{\text{forecast}, i} - P_{\text{reference}, i} \right|$$
3. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |E_i|$$

---

## 6. Empirical Baseline Historical Forecast Error Statistics

> **Note**: These metrics are baseline historical error statistics computed directly from the downloaded real data over Kolkata (`2024-07-01` to `2024-07-28`). They reflect raw NWP model performance **prior to AI blending**.

### A. Model Coverage & Baseline MAE
| Model Name | Total Aligned Rows | Baseline MAE (mm/h) |
| :--- | :---: | :---: |
| **NOAA GFS** | 2,016 | **0.4446** |
| **ECMWF IFS** | 2,016 | **0.4954** |
| **DWD ICON** | 2,016 | **0.5308** |

### B. Lead-Time Horizon Group MAE
| Lead-Time Horizon | Lead Range | Total Aligned Rows | Baseline MAE (mm/h) |
| :--- | :---: | :---: | :---: |
| **Day 1** | 1 to 24 hours | 2,016 | **0.4903** |
| **Day 2** | 25 to 48 hours | 2,016 | **0.4903** |
| **Day 3** | 49 to 72 hours | 2,016 | **0.4903** |

---

## 7. Data Quality & Integrity Checks

Automated data-quality routines were executed during pipeline build:
- **Missing Values**: `0` missing values across all 10 columns.
- **Duplicate Rows**: `0` duplicates found across primary key tuple `(valid_time, latitude, longitude, model, lead_hours)`.
- **Negative Values**: `0` negative precipitation amounts detected ($\ge 0.0\text{ mm/h}$).
- **Timestamp Integrity**: All timestamps verified as valid ISO-8601 UTC strings.
- **Lead Time Validity**: All lead times verified as strictly positive integers ($1 \le \text{lead\_hours} \le 72$).
- **Coverage Validation**: 100% complete temporal and lead-time coverage across all 3 models.

---

## 8. Limitations & Scope

1. **Single Location Scope**: Dataset currently targets Kolkata (`Lat=22.57, Lon=88.36`). Multi-point spatial grid expansion will follow in Phase 2.
2. **Reference Dataset**: ERA5 is an atmospheric reanalysis dataset combining numerical modeling with data assimilation. It serves as a consistent global reference baseline, but is distinct from direct IMD rain gauge observations.
3. **No Skill Claim**: These statistics represent raw un-blended baseline errors. ML model training and blending optimization will be implemented in subsequent phases.
