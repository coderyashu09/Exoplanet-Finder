"""PAGE 5 — CANDIDATE EXPLORER: Searchable database of 15,737 Kepler DR24 TCE candidates."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.baseline import BaselinePipeline
from app.components.styling import apply_custom_css, render_hero
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Candidate Explorer | Exoplanet Finder",
    page_icon="🔍",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()
threshold = controls["threshold"]

render_hero(
    title="CANDIDATE EXPLORER",
    tagline="Search, filter, and inspect 15,737 Kepler DR24 Threshold Crossing Events with ML inference.",
    badges=[
        ("DR24 Archive", "badge-nasa"),
        ("Multi-Parameter Filter", "badge-pc"),
        ("CSV Export", "badge-pc"),
    ],
)


@st.cache_data
def load_data():
    p = cfg.processed_dir / "tce_cleaned.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


@st.cache_resource
def load_baseline():
    try:
        return BaselinePipeline().load()
    except Exception:
        return None


df_all = load_data()
baseline = load_baseline()

if len(df_all) == 0:
    st.error("Cleaned TCE dataset not found. Please run scripts/prepare_dataset.py first.")
    st.stop()

# Filter Bar
st.markdown("### 🔍 Filters & Search Parameters")
fcol1, fcol2, fcol3, fcol4 = st.columns(4)

with fcol1:
    search_kepid = st.text_input("Search KIC ID", "", placeholder="e.g. 11442793")

with fcol2:
    label_filter = st.multiselect(
        "NASA DR24 Label",
        options=["PC", "AFP", "NTP"],
        default=["PC", "AFP", "NTP"],
        help="PC = Planet Candidate, AFP = Astrophysical False Positive, NTP = Non-Transiting Phenomenon",
    )

with fcol3:
    min_p, max_p = float(df_all["tce_period"].min()), float(df_all["tce_period"].max())
    period_range = st.slider(
        "Orbital Period [days]",
        min_value=0.5,
        max_value=round(max_p, 1),
        value=(0.5, 365.0),
    )

with fcol4:
    min_d, max_d = float(df_all["tce_duration"].min()), float(df_all["tce_duration"].max())
    duration_range = st.slider(
        "Transit Duration [hours]",
        min_value=round(min_d, 1),
        max_value=round(max_d, 1),
        value=(round(min_d, 1), 30.0),
    )

# Apply filters
filtered_df = df_all.copy()

if search_kepid.strip():
    try:
        kid_val = int(search_kepid.strip())
        filtered_df = filtered_df[filtered_df["kepid"] == kid_val]
    except ValueError:
        st.warning("Please enter a numeric Kepler ID.")

if label_filter:
    filtered_df = filtered_df[filtered_df["av_training_set"].isin(label_filter)]

filtered_df = filtered_df[
    (filtered_df["tce_period"] >= period_range[0])
    & (filtered_df["tce_period"] <= period_range[1])
    & (filtered_df["tce_duration"] >= duration_range[0])
    & (filtered_df["tce_duration"] <= duration_range[1])
]

# Compute ML Predictions for visible batch
st.markdown(f"#### Results: **{len(filtered_df):,}** matching candidates found")

# Sorting options
sort_col = st.selectbox(
    "Sort By",
    ["tce_period", "tce_duration", "tce_depth", "tce_model_snr"],
    format_func=lambda x: {
        "tce_period": "Orbital Period (Days)",
        "tce_duration": "Transit Duration (Hours)",
        "tce_depth": "Transit Depth (ppm)",
        "tce_model_snr": "Signal-to-Noise Ratio (SNR)",
    }.get(x, x),
)
sort_asc = st.checkbox("Ascending Order", value=True)
filtered_df = filtered_df.sort_values(by=sort_col, ascending=sort_asc)

# Pagination
PAGE_SIZE = 50
total_pages = max(1, (len(filtered_df) + PAGE_SIZE - 1) // PAGE_SIZE)
pcol1, pcol2 = st.columns([1, 4])
with pcol1:
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
with pcol2:
    st.write(f"Showing page {page_num} of {total_pages}")

start_idx = (page_num - 1) * PAGE_SIZE
end_idx = start_idx + PAGE_SIZE
page_df = filtered_df.iloc[start_idx:end_idx].copy()

# Add baseline ML prediction on visible page
if baseline is not None and baseline.is_trained:
    feats = baseline.extractor.transform(page_df)
    page_df["ML_Probability"] = np.round(baseline.model.predict_proba(feats)[:, 1], 4)
    page_df["ML_Prediction"] = np.where(page_df["ML_Probability"] >= threshold, "Planet Candidate", "False Positive")
else:
    page_df["ML_Probability"] = "N/A"
    page_df["ML_Prediction"] = "N/A"

display_cols = [
    "kepid",
    "tce_plnt_num",
    "av_training_set",
    "tce_period",
    "tce_duration",
    "tce_depth",
    "tce_model_snr",
    "ML_Probability",
    "ML_Prediction",
]

col_renames = {
    "kepid": "Kepler ID (KIC)",
    "tce_plnt_num": "TCE #",
    "av_training_set": "NASA Label",
    "tce_period": "Period [d]",
    "tce_duration": "Duration [hrs]",
    "tce_depth": "Depth [ppm]",
    "tce_model_snr": "Model SNR",
    "ML_Probability": "ML Probability",
    "ML_Prediction": "ML Verdict",
}

st.dataframe(
    page_df[display_cols].rename(columns=col_renames),
    use_container_width=True,
    height=480,
)

# Export filtered data
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"📥 Export All Filtered Results ({len(filtered_df):,} TCEs) to CSV",
    data=csv_bytes,
    file_name="kepler_dr24_filtered_candidates.csv",
    mime="text/csv",
)

