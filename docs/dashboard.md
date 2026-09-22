# SkyBlend AI — Premium Operational Weather Intelligence Dashboard

## Overview

**SkyBlend AI** (SIH Problem Statement PS81) is a judge-friendly, high-end operational weather intelligence dashboard demonstrating dynamic multi-model forecast blending. Designed with a dark, climate-tech AI SaaS aesthetic (#070B14 deep navy), SkyBlend AI evaluates context-dependent historical skill across **ECMWF IFS**, **NOAA GFS**, and **DWD ICON**, dynamically weighting each forecast source based on location, forecast horizon, and atmospheric features.

---

## How to Run

Execute the Streamlit application from the project root directory:

```bash
streamlit run dashboard/app.py
```

*Note: Safe path resolution is handled using `pathlib`. You do not need to manually edit working directories.*

---

## Redesigned UI Architecture & Navigation Tabs

1. **Overview**
   - High-impact hero card ("Forecasting doesn't have to trust one model").
   - 5-stage visual system architecture pipeline strip.
   - 4 dark hero KPI cards (06 Locations, 03 NWP Sources, 36,288 Records, 28-day Historical Scope).
   - Key Result Card highlighting **0.3147 mm/h MAE** vs ECMWF IFS (0.3711 mm/h) and Simple Average (0.3964 mm/h).
   - "Why Adaptive Blending?" 3-column breakdown (Location, Lead Time, Context).

2. **Forecast Intelligence**
   - Location selector (Kolkata, Delhi, Mumbai, Chennai, Guwahati, Bengaluru).
   - Lead horizon selector (Day 1: 1–24h, Day 2: 25–48h, Day 3: 49–72h).
   - Dark Plotly time-series chart ("Forecast Signal") displaying ECMWF (cyan), GFS (purple), ICON (green), ERA5 (dashed white), and SkyBlend AI (bright crimson highlight).
   - Context explanation card: "What SkyBlend is doing".

3. **Adaptive Weights**
   - Subtitle: "Who gets trusted — and by how much?"
   - 3 dynamic cards displaying mean adaptive model contributions (ECMWF, GFS, ICON).
   - Interactive stacked-area time-series chart ("How trust changes over time").
   - Weight normalization note: Sum = 1.0 at every forecast time step.

4. **Spatial Intelligence**
   - India Map centerpiece rendered with a dark climate-tech map theme (`#0D1322` background, `#111827` landmass, glowing markers).
   - Hover popups reporting exact model weight percentages and highest adaptive contribution model per city.
   - Scope disclaimer: *"Demonstration scope: Six selected Indian locations • not a nationwide validation."*
   - Summary data table.

5. **Verification**
   - Complete verification table displaying MAE, RMSE, Bias, and Pearson $r$.
   - Side-by-side dark Plotly bar charts comparing MAE and RMSE across all 6 approaches.
   - Held-Out Test Result card emphasizing 0.3147 mm/h MAE achievement on July 24–28, 2024 test period.

6. **Extreme Weather**
   - Status header badge (`BELOW PROJECT ANALYTICAL THRESHOLD` vs `HEAVY-RAINFALL ANALYTICAL SIGNAL`).
   - Metric cards: Blended rainfall rate, project analytical threshold ($1.00\text{ mm/h}$), and signal status.
   - Plotly chart plotting blended rainfall vs ERA5 reference against the $1.0\text{ mm/h}$ threshold line.
   - Prominent disclaimer: *"Notice: Project analytical threshold ($\ge 1.0\text{ mm/h}$) — not an official IMD warning threshold."*

7. **Methodology**
   - Subtitle: "How SkyBlend thinks".
   - 7-stage visual pipeline cards (Forecast Sources $\rightarrow$ Harmonization $\rightarrow$ Historical Skill $\rightarrow$ Context Features $\rightarrow$ Adaptive AI Weighting $\rightarrow$ Blended Forecast $\rightarrow$ Verification).
   - Mathematical blending formulation cards ($F_{\text{blended}} = \sum w_m F_m$, $\sum w_m = 1.0$).
   - Dedicated "Validation Scope & Scientific Limitations" card detailing scope parameters and reanalysis reference context.

---

## Data Sources & Artifact Dependencies

All values displayed in the dashboard are dynamically loaded from generated project artifacts under `data/processed/`. No metrics, predictions, or weights are hardcoded.

| Artifact File | Description |
| :--- | :--- |
| `data/processed/model_performance_test.csv` | Chronological test-set metrics (MAE, RMSE, Bias, Pearson $r$). |
| `data/processed/multilocation_adaptive_weights_test.csv` | Time-series test set predictions and model weights ($w_{\text{ECMWF}}, w_{\text{GFS}}, w_{\text{ICON}}$). |
| `data/processed/model_weight_map_summary.csv` | Aggregated spatial weight summaries per location and lead day. |
| `data/processed/multilocation_rainfall_training_dataset.csv` | Full 4-week raw dataset across 6 locations (July 1–28, 2024 UTC). |
| `data/processed/multilocation_rainfall_ml_features.csv` | ML-ready feature dataset including 100% operational leakage-free rolling historical MAE. |
