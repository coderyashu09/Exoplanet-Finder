"""PAGE 2 — EXOPLANET DETECTOR: Single-candidate AI prediction & scientific explanation."""
import json
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.predict import ExoplanetPredictor
from src.baseline import BaselinePipeline
from src.visualization import plot_global_view, plot_local_view, plot_raw_lightcurve
from app.components.styling import apply_custom_css, render_hero, render_alert
from app.components.sidebar import render_sidebar
from app.components.cards import render_prediction_badge, render_orbital_parameters_card

st.set_page_config(
    page_title="Exoplanet Detector | Exoplanet Finder",
    page_icon="🔭",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()
threshold = controls["threshold"]

render_hero(
    title="EXOPLANET DETECTOR",
    tagline="Analyze individual Kepler targets with dual-view deep convolutional neural inference.",
    badges=[
        ("Inference Engine", "badge-pc"),
        ("Integrated Gradients", "badge-nasa"),
        ("Transit Morphology", "badge-pc"),
    ],
)


@st.cache_data
def load_candidates():
    p = cfg.processed_dir / "tce_cleaned.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_resource
def get_predictor():
    return ExoplanetPredictor()


@st.cache_resource
def get_baseline_pipeline():
    try:
        return BaselinePipeline().load()
    except Exception:
        return None


df_candidates = load_candidates()
predictor = get_predictor()
baseline_pipeline = get_baseline_pipeline()
cache = LightCurveCache()

st.markdown("### 🔍 Target Star & Candidate Selection")
s_col1, s_col2 = st.columns([1, 2])

with s_col1:
    search_mode = st.radio("Selection Mode", ["Preset Highlight Stars", "Search by Kepler ID (KIC)"], horizontal=True)

selected_kepid = None
selected_plnt_num = 1

if search_mode == "Preset Highlight Stars":
    presets = {
        "Kepler-90 (KIC 11442793) — 8-Planet Multi-Transiting System": 11442793,
        "KIC 757450 — Validated Planet Candidate": 757450,
        "KIC 1161345 — Long-Cadence Multi-Quarter Target": 1161345,
        "KIC 1026032 — Deep Astrophysical False Positive (EB)": 1026032,
    }
    preset_choice = st.selectbox("Select Exemplar System", list(presets.keys()))
    selected_kepid = presets[preset_choice]
else:
    kic_input = st.number_input("Enter Kepler ID (KIC):", min_value=1, max_value=20000000, value=11442793)
    selected_kepid = int(kic_input)

# Filter candidate TCEs for this star
tces_for_star = df_candidates[df_candidates["kepid"] == selected_kepid]

if len(tces_for_star) > 0:
    tce_options = {
        f"TCE #{int(r['tce_plnt_num'])}: Period={r['tce_period']:.2f}d, Dur={r['tce_duration']:.2f}h, Depth={r['tce_depth']:.0f}ppm (NASA: {r.get('av_training_set', 'UNK')})": int(r["tce_plnt_num"])
        for _, r in tces_for_star.iterrows()
    }
    selected_tce_str = st.selectbox("Select Transit Candidate (TCE)", list(tce_options.keys()))
    selected_plnt_num = tce_options[selected_tce_str]
    candidate_row = tces_for_star[tces_for_star["tce_plnt_num"] == selected_plnt_num].iloc[0].to_dict()
else:
    st.warning(f"KIC {selected_kepid} is not indexed in the cleaned DR24 TCE table. Enter orbital parameters manually below:")
    col_p1, col_p2, col_p3 = st.columns(3)
    p_in = col_p1.number_input("Orbital Period [days]", min_value=0.1, value=14.449)
    e_in = col_p2.number_input("Transit Epoch [BKJD]", min_value=0.0, value=133.0)
    d_in = col_p3.number_input("Duration [hours]", min_value=0.1, value=3.5)
    candidate_row = {
        "kepid": selected_kepid,
        "tce_plnt_num": 1,
        "tce_period": p_in,
        "tce_time0bk": e_in,
        "tce_duration": d_in,
        "tce_depth": 1000.0,
        "av_training_set": "Manual",
    }

st.markdown("---")

# Display orbital parameters
render_orbital_parameters_card(candidate_row)

# Detection & Analysis Trigger
cache_exists = cache.exists(selected_kepid)
status_color = "#35D49A" if cache_exists else "#FFBE55"
status_text = "Cached On Disk (Instant Load)" if cache_exists else "Not Cached (Will download from NASA MAST)"

st.markdown(
    f"""
    <div style="font-size: 0.82rem; color: #9AAAC1; margin-bottom: 12px;">
        Stellar Light Curve Status: <b style="color: {status_color};">{status_text}</b>
    </div>
    """,
    unsafe_allow_html=True,
)

btn_analyze = st.button("🚀 Run AI Transit Detection & Explainability Analysis", type="primary")

if btn_analyze or cache_exists:
    with st.spinner("Retrieving photometry and computing dual-view phase fold..."):
        # Load or retrieve light curve
        time_arr, flux_arr, flux_err, lc_meta = download_stellar_lightcurve(selected_kepid, cache=cache)

    if time_arr is None or len(time_arr) == 0:
        render_alert(f"Unable to retrieve light curve for KIC {selected_kepid}. Error: {lc_meta.get('error', 'No cadences available')}", "danger")
    else:
        st.success(f"Acquired light curve for KIC {selected_kepid} with {len(time_arr):,} observations.")

        # Baseline tabular prediction
        base_prob, base_pred = None, None
        if baseline_pipeline is not None and baseline_pipeline.is_trained:
            try:
                base_prob, base_pred = baseline_pipeline.predict_single(
                    period=float(candidate_row["tce_period"]),
                    duration=float(candidate_row["tce_duration"]),
                    depth=float(candidate_row.get("tce_depth", 1000.0)),
                )
            except Exception:
                pass

        # CNN prediction
        predictor.threshold = threshold
        result = predictor.predict_from_lightcurve(
            time_arr=time_arr,
            flux_arr=flux_arr,
            period=float(candidate_row["tce_period"]),
            t0=float(candidate_row["tce_time0bk"]),
            duration_hours=float(candidate_row["tce_duration"]),
            depth_ppm=float(candidate_row.get("tce_depth", 0.0)),
            compute_attributions=True,
        )

        cnn_prob = result.get("planet_probability", 0.0)
        category = result.get("category", "Unknown")

        # Top verdict banner
        render_prediction_badge(category, cnn_prob, threshold)

        # Comparative probability breakdown
        st.markdown("### ⚖️ Multi-Model Probability Comparison")
        pcol1, pcol2, pcol3 = st.columns(3)
        with pcol1:
            st.metric(
                label="Two-View 1D CNN Probability",
                value=f"{cnn_prob*100:.1f}%",
                delta=f"{'Above' if cnn_prob >= threshold else 'Below'} threshold ({threshold:.2f})",
            )
        with pcol2:
            if base_prob is not None:
                st.metric(
                    label="Baseline HistGB Probability",
                    value=f"{base_prob*100:.1f}%",
                    delta=f"{'Planet' if base_pred == 1 else 'False Positive'}",
                )
            else:
                st.metric(label="Baseline HistGB Probability", value="N/A", delta="Not Trained")
        with pcol3:
            nasa_lbl = candidate_row.get("av_training_set", "UNK")
            lbl_name = "Planet Candidate (PC)" if nasa_lbl == "PC" else ("False Positive (AFP)" if nasa_lbl == "AFP" else "Non-Transiting (NTP)")
            st.metric(label="Official NASA DR24 Ground Truth", value=nasa_lbl, delta=lbl_name)

        st.markdown("---")

        # Interactive Transit Visualizations with Integrated Gradients
        st.markdown("### 📈 Transit Profiles & Feature Attribution")
        vcol1, vcol2 = st.columns(2)

        with vcol1:
            if "global_view" in result:
                fig_g = plot_global_view(
                    result["global_view"],
                    period=float(candidate_row["tce_period"]),
                    attributions=result.get("ig_global"),
                )
                st.plotly_chart(fig_g, use_container_width=True)

        with vcol2:
            if "local_view" in result:
                fig_l = plot_local_view(
                    result["local_view"],
                    duration_hours=float(candidate_row["tce_duration"]),
                    attributions=result.get("ig_local"),
                )
                st.plotly_chart(fig_l, use_container_width=True)

        # Scientific Explainability Section
        st.markdown("### 🔬 Scientific Interpretability & Transit Morphology")
        morphology = result.get("morphology", {})
        reasons = morphology.get("morphology_reasons", [])

        st.markdown(
            f"""
            <div style="background: #111C30; border: 1px solid #1D2B48; border-radius: 12px; padding: 20px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: #63B3FF; margin-bottom: 10px;">
                    Neural Attribution & Morphological Diagnostic Findings:
                </div>
                <ul style="color: #D1DCF0; line-height: 1.6; font-size: 0.9rem; margin-bottom: 12px;">
                    {"".join([f"<li>{r}</li>" for r in reasons])}
                    <li><b>Symmetry Residual:</b> {morphology.get('symmetry_residual', 0.0)} (Values &lt; 0.35 indicate symmetric ingress/egress).</li>
                    <li><b>Flat-bottom U-shape Variance:</b> {morphology.get('core_flatness_variance', 0.0)} (Values &lt; 0.05 favor non-grazing planetary discs).</li>
                </ul>
                <div style="font-size: 0.78rem; color: #9AAAC1; border-top: 1px solid #1D2B48; padding-top: 8px;">
                    Dotted curves show <b>Integrated Gradients</b> feature attribution. Peaks indicate the exact phase intervals that exerted greatest influence on the CNN's classification.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

