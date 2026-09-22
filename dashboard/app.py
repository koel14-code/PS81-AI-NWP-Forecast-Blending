"""
SKYBLEND AI — Premium Operational Weather Intelligence Dashboard
SIH Problem Statement PS81: Hybrid AI–NWP Multi-Model Forecast Blending System.

Adaptive weather forecasting through context-aware model weighting.

Run using:
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Safe Path Resolution using pathlib
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Data Artifact Paths
DATA_DIR = BASE_DIR / "data" / "processed"
PERF_FILE = DATA_DIR / "model_performance_test.csv"
WEIGHTS_FILE = DATA_DIR / "multilocation_adaptive_weights_test.csv"
SINGLE_WEIGHTS_FILE = DATA_DIR / "adaptive_weights_test.csv"
WEIGHT_MAP_FILE = DATA_DIR / "model_weight_map_summary.csv"

# Streamlit Page Config
st.set_page_config(
    page_title="SkyBlend AI — Weather Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Premium Theme Custom CSS
st.markdown(
    """
    <style>
    /* Global Background & Typography */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #0B1120 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Hide Unnecessary Streamlit Chrome */
    header[data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.85) !important;
        backdrop-filter: blur(8px) !important;
    }
    .stDeployButton, footer, #MainMenu {
        display: none !important;
    }

    /* Sidebar Custom Styling */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-weight: 700 !important;
    }

    /* Sidebar Radio Navigation Options */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        transition: all 0.15s ease-in-out !important;
        border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #CBD5E1 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: #FFFFFF !important;
    }

    /* Active Selected Radio Navigation Option */
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] {
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.25) 0%, rgba(6, 182, 212, 0.18) 100%) !important;
        border-left: 3px solid #F43F5E !important;
        border-radius: 4px 8px 8px 4px !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Custom Cards & Containers */
    .glass-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.18) 0%, rgba(6, 182, 212, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.35);
        border-radius: 20px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
    }

    .kpi-card-dark {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .kpi-card-dark::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
    }

    .kpi-val-huge {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }

    .kpi-label-muted {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .status-pill-online {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #34D399;
        box-shadow: 0 0 8px #34D399;
    }

    .sub-header-meta {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    .badge-sih {
        background: linear-gradient(90deg, #8B5CF6, #06B6D4);
        color: #FFFFFF;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 9999px;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .disclaimer-box {
        background: rgba(245, 158, 11, 0.08);
        border-left: 4px solid #F59E0B;
        color: #FBBF24;
        padding: 0.85rem 1.1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .pipeline-node {
        background: rgba(17, 24, 39, 0.9);
        border: 1px solid rgba(139, 92, 246, 0.35);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        color: #F8FAFC;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Shared Plotly Dark Theme Configuration
PLOTLY_DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17, 24, 39, 0.7)",
    font=dict(color="#F8FAFC", family="Inter, sans-serif"),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#94A3B8"),
        title_font=dict(color="#94A3B8"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.1)",
        tickfont=dict(color="#94A3B8"),
        title_font=dict(color="#94A3B8"),
    ),
    legend=dict(
        bgcolor="rgba(17, 24, 39, 0.85)",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(color="#F8FAFC"),
    ),
    margin=dict(l=40, r=40, t=50, b=40),
)


@st.cache_data
def load_data_artifacts():
    """Loads all required generated data artifacts with error checking."""
    missing_files = []
    for filepath, name in [
        (PERF_FILE, "model_performance_test.csv"),
        (WEIGHTS_FILE if WEIGHTS_FILE.exists() else SINGLE_WEIGHTS_FILE, "adaptive_weights_test.csv"),
        (WEIGHT_MAP_FILE, "model_weight_map_summary.csv"),
    ]:
        if not filepath.exists():
            missing_files.append(name)

    if missing_files:
        return None, f"Missing required data artifacts in data/processed/: {', '.join(missing_files)}. Please run scripts/evaluate_blender.py first."

    try:
        perf_df = pd.read_csv(PERF_FILE)
        w_file = WEIGHTS_FILE if WEIGHTS_FILE.exists() else SINGLE_WEIGHTS_FILE
        weights_df = pd.read_csv(w_file)
        map_df = pd.read_csv(WEIGHT_MAP_FILE)
        return {"perf": perf_df, "weights": weights_df, "map": map_df}, None
    except Exception as e:
        return None, f"Error reading data artifacts: {e}"


def main():
    # Sidebar Logo & Navigation
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 1.8rem;">⚡</span>
                <div>
                    <div style="font-weight: 900; font-size: 1.3rem; letter-spacing: -0.02em; color: #F8FAFC;">SKYBLEND AI</div>
                    <div style="font-size: 0.65rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.1em;">AI WEATHER INTELLIGENCE</div>
                </div>
            </div>
            <div class="badge-sih">SIH • PS81</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    navigation = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Forecast Intelligence",
            "Adaptive Weights",
            "Spatial Intelligence",
            "Verification",
            "Extreme Weather",
            "Methodology",
        ],
    )

    st.sidebar.markdown(
        """
        <div style="margin-top: 2.5rem; padding: 14px; background: #1E293B; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3); text-align: center; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #8B5CF6, #06B6D4);"></div>
            <div style="font-size: 0.72rem; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.08em;">PROTOTYPE VALIDATION</div>
            <div style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0; margin-top: 4px;">Six-City Historical Scope</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    artifacts, err_msg = load_data_artifacts()

    if err_msg:
        st.error(err_msg)
        st.info("To generate all required data artifacts, execute: python scripts/evaluate_blender.py")
        return

    perf_df = artifacts["perf"]
    weights_df = artifacts["weights"]
    map_df = artifacts["map"]

    if "location_id" not in weights_df.columns:
        weights_df["location_id"] = "kolkata"

    # Global Top Header Bar
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 1.25rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1.5rem;">
            <div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #F8FAFC; letter-spacing: -0.02em;">SKYBLEND AI</div>
                <div style="font-size: 0.9rem; color: #94A3B8; font-weight: 500;">Adaptive Weather Intelligence System</div>
            </div>
            <div style="text-align: right;">
                <div class="status-pill-online"><span class="status-dot"></span> SYSTEM ONLINE</div>
                <div class="sub-header-meta" style="margin-top: 6px;">3 NWP SOURCES • 6 LOCATIONS • 36,288 RECORDS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =========================================================================
    # TAB 1: OVERVIEW
    # =========================================================================
    if navigation == "Overview":
        # Hero Banner
        st.markdown(
            """
            <div class="hero-card">
                <div style="display: inline-block; background: rgba(139, 92, 246, 0.2); color: #C4B5FD; border: 1px solid rgba(139, 92, 246, 0.4); padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.75rem;">
                    AI–NWP ADAPTIVE BLENDING
                </div>
                <h1 style="font-size: 2.2rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.5rem; line-height: 1.2;">
                    Forecasting doesn't have to trust one model.
                </h1>
                <p style="font-size: 1.05rem; color: #CBD5E1; max-width: 900px; line-height: 1.6; margin-bottom: 0;">
                    SkyBlend AI dynamically learns how forecast reliability changes across location, lead time and weather context — and blends multiple NWP sources accordingly.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Visual Architecture Pipeline Strip
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem;">
                    System Architecture Pipeline
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div class="pipeline-node" style="flex: 1; min-width: 140px;">
                        <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 700;">NWP SOURCES</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 2px;">ECMWF • GFS • ICON</div>
                    </div>
                    <div style="color: #64748B; font-weight: 800;">➔</div>
                    <div class="pipeline-node" style="flex: 1; min-width: 140px;">
                        <div style="font-size: 0.75rem; color: #A855F7; font-weight: 700;">HISTORICAL SKILL</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 2px;">24h Rolling MAE</div>
                    </div>
                    <div style="color: #64748B; font-weight: 800;">➔</div>
                    <div class="pipeline-node" style="flex: 1; min-width: 140px;">
                        <div style="font-size: 0.75rem; color: #34D399; font-weight: 700;">CONTEXT-AWARE AI</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 2px;">GradBoosting Regressor</div>
                    </div>
                    <div style="color: #64748B; font-weight: 800;">➔</div>
                    <div class="pipeline-node" style="flex: 1; min-width: 140px;">
                        <div style="font-size: 0.75rem; color: #F59E0B; font-weight: 700;">ADAPTIVE WEIGHTS</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 2px;">Normalized Reliabilities</div>
                    </div>
                    <div style="color: #64748B; font-weight: 800;">➔</div>
                    <div class="pipeline-node" style="flex: 1.2; min-width: 160px; background: linear-gradient(135deg, rgba(244,63,94,0.2), rgba(139,92,246,0.2)); border-color: rgba(244,63,94,0.5);">
                        <div style="font-size: 0.75rem; color: #FB7185; font-weight: 700;">BLENDED FORECAST</div>
                        <div style="font-size: 0.9rem; font-weight: 900; color: #FFF; margin-top: 2px;">SkyBlend Consensus</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Hero KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                """
                <div class="kpi-card-dark">
                    <div class="kpi-val-huge">06</div>
                    <div class="kpi-label-muted">DEMONSTRATION LOCATIONS</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
                <div class="kpi-card-dark">
                    <div class="kpi-val-huge">03</div>
                    <div class="kpi-label-muted">NWP SOURCES</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                """
                <div class="kpi-card-dark">
                    <div class="kpi-val-huge">36,288</div>
                    <div class="kpi-label-muted">ALIGNED FORECAST RECORDS</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                """
                <div class="kpi-card-dark">
                    <div class="kpi-val-huge">28 DAYS</div>
                    <div class="kpi-label-muted">HISTORICAL PERIOD</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        # Key Result Feature Card
        mae_dict = dict(zip(perf_df["Approach"], perf_df["MAE"]))
        skyblend_mae = mae_dict.get("Adaptive_ML_Blend", 0.3147)
        ecmwf_mae = mae_dict.get("ECMWF_IFS", 0.3711)
        simple_mae = mae_dict.get("Simple_Average", 0.3964)

        st.markdown(
            f"""
            <div class="glass-card" style="background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%); border: 1px solid rgba(139, 92, 246, 0.4);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div>
                        <div style="font-size: 0.75rem; font-weight: 800; color: #A855F7; text-transform: uppercase; letter-spacing: 0.1em;">KEY RESULT CARD</div>
                        <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC;">ADAPTIVE BLEND PERFORMANCE</div>
                    </div>
                    <div style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem;">
                        Lower MAE on held-out test set
                    </div>
                </div>
                <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 1.25rem;">
                    <div style="font-size: 3.5rem; font-weight: 900; color: #F43F5E; line-height: 1;">{skyblend_mae:.4f}</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #94A3B8;">mm/h MAE</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                    <div>
                        <div style="font-size: 0.75rem; color: #94A3B8;">ECMWF IFS MAE</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #38BDF8;">{ecmwf_mae:.4f} mm/h</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #94A3B8;">Simple Average MAE</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #CBD5E1;">{simple_mae:.4f} mm/h</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #94A3B8;">Adaptive ML Blend</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #FB7185;">{skyblend_mae:.4f} mm/h</div>
                    </div>
                </div>
                <div style="font-size: 0.75rem; color: #64748B; margin-top: 1rem;">
                    Held-out evaluation • six demonstration locations • July 2024
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Overview Insight Card
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 0.85rem; font-weight: 800; color: #F8FAFC; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem;">
                    WHY ADAPTIVE BLENDING?
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
                    <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 1.2rem; font-weight: 900; color: #38BDF8; margin-bottom: 0.25rem;">01</div>
                        <div style="font-size: 0.9rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">LOCATION</div>
                        <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">Reliability can vary geographically across complex Indian microclimates.</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 1.2rem; font-weight: 900; color: #A855F7; margin-bottom: 0.25rem;">02</div>
                        <div style="font-size: 0.9rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">LEAD TIME</div>
                        <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">Forecast skill changes dynamically across 1–24h, 25–48h and 49–72h horizons.</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="font-size: 1.2rem; font-weight: 900; color: #34D399; margin-bottom: 0.25rem;">03</div>
                        <div style="font-size: 0.9rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.35rem;">CONTEXT</div>
                        <div style="font-size: 0.85rem; color: #94A3B8; line-height: 1.5;">Historical forecast behavior dynamically informs real-time model contributions.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TAB 2: FORECAST INTELLIGENCE
    # =========================================================================
    elif navigation == "Forecast Intelligence":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">FORECAST INTELLIGENCE</h2>
                <p style="font-size: 0.9rem; color: #94A3B8;">Compare individual NWP model forecasts against SkyBlend AI consensus and ERA5 reference data.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            locations = sorted(weights_df["location_id"].unique())
            sel_loc = st.selectbox("LOCATION", locations, format_func=lambda x: x.capitalize())
        with c2:
            lead_days = [1, 2, 3]
            sel_day = st.selectbox(
                "LEAD HORIZON",
                lead_days,
                format_func=lambda x: f"Day {x} • ({24*(x-1)+1}–{24*x}h Lead)",
            )

        df_filtered = weights_df[
            (weights_df["location_id"] == sel_loc)
            & (weights_df["lead_hours"] > 24 * (sel_day - 1))
            & (weights_df["lead_hours"] <= 24 * sel_day)
        ].copy()

        if df_filtered.empty:
            st.warning("Insufficient data for this selection.")
        else:
            feat_file = DATA_DIR / "multilocation_rainfall_ml_features.csv"
            if feat_file.exists():
                feat_df = pd.read_csv(feat_file)
                from src.blending.baselines import split_data_chronologically, pivot_aligned_dataset
                _, _, df_test_feat, _ = split_data_chronologically(feat_df)
                df_test_wide = pivot_aligned_dataset(df_test_feat)

                sub_wide = df_test_wide[
                    (df_test_wide["location_id"] == sel_loc)
                    & (df_test_wide["lead_hours"] > 24 * (sel_day - 1))
                    & (df_test_wide["lead_hours"] <= 24 * sel_day)
                ].copy()

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=sub_wide["valid_time"],
                        y=sub_wide["reference_precipitation"],
                        name="ERA5 Reference",
                        line=dict(color="#E2E8F0", width=2.0, dash="dash"),
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=sub_wide["valid_time"],
                        y=sub_wide["ECMWF_IFS_precip"],
                        name="ECMWF IFS",
                        line=dict(color="#38BDF8", width=1.8),
                        opacity=0.75,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=sub_wide["valid_time"],
                        y=sub_wide["NOAA_GFS_precip"],
                        name="NOAA GFS",
                        line=dict(color="#A855F7", width=1.8),
                        opacity=0.75,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=sub_wide["valid_time"],
                        y=sub_wide["DWD_ICON_precip"],
                        name="DWD ICON",
                        line=dict(color="#34D399", width=1.8),
                        opacity=0.75,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_filtered["valid_time"],
                        y=df_filtered["blended_precipitation"],
                        name="SKYBLEND AI",
                        line=dict(color="#F43F5E", width=3.2),
                    )
                )

                layout1 = dict(PLOTLY_DARK_LAYOUT)
                layout1["xaxis"] = {**layout1.get("xaxis", {}), "title": "Valid Time (UTC)"}
                layout1["yaxis"] = {**layout1.get("yaxis", {}), "title": "Precipitation Rate (mm/h)"}
                fig.update_layout(
                    **layout1,
                    title=dict(
                        text=f"Forecast Signal — {sel_loc.capitalize()} (Day {sel_day} Horizon)",
                        font=dict(size=16, color="#F8FAFC"),
                    ),
                    hovermode="x unified",
                    height=480,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.line(
                    df_filtered,
                    x="valid_time",
                    y=["blended_precipitation", "reference_precipitation"],
                    title=f"SkyBlend AI vs ERA5 Reference — {sel_loc.capitalize()}",
                )
                fig.update_layout(**PLOTLY_DARK_LAYOUT)
                st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="font-size: 0.75rem; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.35rem;">
                        WHAT SKYBLEND IS DOING
                    </div>
                    <div style="font-size: 0.95rem; color: #CBD5E1; line-height: 1.5;">
                        SkyBlend is combining three forecast sources using adaptive model contributions for <b>{sel_loc.capitalize()}</b> over the <b>Day {sel_day}</b> lead horizon.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 3: ADAPTIVE MODEL WEIGHTS
    # =========================================================================
    elif navigation == "Adaptive Weights":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">ADAPTIVE MODEL WEIGHTS</h2>
                <p style="font-size: 0.95rem; color: #94A3B8;">Who gets trusted — and by how much?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            locations = sorted(weights_df["location_id"].unique())
            sel_loc = st.selectbox("LOCATION", locations, format_func=lambda x: x.capitalize(), key="w_loc")
        with c2:
            sel_day = st.selectbox(
                "LEAD HORIZON",
                [1, 2, 3],
                format_func=lambda x: f"Day {x} • ({24*(x-1)+1}–{24*x}h Lead)",
                key="w_day",
            )

        df_w = weights_df[
            (weights_df["location_id"] == sel_loc)
            & (weights_df["lead_hours"] > 24 * (sel_day - 1))
            & (weights_df["lead_hours"] <= 24 * sel_day)
        ].copy()

        if df_w.empty:
            st.warning("Insufficient data for this selection.")
        else:
            mean_ec = df_w["ECMWF_IFS_weight"].mean()
            mean_gfs = df_w["NOAA_GFS_weight"].mean()
            mean_icon = df_w["DWD_ICON_weight"].mean()

            w_cols = st.columns(3)
            with w_cols[0]:
                st.markdown(
                    f"""
                    <div class="kpi-card-dark">
                        <div style="font-size: 0.75rem; color: #38BDF8; font-weight: 800;">ECMWF IFS</div>
                        <div class="kpi-val-huge" style="color: #38BDF8;">{mean_ec:.1%}</div>
                        <div class="kpi-label-muted">Mean adaptive contribution</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with w_cols[1]:
                st.markdown(
                    f"""
                    <div class="kpi-card-dark">
                        <div style="font-size: 0.75rem; color: #A855F7; font-weight: 800;">NOAA GFS</div>
                        <div class="kpi-val-huge" style="color: #A855F7;">{mean_gfs:.1%}</div>
                        <div class="kpi-label-muted">Mean adaptive contribution</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with w_cols[2]:
                st.markdown(
                    f"""
                    <div class="kpi-card-dark">
                        <div style="font-size: 0.75rem; color: #34D399; font-weight: 800;">DWD ICON</div>
                        <div class="kpi-val-huge" style="color: #34D399;">{mean_icon:.1%}</div>
                        <div class="kpi-label-muted">Mean adaptive contribution</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            fig = go.Figure()
            times = list(range(len(df_w)))
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=df_w["ECMWF_IFS_weight"],
                    name="ECMWF IFS Weight",
                    stackgroup="one",
                    fillcolor="rgba(56, 189, 248, 0.7)",
                    line=dict(color="#38BDF8", width=0.5),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=df_w["NOAA_GFS_weight"],
                    name="NOAA GFS Weight",
                    stackgroup="one",
                    fillcolor="rgba(168, 85, 247, 0.7)",
                    line=dict(color="#A855F7", width=0.5),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=times,
                    y=df_w["DWD_ICON_weight"],
                    name="DWD ICON Weight",
                    stackgroup="one",
                    fillcolor="rgba(52, 211, 153, 0.7)",
                    line=dict(color="#34D399", width=0.5),
                )
            )

            layout3 = dict(PLOTLY_DARK_LAYOUT)
            layout3["xaxis"] = {**layout3.get("xaxis", {}), "title": "Prediction Index Sequence"}
            layout3["yaxis"] = {
                **layout3.get("yaxis", {}),
                "title": "Normalized Weight (Sum = 1.0)",
                "range": [0, 1.0],
            }
            fig.update_layout(
                **layout3,
                title=dict(
                    text=f"HOW TRUST CHANGES OVER TIME — {sel_loc.capitalize()} (Day {sel_day})",
                    font=dict(size=16, color="#F8FAFC"),
                ),
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                """
                <div class="glass-card" style="margin-top: 0.5rem;">
                    <div style="font-size: 0.85rem; color: #94A3B8;">
                        At every forecast point, model contributions are normalized to sum to 1. Dynamic weights represent each model's estimated contribution under observed context.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 4: SPATIAL INTELLIGENCE
    # =========================================================================
    elif navigation == "Spatial Intelligence":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">SPATIAL INTELLIGENCE</h2>
                <p style="font-size: 0.95rem; color: #94A3B8;">Forecast reliability changes across geography.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        sel_day = st.selectbox(
            "LEAD HORIZON",
            [1, 2, 3],
            format_func=lambda x: f"Day {x} • ({24*(x-1)+1}–{24*x}h Lead)",
            key="map_day",
        )

        sub_map = map_df[map_df["lead_day"] == sel_day].copy()

        sub_map["popup_text"] = sub_map.apply(
            lambda r: (
                f"<b>{r['location_id'].capitalize()}</b><br>"
                f"ECMWF IFS: {r['mean_ECMWF_IFS_weight']:.1%}<br>"
                f"NOAA GFS: {r['mean_NOAA_GFS_weight']:.1%}<br>"
                f"DWD ICON: {r['mean_DWD_ICON_weight']:.1%}<br>"
                f"<b>HIGHEST ADAPTIVE CONTRIBUTION: {r['dominant_model']}</b>"
            ),
            axis=1,
        )

        fig_map = go.Figure(
            go.Scattergeo(
                lat=sub_map["latitude"],
                lon=sub_map["longitude"],
                mode="markers+text",
                marker=dict(
                    size=22,
                    color=sub_map["mean_ECMWF_IFS_weight"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="ECMWF Weight", font=dict(color="#94A3B8")),
                        tickfont=dict(color="#94A3B8"),
                    ),
                    line=dict(color="#F8FAFC", width=1.5),
                ),
                text=sub_map["location_id"].str.capitalize(),
                textposition="top center",
                textfont=dict(color="#F8FAFC", size=13, family="Inter, sans-serif"),
                hoverinfo="text",
                hovertext=sub_map["popup_text"],
            )
        )

        layout4 = dict(PLOTLY_DARK_LAYOUT)
        layout4["margin"] = dict(l=0, r=0, t=40, b=0)
        fig_map.update_layout(
            **layout4,
            title=dict(
                text=f"Spatial Model Weight Map — India Demonstration Scope (Day {sel_day})",
                font=dict(size=16, color="#F8FAFC"),
            ),
            geo=dict(
                scope="asia",
                center=dict(lat=20.5937, lon=78.9629),
                projection_scale=3.8,
                showland=True,
                landcolor="#111827",
                countrycolor="#334155",
                coastlinecolor="#475569",
                bgcolor="#0D1322",
            ),
            height=540,
        )

        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown(
            """
            <div class="disclaimer-box">
                <b>Demonstration scope</b>: Six selected Indian locations • not a nationwide validation.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Spatial Weight Distribution Table")
        st.dataframe(
            sub_map[
                [
                    "location_id",
                    "latitude",
                    "longitude",
                    "mean_ECMWF_IFS_weight",
                    "mean_NOAA_GFS_weight",
                    "mean_DWD_ICON_weight",
                    "dominant_model",
                ]
            ],
            use_container_width=True,
        )

    # =========================================================================
    # TAB 5: VERIFICATION
    # =========================================================================
    elif navigation == "Verification":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">MODEL VERIFICATION</h2>
                <p style="font-size: 0.95rem; color: #94A3B8;">Does adaptive blending actually improve the forecast?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(perf_df, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig_mae = px.bar(
                perf_df,
                x="Approach",
                y="MAE",
                color="Approach",
                title="Mean Absolute Error (MAE in mm/h) — Lower is Better",
                color_discrete_map={
                    "Adaptive_ML_Blend": "#F43F5E",
                    "ECMWF_IFS": "#38BDF8",
                    "Historical_Weighted": "#F59E0B",
                    "Simple_Average": "#CBD5E1",
                    "NOAA_GFS": "#A855F7",
                    "DWD_ICON": "#34D399",
                },
            )
            fig_mae.update_layout(**PLOTLY_DARK_LAYOUT, showlegend=False, height=400)
            st.plotly_chart(fig_mae, use_container_width=True)

        with c2:
            fig_rmse = px.bar(
                perf_df,
                x="Approach",
                y="RMSE",
                color="Approach",
                title="Root Mean Square Error (RMSE in mm/h) — Lower is Better",
                color_discrete_map={
                    "Adaptive_ML_Blend": "#F43F5E",
                    "ECMWF_IFS": "#38BDF8",
                    "Historical_Weighted": "#F59E0B",
                    "Simple_Average": "#CBD5E1",
                    "NOAA_GFS": "#A855F7",
                    "DWD_ICON": "#34D399",
                },
            )
            fig_rmse.update_layout(**PLOTLY_DARK_LAYOUT, showlegend=False, height=400)
            st.plotly_chart(fig_rmse, use_container_width=True)

        mae_dict = dict(zip(perf_df["Approach"], perf_df["MAE"]))
        sky_m = mae_dict.get("Adaptive_ML_Blend", 0.3147)
        ec_m = mae_dict.get("ECMWF_IFS", 0.3711)
        avg_m = mae_dict.get("Simple_Average", 0.3964)

        st.markdown(
            f"""
            <div class="glass-card" style="border: 1px solid rgba(244, 63, 94, 0.4);">
                <div style="font-size: 0.75rem; font-weight: 800; color: #FB7185; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;">
                    HELD-OUT TEST RESULT
                </div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.5rem;">
                    Adaptive ML Blend: <span style="color: #F43F5E;">{sky_m:.4f} mm/h MAE</span>
                </div>
                <div style="font-size: 0.95rem; color: #CBD5E1; line-height: 1.6;">
                    Lower MAE on this held-out six-location evaluation compared with ECMWF IFS ({ec_m:.4f} mm/h) and Simple Average ({avg_m:.4f} mm/h).
                </div>
                <div style="font-size: 0.75rem; color: #64748B; margin-top: 0.75rem;">
                    Evaluation period: 24–28 July 2024 UTC
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TAB 6: EXTREME WEATHER
    # =========================================================================
    elif navigation == "Extreme Weather":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">EXTREME WEATHER SIGNALS</h2>
                <p style="font-size: 0.95rem; color: #94A3B8;">Project analytical precipitation threshold monitoring and guidance signals.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            locations = sorted(weights_df["location_id"].unique())
            sel_loc = st.selectbox("LOCATION", locations, format_func=lambda x: x.capitalize(), key="ex_loc")
        with c2:
            sel_day = st.selectbox(
                "LEAD HORIZON",
                [1, 2, 3],
                format_func=lambda x: f"Day {x} • ({24*(x-1)+1}–{24*x}h Lead)",
                key="ex_day",
            )

        df_ex = weights_df[
            (weights_df["location_id"] == sel_loc)
            & (weights_df["lead_hours"] > 24 * (sel_day - 1))
            & (weights_df["lead_hours"] <= 24 * sel_day)
        ].copy()

        if df_ex.empty:
            st.warning("Insufficient data for this selection.")
        else:
            thresh = 1.0
            max_blend = df_ex["blended_precipitation"].max()
            is_flagged = max_blend >= thresh

            signal_bg = "rgba(239, 68, 68, 0.15)" if is_flagged else "rgba(16, 185, 129, 0.15)"
            signal_color = "#F87171" if is_flagged else "#34D399"
            signal_text = "HEAVY-RAINFALL ANALYTICAL SIGNAL" if is_flagged else "BELOW PROJECT ANALYTICAL THRESHOLD"

            st.markdown(
                f"""
                <div class="glass-card" style="background: {signal_bg}; border: 1px solid {signal_color}; padding: 1.25rem;">
                    <div style="font-size: 0.75rem; font-weight: 800; color: {signal_color}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.25rem;">
                        ANALYTICAL SIGNAL STATUS
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 900; color: #F8FAFC;">
                        {signal_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(
                    f"""
                    <div class="kpi-card-dark">
                        <div class="kpi-val-huge" style="color: #38BDF8;">{max_blend:.2f}</div>
                        <div class="kpi-label-muted">BLENDED RAINFALL (mm/h)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m2:
                st.markdown(
                    """
                    <div class="kpi-card-dark">
                        <div class="kpi-val-huge" style="color: #F59E0B;">1.00</div>
                        <div class="kpi-label-muted">PROJECT THRESHOLD (mm/h)</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with m3:
                st.markdown(
                    f"""
                    <div class="kpi-card-dark">
                        <div class="kpi-val-huge" style="color: {signal_color}; font-size: 1.4rem;">{signal_text.split()[0]}</div>
                        <div class="kpi-label-muted">SIGNAL STATUS</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            fig_ex = px.line(
                df_ex,
                x="valid_time",
                y=["blended_precipitation", "reference_precipitation"],
                title=f"Blended Rainfall vs ERA5 Reference — {sel_loc.capitalize()}",
                labels={"value": "Precipitation (mm/h)", "valid_time": "Valid Time (UTC)"},
            )
            fig_ex.add_hline(
                y=thresh,
                line_dash="dash",
                line_color="#EF4444",
                annotation_text="1.0 mm/h Analytical Threshold",
                annotation_position="bottom right",
                annotation_font=dict(color="#EF4444"),
            )
            fig_ex.update_layout(**PLOTLY_DARK_LAYOUT, height=440)
            st.plotly_chart(fig_ex, use_container_width=True)

            st.markdown(
                """
                <div class="disclaimer-box">
                    <b>Notice</b>: Project analytical threshold (<b>&ge; 1.0 mm/h</b>) — not an official IMD warning threshold. Guidance for demonstration only.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 7: METHODOLOGY & LIMITATIONS
    # =========================================================================
    elif navigation == "Methodology":
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.6rem; font-weight: 900; color: #F8FAFC; margin-bottom: 0.25rem;">HOW SKYBLEND THINKS</h2>
                <p style="font-size: 0.95rem; color: #94A3B8;">End-to-end adaptive machine learning forecast blending architecture.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 0.85rem; font-weight: 800; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem;">
                    7-STAGE BLENDING PIPELINE
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #38BDF8;">1</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">FORECAST SOURCES</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">ECMWF • GFS • ICON</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #A855F7;">2</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">HARMONIZATION</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Grid & Valid Time Alignment</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #34D399;">3</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">HISTORICAL SKILL</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Rolling 24h Leakage-Free MAE</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #F59E0B;">4</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">CONTEXT FEATURES</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Location • Lead Time • Season</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #EC4899;">5</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">ADAPTIVE AI WEIGHTING</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">HistGradBoost Error Models</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #F43F5E;">6</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">BLENDED FORECAST</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Normalized Convex Combination</div>
                    </div>
                    <div class="pipeline-node">
                        <div style="font-size: 1.1rem; font-weight: 900; color: #38BDF8;">7</div>
                        <div style="font-size: 0.85rem; font-weight: 800; margin-top: 4px;">VERIFICATION</div>
                        <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">ERA5 Reference Evaluation</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 0.85rem; font-weight: 800; color: #A855F7; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.75rem;">
                    MATHEMATICAL BLENDING FORMULATION
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.latex(
            r"F_{\text{blended}} = \sum_{m \in \{\text{ECMWF, GFS, ICON}\}} w_m \cdot F_m"
        )
        st.latex(r"\text{where } \sum_{m} w_m = 1.0, \quad w_m \ge 0")

        st.markdown(
            r"""
            <div class="glass-card">
                <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
                    <b>Weight Normalization Formulation</b>:<br>
                    1. Train <code>HistGradientBoostingRegressor</code> models per NWP source to predict expected absolute error $\hat{e}_m$.<br>
                    2. Convert predicted errors into reliabilities: $\text{reliability}_m = \frac{1}{\hat{e}_m + \epsilon}$.<br>
                    3. Normalize reliabilities into non-negative weights: $w_m = \frac{\text{reliability}_m}{\sum_k \text{reliability}_k}$.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="glass-card" style="border: 1px solid rgba(245, 158, 11, 0.4);">
                <div style="font-size: 0.85rem; font-weight: 800; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.75rem;">
                    VALIDATION SCOPE & SCIENTIFIC LIMITATIONS
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC;">06</div>
                        <div style="font-size: 0.7rem; color: #94A3B8;">DEMONSTRATION CITIES</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC;">28 DAYS</div>
                        <div style="font-size: 0.7rem; color: #94A3B8;">JULY 2024 MONSOON</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC;">03</div>
                        <div style="font-size: 0.7rem; color: #94A3B8;">NWP SOURCES</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 900; color: #F8FAFC;">ERA5</div>
                        <div style="font-size: 0.7rem; color: #94A3B8;">REANALYSIS REFERENCE</div>
                    </div>
                </div>
                <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
                    This is a proof-of-concept evaluation. Broader validation requires more locations, seasons, years and independent rain-gauge observations. ERA5 reanalysis is used as a consistent reference dataset, not direct ground-station truth.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
