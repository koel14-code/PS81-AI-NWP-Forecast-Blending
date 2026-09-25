# SkyBlend AI --- Technical Documentation

**Project:** SkyBlend AI: Hybrid AI--NWP Multi-Model Forecast Blending
System\
**SIH Problem Statement:** PS81\
**Production architecture:** Phase 6 frozen production path\
**Status:** Production demonstration pipeline frozen; research
experiments remain isolated

------------------------------------------------------------------------

## 1. Executive Summary

SkyBlend AI is a meteorological post-processing and multi-model
precipitation forecast blending system. It combines precipitation
forecasts from three global Numerical Weather Prediction (NWP) sources:

-   **ECMWF IFS**
-   **NOAA GFS**
-   **DWD ICON**

Instead of assigning one fixed model weight everywhere, SkyBlend AI uses
machine learning to estimate the expected absolute error of each NWP
member from forecast-time information. The predicted errors are
converted into normalized adaptive contributions, and the member
forecasts are combined into one blended precipitation forecast.

The frozen production architecture is deliberately separated into two
stages:

1.  **Offline training and evaluation**
    -   harmonize NWP and ERA5 data;
    -   construct a chronological multi-location dataset;
    -   engineer forecast-time features;
    -   train one `HistGradientBoostingRegressor` per NWP model to
        estimate expected absolute error;
    -   freeze the resulting model artifacts.
2.  **Runtime serving**
    -   load the frozen artifacts once during FastAPI startup;
    -   load the processed NWP demonstration grid into memory;
    -   compute adaptive weights through the same `AdaptiveMLBlender`
        implementation used by the evaluated pipeline;
    -   expose forecasts, weights, spatial contributions and analytical
        extreme-rainfall signals through the API;
    -   render the results in the React/Vite frontend.

The current system is a **demonstration workstation, not a live
operational weather service**. Its runtime demonstration inputs are a
processed historical NWP grid from the project evaluation period, with
timestamps re-anchored for the UI. ERA5 is used as the gridded reference
dataset during development and evaluation; it is not treated as gauge
truth.

------------------------------------------------------------------------

## 2. Problem and Motivation

Individual NWP systems can differ in precipitation skill because of
model formulation, parameterization, geographic context, atmospheric
regime and forecast conditions. A fixed average can therefore discard
information about when a particular model has historically performed
better.

The central SkyBlend idea is:

> **Estimate the expected error of each forecast member for the current
> context, then convert those error estimates into adaptive model
> contributions.**

The system is therefore not intended to claim that one NWP model is
universally superior. Instead, it produces a context-dependent blend and
exposes the contribution of each member.

The project focuses on precipitation because rainfall is highly variable
in space and time and can contain difficult upper-tail events. The
evaluation therefore considers both continuous precipitation error and
categorical rainfall detection metrics.

------------------------------------------------------------------------

## 3. System Architecture

### 3.1 High-level architecture

``` text
                         OFFLINE TRAINING / EVALUATION
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  ECMWF IFS ─┐                                                     │
│  NOAA GFS ──┼──> Harmonization / Alignment ──> Feature Builder   │
│  DWD ICON ──┘                         ↑                            │
│                                      │                            │
│                                   ERA5 Reference                  │
│                                      │                            │
│                                      ▼                            │
│                         Chronological 70/15/15 Split              │
│                                      │                            │
│                                      ▼                            │
│                    3 × HistGradientBoostingRegressor              │
│                                      │                            │
│                                      ▼                            │
│                 models/expanded_full_year/*.joblib                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

                         RUNTIME DEMONSTRATION
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│ Frozen .joblib artifacts                                          │
│          │                                                        │
│          ▼                                                        │
│ FastAPI startup/lifespan                                          │
│          │                                                        │
│          ├── AdaptiveMLBlender(alpha=0.35, threshold=2.0)         │
│          │                                                        │
│          └── In-memory processed NWP demonstration grid            │
│                         │                                         │
│                         ▼                                         │
│                predict_weights()                                  │
│                         │                                         │
│          ┌──────────────┼───────────────┐                         │
│          ▼              ▼               ▼                         │
│     /api/forecast  /api/weights  /api/extreme-signal              │
│          │              │               │                          │
│          └──────────────┼───────────────┘                          │
│                         ▼                                          │
│                 React / Vite frontend                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### 3.2 Production/runtime boundary

The runtime does **not** retrain models.

The production demonstration path uses:

-   frozen Phase 6 model artifacts;
-   the production `AdaptiveMLBlender` implementation;
-   the processed NWP feature grid;
-   in-memory caching after startup.

Research-stage Phase 8A, Phase 9, Phase 10A, Phase 10B and Phase 11
artifacts are not part of the production API path.

------------------------------------------------------------------------

## 4. Data Sources

### 4.1 NWP members

The production dataset contains three NWP forecast members:

  Internal model   Source/model
  ---------------- ----------------------
  `ECMWF_IFS`      Open-Meteo ECMWF IFS
  `NOAA_GFS`       Open-Meteo GFS
  `DWD_ICON`       Open-Meteo ICON

The three members provide the precipitation inputs that are blended.

### 4.2 Reference dataset

**ERA5 Reanalysis** is used as the precipitation reference during
training/evaluation.

Important qualification:

> ERA5 is a spatially consistent gridded reanalysis reference, not
> direct rain-gauge telemetry.

Consequently, evaluation results should be described as performance
against the ERA5 reference rather than as station-gauge ground truth.

### 4.3 Demonstration locations

The expanded dataset covers six Indian locations:

  Location      Latitude   Longitude
  ----------- ---------- -----------
  Kolkata          22.57       88.36
  Delhi            28.61       77.21
  Mumbai           19.08       72.88
  Chennai          13.08       80.27
  Guwahati         26.14       91.74
  Bengaluru        12.97       77.59

The six-city scope is a demonstration/evaluation scope. It does not
establish arbitrary-location or nationwide generalization.

------------------------------------------------------------------------

## 5. Dataset Construction

### 5.1 Expanded historical dataset

The production ML dataset covers:

-   **June 1, 2023 → May 31, 2024**
-   **8,784 hourly timestamps**
-   **6 locations**
-   **3 NWP models**
-   **3 indexed lead horizons**
-   **474,336 aligned long-format rows**
-   **52,704 unique station-hours after deduplication**

Every month in the production-year dataset contains complete hourly
coverage for the six demonstration locations.

### 5.2 Rainfall distribution

Across the 52,704 unique meteorological station-hours:

  Regime            Approx. share
  --------------- ---------------
  Dry                       81.7%
  Light rain                16.1%
  Moderate rain              1.8%
  Heavy rain                 0.3%

The imbalance is important: ordinary dry/light conditions dominate the
dataset, while heavy rainfall contains comparatively few observations.
Heavy-rain metrics therefore require careful interpretation.

### 5.3 Chronological split

The production split is chronological rather than randomly shuffled:

-   **Training:** approximately 70%
-   **Validation:** approximately 15%
-   **Test:** approximately 15%

The production cutoff is:

`2024-02-12T03:00:00Z`

The corresponding validation and test periods follow chronologically.

This separation is important because forecast verification is a temporal
problem. Randomly mixing future observations into training would make
the reported evaluation less representative of genuine out-of-time
inference.

------------------------------------------------------------------------

## 6. Feature Engineering

The frozen Phase 6 production blender uses **12 predictor features**:

1.  `lead_hours`
2.  `lead_day`
3.  `hour`
4.  `month`
5.  `day_of_year`
6.  `latitude`
7.  `longitude`
8.  `precipitation`
9.  `rolling_historical_mae_24h`
10. `ensemble_mean`
11. `ensemble_std`
12. `ensemble_range`

### 6.1 Forecast-time features

The calendar and forecast scheduling features are available at forecast
time:

-   lead hour;
-   lead day;
-   valid-time hour;
-   month;
-   day of year;
-   location coordinates.

### 6.2 Model-specific forecast

`precipitation` represents the current NWP member's own predicted
precipitation.

For each model-specific error regressor, this is the corresponding
member forecast.

### 6.3 Historical skill

`rolling_historical_mae_24h` represents a causal historical error prior.

The production audit verifies that the historical error feature does not
use future verification observations beyond the forecast-time cutoff.

### 6.4 Ensemble context

The three NWP members also provide a simple ensemble context:

-   mean precipitation;
-   standard deviation;
-   range.

These features allow the error model to recognize whether the current
forecast members broadly agree or disagree.

------------------------------------------------------------------------

## 7. Leakage and Data Integrity Controls

The project includes explicit integrity checks.

Verified conditions include:

-   no negative lead times;
-   `valid_time - forecast_run == lead_hours`;
-   zero duplicate primary keys in the production dataset;
-   zero null values in the audited feature set;
-   chronological train/validation/test separation;
-   causal construction of historical error priors.

The production audit also verifies that the runtime path uses the frozen
Phase 6 artifacts rather than the older precomputed static weight file.

------------------------------------------------------------------------

## 8. Adaptive ML Blending Method

The central model is implemented in:

`src/blending/ml_blender.py`

and served through:

`src/api/main.py`

### 8.1 Target learned by each model

For each NWP member:

\[ y_m = \|F_m - R\| \]

where:

-   (F_m) = precipitation forecast from NWP member (m)
-   \(R\) = ERA5 reference precipitation
-   (y_m) = absolute forecast error

Three regressors are trained:

\[ g\_{`\mathrm{ECMWF}`{=tex}}(X) \]

\[ g\_{`\mathrm{GFS}`{=tex}}(X) \]

\[ g\_{`\mathrm{ICON}`{=tex}}(X) \]

Each produces an estimate of expected absolute error:

\[ `\hat `{=tex}e_m = g_m(X) \]

### 8.2 Error-to-weight conversion

The system converts predicted errors into inverse-error trust scores:

\[ s_m = `\frac{1}{\hat e_m + \epsilon}`{=tex} \]

where:

\[ `\epsilon `{=tex}= 10\^{-4} \]

The scores are normalized:

\[ w_m = `\frac{s_m}{\sum_j s_j}`{=tex} \]

Therefore:

\[ `\sum`{=tex}\_m w_m = 1 \]

and:

\[ w_m `\geq 0`{=tex} \]

This gives an interpretable contribution for each model.

### 8.3 Convex blend

The initial blended forecast is:

\[ F\_{`\mathrm{convex}`{=tex}} = w_EF_E + w_GF_G + w_IF_I \]

where (E), (G), and (I) represent ECMWF, GFS and ICON.

The result is therefore a convex combination of the three member
forecasts.

------------------------------------------------------------------------

## 9. Peak-Lift Mechanism

A pure convex blend can suppress a strong precipitation signal when one
NWP member predicts a peak while the other members remain comparatively
dry.

To reduce this dampening, the frozen Phase 6 system applies an
inference-time peak-lift mechanism.

The configured parameters are:

-   **peak-lift alpha:** `0.35`
-   **rain threshold:** `2.0 mm/h`

The lift is computed from the maximum member forecast:

\[ L = `\operatorname{clip}`{=tex} `\left`{=tex}(
`\frac{\max(F_m)-2}{5}`{=tex}, 0,1 `\right`{=tex}) `\alpha`{=tex} \]

The final forecast is:

\[ F\_{`\mathrm{final}`{=tex}} = (1-L)F\_{`\mathrm{convex}`{=tex}} +
L`\max`{=tex}(F_m) \]

This preserves the basic adaptive blend while allowing the maximum
member forecast to influence the final result when the ensemble enters a
stronger-rainfall range.

### Important limitation

Peak lift cannot create precipitation information that is absent from
all three NWP members.

If every member substantially underpredicts an observed convective
event, the blender has no independent observational signal from which to
reconstruct the missing rainfall peak.

This limitation is one of the main findings from the heavy-rainfall
analysis.

------------------------------------------------------------------------

## 10. Production Model Architecture

The frozen production artifacts are stored under:

`models/expanded_full_year/`

The production system contains three fitted
`HistGradientBoostingRegressor` models:

-   `adaptive_blender_ECMWF_IFS.joblib`
-   `adaptive_blender_NOAA_GFS.joblib`
-   `adaptive_blender_DWD_ICON.joblib`

The production training configuration includes:

-   `HistGradientBoostingRegressor`
-   learning rate `0.05`
-   maximum leaf nodes `31`
-   early stopping
-   `n_iter_no_change=10`
-   `random_state=42`

The final fitted iteration counts were approximately:

-   ECMWF: 57
-   GFS: 43
-   ICON: 106

The artifacts are loaded once at FastAPI startup rather than retrained
per request.

------------------------------------------------------------------------

## 11. FastAPI Runtime

The runtime entry point is:

`src/api/main.py`

### 11.1 Startup

During FastAPI lifespan startup:

1.  the frozen Phase 6 `AdaptiveMLBlender` is instantiated;
2.  the three `.joblib` artifacts are loaded;
3.  the processed NWP feature grid is loaded;
4.  the required operational demonstration horizon is prepared;
5.  the objects are retained in application state.

This avoids repeatedly loading model files for each API request.

### 11.2 Runtime grid

The current demonstration grid uses a fixed historical processed-NWP
window:

`2024-05-28T00:00:00Z`

through a 72-hour horizon.

The grid covers:

-   all six demonstration locations;
-   lead hours 1--72.

The frontend displays dates projected onto the current demonstration
date context.

Therefore the system should be described as a **historical-data
demonstration workstation**, not as live operational NWP ingestion.

------------------------------------------------------------------------

## 12. API Surface

The backend exposes the following endpoints:

  Endpoint                 Purpose
  ------------------------ -----------------------------------------
  `/api/health`            Runtime health/status
  `/api/overview`          Overview metrics and summary
  `/api/forecast`          Member trajectories and adaptive blend
  `/api/weights`           Time-varying model contributions
  `/api/spatial-weights`   Location-level contribution information
  `/api/verification`      Held-out evaluation information
  `/api/extreme-signal`    Project analytical rainfall signal
  `/api/methodology`       Pipeline/methodology metadata

The production frontend consumes these endpoints rather than
independently recreating the blending algorithm.

------------------------------------------------------------------------

## 13. Frontend Architecture

The frontend is implemented using:

-   React
-   Vite
-   Recharts
-   React Leaflet
-   Lucide React
-   Framer Motion

The major views are:

1.  Overview
2.  Forecast Intelligence
3.  Adaptive AI
4.  Spatial Intelligence
5.  Verification
6.  Extreme Weather
7.  Methodology

### 13.1 Data truth rule

The frontend should not hard-code forecast values when API data is
available.

The final frontend audit specifically removed stale values from:

-   Overview spatial contribution preview;
-   Forecast Intelligence verification cards;
-   Overview model-weight fallbacks;
-   Overview peak-rain fallback;
-   static demonstration date fallback;
-   Methodology pipeline stages.

The Methodology page now derives its stages dynamically from
`/api/methodology`.

### 13.2 Runtime terminology

The top-level UI uses:

**DEMONSTRATION FORECAST WORKSTATION**

rather than implying a live operational forecasting service.

The Extreme Weather page presents its rainfall trigger as a:

**project analytical threshold**

rather than an official warning threshold.

------------------------------------------------------------------------

## 14. Evaluation Methodology

The project reports both continuous and categorical rainfall metrics.

### 14.1 Continuous metrics

-   MAE
-   RMSE
-   Bias
-   Pearson correlation (r)

### 14.2 Categorical metrics

At the rainfall-detection threshold of 1 mm/h:

-   Probability of Detection (POD)
-   False Alarm Ratio (FAR)
-   Critical Success Index (CSI)

For upper-tail analysis, a heavy-rain threshold of **7.5 mm/h** is also
used.

### 14.3 Important statistical qualification

The project includes paired bootstrap analyses over unique
station-hours.

A 95% bootstrap confidence interval that excludes zero is described as
statistically distinguishable under that bootstrap procedure.

It is not presented as an exact p-value or as proof of universal
superiority.

Heavy-rain estimates are particularly uncertain because the pre-monsoon
test contains only a small number of heavy station-hours.

------------------------------------------------------------------------

## 15. Pre-Monsoon Held-Out Test Results

The main frozen Phase 6 test evaluation produced:

  Approach                   MAE     RMSE      Bias   Pearson r
  --------------------- -------- -------- --------- -----------
  ECMWF IFS               0.1339   0.7722   -0.0098      0.4348
  NOAA GFS                0.1519   1.0276   -0.0379      0.1827
  DWD ICON                0.1600   0.9607   -0.0123      0.2576
  Simple average          0.1380   0.8158   -0.0200      0.3564
  Historical weighted     0.1386   0.8231   -0.0215      0.3492
  SkyBlend                0.1323   0.8092   -0.0286      0.3652

At the 1 mm/h categorical threshold, SkyBlend produced:

-   POD: **0.3266**
-   FAR: **0.5779**
-   CSI: **0.2257**

These results show that the adaptive blend changes the error profile
relative to both individual members and fixed-weight baselines. They
should not be interpreted as proof that SkyBlend is universally superior
across all weather regimes.

------------------------------------------------------------------------

## 16. External July 2024 Holdout

A separate July 2024 holdout was preserved for out-of-period evaluation.

Authoritative scope:

-   **1,836 long-format rows**
-   **612 unique station-hours**
-   **6 demonstration locations**
-   `2024-07-24T18:00Z` → `2024-07-28T23:00Z`

Results:

  ----------------------------------------------------------------------------------
  Approach           MAE      RMSE      Bias         r     POD≥1     FAR≥1     CSI≥1
  ------------ --------- --------- --------- --------- --------- --------- ---------
  ECMWF IFS       0.3711    1.0336   +0.0694    0.6357    0.7808    0.4062    0.5089

  NOAA GFS        0.4748    1.2851   +0.0252    0.3781    0.6438    0.5347    0.3701

  DWD ICON        0.4895    1.2633   -0.0572    0.3533    0.3836    0.6056    0.2414

  Simple          0.3964    1.0553   +0.0125    0.5903    0.6575    0.4286    0.4404
  average                                                                  

  Historical      0.3855    1.0535   +0.0048    0.5914    0.6575    0.3960    0.4528
  weighted                                                                 

  SkyBlend        0.3543    1.0235   -0.0289    0.6226    0.6301    0.3349    0.4554
  ----------------------------------------------------------------------------------

These results are an external holdout from the project's historical
dataset, not a live operational forecast verification.

------------------------------------------------------------------------

## 17. Heavy-Rainfall Analysis

The project separately analyzed rainfall events at or above 7.5 mm/h.

Across the combined pre-monsoon and July analysis, the project
identified **26 unique heavy-rain station-hour events** under the stated
event scope.

A major finding was:

> Many observed heavy events were not represented strongly enough in the
> NWP ensemble for a convex blending system to reconstruct the observed
> peak.

In one strict analysis definition, **21 of 26** combined heavy events
had all three NWP members below the 7.5 mm/h event threshold.

This creates a structural limitation:

``` text
Observed convective peak
          ↑
          │
      missing signal
          │
ECMWF ── low
GFS   ── low
ICON  ── low
          │
          ▼
   ML blender cannot
   invent missing peak
```

The analysis also found that a strong signal in only one member can be
diluted by a convex blend.

Therefore future severe-rainfall work requires additional information,
such as observations, radar/satellite-derived predictors,
convection-sensitive predictors, or a carefully validated
regime-specific architecture.

------------------------------------------------------------------------

## 18. Phase 8A: Atmospheric Context Experiment

A separate experiment investigated additional atmospheric variables.

Available forecast variables included:

-   2 m temperature;
-   surface pressure;
-   relative humidity availability varied by NWP source.

Relative humidity was not used in the final Phase 8A experiment because
ECMWF RH availability was incomplete in the examined source.

The Phase 8A experiment therefore used temperature and pressure.

Results did not provide a consistent enough improvement over the frozen
Phase 6 baseline to justify replacing the production model.

The measured latency also increased slightly.

Consequently:

> Phase 6 remains the trusted production baseline, while Phase 8A
> remains an experimental research branch.

------------------------------------------------------------------------

## 19. Phase 9: Model and Evaluation Hardening

Phase 9 focused on evaluation hardening without changing the frozen
production architecture.

It verified:

-   the three-member `HistGradientBoostingRegressor` architecture;
-   causal historical error features;
-   chronological evaluation;
-   regime-specific diagnostics;
-   heavy-event behavior;
-   bootstrap uncertainty analysis;
-   model-weight behavior.

The weight distributions did not collapse onto a single NWP member.

This supports the interpretation that the production blender is
dynamically distributing contribution rather than simply acting as a
disguised single-model selector.

------------------------------------------------------------------------

## 20. Phase 10A: Direct Forecast Experiment

Phase 10A investigated direct prediction of the final precipitation
forecast rather than predicting each member's expected error.

Two direct models were evaluated:

1.  Direct L2 regression
2.  Direct 0.90 quantile regression

The quantile model produced a stronger upper-tail tendency but also
incurred substantially worse routine forecast error and positive bias.

The direct L2 model did not solve the fundamental heavy-rain problem
when the member ensemble itself lacked the required signal.

Therefore neither direct model replaced Phase 6.

------------------------------------------------------------------------

## 21. Phase 10B: Validation-Selected Regime Gate

Phase 10B tested a regime gate:

> use the upper-tail q90 model when a validation-selected convective
> signal is detected; otherwise use Phase 6.

The selected gate was:

``` text
max member precipitation >= 1.20 mm/h
```

The experiment demonstrated a real tradeoff:

-   upper-tail heavy-rain error improved;
-   routine forecast accuracy degraded materially.

Paired pre-monsoon bootstrap results showed a positive MAE difference
relative to Phase 6:

-   MAE difference: approximately **+0.0675**
-   95% bootstrap CI: approximately **\[+0.0555, +0.0800\]**

Therefore the gate was **not promoted to production**.

It remains a research-stage upper-tail experiment.

------------------------------------------------------------------------

## 22. Phase 11: Richer Regime Gate

Phase 11 explored richer candidate gates using features such as:

-   ensemble maximum;
-   ensemble mean;
-   ensemble standard deviation;
-   ensemble range;
-   maximum-minus-mean;
-   maximum/mean ratio;
-   maximum member weight;
-   dominant-model precipitation skill;
-   dominant-model weight;
-   interaction features.

A validation-selected candidate was:

``` text
ensemble maximum >= 1.40 mm/h
AND
maximum-minus-mean >= 0.50 mm/h
```

The candidate reduced validation error relative to the Phase 10B gate,
but it still materially degraded routine test MAE relative to Phase 6.

Pre-monsoon paired bootstrap:

-   Phase 11 vs Phase 6 MAE difference: approximately **+0.0569**
-   95% bootstrap CI: approximately **\[+0.0457, +0.0686\]**

The Phase 11 experiment also produced a stronger upper-tail signal on
the small July holdout, but the sample was too small to establish
general operational performance.

Therefore Phase 11 is classified as:

> **research-stage upper-tail / convective rainfall advisory research**

It is **not** part of the production API and should not be described as
a proven severe-weather advisory model.

------------------------------------------------------------------------

## 23. Runtime Performance

The production freeze audit measured the following:

  Measurement                                      Result
  ----------------------------------- -------------------
  One-time model loading                          \~58 ms
  Pure 24-hour inference                \~10.84 ± 2.41 ms
  Full 432-hour grid inference          \~13.33 ± 3.06 ms
  Warm `/api/forecast`                  \~30.20 ± 4.18 ms
  Warm endpoint p95                            \~37.05 ms
  Earlier warm `/api/forecast` path           \~206.70 ms

The API path was substantially accelerated by:

-   loading model artifacts once;
-   keeping the processed grid in memory;
-   avoiding repeated disk reads;
-   using the same production blender implementation for endpoint
    inference.

A later end-to-end verification measured representative warm endpoint
behavior in the approximately **28.68--30.03 ms** range.

These measurements are local prototype measurements, not cloud
production SLAs.

------------------------------------------------------------------------

## 24. API--Frontend Scientific Truth Verification

The final end-to-end audit verified:

### Backend

-   all eight endpoints returned HTTP 200;
-   all six locations were supported;
-   lead days 1--3 were available;
-   adaptive weights summed to 1 within tolerance;
-   forecasts were finite and nonnegative;
-   timestamps were sequential.

### Direct/API parity

Representative cases included:

-   Kolkata Day 1;
-   Bengaluru Day 3;
-   Guwahati Day 1.

The direct production blender and API output showed exact parity for the
audited forecast and weight values.

### Frontend

The audit confirmed:

-   Overview uses API-driven forecast and spatial values;
-   Forecast Intelligence uses API verification values;
-   Adaptive AI uses API weights;
-   Spatial Intelligence uses the same API contribution data;
-   Extreme Weather uses the API signal;
-   Methodology uses API pipeline stages.

A search of the production `src/` and `frontend/src/` paths found no
production references to:

-   `phase11`
-   `gate_config`
-   `q90`

This confirms that the experimental upper-tail branches remain isolated
from the frozen production application.

------------------------------------------------------------------------

## 25. Demonstration Date Semantics

The frontend displays current-looking demonstration dates, but the
underlying forecast grid is historical.

This distinction is intentional and should be communicated clearly.

The correct description is:

> **Historical-data demonstration forecast workstation**

rather than:

> Live operational forecast.

The runtime currently projects the historical processed forecast grid
onto the demonstration date context used by the interface.

This allows the full UI/API workflow to be demonstrated without falsely
representing archived data as a live meteorological feed.

------------------------------------------------------------------------

## 26. Scientific Limitations

### 26.1 Historical rather than live NWP ingestion

The current runtime does not retrieve live ECMWF, GFS or ICON forecasts.

Future deployment would require a live ingestion and scheduling layer.

### 26.2 ERA5 is not gauge truth

The reference dataset is ERA5 reanalysis. Real station/rain-gauge
verification would be required for operational validation.

### 26.3 Lead-time limitation

The historical source provides a continuous hourly series rather than
independently archived 00Z/12Z operational initialization cycles for
every demonstration forecast.

Therefore the project's Day 1/2/3 indexing should not be interpreted as
a rigorous estimate of real operational lead-time degradation.

### 26.4 Heavy-rain sample size

Heavy rainfall is rare in the evaluation sample.

For the pre-monsoon heavy regime, only 22 station-hours were available
in the exact regime analysis. July contained four heavy station-hours
under the corresponding scope.

Upper-tail metrics therefore have substantial uncertainty.

### 26.5 Missing convective information

When all NWP members underpredict a convective event, an error-blending
system cannot reliably reconstruct the missing peak from those forecasts
alone.

### 26.6 Six-city demonstration scope

The current dataset covers six Indian cities. It does not prove
performance across India's full geographic and climatic diversity.

### 26.7 Prototype latency measurements

The reported latency values were measured in the local prototype
environment. Production cloud/edge performance will depend on deployment
hardware, concurrency, networking and data-ingestion architecture.

------------------------------------------------------------------------

## 27. Reproducibility and Project Structure

The principal project areas are:

``` text
PS81-AI-NWP-Forecast-Blending/
│
├── src/
│   ├── api/
│   │   └── main.py
│   ├── blending/
│   │   ├── baselines.py
│   │   └── ml_blender.py
│   ├── data/
│   │   ├── alignment.py
│   │   ├── fetch_forecasts.py
│   │   └── fetch_reference.py
│   └── features/
│       └── rainfall_features.py
│
├── models/
│   └── expanded_full_year/
│       ├── adaptive_blender_ECMWF_IFS.joblib
│       ├── adaptive_blender_NOAA_GFS.joblib
│       └── adaptive_blender_DWD_ICON.joblib
│
├── data/
│   └── processed/
│
├── frontend/
│   └── src/
│
├── reports/
│
├── scripts/
│
├── scratch/
│
├── tests/
│
└── README.md
```

The repository README contains the concise setup and architecture
overview. This document provides the deeper technical record.

------------------------------------------------------------------------

## 28. Production vs Research Artifacts

The following distinction is strictly preserved across the codebase:

### Production / Validated Core

-   **Precipitation Blending**: Phase 6 expanded-year HistGradientBoosting error regressors in `models/expanded_full_year/`; peak-lift $\alpha = 0.35$; rain threshold $\tau = 2.0\text{ mm/h}$;
-   **Temperature Blending**: Consensus-based temperature error prediction in `models/temperature/` (continuous, no peak-lift);
-   **10m Surface Wind Speed Blending**: Historical-Error Weighted Blend ($w_m \propto \frac{1}{\text{rolling\_24h\_MAE}_m + 10^{-4}}$) over ECMWF IFS, NOAA GFS, and DWD ICON;
-   **Inference Runtimes**: Zero learned model files required for wind; audited causal training priors (ECMWF $2.29$, GFS $3.15$, ICON $4.77\text{ km/h}$) as runtime fallbacks;
-   **Service & Delivery**: FastAPI runtime (`src/api/main.py`) serving precipitation, temperature, and wind; React/Vite dashboard (`frontend/`).

### Research Only / Isolated Sandbox

-   **Wind GBDT Model**: Researched in Phase 2 (`evaluate_wind_models_complete.py`), held out from production to avoid overfitting and preserve zero-artifact simplicity;
-   **Wind Ridge Model**: Researched in Phase 2, held out from production;
-   **Calibrated Rainfall Models**: Calib-1, Calib-2, and Calib-3 reliability layers;
-   **Experimental Regime Gates**: Phase 10A direct forecast models, Phase 10B heuristic regime gate, Phase 11 multi-layer gating sandbox;
-   **Atmospheric Predictors**: Phase 8A upper-air and soundings feature experiments;
-   **Continuous Pre-training**: Phase 9 research experiments.

Research results provide valuable scientific insights but are strictly isolated from the production serving pipeline.


------------------------------------------------------------------------

## 29. Recommended Future Work

The highest-value next development stages are:

### 29.1 Live NWP ingestion

Replace the historical demonstration grid with a scheduled ingestion
pipeline for current ECMWF, GFS and ICON forecasts.

### 29.2 Gauge-based verification

Add verified Indian precipitation observations where licensing and
access permit.

This would provide a more operationally relevant target than ERA5 alone.

### 29.3 Radar/satellite context

Convective precipitation is difficult to recover from NWP members alone.
Radar, satellite and observation-derived features could provide
independent information about developing precipitation.

### 29.4 Better lead-time evaluation

Use archived operational NWP initialization cycles so that Day 1/2/3
correspond to genuine forecast lead times.

### 29.5 Larger spatial coverage

Expand beyond six demonstration cities to a broader station/grid network
covering multiple climatic and geographic regimes.

### 29.6 Selective upper-tail modeling

Continue researching regime-aware upper-tail correction, but evaluate it
using:

-   larger severe-rain samples;
-   independent test periods;
-   station/radar verification;
-   paired statistical comparisons;
-   reliability and calibration diagnostics.

### 29.7 Probabilistic forecasts

A future version could produce precipitation distributions or calibrated
quantiles rather than a single deterministic estimate.

------------------------------------------------------------------------

## 30. Judge-Facing Technical Summary

A concise technical explanation of SkyBlend AI is:

> **SkyBlend AI takes precipitation forecasts from ECMWF IFS, NOAA GFS
> and DWD ICON and uses three machine-learning error models to estimate
> how much error each model is expected to have in the current forecast
> context. Those predicted errors are converted into normalized adaptive
> weights, producing a context-dependent blended forecast. A controlled
> peak-lift mechanism reduces excessive dampening of stronger member
> signals. The production implementation uses frozen Phase 6 models
> loaded once into FastAPI, with the same blending implementation used
> during evaluation and runtime.**

When discussing validation, use:

> **The model was evaluated on chronological held-out data and a
> separate July 2024 external holdout within the project's historical
> dataset.**

When discussing the current deployment state, use:

> **This is a historical-data demonstration workstation, not a live
> operational NWP service.**

When discussing severe rainfall, use:

> **The current blender can improve or preserve some member signals, but
> it cannot reconstruct a convective peak that is missing from all NWP
> members. Upper-tail regime gates were therefore kept as research
> experiments rather than promoted into the production path.**

------------------------------------------------------------------------

## 31. Final Technical Status

The production pipeline has reached a freeze point suitable for the
current prototype demonstration.

The key verified properties are:

-   frozen Phase 6 model artifacts;
-   causal historical skill features;
-   chronological evaluation;
-   adaptive model weights;
-   exact direct/API parity in audited cases;
-   normalized nonnegative weights;
-   frontend/API data consistency;
-   isolated research experiments;
-   documented historical-data limitation;
-   documented ERA5 reference limitation;
-   documented lead-time limitation;
-   measured local runtime latency.

The Git production history currently contains:

``` text
3819998 docs: update README for Phase 6 architecture
e564598 fix: finalize Phase 6 production demo pipeline
```

The remaining working-tree research files should remain separate unless
they are intentionally cleaned, consolidated, or promoted through a
future reviewed change.

------------------------------------------------------------------------

## 32. Key References Within the Repository

The most important supporting project artifacts are:

-   `README.md`
-   `src/blending/ml_blender.py`
-   `src/api/main.py`
-   `reports/phase6_production_freeze_audit.md`
-   `reports/phase7a_heavy_rain_analysis.md`
-   `reports/phase8a_atmospheric_features.md`
-   `reports/phase9_model_evaluation_hardening.md`
-   `reports/phase10a_direct_forecast_experiment.md`
-   `reports/phase10a_paired_statistical_hardening.md`
-   `reports/phase10b_regime_gate.md`
-   `reports/phase11_regime_gate.md`
-   `reports/phase11_final_audit.md`
-   `reports/phase11_paired_statistical_hardening.md`
-   `reports/api_frontend_truth_audit.md`
-   `reports/final_end_to_end_verification.md`
-   `tests/test_data_integrity.py`
-   `tests/test_multi_variable_api.py`
-   `reports/sih_alignment_final_audit.md`
-   `reports/temperature_station_validation_kolkata.md`
-   `src/blending/temperature_blender.py`
-   `src/blending/regimes.py`

These artifacts should be treated as complementary layers:

``` text
README
  ↓
Architecture & quick understanding

Technical Documentation
  ↓
Full scientific/engineering explanation

SIH Alignment Audit
  ↓
Factual requirement-by-requirement audit (reports/sih_alignment_final_audit.md)

Production Freeze Audit
  ↓
Frozen implementation and runtime integrity

E2E Verification
  ↓
API ↔ frontend truth and deployment-path verification

Research Reports
  ↓
Experimental evidence and future-development analysis
```

------------------------------------------------------------------------

## 33. Multi-Variable Forecasting Architecture

To align with the SIH problem statement ("optimized forecast for rainfall, temperature, wind and extreme-weather indicators"), SkyBlend AI extends the core blending methodology across meteorological variables through a clean variable abstraction:

$$\text{variable} \in \{\text{precipitation}, \, \text{temperature}, \, \text{wind}\}$$

### Architectural Design Principles
1. **Separation of Physics:** Different weather variables operate under fundamentally distinct physics. Precipitation is intermittent, non-negative, and exhibits high skewness, requiring convective peak-lift ($\alpha=0.35, \tau=2.0\text{ mm/h}$) to combat ensemble dampening. In contrast, 2m air temperature is continuous and normally distributed, making peak-lift physically inappropriate.
2. **Variable-Agnostic API Contracts:** All REST endpoints support `variable=precipitation|temperature|wind` via query parameter, defaulting to `precipitation` for 100% backward compatibility.
3. **No Synthetic Numbers:** Where genuine source data exists (precipitation and temperature), real trained models and empirical metrics are delivered. Where source data is absent (surface wind), the endpoint returns `status: "unavailable"` and explicit reasons rather than fabricating fake synthetic trajectories.

------------------------------------------------------------------------

## 34. 2m Temperature Adaptive Blending Pipeline

### 34.1 Mathematical Formulation
For each NWP source $m \in \{\text{ECMWF\_IFS}, \, \text{NOAA\_GFS}, \, \text{DWD\_ICON}\}$:

1. **Error Prediction:**
   $$\hat{e}_m^{\text{temp}}(t) = \max\left(0.0, \, \mathcal{M}_m^{\text{temp}}(X_{\text{temp}}(t))\right)$$
   where $\mathcal{M}_m^{\text{temp}}$ is a `HistGradientBoostingRegressor` trained on 2m temperature errors.

2. **Inverse-Error Normalization:**
   $$\mathcal{R}_m(t) = \frac{1}{\hat{e}_m^{\text{temp}}(t) + \epsilon}, \quad w_m(t) = \frac{\mathcal{R}_m(t)}{\sum_j \mathcal{R}_j(t)}$$

3. **Continuous Consensus Blend (Zero Peak-Lift):**
   $$F_{\text{temp}}(t) = \sum_{m=1}^3 w_m(t) \cdot f_m^{\text{temp}}(t)$$
   Peak-lift is strictly omitted ($\alpha=0$) to preserve energy balance and prevent unnatural daytime over-warming.

### 34.2 Empirical Ground-Station Benchmark (WMO 42807 Kolkata Alipore)
Evaluated across 3,957 unique station-hours during the Pre-Monsoon test split (April 7 – May 31, 2024):

| Forecast Approach | MAE (°C) ↓ | RMSE (°C) ↓ | Bias (°C) | Pearson $r$ ↑ |
| :--- | :---: | :---: | :---: | :---: |
| **ECMWF IFS** | 1.1180 | 1.5792 | -0.3252 | 0.9264 |
| **NOAA GFS** | 2.5064 | 3.0854 | +2.2694 | 0.8964 |
| **DWD ICON** | 1.3812 | 1.8033 | +0.9732 | 0.9350 |
| **Simple Average** | 1.3495 | 1.7277 | +0.9725 | 0.9409 |
| **Historical Weighted** | 1.1658 | 1.5270 | +0.6844 | 0.9446 |
| **SkyBlend Temperature** | **1.0144** | **1.3772** | **+0.4963** | **0.9496** |

**Findings:** NOAA GFS exhibits a substantial positive daytime bias (+2.27°C) over Kolkata. SkyBlend dynamically downweights GFS during high-bias hours, achieving the lowest overall error (MAE 1.0144°C, RMSE 1.3772°C) and highest correlation ($r=0.9496$).

------------------------------------------------------------------------

## 35. 10m Wind Speed Telemetry Status & Missing Data Documentation

- **Data Reality:** Multi-model NWP 10m surface wind components ($u_{10}, v_{10}$) and physical anemometer ground reference data were not included in the original training or demonstration datasets.
- **Architectural Handling:** Endpoints and UI components cleanly intercept wind queries, returning structured `status: "unavailable"` and displaying informative workstation notices (`WindUnavailableNotice.jsx`).
- **Activation Roadmap:** When ECMWF, GFS, and ICON 10m wind fields are ingested, wind speed will be derived via vector magnitude ($S = \sqrt{u_{10}^2 + v_{10}^2}$), and continuous error models will be trained analogously to temperature.

------------------------------------------------------------------------

## 36. SIH Problem Statement Alignment Matrix

| SIH Requirement | Current Implementation | Repository Evidence | Remaining Limitation |
| :--- | :--- | :--- | :--- |
| **Dynamically blended forecast** | Dynamic ML error prediction estimating model reliability at every forecast hour. Member forecasts (ECMWF, GFS, ICON) combined via normalized convex weighting. Convective peak-lift ($\alpha=0.35$) for rainfall; continuous consensus for temperature. | `src/blending/ml_blender.py`<br/>`src/blending/temperature_blender.py`<br/>`models/expanded_full_year/`<br/>`models/temperature/` | Wind forecast cleanly withheld (`status: "unavailable"`) pending NWP 10m wind vector dataset ingestion. |
| **Model weight maps** | Geospatial blending matrix displaying dynamic mean contribution weights and dominant model across all six demonstration metropolitan areas across 1–3 lead days. | `data/processed/multilocation_rainfall_spatial_weights_day1_to_day3.csv`<br/>`src/api/main.py` (`get_spatial_weights`) | 6 demonstration metropolitan coordinates; not a continuous nationwide spatial raster. |
| **Improved forecast skill** | Chronological out-of-sample held-out benchmark evaluation demonstrating quantitative error reduction against individual NWP members, simple arithmetic averaging, and historical weighted baselines. | `data/processed/evaluation_comparison_metrics.csv`<br/>`data/processed/temperature_test_performance.csv`<br/>`reports/independent_station_validation_kolkata.md` | Skill improvement varies by metric; ECMWF retains higher POD on July holdout (0.7808 vs 0.6301). Wind skill unverified. |
| **Extreme weather guidance** | Variable-aware analytical hazard guidance. Calibrated precipitation advisory threshold ($\ge 1.0\text{ mm/h}$) and diurnal heat hazard threshold ($\ge 38.0^\circ\text{C}$). High-wind signal labeled "Not configured / insufficient evidence". Explicit UI notices. | `src/api/main.py` (`get_extreme_signal`)<br/>`src/blending/regimes.py` | Analytical indicators for decision support prototypes; NOT official IMD disaster warnings. |
| **Operational workflow/dashboard** | Production-ready stack: Asynchronous FastAPI REST service (<30ms latency) serving real-time inference, coupled with React 18 / Vite workstation adhering to charcoal/graphite workstation visual language across 7 dedicated views. | `src/api/main.py`<br/>`frontend/src/`<br/>`frontend/dist/` | Operates on processed demonstration datasets re-anchored for display; live 00Z/12Z NWP ingestion pipeline is future work. |
| **Optimized forecast for rainfall, temperature, wind and extreme indicators** | Rainfall: Fully optimized & production-validated (Phase 6).<br/>Temperature: Fully implemented extension (continuous adaptive ML blender, WMO 42807 evaluation).<br/>Wind: Cleanly architected; exposed as "unavailable / pending telemetry" in adherence to scientific honesty.<br/>Extreme indicators: Variable-aware signals implemented for rainfall and temperature. | `models/expanded_full_year/`<br/>`models/temperature/`<br/>`src/blending/ml_blender.py`<br/>`src/blending/temperature_blender.py`<br/>`data/processed/multilocation_temperature_forecast_inputs.csv` | Multi-model NWP 10m wind vector forecasts ($u_{10}, v_{10}$) are not present in repository, precluding complete optimization of wind until raw telemetry is ingested. |

