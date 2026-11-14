"""PAGE 7 — EXPERIMENT HISTORY: Reproducible experiment registry backed by SQLite database."""
import json
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.experiment_tracker import ExperimentTracker
from src.visualization import apply_space_theme, ACCENT_PRIMARY, SUCCESS_COLOR
from app.components.styling import apply_custom_css, render_hero, render_metric_card
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Experiment History | Exoplanet Finder",
    page_icon="📜",
    layout="wide",
)

apply_custom_css()
controls = render_sidebar()

render_hero(
    title="EXPERIMENT HISTORY & REPRODUCIBILITY",
    tagline="Complete registry of AI/ML training runs, hyperparameters, validation benchmarks, and test evaluation metrics.",
    badges=[
        ("SQLite Registry", "badge-nasa"),
        ("Reproducibility", "badge-pc"),
        ("Run Comparison", "badge-pc"),
    ],
)

tracker = ExperimentTracker()
df_exp = tracker.get_all_experiments()

if len(df_exp) == 0:
    st.info("No training experiments recorded yet. Run `python scripts/train_model.py` to log a training experiment.")
    st.stop()

# Summary Metrics
st.markdown("### 📊 Experiment Overview")
m1, m2, m3, m4 = st.columns(4)

with m1:
    render_metric_card("Total Experiments", f"{len(df_exp)}", "Logged in SQLite", "blue")
with m2:
    best_auc = df_exp["test_auc"].max() if "test_auc" in df_exp.columns else 0.0
    render_metric_card("Best Test ROC-AUC", f"{best_auc:.4f}", "Across all runs", "green")
with m3:
    best_f1 = df_exp["f1_score"].max() if "f1_score" in df_exp.columns else 0.0
    render_metric_card("Best Test F1-Score", f"{best_f1:.4f}", "Planet Class", "purple")
with m4:
    latest_run = df_exp.iloc[0]["timestamp"] if len(df_exp) > 0 else "N/A"
    render_metric_card("Latest Training Run", str(latest_run).split(" ")[0], str(latest_run).split(" ")[-1] if " " in str(latest_run) else "", "amber")

st.markdown("---")

# Experiment Progression Chart
st.markdown("### 📈 Test Performance Progression Over Time")
if "timestamp" in df_exp.columns and "test_auc" in df_exp.columns:
    df_chart = df_exp.sort_values(by="timestamp").copy()
    fig = px.line(
        df_chart,
        x="timestamp",
        y="test_auc",
        color="model_type",
        markers=True,
        title="Test ROC-AUC across Experiment Runs",
        labels={"timestamp": "Execution Timestamp", "test_auc": "Test ROC-AUC"},
        color_discrete_map={"HistGradientBoostingClassifier": "#FFBE55", "DualViewExoplanetCNN": ACCENT_PRIMARY},
    )
    apply_space_theme(fig, "Test ROC-AUC by Model Version", height=380)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Experiment Table
st.markdown("### 📋 Experiment Registry Table")
display_cols = [
    "experiment_id",
    "timestamp",
    "model_type",
    "test_auc",
    "average_precision",
    "f1_score",
    "training_duration",
    "model_version",
    "random_seed",
]

col_renames = {
    "experiment_id": "Experiment ID",
    "timestamp": "Timestamp",
    "model_type": "Architecture",
    "test_auc": "Test AUC",
    "average_precision": "Avg Precision",
    "f1_score": "F1 Score",
    "training_duration": "Duration [s]",
    "model_version": "Version",
    "random_seed": "Seed",
}

st.dataframe(
    df_exp[display_cols].rename(columns=col_renames),
    use_container_width=True,
)

# Detailed Experiment Inspector
st.markdown("---")
st.markdown("### 🔍 Experiment Deep-Dive Inspector")

exp_ids = df_exp["experiment_id"].tolist()
chosen_exp_id = st.selectbox("Select Experiment to Inspect Details", exp_ids)
exp_detail = tracker.get_experiment_by_id(chosen_exp_id)

if exp_detail:
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.markdown(f"#### Run Metadata: `{chosen_exp_id}`")
        st.write(f"**Model Architecture:** {exp_detail.get('model_type')}")
        st.write(f"**Date & Time:** {exp_detail.get('timestamp')}")
        st.write(f"**Model Artifact Location:** `{exp_detail.get('model_path')}`")
        st.write(f"**Dataset Version:** {exp_detail.get('dataset_version')}")
        st.write(f"**Random Seed:** {exp_detail.get('random_seed')}")
        st.write(f"**Training Duration:** {exp_detail.get('training_duration')} seconds")

    with dcol2:
        st.markdown("#### Hyperparameter Configuration")
        params = exp_detail.get("parameters", {})
        st.json(params)

