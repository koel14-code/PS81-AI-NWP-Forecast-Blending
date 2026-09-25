# PS81 Weather Forecast Data Ingestion & Alignment Pipeline Documentation

## 1. Overview & Data Sources

The **PS81 Data Ingestion and Alignment Pipeline** retrieves, standardizes, and aligns multi-model Numerical Weather Prediction (NWP) precipitation forecasts with ERA5 reanalysis reference data.

### Supported Sources
- **ECMWF IFS** (European Centre for Medium-Range Weather Forecasts - Integrated Forecasting System)
- **NOAA GFS** (National Oceanic and Atmospheric Administration - Global Forecast System)
- **DWD ICON** (Deutscher Wetterdienst - Icosahedral Nonhydrostatic Model)
- **ERA5** (ECMWF 5th Generation Atmospheric Reanalysis Reference)

---

## 2. API Access Method

Forecast and reference data are retrieved using the Open-Meteo Historical Forecast & Climate Archive REST APIs.
- **Historical Forecast API Endpoint**: `https://historical-forecast-api.open-meteo.com/v1/forecast`
- **Climate Archive Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Data Format**: Standardized JSON responses parsed into tabular DataFrames.

---

## 3. Dataset Schema

The pipeline produces aligned datasets following this schema:

| Column Name | Data Type | Units / Format | Description |
| :--- | :--- | :--- | :--- |
| `valid_time` | String (ISO-8601) | `YYYY-MM-DDTHH:MM:SSZ` | Forecast target valid timestamp in UTC |
| `latitude` | Float | Degrees | Target location latitude coordinate |
| `longitude` | Float | Degrees | Target location longitude coordinate |
| `model` | String | Categorical | NWP model source (`ECMWF_IFS`, `NOAA_GFS`, `DWD_ICON`) |
| `forecast_run` | String (ISO-8601) | `YYYY-MM-DDTHH:MM:SSZ` | Model run initialization timestamp (00:00 UTC cycle) |
| `lead_hours` | Integer | Hours | Forecast lead time horizon ($t_{\text{valid}} - t_{\text{run}}$) |
| `precipitation` | Float | mm/h | Model-predicted hourly rainfall rate |
| `reference_precipitation` | Float | mm/h | ERA5 reanalysis reference precipitation rate |

---

## 4. Pipeline Operations & Data Handling

### Timestamp & Timezone Handling
- All input timestamps are explicitly converted and validated as **Coordinated Universal Time (UTC)**.
- Formatted as standard ISO-8601 strings (`YYYY-MM-DDTHH:MM:SZ`).

### Lead-Time Calculation
- Forecast initialization times (`forecast_run`) are anchored to operational model run cycles (e.g., 00:00 UTC).
- Lead time in hours is calculated as:
  $$\text{lead\_hours} = \frac{t_{\text{valid}} - t_{\text{run}}}{3600 \text{ seconds}}$$

### Alignment Methodology
1. Raw hourly precipitation forecasts are fetched for each model over the requested date range.
2. Hourly ERA5 reference precipitation data is fetched for matching timestamps.
3. Records are joined across primary key dimensions: `(valid_time, latitude, longitude, model, lead_hours)`.

### Data Quality Checks & Validation
The pipeline automatically executes validation routines:
- **Duplicate Records**: Checks and removes duplicate tuples.
- **Missing Values**: Identifies and logs missing forecast or reference entries.
- **Invalid Timestamps**: Flagged if string formatting fails or timezones deviate from UTC.
- **Negative Values**: Verifies precipitation amounts are $\ge 0.0\text{ mm/h}$.
- **Lead-Time Consistency**: Ensures $\text{lead\_hours} > 0$.

---

## 5. Distinction: ERA5 Reanalysis vs Direct Ground Observation

> **Important Conceptual Note**:  
> **ERA5 is a reanalysis reference dataset, NOT direct ground-station observational truth.**

- **Reanalysis (ERA5)**: Combines historical observations from satellites, weather balloons, and stations with advanced numerical weather prediction physics models via data assimilation (4D-Var). It provides spatially continuous gridded estimations (~31 km resolution).
- **Ground Observations (IMD Rain Gauges)**: Direct physical point measurements recorded by rain gauge instruments at specific weather stations.

In the initial pipeline phase, ERA5 serves as a high-quality global reference baseline. In later iterations, direct Indian Meteorological Department (IMD) gridded rain gauge observations will be integrated alongside ERA5.

---

## 6. Pipeline Limitations & Future Scope
- **Current Resolution**: Point extraction based on spatial interpolation (~0.25°). Full 2D spatial grid slicing will be added in Phase 2.
- **Real-Time Data**: Archive endpoints operate with a 5-day latency for ERA5; real-time blending will utilize live observation feeds.
