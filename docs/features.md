# Feature Engineering & Data Leakage Audit Specification

## 1. Overview & Architecture

This document specifies the feature engineering design for the **PS81 Hybrid AI–NWP Multi-Model Forecast Blending System**. 

The feature pipeline transforms raw aligned NWP forecasts and reference observations into a structured ML-ready dataset (`data/processed/rainfall_ml_features.csv`). The feature set provides temporal context, lead-time dynamics, model encodings, and historical skill indices while strictly enforcing **zero data leakage**.

---

## 2. Complete Feature Inventory (21 Features)

| # | Feature Name | Description / Formula | Primary Source | Available at Forecast Time? | Leakage Considerations & Mitigation |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | `valid_time` | ISO-8601 UTC timestamp of target forecast hour | Open-Meteo API | **YES** | Forecast target identifier. Known at run time. |
| **2** | `latitude` | Geographic latitude coordinate (22.57° N) | System Config | **YES** | Static spatial feature. No leakage. |
| **3** | `longitude` | Geographic longitude coordinate (88.36° E) | System Config | **YES** | Static spatial feature. No leakage. |
| **4** | `model` | Name of NWP forecast model (ECMWF_IFS, NOAA_GFS, DWD_ICON) | NWP Model Meta | **YES** | Categorical identifier. No leakage. |
| **5** | `forecast_run` | Initialization timestamp of NWP model run (00:00 UTC) | NWP Model Meta | **YES** | Run cycle timestamp. No leakage. |
| **6** | `lead_hours` | Forecast lead time in hours ($t_{\text{valid}} - t_{\text{run}}$) | Derived | **YES** | Deterministic function of target and run time. No leakage. |
| **7** | `precipitation` | Model-predicted hourly rainfall rate (mm/h) | NWP Forecast | **YES** | Primary input predictor. Provided by NWP model. |
| **8** | `reference_precipitation` | ERA5 reanalysis reference precipitation (mm/h) | ERA5 Archive | **NO** (Target Only) | **TARGET / EVALUATION ONLY**: Excluded from predictor input set. |
| **9** | `forecast_error` | Diagnostic error ($P_{\text{forecast}} - P_{\text{reference}}$) | Derived | **NO** (Target Only) | **TARGET / EVALUATION ONLY**: Excluded from predictor input set. |
| **10** | `absolute_error` | Diagnostic absolute error ($\|P_{\text{forecast}} - P_{\text{reference}}\||$) | Derived | **NO** (Target Only) | **TARGET / EVALUATION ONLY**: Excluded from predictor input set. |
| **11** | `month` | Calendar month integer (1–12) | Derived from `valid_time` | **YES** | Temporal feature. Fully deterministic at run time. |
| **12** | `day_of_year` | Day of year integer (1–366) | Derived from `valid_time` | **YES** | Seasonal cycle feature. Fully deterministic. |
| **13** | `hour` | Hour of day integer (0–23) | Derived from `valid_time` | **YES** | Diurnal cycle feature. Fully deterministic. |
| **14** | `season` | Meteorological season (`monsoon`, `post_monsoon`, etc.) | Derived from `month` | **YES** | Broad seasonal regime indicator. No leakage. |
| **15** | `lead_day` | Binned lead day index (1 = 1–24h, 2 = 25–48h, 3 = 49–72h) | Derived from `lead_hours` | **YES** | Lead-time grouping index. No leakage. |
| **16** | `forecast_rainfall_regime` | Analytical rainfall intensity bin for model forecast | Derived from `precipitation` | **YES** | Binned predictor (`no_rain`, `light`, `moderate`, `heavy`). |
| **17** | `ref_rainfall_regime` | Analytical rainfall intensity bin for ERA5 reference | Derived from `reference_precipitation` | **NO** (Target Only) | **DIAGNOSTIC ONLY**: Excluded from model predictors. |
| **18** | `rolling_historical_mae_24h` | 24-hour rolling mean of past model absolute errors | Historical Lagged Errors | **YES** | **STRICTLY SHIFTED BY 1 STEP (`.shift(1)`)**: Only uses past errors prior to current valid time. |
| **19** | `model_DWD_ICON` | One-hot indicator (1 if model is DWD ICON else 0) | Derived from `model` | **YES** | Binary indicator. No leakage. |
| **20** | `model_ECMWF_IFS` | One-hot indicator (1 if model is ECMWF IFS else 0) | Derived from `model` | **YES** | Binary indicator. No leakage. |
| **21** | `model_NOAA_GFS` | One-hot indicator (1 if model is NOAA GFS else 0) | Derived from `model` | **YES** | Binary indicator. No leakage. |

---

## 3. Rainfall Intensity Bins (Project-Defined Analytical Bins)

To categorize rainfall intensity into operational weather regimes:
- **`no_rain`**: $P < 0.1 \text{ mm/h}$
- **`light`**: $0.1 \le P < 2.5 \text{ mm/h}$
- **`moderate`**: $2.5 \le P < 7.5 \text{ mm/h}$
- **`heavy`**: $P \ge 7.5 \text{ mm/h}$

*Note*: These thresholds represent project-defined analytical regime bins for multi-model skill segmentation.

---

## 4. Strict Data Leakage Audit & Mitigation

1. **Target Separation**:  
   `reference_precipitation`, `forecast_error`, `absolute_error`, and `ref_rainfall_regime` are explicitly designated as target or evaluation variables. They are **never** passed into feature matrices during model training or inference.

2. **Lagged Rolling Error Calculation**:  
   The `rolling_historical_mae_24h` feature measures a model's recent track record. To guarantee zero lookahead bias:
   $$\text{rolling\_mae}_t = \frac{1}{K} \sum_{k=1}^{K} |E_{t-k}| \quad \text{where } K \le 24 \text{ past hours}$$
   The rolling window uses `.shift(1)`, strictly excluding observation at target hour $t$.

3. **Temporal Ordering Integrity**:  
   All rolling features are computed strictly along chronological `valid_time` sequences for each NWP model.

---

## 5. Summary Quality Check Result

- **Total Rows**: `6,048`
- **Total Features**: `21`
- **Missing Values**: `0`
- **Duplicate Rows**: `0`
- **Leakage Status**: **PASSED CLEAN (Zero Data Leakage)**
