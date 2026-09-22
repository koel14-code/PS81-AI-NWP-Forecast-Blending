# Hybrid AI–NWP Multi-Model Forecast Blending System (SIH Problem Statement PS81)

## Overview
This repository contains the architecture and implementation for the **Hybrid AI–NWP Multi-Model Forecast Blending System**, designed to address SIH Problem Statement PS81.

The primary goal of this project is to develop an intelligent, data-driven weather forecast blending engine that dynamically combines multiple Numerical Weather Prediction (NWP) model outputs (e.g., GFS, NCUM, ECMWF, IMD GFS) with observational datasets. The blending weights and corrections adapt based on historical forecast skill, geographic region, forecast lead time, season, and meteorological weather regime.

For the initial Minimum Viable Product (MVP), the system focuses specifically on **rainfall forecast blending** over target regions. Additional parameters such as temperature, wind vectors, and extreme weather indicators will be integrated in subsequent phases.

---

## Key Features & Goals (MVP Scope)
- **Multi-Source NWP Ingestion**: Flexible data pipelines for ingesting multi-model gridded rainfall forecasts (NetCDF/GRIB2/CSV).
- **Observational Alignment**: Grid alignment and spatial-temporal matching with ground truth / satellite rainfall data (e.g., IMD / GPM / TRMM observations).
- **Dynamic Skill Assessment**: Evaluation of regional, seasonal, and lead-time-dependent error metrics (RMSE, Bias, POD, FAR, ETS) for each individual NWP model.
- **AI/ML Blending Algorithms**: Spatial and regime-aware machine learning models (e.g., Quantile Mapping, Weighted Ensembles, Gradient Boosted Regressors, Neural Blenders) to generate optimal consensus forecasts.
- **Extensible Architecture**: Modular codebase allowing separate team members to independently develop data processors, feature extractors, blending models, and evaluation suites.

---

## Directory Structure

```text
PS81-AI-NWP-Forecast-Blending/
├── README.md
├── .gitignore
├── requirements.txt
├── .env.example
│
├── data/
│   ├── raw/                  # Unprocessed NWP model outputs and observational data (git-ignored)
│   ├── processed/            # Regridded, aligned, and cleaned datasets ready for modeling (git-ignored)
│   └── README.md             # Documentation on data schemas and sourcing guidelines
│
├── notebooks/                # Exploratory Data Analysis (EDA) and prototyping notebooks
│   └── .gitkeep
│
├── docs/                     # Project documentation and architectural diagrams
│   └── README.md
│
├── tests/                    # Unit tests and integration tests
│   ├── __init__.py
│   └── .gitkeep
│
└── src/                      # Source code package for the blending system
    ├── __init__.py
    ├── config.py             # Central configuration management (paths, model settings, parameters)
    ├── data/                 # Ingestion, regridding, spatial matching, and loading modules
    │   ├── __init__.py
    │   └── .gitkeep
    ├── features/             # Feature engineering (lead time encoding, weather regimes, skill indices)
    │   ├── __init__.py
    │   └── .gitkeep
    ├── models/               # AI/ML blending models (Ensemble, Regressors, Neural networks)
    │   ├── __init__.py
    │   └── .gitkeep
    ├── evaluation/           # Verification metrics (RMSE, Threat Score, Bias, Skill Score)
    │   ├── __init__.py
    │   └── .gitkeep
    └── utils/                # Helper utilities (logging, spatial transforms, IO helpers)
        ├── __init__.py
        └── .gitkeep
```

---

## Setup & Environment

### Prerequisites
- Python 3.9+ (Python 3.10 recommended)
- `pip` and `virtualenv` / `conda`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/koel14-code/PS81-AI-NWP-Forecast-Blending.git
   cd PS81-AI-NWP-Forecast-Blending
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv (Linux/macOS)
   python -m venv venv
   source venv/bin/activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install project dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to configure local data paths and settings
   ```

---

## Collaboration & Git Workflow

To maintain code quality and support parallel development across team members:

1. **Branching Strategy**:
   - `main`: Stable, production-ready release branch.
   - `dev`: Active integration branch.
   - Feature branches: `feature/<feature-name>` (e.g., `feature/gfs-ingestion-pipeline`, `feature/weighted-ensemble-model`).
   - Bug fix branches: `fix/<issue-description>`.

2. **Pull Requests**:
   - All code contributions must be made via Pull Requests targeting `dev` or `main`.
   - Ensure code passes existing unit tests (`pytest`) before creating a PR.

3. **Modular Division**:
   - **Data Team**: Works under `src/data/` (ingestion, spatial interpolation, NetCDF parsing).
   - **Feature Team**: Works under `src/features/` (weather regime clustering, skill index creation).
   - **Modeling Team**: Works under `src/models/` (statistical & ML blending architectures).
   - **Evaluation Team**: Works under `src/evaluation/` (meteorological verification metrics).

---

## License & Attribution
Developed for Smart India Hackathon (SIH) - Problem Statement PS81.
