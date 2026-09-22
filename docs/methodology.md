# Rainfall Blending & Verification Methodology

## Overview
This document outlines the scientific and mathematical methodology for rainfall forecast blending under SIH Problem Statement PS81.

## 1. Skill Score Weighting & Inverse Variance
Weights for each NWP model ($m \in \{1, \dots, M\}$) at grid point $(x, y)$ and lead time $t$ are dynamically assigned based on historical forecast error:

$$w_m(x, y, t) = \frac{\frac{1}{\text{MSE}_m(x, y, t)}}{\sum_{k=1}^M \frac{1}{\text{MSE}_k(x, y, t)}}$$

Where $\text{MSE}_m$ represents the historical mean squared error of model $m$ over a rolling window.

## 2. Quantile Mapping Bias Correction
To handle extreme rainfall events and non-Gaussian precipitation distributions, quantile mapping aligns cumulative distribution functions (CDFs) of raw NWP forecasts ($F$) with observational distributions ($O$):

$$\hat{P} = F_O^{-1} \left( F_M(P) \right)$$

## 3. Weather Regime Clustering
Monsoon precipitation in India exhibits strong regime-dependence (e.g., active monsoon phase, break phase, low-pressure system, depression). Unsupervised clustering (K-Means / GMM) on large-scale atmospheric fields identifies active regimes to dynamically select optimal regime-specific blending weights.

## 4. Verification Framework
Forecast accuracy is evaluated against observations using standard meteorological metrics:
- **Root Mean Square Error (RMSE)**
- **Mean Absolute Error (MAE)**
- **Equitable Threat Score (ETS)** / **Critical Success Index (CSI)** for rainfall intensity thresholds ($>2.5\text{ mm}$, $>15.6\text{ mm}$, $>64.5\text{ mm}$, $>115.5\text{ mm}$).
- **Probability of Detection (POD)** & **False Alarm Ratio (FAR)**.
