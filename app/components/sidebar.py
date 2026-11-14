"""Persistent sidebar navigation, model status, and mission telemetry controls."""
import json
from pathlib import Path
import streamlit as st

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache


def render_sidebar() -> dict:
    """Render the master mission control sidebar with telemetry and configuration."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <div style="font-size: 1.3rem; font-weight: 800; color: #63B3FF; letter-spacing: 0.05em;">
                    🌌 EXOPLANET FINDER
                </div>
                <div style="font-size: 0.75rem; color: #9AAAC1; margin-top: 4px;">
                    NASA Kepler Mission DR24 AI
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🛰️ Mission Telemetry")

        # Cache status
        cache = LightCurveCache()
        cached_stars = cache.list_cached_stars()
        st.metric(label="Cached Stellar Systems", value=f"{len(cached_stars):,}")

        # Model Status
        baseline_file = cfg.metrics_dir / "baseline_metrics.json"
        cnn_file = cfg.metrics_dir / "cnn_metrics.json"
        thresh_file = cfg.metadata_dir / "classification_threshold.json"

        st.markdown("---")
        st.markdown("### 🧠 Neural Intelligence")

        if baseline_file.exists():
            with open(baseline_file, "r", encoding="utf-8") as f:
                b_metrics = json.load(f)
            st.markdown(
                f"""
                <div style="background: #111C30; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #FFBE55; margin-bottom: 8px;">
                    <div style="font-size: 0.72rem; color: #9AAAC1;">BASELINE MODEL</div>
                    <div style="font-size: 0.92rem; font-weight: 600; color: #F4F7FF;">HistGradientBoosting</div>
                    <div style="font-size: 0.75rem; color: #35D49A;">ROC-AUC: {b_metrics.get('roc_auc', 0.0):.4f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        cnn_ckpt = cfg.checkpoints_dir / "best_model.pth"
        if cnn_ckpt.exists() and cnn_file.exists():
            with open(cnn_file, "r", encoding="utf-8") as f:
                c_metrics = json.load(f)
            st.markdown(
                f"""
                <div style="background: #111C30; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #63B3FF; margin-bottom: 8px;">
                    <div style="font-size: 0.72rem; color: #9AAAC1;">TWO-VIEW 1D CNN</div>
                    <div style="font-size: 0.92rem; font-weight: 600; color: #F4F7FF;">Dual-Branch Deep Net</div>
                    <div style="font-size: 0.75rem; color: #35D49A;">ROC-AUC: {c_metrics.get('roc_auc', 0.0):.4f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif cnn_ckpt.exists():
            st.markdown(
                """
                <div style="background: #111C30; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #35D49A; margin-bottom: 8px;">
                    <div style="font-size: 0.72rem; color: #9AAAC1;">TWO-VIEW 1D CNN</div>
                    <div style="font-size: 0.92rem; font-weight: 600; color: #F4F7FF;">Checkpoint Ready</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="background: #111C30; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #9AAAC1; margin-bottom: 8px;">
                    <div style="font-size: 0.72rem; color: #9AAAC1;">TWO-VIEW 1D CNN</div>
                    <div style="font-size: 0.85rem; color: #9AAAC1;">Awaiting Training</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### ⚙️ Inference Controls")

        # Threshold slider
        default_thresh = 0.50
        if thresh_file.exists():
            try:
                with open(thresh_file, "r", encoding="utf-8") as f:
                    default_thresh = float(json.load(f).get("threshold", 0.50))
            except Exception:
                pass

        threshold = st.slider(
            "Classification Threshold",
            min_value=0.10,
            max_value=0.90,
            value=float(default_thresh),
            step=0.01,
            help="Threshold separating Planet-like Signals from Non-Planet False Positives.",
        )

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size: 0.72rem; color: #62728D; line-height: 1.4;">
                <b>Scientific Disclaimer:</b> Model outputs designate planetary-like periodic transit signatures. They do not constitute official planetary confirmation without spectroscopic ground-based follow-up.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return {"threshold": threshold, "cached_stars_count": len(cached_stars)}

