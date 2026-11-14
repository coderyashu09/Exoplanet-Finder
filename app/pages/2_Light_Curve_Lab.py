"""PAGE 3 — LIGHT CURVE LAB: Dedicated interactive astronomical visualization laboratory."""
import io
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve, compute_transit_mask
from src.phase_folding import generate_two_views, fold_lightcurve
from src.visualization import (
    plot_raw_lightcurve,
    plot_raw_vs_flattened,
    plot_global_view,
    plot_local_view,
    apply_space_theme,
    ACCENT_PRIMARY,
    WARNING_COLOR,
    SUCCESS_COLOR,
    DANGER_COLOR,
    TEXT_MUTED,
)
from app.components.styling import apply_custom_css, render_hero
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Light Curve Lab | Exoplanet Finder",
    page_icon="📈",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()

render_hero(
    title="LIGHT CURVE LAB",
    tagline="Interactive astronomical laboratory for photometric detrending, transit masking, and phase-space analysis.",
    badges=[
        ("Photometry Studio", "badge-nasa"),
        ("Savitzky-Golay", "badge-pc"),
        ("Phase Folding", "badge-pc"),
    ],
)

cache = LightCurveCache()
cached_stars = cache.list_cached_stars()

st.markdown("### 🎛️ Observation Selection & Preprocessing Controls")
c_col1, c_col2 = st.columns([1, 2])

with c_col1:
    star_options = cached_stars if cached_stars else [cfg.kepler90_kepid]
    star_choice = st.selectbox(
        "Select Stellar System (KIC)",
        star_options,
        index=star_options.index(cfg.kepler90_kepid) if cfg.kepler90_kepid in star_options else 0,
        help="Select any cached star or Kepler-90",
    )

with c_col2:
    p_ctrl1, p_ctrl2, p_ctrl3, p_ctrl4 = st.columns(4)
    period = p_ctrl1.number_input("Orbital Period [days]", min_value=0.1, max_value=1000.0, value=14.4491, step=0.01)
    epoch = p_ctrl2.number_input("Transit Epoch [BKJD]", min_value=0.0, max_value=2000.0, value=133.0, step=0.1)
    duration = p_ctrl3.number_input("Duration [hours]", min_value=0.1, max_value=100.0, value=3.5, step=0.1)
    window_len = p_ctrl4.number_input("Flattening Window [cadences]", min_value=51, max_value=1001, value=401, step=50)

# Fetch data
with st.spinner(f"Loading photometry for KIC {star_choice}..."):
    time_arr, flux_arr, flux_err, meta = download_stellar_lightcurve(star_choice, cache=cache)

if time_arr is None or len(time_arr) == 0:
    st.error(f"Unable to load light curve for KIC {star_choice}.")
else:
    t_clean = validate_and_align_time_system(time_arr)

    # Process
    flat_flux, trend, flat_meta = flatten_lightcurve(
        time_arr=t_clean,
        flux_arr=flux_arr,
        period=period,
        t0=epoch,
        duration_hours=duration,
        window_length=int(window_len),
    )

    in_transit_mask = compute_transit_mask(
        time_arr=t_clean,
        period=period,
        t0=epoch,
        duration_hours=duration,
    )

    global_view, local_view, fold_meta = generate_two_views(
        time_arr=t_clean,
        flux_arr=flat_flux,
        period=period,
        t0=epoch,
        duration_hours=duration,
        global_bins=cfg.cnn_global_length,
        local_bins=cfg.cnn_local_length,
    )

    phases_all, sorted_fluxes = fold_lightcurve(t_clean, flat_flux, period=period, t0=epoch)

    st.markdown("---")

    # Lab Tabbed Interface
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "1. Raw Stellar Flux",
        "2. Detrending & Transit Mask",
        "3. Global Phase Fold (2001 bins)",
        "4. Local Transit Zoom (201 bins)",
        "5. Binned vs Unbinned Phase Curve",
        "6. Transit Depth & Profile Model",
        "7. Export Arrays & Inspector",
    ])

    with tab1:
        st.markdown("#### Kepler Raw Photometry Time Series")
        fig_raw = plot_raw_lightcurve(t_clean, flux_arr, title=f"KIC {star_choice} — Raw Stellar Flux")
        st.plotly_chart(fig_raw, use_container_width=True)

    with tab2:
        st.markdown("#### Continuum Fitting with Transit Protection")
        fig_detrend = plot_raw_vs_flattened(t_clean, flux_arr, trend, flat_flux)
        st.plotly_chart(fig_detrend, use_container_width=True)

        st.markdown("#### Transit Region Mask Inspection")
        fig_mask = go.Figure()
        stride = max(1, len(t_clean) // 15000)
        fig_mask.add_trace(
            go.Scattergl(
                x=t_clean[::stride],
                y=flux_arr[::stride],
                mode="markers",
                marker={"size": 2, "color": TEXT_MUTED, "opacity": 0.5},
                name="Out-of-Transit Continuum",
            )
        )
        if np.any(in_transit_mask):
            fig_mask.add_trace(
                go.Scattergl(
                    x=t_clean[in_transit_mask],
                    y=flux_arr[in_transit_mask],
                    mode="markers",
                    marker={"size": 3, "color": DANGER_COLOR},
                    name="Protected In-Transit Points",
                )
            )
        fig_mask.update_xaxes(title_text="Time [BKJD]")
        fig_mask.update_yaxes(title_text="Flux [e-/s]")
        apply_space_theme(fig_mask, f"Protected Transit Points ({np.sum(in_transit_mask):,} cadences masked)")
        st.plotly_chart(fig_mask, use_container_width=True)

    with tab3:
        st.markdown("#### Full Orbital Cycle Phase Fold (2001 Bins)")
        fig_g = plot_global_view(global_view, period=period)
        st.plotly_chart(fig_g, use_container_width=True)

    with tab4:
        st.markdown("#### Zoomed Transit Profile (201 Bins)")
        fig_l = plot_local_view(local_view, duration_hours=duration)
        st.plotly_chart(fig_l, use_container_width=True)

    with tab5:
        st.markdown("#### Binned vs Unbinned Phase Curve Comparison")
        fig_binned = go.Figure()
        # Unbinned cadences (downsampled if very dense)
        stride_unb = max(1, len(phases_all) // 8000)
        fig_binned.add_trace(
            go.Scattergl(
                x=phases_all[::stride_unb],
                y=sorted_fluxes[::stride_unb],
                mode="markers",
                marker={"size": 2.5, "color": TEXT_MUTED, "opacity": 0.35},
                name="Individual Observation Cadences",
            )
        )
        # Binned curve overlay
        half_p = period / 2.0
        bin_phases = np.linspace(-half_p, half_p, 101)
        # Shift global view back to relative flux scale
        binned_flux_plot = 1.0 + global_view[::20] * (abs(np.min(sorted_fluxes) - 1.0))
        fig_binned.add_trace(
            go.Scatter(
                x=np.linspace(-half_p, half_p, len(binned_flux_plot)),
                y=binned_flux_plot,
                mode="lines+markers",
                line={"color": ACCENT_PRIMARY, "width": 2.5},
                marker={"size": 4, "color": ACCENT_PRIMARY},
                name="Median-Binned Phase Curve",
            )
        )
        fig_binned.update_xaxes(title_text="Orbital Phase [Days]")
        fig_binned.update_yaxes(title_text="Relative Flux")
        apply_space_theme(fig_binned, "Binned vs Unbinned Phase Folded Light Curve")
        st.plotly_chart(fig_binned, use_container_width=True)

    with tab6:
        st.markdown("#### Transit Depth Visualization & Analytic Profile Fit")
        dur_days = duration / 24.0
        zoom_window = 3.0 * dur_days
        in_zoom = (phases_all >= -zoom_window) & (phases_all <= zoom_window)

        fig_depth = go.Figure()
        fig_depth.add_trace(
            go.Scatter(
                x=phases_all[in_zoom] * 24.0,  # convert to hours
                y=sorted_fluxes[in_zoom],
                mode="markers",
                marker={"size": 3.5, "color": TEXT_MUTED, "opacity": 0.5},
                name="Photometric Measurements",
            )
        )

        # Simplified analytic transit curve model (trapezoidal / limb-darkened approximation)
        h_hours = np.linspace(-zoom_window * 24.0, zoom_window * 24.0, 300)
        estimated_depth = abs(1.0 - np.nanmin(sorted_fluxes[in_zoom])) if np.any(in_zoom) else 0.005
        # Ingress / bottom / egress
        tau = duration / 2.0
        ingress_time = tau * 0.3
        model_flux = np.ones_like(h_hours)
        for i, h in enumerate(h_hours):
            ah = abs(h)
            if ah < (tau - ingress_time):
                model_flux[i] = 1.0 - estimated_depth
            elif ah < tau:
                frac = (tau - ah) / ingress_time
                model_flux[i] = 1.0 - estimated_depth * frac

        fig_depth.add_trace(
            go.Scatter(
                x=h_hours,
                y=model_flux,
                mode="lines",
                line={"color": SUCCESS_COLOR, "width": 3},
                name=f"Analytic Transit Fit (Depth: {estimated_depth*1e6:.0f} ppm)",
            )
        )
        fig_depth.update_xaxes(title_text="Time from Mid-Transit [Hours]")
        fig_depth.update_yaxes(title_text="Relative Normalized Flux")
        apply_space_theme(fig_depth, f"Zoomed Transit Profile & Depth (Estimated: {estimated_depth*1e6:,.0f} ppm)")
        st.plotly_chart(fig_depth, use_container_width=True)

    with tab7:
        st.markdown("#### Export Processed Scientific Arrays")
        ecol1, ecol2 = st.columns(2)

        with ecol1:
            st.markdown("##### Global View Array [2001]")
            st.dataframe(pd.DataFrame({"bin_index": range(len(global_view)), "normalized_flux": global_view}), height=250)
            csv_g = pd.DataFrame({"normalized_flux": global_view}).to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Global View CSV", csv_g, f"kic_{star_choice}_global_view.csv", "text/csv")

        with ecol2:
            st.markdown("##### Local View Array [201]")
            st.dataframe(pd.DataFrame({"bin_index": range(len(local_view)), "normalized_flux": local_view}), height=250)
            csv_l = pd.DataFrame({"normalized_flux": local_view}).to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Local View CSV", csv_l, f"kic_{star_choice}_local_view.csv", "text/csv")
