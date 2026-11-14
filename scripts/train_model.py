"""Model training script supporting Baseline HistGradientBoosting and Dual-View PyTorch CNN."""
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import cfg
from src.baseline import BaselinePipeline
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve
from src.phase_folding import generate_two_views
from src.model import DualViewExoplanetCNN
from src.dataset import ExoplanetDualViewDataset, create_dataloaders
from src.train import train_cnn_model, get_device
from src.evaluate import evaluate_cnn_predictions, compute_grouped_bootstrap_ci, compare_models
from src.experiment_tracker import ExperimentTracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def train_baseline_pipeline() -> Dict[str, Any]:
    """Train and evaluate the baseline HistGradientBoostingClassifier benchmark."""
    logger.info("=" * 70)
    logger.info("TRAINING BASELINE HIST-GRADIENT-BOOSTING MODEL")
    logger.info("=" * 70)

    train_path = cfg.processed_dir / "tce_train.csv"
    val_path = cfg.processed_dir / "tce_val.csv"
    test_path = cfg.processed_dir / "tce_test.csv"

    if not (train_path.exists() and val_path.exists() and test_path.exists()):
        logger.error("Splits not found. Running scripts/prepare_dataset.py first...")
        from scripts.prepare_dataset import main as prep_main
        prep_main()

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    start_time = time.time()
    pipeline = BaselinePipeline()
    val_metrics = pipeline.train(df_train, df_val)
    eval_result = pipeline.evaluate(df_test)
    test_metrics = eval_result["metrics"]
    duration = time.time() - start_time

    # Save baseline artifacts
    pipeline.save()
    with open(cfg.metrics_dir / "baseline_metrics.json", "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2)

    with open(cfg.metrics_dir / "baseline_curves.json", "w", encoding="utf-8") as f:
        json.dump(eval_result["curves"], f, indent=2)

    # Log to SQLite experiment history
    tracker = ExperimentTracker()
    tracker.log_experiment(
        experiment_id=f"EXP-BASE-{int(time.time())}",
        model_type="HistGradientBoostingClassifier",
        training_duration=duration,
        best_val_auc=val_metrics["roc_auc"],
        test_metrics=test_metrics,
        parameters={
            "features": cfg.baseline_features,
            "max_iter": cfg.baseline_max_iter,
            "learning_rate": cfg.baseline_learning_rate,
            "max_leaf_nodes": cfg.baseline_max_leaf_nodes,
        },
        model_path=str(cfg.baseline_dir / "baseline_model.joblib"),
        notes="Baseline tabular model trained strictly on training stars.",
    )

    logger.info("=" * 70)
    logger.info(f"BASELINE TEST RESULTS: ROC-AUC: {test_metrics['roc_auc']} | AvgPrec: {test_metrics['average_precision']} | F1: {test_metrics['f1_score']}")
    logger.info("=" * 70)
    return test_metrics


def build_views_for_split(
    df_split: pd.DataFrame,
    cache: LightCurveCache,
    split_name: str,
    max_candidates: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate or retrieve cached 2-view representations (Global 2001, Local 201) for TCEs."""
    cache_file = cfg.processed_dir / f"cnn_views_{split_name}.npz"
    if cache_file.exists():
        logger.info(f"Loading pre-computed {split_name} views from {cache_file.name}...")
        data = np.load(cache_file)
        return data["global_views"], data["local_views"], data["labels"], data["kepids"], data["plnt_nums"]

    logger.info(f"Computing dual-view representations for {split_name} split...")
    global_list, local_list, label_list, kepid_list, plnt_list = [], [], [], [], []

    # Get available cached stars
    cached_star_ids = set(cache.list_cached_stars())
    df_available = df_split[df_split["kepid"].isin(cached_star_ids)].copy()

    if len(df_available) == 0:
        logger.warning(f"No cached light curves match stars in {split_name} split.")
        # If no stars in this split are cached yet, download a sample
        sample_stars = df_split["kepid"].unique()[:20]
        for s in sample_stars:
            download_stellar_lightcurve(int(s), cache=cache)
        cached_star_ids = set(cache.list_cached_stars())
        df_available = df_split[df_split["kepid"].isin(cached_star_ids)].copy()

    if max_candidates is not None and len(df_available) > max_candidates:
        df_available = df_available.sample(max_candidates, random_state=cfg.random_seed)

    for idx, row in df_available.iterrows():
        kid = int(row["kepid"])
        lc_data = cache.load(kid)
        if lc_data is None:
            continue
        t_arr, f_arr, _ = lc_data
        t_clean = validate_and_align_time_system(t_arr)

        try:
            flat_flux, _, _ = flatten_lightcurve(
                time_arr=t_clean,
                flux_arr=f_arr,
                period=float(row["tce_period"]),
                t0=float(row["tce_time0bk"]),
                duration_hours=float(row["tce_duration"]),
                window_length=cfg.flatten_window_length,
            )
            g_view, l_view, _ = generate_two_views(
                time_arr=t_clean,
                flux_arr=flat_flux,
                period=float(row["tce_period"]),
                t0=float(row["tce_time0bk"]),
                duration_hours=float(row["tce_duration"]),
                global_bins=cfg.cnn_global_length,
                local_bins=cfg.cnn_local_length,
                local_factor=cfg.local_duration_factor,
            )
            global_list.append(g_view)
            local_list.append(l_view)
            label_list.append(int(row["planet"]))
            kepid_list.append(kid)
            plnt_list.append(int(row["tce_plnt_num"]))
        except Exception as e:
            logger.debug(f"Skipping TCE KIC {kid}: {e}")

    g_arr = np.array(global_list, dtype=np.float32)
    l_arr = np.array(local_list, dtype=np.float32)
    y_arr = np.array(label_list, dtype=np.float32)
    k_arr = np.array(kepid_list, dtype=np.int64)
    p_arr = np.array(plnt_list, dtype=np.int32)

    if len(g_arr) > 0:
        np.savez_compressed(
            cache_file,
            global_views=g_arr,
            local_views=l_arr,
            labels=y_arr,
            kepids=k_arr,
            plnt_nums=p_arr,
        )
        logger.info(f"Saved {len(g_arr)} processed views to {cache_file.name}")

    return g_arr, l_arr, y_arr, k_arr, p_arr


def train_cnn_pipeline(epochs: int = 30, batch_size: int = 8) -> Dict[str, Any]:
    """Train and evaluate the Two-View 1D CNN architecture."""
    logger.info("=" * 70)
    logger.info("TRAINING TWO-VIEW 1D CONVOLUTIONAL NEURAL NETWORK")
    logger.info("=" * 70)

    train_path = cfg.processed_dir / "tce_train.csv"
    val_path = cfg.processed_dir / "tce_val.csv"
    test_path = cfg.processed_dir / "tce_test.csv"

    if not (train_path.exists() and val_path.exists() and test_path.exists()):
        logger.error("Splits not found. Running scripts/prepare_dataset.py first...")
        from scripts.prepare_dataset import main as prep_main
        prep_main()

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    cache = LightCurveCache()

    # Pre-process or load views
    g_train, l_train, y_train, k_train, p_train = build_views_for_split(df_train, cache, "train")
    g_val, l_val, y_val, k_val, p_val = build_views_for_split(df_val, cache, "val")
    g_test, l_test, y_test, k_test, p_test = build_views_for_split(df_test, cache, "test")

    if len(g_train) < 5 or len(g_val) < 2:
        logger.error("Insufficient cached light curves for CNN training. Run scripts/download_lightcurves.py first!")
        sys.exit(1)

    train_ds = ExoplanetDualViewDataset(g_train, l_train, y_train, k_train, p_train)
    val_ds = ExoplanetDualViewDataset(g_val, l_val, y_val, k_val, p_val)
    test_ds = ExoplanetDualViewDataset(g_test, l_test, y_test, k_test, p_test) if len(g_test) > 0 else None

    device = get_device(cfg.cnn_device)
    train_loader, val_loader, test_loader = create_dataloaders(
        train_ds, val_ds, test_ds, batch_size=batch_size, pin_memory=(device.type == "cuda")
    )

    model = DualViewExoplanetCNN(
        global_in_len=cfg.cnn_global_length,
        local_in_len=cfg.cnn_local_length,
        dropout_rate=cfg.cnn_dropout,
    )

    trained_model, train_res = train_cnn_model(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        train_labels=y_train,
        epochs=epochs,
        lr=cfg.cnn_learning_rate,
        weight_decay=cfg.cnn_weight_decay,
        patience=cfg.cnn_early_stopping_patience,
        device=device,
    )

    # Test set evaluation
    opt_threshold = train_res["optimal_threshold"]
    if test_loader is not None and len(test_ds) > 0:
        trained_model.eval()
        test_probs, test_targets = [], []
        with torch.no_grad():
            for g_x, l_x, y, _ in test_loader:
                probs = trained_model.predict_proba(g_x.to(device), l_x.to(device)).cpu().numpy().flatten()
                test_probs.extend(probs)
                test_targets.extend(y.cpu().numpy().flatten())

        test_y = np.array(test_targets)
        test_p = np.array(test_probs)

        test_metrics, curves = evaluate_cnn_predictions(test_y, test_p, opt_threshold)
        boot_ci = compute_grouped_bootstrap_ci(test_y, test_p, k_test, opt_threshold)
        test_metrics["confidence_intervals_95"] = boot_ci

        with open(cfg.metrics_dir / "cnn_metrics.json", "w", encoding="utf-8") as f:
            json.dump(test_metrics, f, indent=2)

        with open(cfg.metrics_dir / "cnn_curves.json", "w", encoding="utf-8") as f:
            json.dump(curves, f, indent=2)

        # Baseline comparison if baseline was trained
        base_metric_path = cfg.metrics_dir / "baseline_metrics.json"
        if base_metric_path.exists():
            with open(base_metric_path, "r", encoding="utf-8") as f:
                b_metrics = json.load(f)
            comparison = compare_models(b_metrics, test_metrics)
            with open(cfg.metrics_dir / "model_comparison.json", "w", encoding="utf-8") as f:
                json.dump(comparison, f, indent=2)
            logger.info("Model Comparison saved to model_comparison.json")

        # Log to experiment tracker
        tracker = ExperimentTracker()
        tracker.log_experiment(
            experiment_id=f"EXP-CNN-{int(time.time())}",
            model_type="DualViewExoplanetCNN",
            training_duration=train_res["duration_seconds"],
            best_val_auc=train_res["best_val_auc"],
            test_metrics=test_metrics,
            parameters={
                "global_len": cfg.cnn_global_length,
                "local_len": cfg.cnn_local_length,
                "epochs": epochs,
                "batch_size": batch_size,
                "lr": cfg.cnn_learning_rate,
            },
            model_path=str(cfg.checkpoints_dir / "best_model.pth"),
            notes="Two-View 1D CNN trained on authentic NASA Kepler DR24 light curves.",
        )

        logger.info("=" * 70)
        logger.info(f"CNN TEST RESULTS: ROC-AUC: {test_metrics['roc_auc']} | AvgPrec: {test_metrics['average_precision']} | F1: {test_metrics['f1_score']}")
        logger.info("=" * 70)
        return test_metrics

    return train_res


def main():
    parser = argparse.ArgumentParser(description="Train baseline or Dual-View CNN models.")
    parser.add_argument("--model", type=str, choices=["baseline", "cnn", "both"], default="baseline")
    parser.add_argument("--epochs", type=int, default=40, help="Epochs for CNN training")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for CNN training")
    args = parser.parse_args()

    if args.model in ["baseline", "both"]:
        train_baseline_pipeline()
    if args.model in ["cnn", "both"]:
        train_cnn_pipeline(epochs=args.epochs, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
