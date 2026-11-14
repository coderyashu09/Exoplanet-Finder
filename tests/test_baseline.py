"""Unit tests for tabular baseline feature engineering and classification pipeline."""
import numpy as np
import pandas as pd
import pytest

from src.feature_engineering import BaselineFeatureExtractor
from src.baseline import BaselinePipeline, compute_classification_metrics, find_optimal_threshold


def test_baseline_feature_extractor():
    """Verify feature extraction, log1p transformation, and scaling."""
    df_train = pd.DataFrame({
        "tce_period": [1.0, 10.0, 100.0],
        "tce_duration": [1.0, 3.0, 10.0],
        "tce_depth": [100.0, 1000.0, 10000.0],
        "planet": [1, 0, 1],
    })

    extractor = BaselineFeatureExtractor()
    extractor.fit(df_train)
    assert extractor.is_fitted is True

    X_train = extractor.transform(df_train)
    assert X_train.shape == (3, 3)
    assert np.all(np.isfinite(X_train))


def test_compute_classification_metrics():
    """Verify classification metrics calculation with controlled true and predicted values."""
    y_true = np.array([1, 1, 0, 0])
    y_prob = np.array([0.9, 0.8, 0.2, 0.1])

    metrics = compute_classification_metrics(y_true, y_prob, threshold=0.5)

    assert metrics["roc_auc"] == 1.0
    assert metrics["average_precision"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["specificity"] == 1.0
    assert metrics["confusion_matrix"]["tp"] == 2
    assert metrics["confusion_matrix"]["tn"] == 2
    assert metrics["confusion_matrix"]["fp"] == 0
    assert metrics["confusion_matrix"]["fn"] == 0


def test_find_optimal_threshold():
    """Verify threshold optimization finds a value between 0.1 and 0.9."""
    y_true = np.array([1, 1, 1, 0, 0, 0])
    y_prob = np.array([0.95, 0.85, 0.70, 0.60, 0.30, 0.10])

    thresh = find_optimal_threshold(y_true, y_prob)
    assert 0.1 <= thresh <= 0.9

