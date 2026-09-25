# Independent Ground-Station Validation Report: Kolkata / Alipore (WMO 42807) — 2m Temperature
**Project:** SkyBlend AI — Multi-Variable Forecast Blending (Temperature Module)  
**Evaluation Scope:** Out-of-sample ground-station verification against physical thermometer observations at Kolkata Alipore (WMO 42807).  
**Period:** Pre-Monsoon Benchmark Test Split (`2024-04-07T01:00:00Z` to `2024-05-31T23:00:00Z`) — 3,957 matched instances.  

---

## 1. Overview & Methodology

Temperature is a continuous thermal state variable that follows diurnally forced thermodynamic cycles. Unlike rainfall, temperature forecasts do not exhibit zero-inflation or localized convective intermittency; therefore, SkyBlend's temperature engine utilizes **continuous inverse-error adaptive weighting** without peak-lift thresholding.

### Model Features (11 Predictors):
- Forecast lead time: `lead_hours`, `lead_day`
- Temporal cycle: `hour` (diurnal phase), `month`, `day_of_year`
- Geographic position: `latitude`, `longitude`
- Member forecast: `model_temp`
- Ensemble consensus & spread: `ensemble_mean`, `ensemble_std`, `ensemble_range`

---

## 2. Empirical Performance Comparison (Test Split)

| Forecast Approach | MAE (°C) ↓ | RMSE (°C) ↓ | Bias (°C) | Pearson $r$ ↑ |
| :--- | :---: | :---: | :---: | :---: |
| **ECMWF IFS** | 1.1180 | 1.5792 | -0.3252 | 0.9264 |
| **NOAA GFS** | 2.5064 | 3.0854 | +2.2694 | 0.8964 |
| **DWD ICON** | 1.3812 | 1.8033 | +0.9732 | 0.9350 |
| **Simple Average** | 1.3495 | 1.7277 | +0.9725 | 0.9409 |
| **Historical Weighted** | 1.1658 | 1.5270 | +0.6844 | 0.9446 |
| **SkyBlend AI (Temperature)** | **1.0144** | **1.3772** | **+0.4963** | **0.9496** |

---

## 3. Key Findings

1. **Systematic Bias Mitigation:** NOAA GFS exhibits a pronounced warm bias over the lower Gangetic delta (+2.27°C). SkyBlend dynamically downweights GFS in high-solar noon conditions, shrinking the overall ensemble bias.
2. **Error Reduction:** SkyBlend Temperature achieves an MAE of **1.0144°C**, outperforming ECMWF IFS (1.1180°C), DWD ICON (1.3812°C), and Simple Average (1.3495°C).
3. **Correlation:** Blending achieves the highest linear correlation with observed thermometer readings (**$r = 0.9496$**).
