"""Comprehensive model evaluation, baseline comparison, grouped bootstrap confidence intervals, and false positive analysis."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)
from torch.utils.data import DataLoader

from src.config import cfg
from src.baseline import compute_classification_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_cnn_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.50,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Compute all standard exoplanet classification metrics plus ROC and PR curves."""
    metrics = compute_classification_metrics(y_true, y_prob, threshold)

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)

    curves = {
        "roc": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
        "pr": {"precision": prec.tolist(), "recall": rec.tolist()},
        "probabilities": [float(p) for p in y_prob],
        "labels": [int(y) for y in y_true],
    }
    return metrics, curves


def compute_grouped_bootstrap_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    star_ids: np.ndarray,
    threshold: float = 0.50,
    n_bootstraps: int = 200,
    random_seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Compute 95% Confidence Intervals using grouped star-level bootstrap resampling.

    Resamples stars with replacement to reflect real astrophysical grouping variance.
    """
    np.random.seed(random_seed)
    unique_stars = np.unique(star_ids)
    n_stars = len(unique_stars)

    # Pre-index candidates by star
    star_indices = {s: np.where(star_ids == s)[0] for s in unique_stars}

    boot_auc = []
    boot_ap = []
    boot_f1 = []

    for _ in range(n_bootstraps):
        sampled_stars = np.random.choice(unique_stars, size=n_stars, replace=True)
        sample_idx = np.concatenate([star_indices[s] for s in sampled_stars])

        b_y = y_true[sample_idx]
        b_p = y_prob[sample_idx]

        if len(np.unique(b_y)) > 1:
            boot_auc.append(roc_auc_score(b_y, b_p))
            boot_ap.append(average_precision_score(b_y, b_p))
            b_pred = (b_p >= threshold).astype(int)
            boot_f1.append(f1_score(b_y, b_pred, zero_division=0))

    def get_ci(arr: list) -> Dict[str, float]:
        if not arr:
            return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}
        return {
            "mean": round(float(np.mean(arr)), 4),
            "ci_lower": round(float(np.percentile(arr, 2.5)), 4),
            "ci_upper": round(float(np.percentile(arr, 97.5)), 4),
        }

    return {
        "roc_auc": get_ci(boot_auc),
        "average_precision": get_ci(boot_ap),
        "f1_score": get_ci(boot_f1),
    }


def analyze_false_positives_and_negatives(
    df_test: pd.DataFrame,
    y_prob: np.ndarray,
    threshold: float = 0.50,
) -> Dict[str, Any]:
    """Inspect misclassifications to diagnose astrophysical and instrumental failure modes.

    Investigates:
    - False Positives (predicted planet, but ground truth is AFP or NTP)
      (e.g., eclipsing binaries, stellar variability)
    - False Negatives (actual planet candidate missed)
      (e.g., shallow transits, long periods with low SNR)
    """
    df = df_test.copy()
    df["probability"] = y_prob
    df["predicted"] = (y_prob >= threshold).astype(int)

    fp_mask = (df["planet"] == 0) & (df["predicted"] == 1)
    fn_mask = (df["planet"] == 1) & (df["predicted"] == 0)

    df_fp = df[fp_mask]
    df_fn = df[fn_mask]

    # Analysis characteristics
    fp_summary = {
        "count": int(len(df_fp)),
        "mean_period": round(float(df_fp["tce_period"].mean()), 2) if len(df_fp) > 0 else 0.0,
        "mean_depth_ppm": round(float(df_fp["tce_depth"].mean()), 2) if len(df_fp) > 0 else 0.0,
        "afp_count": int((df_fp["av_training_set"] == "AFP").sum()) if "av_training_set" in df_fp.columns else 0,
        "ntp_count": int((df_fp["av_training_set"] == "NTP").sum()) if "av_training_set" in df_fp.columns else 0,
        "top_examples": df_fp[["kepid", "tce_plnt_num", "tce_period", "tce_depth", "probability"]].head(5).to_dict(orient="records") if len(df_fp) > 0 else [],
    }

    fn_summary = {
        "count": int(len(df_fn)),
        "mean_period": round(float(df_fn["tce_period"].mean()), 2) if len(df_fn) > 0 else 0.0,
        "mean_depth_ppm": round(float(df_fn["tce_depth"].mean()), 2) if len(df_fn) > 0 else 0.0,
        "top_examples": df_fn[["kepid", "tce_plnt_num", "tce_period", "tce_depth", "probability"]].head(5).to_dict(orient="records") if len(df_fn) > 0 else [],
    }

    return {
        "false_positives": fp_summary,
        "false_negatives": fn_summary,
        "threshold_used": threshold,
    }


def compare_models(
    baseline_metrics: Dict[str, Any],
    cnn_metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate side-by-side comparison between Baseline and Dual-View CNN."""
    keys = ["roc_auc", "average_precision", "precision", "recall", "f1_score", "specificity"]
    comparison = {}
    for k in keys:
        b_val = baseline_metrics.get(k, 0.0)
        c_val = cnn_metrics.get(k, 0.0)
        diff = round(c_val - b_val, 4)
        comparison[k] = {
            "baseline": b_val,
            "cnn": c_val,
            "absolute_delta": diff,
            "relative_improvement_pct": round((diff / b_val * 100), 2) if b_val > 0 else 0.0,
        }
    return comparison

