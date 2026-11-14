"""Model Intelligence Center router: metrics, comparison, training curves, ROC/PR curves."""
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from fastapi import APIRouter

from src.config import cfg

router = APIRouter(prefix="/api/models", tags=["Models"])


def _downsample_curve(x_list: List[float], y_list: List[float], target_pts: int = 150) -> Dict[str, List[float]]:
    if len(x_list) <= target_pts:
        return {"x": [round(float(v), 5) for v in x_list], "y": [round(float(v), 5) for v in y_list]}
    indices = np.linspace(0, len(x_list) - 1, target_pts).astype(int)
    # Ensure first and last points are included
    indices[0] = 0
    indices[-1] = len(x_list) - 1
    return {
        "x": [round(float(x_list[i]), 5) for i in indices],
        "y": [round(float(y_list[i]), 5) for i in indices],
    }


@router.get("/comparison")
def get_model_comparison() -> Dict[str, Any]:
    metrics_dir = cfg.outputs_dir / "metrics"
    meta_dir = cfg.metadata_dir

    # 1. Comparison table
    comp_data = {}
    comp_file = metrics_dir / "model_comparison.json"
    if comp_file.exists():
        with open(comp_file, "r", encoding="utf-8") as f:
            comp_data = json.load(f)

    # 2. Baseline metrics & confusion matrix
    baseline_metrics = {}
    base_file = metrics_dir / "baseline_metrics.json"
    if base_file.exists():
        with open(base_file, "r", encoding="utf-8") as f:
            baseline_metrics = json.load(f)

    # 3. CNN metrics & confusion matrix
    cnn_metrics = {}
    cnn_file = metrics_dir / "cnn_metrics.json"
    if cnn_file.exists():
        with open(cnn_file, "r", encoding="utf-8") as f:
            cnn_metrics = json.load(f)

    # 4. Training history
    history = {}
    hist_file = meta_dir / "training_history.json"
    if hist_file.exists():
        with open(hist_file, "r", encoding="utf-8") as f:
            history = json.load(f)

    # 5. ROC and PR curves
    curves = {"baseline": {}, "cnn": {}}

    base_curves_file = metrics_dir / "baseline_curves.json"
    if base_curves_file.exists():
        with open(base_curves_file, "r", encoding="utf-8") as f:
            b_data = json.load(f)
            roc_b = b_data.get("roc", {})
            pr_b = b_data.get("pr", {})
            curves["baseline"]["roc"] = _downsample_curve(roc_b.get("fpr", []), roc_b.get("tpr", []))
            curves["baseline"]["pr"] = _downsample_curve(pr_b.get("recall", []), pr_b.get("precision", []))

    cnn_curves_file = metrics_dir / "cnn_curves.json"
    if cnn_curves_file.exists():
        with open(cnn_curves_file, "r", encoding="utf-8") as f:
            c_data = json.load(f)
            roc_c = c_data.get("roc", {})
            pr_c = c_data.get("pr", {})
            curves["cnn"]["roc"] = _downsample_curve(roc_c.get("fpr", []), roc_c.get("tpr", []))
            curves["cnn"]["pr"] = _downsample_curve(pr_c.get("recall", []), pr_c.get("precision", []))

    return {
        "comparison": comp_data,
        "baseline_metrics": baseline_metrics,
        "cnn_metrics": cnn_metrics,
        "training_history": history,
        "curves": curves,
    }

