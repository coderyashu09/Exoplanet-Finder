"""PAGE 8 — DATA MANAGEMENT: Data integrity audit, cache inspection, and maintenance operations."""
import shutil
from pathlib import Path
import pandas as pd
import streamlit as st

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache
from app.components.styling import apply_custom_css, render_hero, render_metric_card, render_alert
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Data Management | Exoplanet Finder",
    page_icon="💾",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()

render_hero(
    title="DATA MANAGEMENT & INTEGRITY",
    tagline="Audit NASA catalog files, inspect persistent photometric cache, and maintain scientific pipeline artifacts.",
    badges=[
        ("Integrity Guard", "badge-pc"),
        ("Zero Overwrite Policy", "badge-nasa"),
        ("Parquet Storage", "badge-pc"),
    ],
)

cache = LightCurveCache()
cached_stars = cache.list_cached_stars()

# Storage Audit Cards
st.markdown("### 🗄️ Dataset Files & Storage Audit")
m1, m2, m3, m4 = st.columns(4)

raw_size = cfg.original_data_file.stat().st_size / (1024 * 1024) if cfg.original_data_file.exists() else 0.0
catalog_size = cfg.tce_catalog_file.stat().st_size / (1024 * 1024) if cfg.tce_catalog_file.exists() else 0.0

lc_files = list(cfg.lightcurves_dir.glob("*.parquet"))
lc_total_size = sum(f.stat().st_size for f in lc_files) / (1024 * 1024) if lc_files else 0.0

with m1:
    render_metric_card("Original NASA File", f"{raw_size:.2f} MB", cfg.original_data_file.name, "blue")
with m2:
    render_metric_card("Complete DR24 Catalog", f"{catalog_size:.2f} MB", cfg.tce_catalog_file.name, "purple")
with m3:
    render_metric_card("Photometric Cache", f"{lc_total_size:.2f} MB", f"{len(cached_stars)} Stars Stored", "green")
with m4:
    render_metric_card("Processed Data", "Cleaned Splits", "Train / Val / Test (80/10/10)", "amber")

st.markdown("---")

# Cached Stars Table & Inspection
st.markdown("### 🔭 Cached Kepler Stars on Disk")
if cached_stars:
    star_records = []
    for kid in cached_stars:
        p = cfg.lightcurves_dir / f"kic_{kid}.parquet"
        sz_kb = p.stat().st_size / 1024 if p.exists() else 0
        star_records.append({
            "Kepler ID (KIC)": kid,
            "File Name": p.name,
            "File Size [KB]": f"{sz_kb:.1f} KB",
            "Target Note": "Kepler-90 (8 planets)" if kid == cfg.kepler90_kepid else "Kepler Science Target",
        })
    st.dataframe(pd.DataFrame(star_records), use_container_width=True)
else:
    st.info("No light curves are cached on disk yet. Download using scripts/download_lightcurves.py or Exoplanet Detector page.")

st.markdown("---")

# Safe Maintenance Controls
st.markdown("### 🛡️ Pipeline Maintenance Operations")
render_alert(
    "<b>Engineering Safety Guarantee:</b> Original NASA datasets in <code>Data/</code> and <code>Data/raw/</code> are strictly protected and will NEVER be deleted by maintenance routines.",
    "info",
)

col_act1, col_act2 = st.columns(2)

with col_act1:
    st.markdown("#### Refresh Processed Splits & Views")
    st.write("Re-runs data cleaning and grouped star splitting without affecting raw datasets.")
    if st.button("🔄 Re-generate Processed Splits"):
        with st.spinner("Re-generating clean splits..."):
            from scripts.prepare_dataset import main as prep_main
            prep_main()
            st.success("Splits and cleaning audits successfully re-generated!")

with col_act2:
    st.markdown("#### Temporary Preprocessing Cache Maintenance")
    st.write("Clears pre-computed numpy view files (`cnn_views_*.npz`) in `Data/processed/`.")
    if st.button("🧹 Clear Pre-Computed View Cache"):
        for f in cfg.processed_dir.glob("cnn_views_*.npz"):
            f.unlink(missing_ok=True)
        st.success("Pre-computed CNN view cache cleared safely. Raw and parquet data remains intact.")

