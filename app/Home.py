"""EXOPLANET FINDER — SPACE COMMAND CENTER (Home Dashboard)."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache
from app.components.styling import apply_custom_css, render_hero, render_metric_card
from app.components.sidebar import render_sidebar
from src.visualization import plot_dataset_distributions

# Page configuration
st.set_page_config(
    page_title="Space Command Center | Exoplanet Finder",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
controls = render_sidebar()

# Hero Header
render_hero(
    title="EXOPLANET FINDER",
    tagline="Discover New Worlds Beyond Our Solar System — Powered by NASA Kepler DR24 & Dual-View Deep Learning.",
    badges=[
        ("NASA Kepler Q1-Q17 DR24", "badge-nasa"),
        ("15,737 Verified TCEs", "badge-pc"),
        ("Dual-View 1D CNN", "badge-pc"),
    ],
)


@st.cache_data
def load_tce_summary():
    """Load cleaned TCE dataset and compute mission statistics."""
    tce_file = cfg.processed_dir / "tce_cleaned.csv"
    if not tce_file.exists():
        return None
    return pd.read_csv(tce_file)


df_tce = load_tce_summary()
cache = LightCurveCache()
cached_count = len(cache.list_cached_stars())

# Metrics Grid
st.markdown("### 🛰️ Kepler Mission DR24 Telemetry")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_tce = len(df_tce) if df_tce is not None else 0
    render_metric_card("Total Valid TCEs", f"{total_tce:,}", "Cleaned Q1-Q17 Catalog", "blue")

with col2:
    pc_count = int((df_tce["planet"] == 1).sum()) if df_tce is not None else 0
    render_metric_card("Planet Candidates", f"{pc_count:,}", "Target Label PC = 1", "green")

with col3:
    afp_count = int((df_tce["av_training_set"] == "AFP").sum()) if df_tce is not None else 0
    render_metric_card("False Positives", f"{afp_count:,}", "Astrophysical EBs/Blends", "rose")

with col4:
    ntp_count = int((df_tce["av_training_set"] == "NTP").sum()) if df_tce is not None else 0
    render_metric_card("Non-Transiting", f"{ntp_count:,}", "Stellar Noise / Glitches", "amber")

with col5:
    stars_count = int(df_tce["kepid"].nunique()) if df_tce is not None else 0
    render_metric_card("Unique Target Stars", f"{stars_count:,}", f"{cached_count} Cached Locally", "purple")

st.markdown("---")

# Astrophysical Distributions
if df_tce is not None:
    st.markdown("### 📊 Astrophysical Parameter Distributions")
    figs = plot_dataset_distributions(df_tce)

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        if "label_distribution" in figs:
            st.plotly_chart(figs["label_distribution"], use_container_width=True)
        if "duration_distribution" in figs:
            st.plotly_chart(figs["duration_distribution"], use_container_width=True)

    with dcol2:
        if "period_distribution" in figs:
            st.plotly_chart(figs["period_distribution"], use_container_width=True)
        if "depth_distribution" in figs:
            st.plotly_chart(figs["depth_distribution"], use_container_width=True)

st.markdown("---")

# Model Performance Highlights
st.markdown("### 🏆 AI Model Performance Highlights")
mcol1, mcol2 = st.columns([1, 1])

baseline_path = cfg.metrics_dir / "baseline_metrics.json"
cnn_path = cfg.metrics_dir / "cnn_metrics.json"

with mcol1:
    st.markdown(
        """
        <div style="background: #111C30; border: 1px solid #1D2B48; border-radius: 12px; padding: 22px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #FFBE55; letter-spacing: 0.08em; text-transform: uppercase;">
                TABULAR BENCHMARK MODEL
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #F4F7FF; margin: 4px 0 12px 0;">
                HistGradientBoostingClassifier
            </div>
            <p style="font-size: 0.85rem; color: #9AAAC1; margin-bottom: 15px;">
                Trained on orbital parameters (period, duration, depth) across strictly isolated training stars.
            </p>
        """,
        unsafe_allow_html=True,
    )
    if baseline_path.exists():
        with open(baseline_path, "r", encoding="utf-8") as f:
            bm = json.load(f)
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("ROC-AUC", f"{bm.get('roc_auc', 0):.4f}")
        bc2.metric("Avg Precision", f"{bm.get('average_precision', 0):.4f}")
        bc3.metric("F1 Score", f"{bm.get('f1_score', 0):.4f}")
    st.markdown("</div>", unsafe_allow_html=True)

with mcol2:
    st.markdown(
        """
        <div style="background: #111C30; border: 1px solid #1D2B48; border-radius: 12px; padding: 22px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #63B3FF; letter-spacing: 0.08em; text-transform: uppercase;">
                DEEP LEARNING ARCHITECTURE
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #F4F7FF; margin: 4px 0 12px 0;">
                Dual-View 1D Convolutional Neural Network
            </div>
            <p style="font-size: 0.85rem; color: #9AAAC1; margin-bottom: 15px;">
                Dual branches processing Global (2001 bins) and Local (201 bins) folded photometric transit profiles.
            </p>
        """,
        unsafe_allow_html=True,
    )
    if cnn_path.exists():
        with open(cnn_path, "r", encoding="utf-8") as f:
            cm = json.load(f)
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("ROC-AUC", f"{cm.get('roc_auc', 0):.4f}")
        cc2.metric("Avg Precision", f"{cm.get('average_precision', 0):.4f}")
        cc3.metric("F1 Score", f"{cm.get('f1_score', 0):.4f}")
    else:
        st.info("CNN evaluation metrics pending. Train the CNN in scripts or Model Intelligence page.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Quick Navigation cards
st.markdown("### 🚀 Mission Navigation")
n1, n2, n3, n4 = st.columns(4)
with n1:
    st.markdown(
        """
        <div class="metric-card accent-blue">
            <div class="metric-label">FEATURED PAGE</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">🔭 Exoplanet Detector</div>
            <div class="metric-subtext">Predict on any Kepler star and analyze transit morphology.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with n2:
    st.markdown(
        """
        <div class="metric-card accent-green">
            <div class="metric-label">INTERACTIVE LAB</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">📈 Light Curve Lab</div>
            <div class="metric-subtext">Raw photometry, Savitzky-Golay flattening & phase folding.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with n3:
    st.markdown(
        """
        <div class="metric-card accent-purple">
            <div class="metric-label">HISTORIC SYSTEM</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">🪐 Kepler-90 System</div>
            <div class="metric-subtext">Explore the 8-planet planetary system discovered with ML.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with n4:
    st.markdown(
        """
        <div class="metric-card accent-amber">
            <div class="metric-label">CANDIDATE DATABASE</div>
            <div style="font-size: 1.1rem; font-weight: 700; margin: 4px 0;">🔍 Candidate Explorer</div>
            <div class="metric-subtext">Filter, sort, and export 15,737 DR24 TCE candidates.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

