"""Model evaluation script: compare baseline and CNN, run bootstrap CI and error analysis."""
import json
import logging
import sys
from pathlib import Path

import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.baseline import BaselinePipeline
from src.evaluate import (
    compare_models,
    compute_grouped_bootstrap_ci,
    analyze_false_positives_and_negatives,
    evaluate_cnn_predictions,
)
from src.predict import ExoplanetPredictor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("EXOPLANET FINDER — COMPREHENSIVE MODEL EVALUATION")
    logger.info("=" * 70)

    test_path = cfg.processed_dir / "tce_test.csv"
    if not test_path.exists():
        logger.error(f"Test split not found at {test_path}")
        sys.exit(1)

    df_test = pd.read_csv(test_path)
    logger.info(f"Loaded {len(df_test)} test TCEs from {df_test['kepid'].nunique()} unique stars.")

    # 1. Baseline Evaluation
    baseline_metrics = None
    baseline_file = cfg.metrics_dir / "baseline_metrics.json"
    if baseline_file.exists():
        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline_metrics = json.load(f)
        logger.info(f"Loaded Baseline test metrics: ROC-AUC={baseline_metrics['roc_auc']}, AvgPrec={baseline_metrics['average_precision']}")
    else:
        logger.info("Evaluating baseline model...")
        pipeline = BaselinePipeline().load()
        res = pipeline.evaluate(df_test)
        baseline_metrics = res["metrics"]

    # 2. CNN Evaluation
    cnn_metrics = None
    cnn_file = cfg.metrics_dir / "cnn_metrics.json"
    if cnn_file.exists():
        with open(cnn_file, "r", encoding="utf-8") as f:
            cnn_metrics = json.load(f)
        logger.info(f"Loaded CNN test metrics: ROC-AUC={cnn_metrics['roc_auc']}, AvgPrec={cnn_metrics['average_precision']}")

    # 3. Model Comparison
    if baseline_metrics and cnn_metrics:
        comparison = compare_models(baseline_metrics, cnn_metrics)
        logger.info("\n" + "=" * 50)
        logger.info("MODEL COMPARISON (Baseline vs Dual-View CNN):")
        logger.info(f"{'Metric':<20} | {'Baseline':<10} | {'CNN':<10} | {'Delta':<10}")
        logger.info("-" * 55)
        for metric, vals in comparison.items():
            logger.info(f"{metric:<20} | {vals['baseline']:<10.4f} | {vals['cnn']:<10.4f} | {vals['absolute_delta']:<+10.4f}")
        logger.info("=" * 50)

        with open(cfg.metrics_dir / "model_comparison.json", "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2)

    # 4. Error Analysis
    if baseline_file.exists():
        curves_file = cfg.metrics_dir / "baseline_curves.json"
        if curves_file.exists():
            with open(curves_file, "r", encoding="utf-8") as f:
                b_curves = json.load(f)
            y_probs = b_curves.get("probabilities", [])
            if len(y_probs) == len(df_test):
                err_analysis = analyze_false_positives_and_negatives(
                    df_test, y_prob=pd.Series(y_probs).to_numpy(), threshold=baseline_metrics.get("threshold", 0.5)
                )
                with open(cfg.metrics_dir / "error_analysis.json", "w", encoding="utf-8") as f:
                    json.dump(err_analysis, f, indent=2)
                logger.info(f"Error Analysis saved. False Positives: {err_analysis['false_positives']['count']}, False Negatives: {err_analysis['false_negatives']['count']}")

    logger.info("Evaluation complete. Metrics saved to outputs/metrics/")


if __name__ == "__main__":
    main()

