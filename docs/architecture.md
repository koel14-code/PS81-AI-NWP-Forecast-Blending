# System Architecture Specification

## Problem Statement PS81: Hybrid AI–NWP Multi-Model Forecast Blending System

### High-Level Architecture Overview

The system processes gridded forecasts from multiple Numerical Weather Prediction (NWP) models alongside satellite/ground-based rainfall observations to produce dynamically optimized consensus forecasts.

```text
+-------------------+      +-------------------+      +-------------------+
|  NWP Model: GFS   |      |  NWP Model: NCUM  |      | NWP Model: ECMWF  |
+---------+---------+      +---------+---------+      +---------+---------+
          |                          |                          |
          +--------------------------+--------------------------+
                                     |
                                     v
                        +-------------------------+
                        |   Data Ingestion &      |
                        |   Spatial Alignment     | (src/data/)
                        +------------+------------+
                                     |
                                     v
                        +-------------------------+
                        | Feature Engineering &   |
                        | Weather Regime Mining   | (src/features/)
                        +------------+------------+
                                     |
                                     v
                        +-------------------------+
                        | AI/ML Blending Engine   | (src/blending/ & src/models/)
                        +------------+------------+
                                     |
                                     v
                        +-------------------------+
                        |  Verification Metrics   | (src/evaluation/)
                        |  & Dashboard Display    | (dashboard/)
                        +-------------------------+
```

### Modular System Components

1. **Ingestion & Alignment Engine (`src/data/`)**:
   - Ingests raw NetCDF / GRIB2 files from multiple sources.
   - Interpolates all grids onto a standardized spatial grid (0.25° latitude/longitude).
   - Aligns temporal lead times (24h, 48h, 72h, 120h).

2. **Feature Engineering Module (`src/features/`)**:
   - Computes rolling spatial error indices (RMSE, Bias) for each input model.
   - Encodes seasonal factors, geographic properties (elevation, latitude/longitude), and monsoon regime clusters.

3. **Blending & Machine Learning Engine (`src/blending/` & `src/models/`)**:
   - Baseline statistical blenders (Inverse Variance, Equal Weighting).
   - ML Blenders (Gradient Boosting, Quantile Mapping, Deep Learning spatial-temporal blenders).

4. **Verification & Skill Score Module (`src/evaluation/`)**:
   - Continuous error metrics (RMSE, MAE, Bias).
   - Categorical rainfall metrics (POD, FAR, ETS, HKD across light, moderate, heavy rainfall thresholds).
