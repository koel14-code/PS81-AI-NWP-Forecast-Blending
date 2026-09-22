# SkyBlend AI — React Frontend

## Overview

**SkyBlend AI** (SIH Problem Statement PS81) React + Vite operational frontend. Connects to the Python FastAPI backend (`src/api/main.py`) to deliver a dark, climate-tech AI SaaS weather intelligence platform.

---

## Quick Start

### 1. Start FastAPI Backend

From project root:

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

FastAPI Swagger Documentation: `http://localhost:8000/docs`

### 2. Start React Frontend

From `frontend/` directory:

```bash
npm install
npm run dev
```

Frontend application will be accessible at: `http://localhost:5173`

### 3. Production Build

To build the static production bundle:

```bash
npm run build
```

---

## Architecture & Page Map

- `src/pages/Overview.jsx` — System Landing Page & Key Result KPI Cards
- `src/pages/ForecastIntelligence.jsx` — Interactive Multi-Model Precipitation Trace
- `src/pages/AdaptiveWeights.jsx` — Dynamic Weight Stacked-Area Charts
- `src/pages/SpatialIntelligence.jsx` — Leaflet Spatial Intelligence Map of India
- `src/pages/Verification.jsx` — Test-Set Verification Table & Side-by-Side MAE/RMSE Bar Charts
- `src/pages/ExtremeWeather.jsx` — Analytical Heavy-Rainfall Signal Monitor
- `src/pages/Methodology.jsx` — 7-Stage Pipeline Diagram & Mathematical Formulation
