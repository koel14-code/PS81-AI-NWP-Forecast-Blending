# Phase 6: Production Model Freeze Audit

**Project:** SkyBlend AI — AI-based NWP Forecast Blending  
**Evaluation Scope:** Comprehensive read-only audit of the Phase 6 production inference path, model artifacts, feature pipeline, training cutoffs, latency, and system dependencies.  
**Audited Artifacts:**
- Production Backend Service: [`src/api/main.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/api/main.py)
- Blending Engine: [`src/blending/ml_blender.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/ml_blender.py)
- Data Schemas & Splitters: [`src/blending/baselines.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/baselines.py), [`src/features/rainfall_features.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/features/rainfall_features.py)
- Phase 6 Expanded Models: [`models/expanded_full_year/`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/expanded_full_year/)
- Prototype July Models: [`models/`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/)
- Processed Serving Artifacts: [`data/processed/multilocation_adaptive_weights_test.csv`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/data/processed/multilocation_adaptive_weights_test.csv), [`data/processed/multilocation_rainfall_ml_features.csv`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/data/processed/multilocation_rainfall_ml_features.csv)

---

## 1. Trace of the Complete Production Inference Path

The repository currently exhibits two distinct operational execution pathways:
1. **The Live API Server Path** (how requests are currently handled in `src/api/main.py`).
2. **The Algorithmic Model Inference Path** (how live predictions are computed from raw NWP inputs in `src/blending/ml_blender.py`).

```mermaid
graph TD
    subgraph "A. Current Live API Path (FastAPI)"
        Req[Client GET /api/forecast?location=kolkata&lead_day=1] --> Parse[Parse location_id & lead_day]
        Parse --> ReadCSV[Read data/processed/multilocation_adaptive_weights_test.csv]
        ReadCSV --> ReadFeat[Read data/processed/multilocation_rainfall_ml_features.csv]
        ReadFeat --> TimeRef[Calculate current 00:00:00Z UTC run time]
        TimeRef --> Slice[Filter 24 hourly steps for location & lead_day]
        Slice --> Merge[Merge NWP member forecasts + precomputed weights]
        Merge --> Resp[Return 24h JSON forecast series]
    end

    subgraph "B. Algorithmic Model Inference Path (AdaptiveMLBlender)"
        NWP[Raw NWP Inputs: ECMWF, GFS, ICON] --> FeatEng[Construct 12 Spatio-Temporal & Uncertainty Features]
        FeatEng --> LoadM[Load models/expanded_full_year/*.joblib]
        LoadM --> PredErr[Predict Absolute Error e_m for each NWP model]
        PredErr --> RelWeight[Compute Inverse-Error Reliabilities: R_m = 1 / e_m + 1e-4]
        RelWeight --> NormW[Normalize Weights: w_m = R_m / sum R_j]
        NormW --> Convex[Convex Blend: F_convex = sum w_m * F_m]
        Convex --> PeakLift[Peak-Preserving Lift: alpha = 0.35, threshold = 2.0 mm/h]
        PeakLift --> FinalF[Final Operational Blended Forecast]
    end
```

### Trace Step-by-Step:
1. **API Request (`src/api/main.py:127–137`):**
   Client issues `GET /api/forecast?location=kolkata&lead_day=1`. The API parses query parameters and normalizes location string (`loc_clean = location.lower()`).
2. **Forecast Reference Anchor (`src/api/main.py:46–52`):**
   `get_forecast_reference_time()` derives the current operational run date at `00:00:00 UTC` dynamically from system time.
3. **Weight File Lookup (`src/api/main.py:55–65`):**
   `get_weights_df()` checks `DATA_DIR / "multilocation_adaptive_weights_test.csv"`.
4. **Data Slicing (`src/api/main.py:138–150`):**
   Filters rows where `location_id == loc_clean` and `lead_hours` falls into $(24 \times (d-1), 24 \times d]$. Extracts 24 hourly records.
5. **Feature & Member Alignment (`src/api/main.py:152–174`):**
   Reads `multilocation_rainfall_ml_features.csv`, invokes `split_data_chronologically()`, pivots test partition to wide format via `pivot_aligned_dataset()`, and inner-joins raw NWP member inputs (`ECMWF_IFS_precip`, `NOAA_GFS_precip`, `DWD_ICON_precip`) with `blended_precipitation`.
6. **JSON Serialization (`src/api/main.py:175–226`):**
   Constructs 24-step hourly forecast series with timestamps, individual member rain depths, and final blended precipitation.

> [!IMPORTANT]
> **Forensic Finding:** The live API endpoint (`src/api/main.py`) does **NOT** call `.predict()` on the Phase 6 `.joblib` models on the fly. It serves pre-computed forecasts from `data/processed/multilocation_adaptive_weights_test.csv`.

---

## 2. Exact Production Artifacts

### A. Phase 6 Production Model Artifacts (`models/expanded_full_year/`)

All three models are instances of scikit-learn's `HistGradientBoostingRegressor`, trained on the full-year dataset (36,888 unique station-hours):

| Artifact Filename | Size (Bytes) | Model Class | Iterations (`n_iter_`) | Expected Input Features ($N=12$) | Hyperparameters | Loaded in API? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| [`adaptive_blender_ECMWF_IFS.joblib`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/expanded_full_year/adaptive_blender_ECMWF_IFS.joblib) | 218,080 | `HistGradientBoostingRegressor` | 57 | `lead_hours`, `lead_day`, `month`, `day_of_year`, `hour`, `latitude`, `longitude`, `precipitation`, `rolling_historical_mae_24h`, `ensemble_mean`, `ensemble_std`, `ensemble_range` | `lr=0.05, max_iter=150, max_leaf_nodes=31, loss='squared_error', random_state=42, early_stopping=True` | No (loaded by research pipelines) |
| [`adaptive_blender_NOAA_GFS.joblib`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/expanded_full_year/adaptive_blender_NOAA_GFS.joblib) | 168,032 | `HistGradientBoostingRegressor` | 43 | Same 12 features | Same hyperparameters | No (loaded by research pipelines) |
| [`adaptive_blender_DWD_ICON.joblib`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/expanded_full_year/adaptive_blender_DWD_ICON.joblib) | 395,608 | `HistGradientBoostingRegressor` | 106 | Same 12 features | Same hyperparameters | No (loaded by research pipelines) |

### B. Preprocessing & Ancillary Artifacts
- **Normalization Artifacts:** **None.** Inverse-error weighting is computed analytically in closed form inside `AdaptiveMLBlender.predict_weights()`: $w_i = R_i / \sum R_j$.
- **Scaler Artifacts:** **None.** `HistGradientBoostingRegressor` partitions raw numerical values into 256 discrete histogram bins natively; no StandardScaler or MinMaxScaler is required or used.
- **Metadata Files:** No standalone JSON metadata exists in `models/expanded_full_year/`. Model training metadata was recorded in [`reports/expanded_model_training_summary.json`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/reports/expanded_model_training_summary.json).
- **Configuration Files:** Hyperparameters and constants are embedded in the `AdaptiveMLBlender` class constructor:
  - $\epsilon = 10^{-4}$ (numerical stability denominator)
  - `random_state = 42`
  - $\alpha_{\text{lift}} = 0.35$ (peak preservation lift)
  - $\tau_{\text{rain}} = 2.0\text{ mm/h}$ (peak activation threshold)

---

## 3. Verification: Phase 6 Model is Frozen

Audited against all six freeze invariants:

| Freeze Verification Criterion | Confirmed Value / Status | Evidence in Codebase |
| :--- | :---: | :--- |
| **No Model Retraining** | **VERIFIED** | Zero calls to `.fit()` exist in `src/api/` or `src/blending/` during inference. Model files have fixed timestamps from initial Phase 6 training. |
| **No Scaler Fitting** | **VERIFIED** | No scaler classes (`StandardScaler`, `MinMaxScaler`) exist in the inference path. |
| **No Test / Validation Labels Used** | **VERIFIED** | Prediction inputs consist exclusively of NWP member forecasts, station coordinates, calendar dates, and causal rolling MAE. Target `reference_precipitation` is never accessed. |
| **No Phase 10/11 Contamination** | **VERIFIED** | Zero references to `phase10a`, `phase10b`, `phase11`, or `gate_config` exist in `src/`. |
| **No Dynamic Threshold Tuning** | **VERIFIED** | Thresholds are static class defaults. |
| **`peak_lift_alpha`** | **Fixed at `0.35`** | [`src/blending/ml_blender.py:54`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/ml_blender.py#L54) |
| **`rain_threshold`** | **Fixed at `2.0 mm/h`** | [`src/blending/ml_blender.py:55`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/ml_blender.py#L55) |
| **`epsilon`** | **Fixed at `1e-4`** | [`src/blending/ml_blender.py:52`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/ml_blender.py#L52) |

---

## 4. Feature Construction and Temporal Leakage Audit

Phase 6 error regressors utilize exactly 12 predictor features (`FEATURE_COLS`):

| # | Feature Name | Source | Temporal Character | Leakage Risk | Inference Availability |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 1 | `lead_hours` | Target forecast horizon | Forecast-time step | None | Instantly available ($1 \dots 72$) |
| 2 | `lead_day` | $\lceil \text{lead\_hours} / 24 \rceil$ | Forecast-time step | None | Instantly available ($1, 2, 3$) |
| 3 | `month` | Calendar month of `valid_time` | Forecast valid date | None | Available ($1 \dots 12$) |
| 4 | `day_of_year` | Day of year of `valid_time` | Forecast valid date | None | Available ($1 \dots 366$) |
| 5 | `hour` | Hour of day of `valid_time` | Forecast valid date | None | Available ($0 \dots 23$) |
| 6 | `latitude` | Station metadata | Fixed geographic coordinate | None | Invariant per location |
| 7 | `longitude` | Station metadata | Fixed geographic coordinate | None | Invariant per location |
| 8 | `precipitation` | Member NWP forecast ($f_m$) | Forecast-time NWP signal | None | Available from NWP feed |
| 9 | `rolling_historical_mae_24h` | Causal 24h rolling error window | Historical error buffer | None | Available from preceding verification cycle |
| 10 | `ensemble_mean` | $\frac{1}{3} \sum f_m$ | Forecast-time consensus | None | Computed on the fly |
| 11 | `ensemble_std` | $\sigma(f_{\text{ECMWF}}, f_{\text{GFS}}, f_{\text{ICON}})$ | Forecast-time uncertainty | None | Computed on the fly |
| 12 | `ensemble_range` | $\max(f_m) - \min(f_m)$ | Forecast-time member spread | None | Computed on the fly |

### Deep Audit: `rolling_historical_mae_24h`
In [`src/features/rainfall_features.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/features/rainfall_features.py) (lines 90–160):
- **Causal Window Guarantee:**
  ```python
  mask = (times < run_time) & (times >= win_start)  # win_start = run_time - 24 hours
  ```
  Only observations strictly prior to the forecast initialization cycle (`valid_time < run_time`) are queried.
- **Expanding Fallback:** If fewer than required observations exist in the immediate 24h window, it falls back to past observations strictly before `run_time`.
- **Cold-Start Boundary:** At the beginning of the operational record before any past observations exist, it applies a fallback prior calculated exclusively from the training split (`times <= train_cutoff_time`).
- **Conclusion:** The rolling MAE feature is strictly causal and cannot leak future observations.

---

## 5. Training, Validation, and Test Chronological Cutoffs

Audited by executing `split_data_chronologically()` across both primary datasets:

### A. Full-Year Expanded Dataset (`multilocation_rainfall_ml_features_2023_06_to_2024_05.csv`)
- **Total Records:** 474,336 long-format rows ($52,704$ unique station-hours across 6 locations)
- **Train Split (70%):**
  - **Interval:** `2023-06-01T00:00:00Z` to `2024-02-12T03:00:00Z`
  - **Volume:** 331,992 long rows | **36,888 unique station-hours**
  - **Role:** Error model feature-to-target fitting.
- **Validation Split (15%):**
  - **Interval:** `2024-02-12T04:00:00Z` to `2024-04-07T00:00:00Z`
  - **Volume:** 71,118 long rows | **7,902 unique station-hours**
  - **Role:** Early stopping loss evaluation (`n_iter_no_change=10`) during training.
- **Pre-Monsoon Benchmark Test Split (15%):**
  - **Interval:** `2024-04-07T01:00:00Z` to `2024-05-31T23:00:00Z`
  - **Volume:** 71,226 long rows | **7,914 unique station-hours**
  - **Role:** Strictly frozen post-training out-of-sample benchmark. Zero influence on models.

### B. Out-of-Period July 2024 Holdout (`multilocation_rainfall_ml_features.csv`)
- **July Test Split:**
  - **Interval:** `2024-07-24T18:00:00Z` to `2024-07-28T23:00:00Z`
  - **Volume:** 5,508 long rows | **612 unique station-hours**
  - **Role:** Completely independent external temporal holdout (active monsoon regime).

**Causal Cutoff Verification:** Training cutoff is strictly `2024-02-12T03:00:00Z`. Zero validation, pre-monsoon test, or July holdout data was present during parameter estimation.

---

## 6. Mathematical Specification of the Phase 6 Blending Engine

Implemented in [`src/blending/ml_blender.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/blending/ml_blender.py) (lines 151–184):

### Step 1: Member Expected Error Prediction
For each NWP source $m \in \{\text{ECMWF\_IFS}, \text{NOAA\_GFS}, \text{DWD\_ICON}\}$:
$$\hat{e}_m = \max\left(0.0, \, \mathcal{M}_m(X_{\text{infer}})\right)$$

### Step 2: Inverse Error Reliability Metric
$$\mathcal{R}_m = \frac{1}{\hat{e}_m + \epsilon}, \quad \text{where } \epsilon = 10^{-4}\text{ mm/h}$$

### Step 3: Normalized Convex Weights
$$w_m = \frac{\mathcal{R}_m}{\sum_{j \in \mathcal{M}} \mathcal{R}_j}, \quad \text{subject to } w_m \ge 0, \quad \sum_{m \in \mathcal{M}} w_m = 1.0$$

### Step 4: Convex Consensus Forecast
$$F_{\text{convex}} = \sum_{m \in \mathcal{M}} w_m \cdot f_m = (w_{\text{ECMWF}} \cdot f_{\text{ECMWF}}) + (w_{\text{GFS}} \cdot f_{\text{GFS}}) + (w_{\text{ICON}} \cdot f_{\text{ICON}})$$

### Step 5: Peak-Preserving Convective Adjustment
To prevent the convex combination from attenuating single-member convective storm cells when the ensemble signals precipitation:
$$\gamma = \text{clip}\left(\frac{\text{ens\_max} - \tau_{\text{rain}}}{5.0}, \, 0.0, \, 1.0\right) \times \alpha_{\text{lift}}$$
$$F_{\text{Phase 6}} = (1.0 - \gamma) \cdot F_{\text{convex}} + \gamma \cdot \text{ens\_max}$$
Where:
- $\text{ens\_max} = \max(f_{\text{ECMWF}}, f_{\text{GFS}}, f_{\text{ICON}})$
- $\tau_{\text{rain}} = 2.0\text{ mm/h}$
- $\alpha_{\text{lift}} = 0.35$

---

## 7. Accidental Dependency and Leakage Check

Grep analysis across the entire production codebase (`src/`) was executed for:
- `phase10a`
- `phase10b`
- `phase11`
- `direct_quantile`
- `gate_config`

### Result:
**ZERO occurrences found in `src/`.**  
All experimental Phase 10 and Phase 11 artifacts, decision trees, quantile regressors, and gate search configurations are strictly isolated in `scratch/`, `reports/`, and `models/phase10*` / `models/phase11*`. They cannot alter production behavior.

---

## 8. Empirical Latency Benchmark

Conducted using `scratch/audit_phase6_latency.py`:

### Benchmark A: FastAPI Production Service (`/api/forecast`)
- **Cold-Start Response Latency:** `2,492.03 ms` (Python import, FastAPI routing, and initial CSV parse)
- **Warm Response Latency (Mean $\pm$ Std):** **`206.70 ms` $\pm$ `41.83 ms`**
- **Warm Latency p50:** `208.87 ms`
- **Warm Latency p95:** `271.47 ms`
- **Warm Latency p99:** `286.33 ms`
- **CSV Disk I/O Breakdown:** Reading `multilocation_adaptive_weights_test.csv` + `multilocation_rainfall_ml_features.csv` takes **`120.63 ms` per request** (**58.4% of total endpoint runtime**).

### Benchmark B: Phase 6 Algorithmic Model Inference (`AdaptiveMLBlender`)
- **Cold Model Loading from Disk:** **`40.73 ms`** (deserializing all 3 `HistGradientBoostingRegressor` `.joblib` files)
- **Warm Single-Station 24h Horizon Inference (Mean $\pm$ Std):** **`13.58 ms` $\pm$ `3.55 ms`**
- **Warm Multi-Location 72h Full Operational Horizon (6 Stations $\times$ 72 Lead Hours = 432 Forecast Points):**
  - **Total 432h Inference Runtime:** **`12.03 ms` $\pm$ `2.65 ms`**
  - **Latency per Station-Hour:** **`0.0279 ms`** (approx. 28 microseconds per forecast point)

> [!NOTE]
> **Performance Insight:** The Phase 6 GBDT blending engine is exceptionally fast, processing an entire 6-station 72-hour operational cycle in **12 milliseconds**. The FastAPI response time (~206 ms) is completely dominated by repeated CSV disk reading.

---

## 9. Final Scientific & Production Classification

### **Classification: D — Production path is not actually using the intended Phase 6 model**

### Comprehensive Justification:
1. **The Disconnect:**
   - In research and evaluation reports (Phases 6, 7A, 8, 9, 10A, 10B, 11), "Phase 6" is explicitly defined as the full-year expanded blender whose weights are saved in [`models/expanded_full_year/`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/expanded_full_year/).
   - However, the FastAPI production backend ([`src/api/main.py`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/src/api/main.py)) serves pre-computed forecasts from [`data/processed/multilocation_adaptive_weights_test.csv`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/data/processed/multilocation_adaptive_weights_test.csv).
   - Numerical comparison proves that the weights in `multilocation_adaptive_weights_test.csv` match the old prototype models in [`models/`](file:///C:/Users/Koel/Documents/GitHub/PS81-AI-NWP-Forecast-Blending/models/) with **maximum error 0.0**, but deviate from the official Phase 6 models in `models/expanded_full_year/` by up to **0.5404**.
2. **Static vs Dynamic Inference:**
   - The production API does not execute live model inference. It replays the July 24–28 test set forecasts re-indexed to current calendar dates.
3. **Integrity of Research Models:**
   - The official Phase 6 model artifacts in `models/expanded_full_year/` are mathematically intact, completely frozen, strictly leakage-free, and reproduce all benchmark results. However, they have not yet been wired into the live API serving layer.

---

## 10. Recommended Next Actions

1. **Production Serving Modernization (When Modifying Code is Authorized):**
   - Wire `AdaptiveMLBlender` directly into the FastAPI application state (`app.state.blender`) during server startup, loading from `models/expanded_full_year/`.
   - Implement live, on-the-fly inference for `/api/forecast` using incoming Open-Meteo forecasts rather than reading static July test CSVs from disk.
   - This will simultaneously eliminate the disk I/O bottleneck (cutting API latency from ~206 ms to ~15 ms) and align the API with the official Phase 6 full-year model.
2. **Preserve Prototype Stability:**
   - Maintain the frozen research baseline in `models/expanded_full_year/`.
   - Keep Phase 10 and Phase 11 artifacts cataloged as advisory research assets.
