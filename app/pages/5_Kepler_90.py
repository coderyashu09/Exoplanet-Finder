"""PAGE 6 — KEPLER-90 SYSTEM: Deep astronomical exploration of the historic 8-planet planetary system."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.predict import ExoplanetPredictor
from src.visualization import (
    plot_raw_lightcurve,
    plot_global_view,
    plot_local_view,
    apply_space_theme,
    ACCENT_PRIMARY,
    SUCCESS_COLOR,
    WARNING_COLOR,
    CARD_COLOR,
    TEXT_MUTED,
)
from app.components.styling import apply_custom_css, render_hero, render_metric_card
from app.components.sidebar import render_sidebar
from app.components.cards import render_prediction_badge

st.set_page_config(
    page_title="Kepler-90 Exploration | Exoplanet Finder",
    page_icon="🪐",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()
threshold = controls["threshold"]

render_hero(
    title="KEPLER-90 SYSTEM EXPLORATION",
    tagline="Investigating the iconic 8-planet star system (KIC 11442793) — the first known solar system analog discovered with AI.",
    badges=[
        ("KIC 11442793", "badge-nasa"),
        ("8 Confirmed Planets", "badge-pc"),
        ("Google/NASA AI Milestone", "badge-nasa"),
    ],
)

# Kepler-90 Planetary Architecture Database
KEPLER_90_PLANETS = [
    {"name": "Kepler-90b", "period": 7.008, "epoch": 134.50, "duration": 3.99, "radius": 1.31, "depth_ppm": 240, "semi_major_au": 0.074, "discovery": "Kepler DR20 (Transit)"},
    {"name": "Kepler-90c", "period": 8.719, "epoch": 139.40, "duration": 4.41, "radius": 1.18, "depth_ppm": 210, "semi_major_au": 0.089, "discovery": "Kepler DR20 (Transit)"},
    {"name": "Kepler-90i", "period": 14.449, "epoch": 133.01, "duration": 2.80, "radius": 1.32, "depth_ppm": 280, "semi_major_au": 0.123, "discovery": "Google Brain / NASA (Shallue & Vanderburg 2018, Deep Learning)"},
    {"name": "Kepler-90d", "period": 59.736, "epoch": 162.10, "duration": 8.40, "radius": 2.88, "depth_ppm": 1200, "semi_major_au": 0.320, "discovery": "Kepler Transit"},
    {"name": "Kepler-90e", "period": 91.939, "epoch": 210.50, "duration": 9.71, "radius": 2.67, "depth_ppm": 1100, "semi_major_au": 0.420, "discovery": "Kepler Transit"},
    {"name": "Kepler-90f", "period": 124.914, "epoch": 178.20, "duration": 10.94, "radius": 2.89, "depth_ppm": 1350, "semi_major_au": 0.510, "discovery": "Kepler Transit"},
    {"name": "Kepler-90g", "period": 210.607, "epoch": 255.40, "duration": 15.30, "radius": 8.13, "depth_ppm": 9800, "semi_major_au": 0.710, "discovery": "Kepler Transit"},
    {"name": "Kepler-90h", "period": 331.603, "epoch": 160.05, "duration": 14.80, "radius": 11.32, "depth_ppm": 7500, "semi_major_au": 1.010, "discovery": "Kepler DR24 TCE #1"},
]

# Solar System inner planets for scale
SOLAR_SYSTEM = [
    {"name": "Mercury", "period": 87.97, "radius": 0.38, "semi_major_au": 0.387},
    {"name": "Venus", "period": 224.70, "radius": 0.95, "semi_major_au": 0.723},
    {"name": "Earth", "period": 365.25, "radius": 1.00, "semi_major_au": 1.000},
]

# System Metrics
st.markdown("### 🌟 Host Star Astrophysics (Kepler-90 / KIC 11442793)")
sc1, sc2, sc3, sc4, sc5 = st.columns(5)
with sc1:
    render_metric_card("Spectral Type", "G0V", "Sun-like Main Sequence", "amber")
with sc2:
    render_metric_card("Effective Temp", "6,080 K", "+/- 160 K", "rose")
with sc3:
    render_metric_card("Stellar Radius", "1.20 R☉", "Solar Radii", "blue")
with sc4:
    render_metric_card("Distance", "2,840 ly", "Constellation Draco", "purple")
with sc5:
    render_metric_card("Confirmed Worlds", "8 Planets", "Tied with Solar System", "green")

st.markdown("---")

# Planetary Architecture Orbital Chart
st.markdown("### 🪐 Kepler-90 Orbital Period Architecture")
df_p = pd.DataFrame(KEPLER_90_PLANETS)

fig_orbit = go.Figure()
fig_orbit.add_trace(
    go.Scatter(
        x=df_p["period"],
        y=df_p["radius"],
        mode="markers+text",
        text=df_p["name"],
        textposition="top center",
        marker={
            "size": df_p["radius"] * 4 + 8,
            "color": [
                "#35D49A" if "Shallue" in d else ("#63B3FF" if "DR24" in d else "#8B7CFF")
                for d in df_p["discovery"]
            ],
            "opacity": 0.85,
            "line": {"color": "#F4F7FF", "width": 1.5},
        },
        hovertemplate="<b>%{text}</b><br>Orbital Period: %{x:.2f} days<br>Planet Radius: %{y:.2f} R⊕<extra></extra>",
    )
)
fig_orbit.update_xaxes(title_text="Orbital Period [Days, Logarithmic Scale]", type="log")
fig_orbit.update_yaxes(title_text="Planetary Radius [Earth Radii, R⊕]")
apply_space_theme(fig_orbit, "Kepler-90 Planetary System: Period vs Planet Radius (R⊕)", height=400)
st.plotly_chart(fig_orbit, use_container_width=True)

# Side-by-side Solar System Comparison
st.markdown("### 🌌 Kepler-90 vs Solar System Scale Comparison")
fig_comp = go.Figure()

# Kepler-90 planets
fig_comp.add_trace(
    go.Scatter(
        x=df_p["semi_major_au"],
        y=[1.0] * len(df_p),
        mode="markers+text",
        text=df_p["name"],
        textposition="top center",
        marker={"size": df_p["radius"] * 3 + 6, "color": "#63B3FF"},
        name="Kepler-90 System (8 planets within 1.01 AU)",
    )
)

# Solar System comparison
df_sol = pd.DataFrame(SOLAR_SYSTEM)
fig_comp.add_trace(
    go.Scatter(
        x=df_sol["semi_major_au"],
        y=[0.0] * len(df_sol),
        mode="markers+text",
        text=df_sol["name"],
        textposition="bottom center",
        marker={"size": df_sol["radius"] * 5 + 6, "color": "#FFBE55"},
        name="Inner Solar System (Mercury, Venus, Earth)",
    )
)

fig_comp.update_xaxes(title_text="Semi-Major Axis Distance from Host Star [Astronomical Units (AU)]", range=[0.0, 1.15])
fig_comp.update_yaxes(showticklabels=False, range=[-0.5, 1.6], showgrid=False)
apply_space_theme(fig_comp, "Kepler-90 is Ultra-Compact: All 8 Planets Fit Inside Earth's Orbit!", height=350)
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown(
    """
    <div style="background: #111C30; border-left: 4px solid #8B7CFF; padding: 14px 18px; border-radius: 6px; font-size: 0.88rem; color: #D1DCF0; margin-bottom: 25px;">
        <b>Historical Scientific Context:</b> In December 2017, researcher Christopher Shallue (Google Brain) and astrophysicist Andrew Vanderburg (University of Texas at Austin) deployed a convolutional neural network to search 670 multi-planet systems for weak transit signals. The network identified a 14.449-day periodic signal from Kepler-90 with a signal-to-noise ratio of only 5.9, leading to the discovery of <b>Kepler-90i</b>. This established Kepler-90 as the only known star with as many planets as our Sun.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Dedicated Planet Inspection & Model Prediction
st.markdown("### 🔬 Analyze Kepler-90 System Candidates with Trained Models")

planet_names = [p["name"] for p in KEPLER_90_PLANETS]
selected_planet_name = st.selectbox("Select Kepler-90 Planet to Analyze", planet_names, index=7)
planet_info = next(p for p in KEPLER_90_PLANETS if p["name"] == selected_planet_name)

# Display planet data
pcol1, pcol2, pcol3, pcol4 = st.columns(4)
pcol1.metric("Orbital Period", f"{planet_info['period']:.3f} days")
pcol2.metric("Transit Duration", f"{planet_info['duration']:.2f} hours")
pcol3.metric("Transit Depth", f"{planet_info['depth_ppm']:,} ppm")
pcol4.metric("Semi-Major Axis", f"{planet_info['semi_major_au']:.3f} AU")

cache = LightCurveCache()
predictor = ExoplanetPredictor()
predictor.threshold = threshold

if st.button(f"🚀 Analyze {selected_planet_name} Transit Signal", type="primary"):
    with st.spinner(f"Extracting Kepler-90 light curve and folding at P = {planet_info['period']:.4f} days..."):
        time_arr, flux_arr, flux_err, _ = download_stellar_lightcurve(11442793, cache=cache)

    if time_arr is not None:
        result = predictor.predict_from_lightcurve(
            time_arr=time_arr,
            flux_arr=flux_arr,
            period=planet_info["period"],
            t0=planet_info["epoch"],
            duration_hours=planet_info["duration"],
            depth_ppm=planet_info["depth_ppm"],
            compute_attributions=True,
        )

        prob = result.get("planet_probability", 0.0)
        cat = result.get("category", "Unknown")

        render_prediction_badge(cat, prob, threshold)

        rcol1, rcol2 = st.columns(2)
        with rcol1:
            fig_g = plot_global_view(result["global_view"], period=planet_info["period"], attributions=result.get("ig_global"))
            st.plotly_chart(fig_g, use_container_width=True)
        with rcol2:
            fig_l = plot_local_view(result["local_view"], duration_hours=planet_info["duration"], attributions=result.get("ig_local"))
            st.plotly_chart(fig_l, use_container_width=True)
