"""Baseline Machine Learning Model using HistGradientBoostingClassifier."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
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

from src.config import cfg
from src.feature_engineering import BaselineFeatureExtractor, BASELINE_FEATURES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """Compute comprehensive classification performance metrics."""
    y_pred = (y_prob >= threshold).astype(int)

    roc_auc = float(roc_auc_score(y_true, y_prob))
    avg_precision = float(average_precision_score(y_true, y_prob))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    return {
        "roc_auc": round(roc_auc, 4),
        "average_precision": round(avg_precision, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "specificity": round(specificity, 4),
        "threshold": round(threshold, 4),
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
    }


def find_optimal_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Find the classification threshold that maximizes F1 score on validation set."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, y_prob)
    # Handle zero division
    f1_scores = np.zeros_like(thresholds)
    for i, t in enumerate(thresholds):
        p, r = precisions[i], recalls[i]
        f1_scores[i] = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

    best_idx = int(np.argmax(f1_scores)) if len(f1_scores) > 0 else 0
    best_thresh = float(thresholds[best_idx]) if len(thresholds) > 0 else 0.50
    return max(0.1, min(0.9, best_thresh))


class BaselinePipeline:
    """End-to-end baseline model trainer and evaluator."""

    def __init__(self):
        self.extractor = BaselineFeatureExtractor(BASELINE_FEATURES)
        self.model = HistGradientBoostingClassifier(
            random_state=cfg.baseline_random_state,
            max_iter=cfg.baseline_max_iter,
            learning_rate=cfg.baseline_learning_rate,
            max_leaf_nodes=cfg.baseline_max_leaf_nodes,
            class_weight="balanced",
        )
        self.optimal_threshold: float = 0.50
        self.is_trained = False

    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame) -> Dict[str, Any]:
        logger.info(f"Training Baseline HistGradientBoosting on {len(df_train)} training records...")
        self.extractor.fit(df_train)
        X_train = self.extractor.transform(df_train)
        y_train = df_train["planet"].to_numpy().astype(int)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate on validation to find optimal threshold
        X_val = self.extractor.transform(df_val)
        y_val = df_val["planet"].to_numpy().astype(int)
        val_probs = self.model.predict_proba(X_val)[:, 1]

        self.optimal_threshold = find_optimal_threshold(y_val, val_probs)
        logger.info(f"Optimal validation threshold: {self.optimal_threshold:.4f}")

        val_metrics = compute_classification_metrics(y_val, val_probs, self.optimal_threshold)
        logger.info(f"Validation Performance: ROC-AUC={val_metrics['roc_auc']}, F1={val_metrics['f1_score']}")
        return val_metrics

    def evaluate(self, df_test: pd.DataFrame) -> Dict[str, Any]:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before evaluation.")
        X_test = self.extractor.transform(df_test)
        y_test = df_test["planet"].to_numpy().astype(int)
        test_probs = self.model.predict_proba(X_test)[:, 1]

        metrics = compute_classification_metrics(y_test, test_probs, self.optimal_threshold)

        # Compute ROC and PR curves
        fpr, tpr, roc_thresh = roc_curve(y_test, test_probs)
        prec, rec, pr_thresh = precision_recall_curve(y_test, test_probs)

        curve_data = {
            "roc": {
                "fpr": fpr.tolist(),
                "tpr": tpr.tolist(),
            },
            "pr": {
                "precision": prec.tolist(),
                "recall": rec.tolist(),
            },
            "probabilities": test_probs.tolist(),
            "labels": y_test.tolist(),
        }

        logger.info(f"Test Set Performance: ROC-AUC={metrics['roc_auc']}, AvgPrec={metrics['average_precision']}, F1={metrics['f1_score']}")
        return {"metrics": metrics, "curves": curve_data}

    def predict_single(self, period: float, duration: float, depth: float) -> Tuple[float, int]:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before inference.")
        df_single = pd.DataFrame([{
            "tce_period": period,
            "tce_duration": duration,
            "tce_depth": depth,
        }])
        X_feat = self.extractor.transform(df_single)
        prob = float(self.model.predict_proba(X_feat)[0, 1])
        pred = int(prob >= self.optimal_threshold)
        return prob, pred

    def save(self) -> None:
        cfg.baseline_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, cfg.baseline_dir / "baseline_model.joblib")
        joblib.dump(self.extractor, cfg.baseline_dir / "feature_extractor.joblib")
        with open(cfg.baseline_dir / "baseline_threshold.json", "w", encoding="utf-8") as f:
            json.dump({"threshold": self.optimal_threshold}, f, indent=2)
        logger.info(f"Saved baseline artifacts to {cfg.baseline_dir}")

    def load(self) -> "BaselinePipeline":
        model_path = cfg.baseline_dir / "baseline_model.joblib"
        extractor_path = cfg.baseline_dir / "feature_extractor.joblib"
        threshold_path = cfg.baseline_dir / "baseline_threshold.json"

        if not (model_path.exists() and extractor_path.exists()):
            raise FileNotFoundError(f"Baseline artifacts not found in {cfg.baseline_dir}")

        self.model = joblib.load(model_path)
        self.extractor = joblib.load(extractor_path)
        if threshold_path.exists():
            with open(threshold_path, "r", encoding="utf-8") as f:
                self.optimal_threshold = json.load(f).get("threshold", 0.50)
        self.is_trained = True
        logger.info("Loaded baseline model and feature extractor successfully.")
        return self

