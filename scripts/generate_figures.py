"""Generate publication-grade figures and predictions for outputs/ directory."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve
from src.phase_folding import generate_two_views
from src.baseline import BaselinePipeline
from src.predict import ExoplanetPredictor
from src.visualization import (
    plot_roc_curves_comparison,
    plot_pr_curves_comparison,
    plot_confusion_matrix,
    plot_global_view,
    plot_local_view,
    plot_dataset_distributions,
    apply_space_theme,
)


def main():
    print("Generating publication-grade research figures in outputs/figures/...")
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Metrics & Curves
    b_metrics = json.load(open(cfg.metrics_dir / "baseline_metrics.json"))
    b_curves = json.load(open(cfg.metrics_dir / "baseline_curves.json"))
    c_metrics = json.load(open(cfg.metrics_dir / "cnn_metrics.json"))
    c_curves = json.load(open(cfg.metrics_dir / "cnn_curves.json"))

    # ROC comparison
    fig_roc = plot_roc_curves_comparison(
        baseline_fpr=b_curves["roc"]["fpr"],
        baseline_tpr=b_curves["roc"]["tpr"],
        baseline_auc=b_metrics["roc_auc"],
        cnn_fpr=c_curves["roc"]["fpr"],
        cnn_tpr=c_curves["roc"]["tpr"],
        cnn_auc=c_metrics["roc_auc"],
    )
    fig_roc.write_html(str(cfg.figures_dir / "roc_curve_comparison.html"))

    # PR comparison
    fig_pr = plot_pr_curves_comparison(
        baseline_rec=b_curves["pr"]["recall"],
        baseline_prec=b_curves["pr"]["precision"],
        baseline_ap=b_metrics["average_precision"],
        cnn_rec=c_curves["pr"]["recall"],
        cnn_prec=c_curves["pr"]["precision"],
        cnn_ap=c_metrics["average_precision"],
    )
    fig_pr.write_html(str(cfg.figures_dir / "precision_recall_comparison.html"))

    # Confusion matrix
    fig_cm = plot_confusion_matrix(b_metrics["confusion_matrix"], title="Baseline HistGB — Confusion Matrix")
    fig_cm.write_html(str(cfg.figures_dir / "confusion_matrix_baseline.html"))

    # 2. Kepler-90 Transit Profile
    cache = LightCurveCache()
    t, f, _, _ = download_stellar_lightcurve(cfg.kepler90_kepid, cache=cache)
    if t is not None:
        t_clean = validate_and_align_time_system(t)
        flat_f, _, _ = flatten_lightcurve(t_clean, f, period=14.449, t0=133.0, duration_hours=3.5)
        g_view, l_view, _ = generate_two_views(t_clean, flat_f, period=14.449, t0=133.0, duration_hours=3.5)
        fig_g = plot_global_view(g_view, period=14.449)
        fig_g.write_html(str(cfg.figures_dir / "kepler90_global_view.html"))
        fig_l = plot_local_view(l_view, duration_hours=3.5)
        fig_l.write_html(str(cfg.figures_dir / "kepler90_local_view.html"))

    # 3. Dataset Distributions
    df_clean = pd.read_csv(cfg.processed_dir / "tce_cleaned.csv")
    dist_figs = plot_dataset_distributions(df_clean)
    for name, f_obj in dist_figs.items():
        f_obj.write_html(str(cfg.figures_dir / f"{name}.html"))

    # 4. Generate Predictions Batch File
    print("Generating candidate predictions table in outputs/predictions/...")
    pipe = BaselinePipeline().load()
    sample_df = df_clean.head(100).copy()
    feats = pipe.extractor.transform(sample_df)
    sample_df["ML_Probability"] = np.round(pipe.model.predict_proba(feats)[:, 1], 4)
    sample_df["ML_Prediction"] = np.where(sample_df["ML_Probability"] >= pipe.optimal_threshold, "Planet Candidate", "False Positive")
    sample_df.to_csv(cfg.predictions_dir / "sample_predictions_top100.csv", index=False)

    print("All figures and predictions generated successfully in outputs/!")


if __name__ == "__main__":
    main()

