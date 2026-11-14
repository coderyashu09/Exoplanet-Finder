"""Training pipeline for Two-View 1D Convolutional Neural Network with validation & early stopping."""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Callable

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve
from torch.utils.data import DataLoader

from src.config import cfg
from src.model import DualViewExoplanetCNN

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_device(preference: str = "auto") -> torch.device:
    """Select compute device (CUDA / CPU) based on system capability and user configuration."""
    if preference == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    elif preference.lower() in ["cuda", "gpu"] and torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    logger.info(f"Using compute device: {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    return device


def compute_pos_weight(labels: np.ndarray) -> torch.Tensor:
    """Compute pos_weight for BCEWithLogitsLoss based strictly on training labels."""
    labels = np.asarray(labels).flatten()
    n_pos = np.sum(labels == 1)
    n_neg = np.sum(labels == 0)
    if n_pos == 0:
        return torch.tensor([1.0], dtype=torch.float32)
    ratio = float(n_neg) / float(n_pos)
    logger.info(f"Training class balance: {n_pos} PCs, {n_neg} non-PCs (pos_weight={ratio:.2f})")
    return torch.tensor([ratio], dtype=torch.float32)


def evaluate_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, float, np.ndarray, np.ndarray]:
    """Evaluate model on a DataLoader, returning loss, ROC-AUC, Avg Precision, labels, and probabilities."""
    model.eval()
    total_loss = 0.0
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for global_x, local_x, y, _ in loader:
            global_x = global_x.to(device)
            local_x = local_x.to(device)
            y = y.to(device)

            logits = model(global_x, local_x)
            loss = criterion(logits, y)
            total_loss += loss.item() * len(y)

            probs = torch.sigmoid(logits).cpu().numpy().flatten()
            labels = y.cpu().numpy().flatten()

            all_probs.extend(probs)
            all_labels.extend(labels)

    avg_loss = total_loss / len(loader.dataset)
    y_true = np.array(all_labels)
    y_pred = np.array(all_probs)

    # In case a mini-batch only has 1 class
    if len(np.unique(y_true)) > 1:
        auc = float(roc_auc_score(y_true, y_pred))
        ap = float(average_precision_score(y_true, y_pred))
    else:
        auc = 0.5
        ap = float(np.mean(y_true))

    return avg_loss, auc, ap, y_true, y_pred


def train_cnn_model(
    model: DualViewExoplanetCNN,
    train_loader: DataLoader,
    val_loader: DataLoader,
    train_labels: np.ndarray,
    epochs: int = 50,
    lr: float = 0.001,
    weight_decay: float = 1e-4,
    patience: int = 10,
    device: Optional[torch.device] = None,
    progress_callback: Optional[Callable[[int, int, Dict[str, float]], None]] = None,
) -> Tuple[DualViewExoplanetCNN, Dict[str, Any]]:
    """Execute training loop with AdamW, early stopping, LR scheduling, and artifact checkpointing."""
    device = device or get_device(cfg.cnn_device)
    model.to(device)

    # Class imbalance weighting
    pos_weight = compute_pos_weight(train_labels).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=3
    )

    history: Dict[str, list] = {
        "epoch": [],
        "train_loss": [],
        "train_auc": [],
        "val_loss": [],
        "val_auc": [],
        "val_ap": [],
        "lr": [],
    }

    best_val_auc = -1.0
    best_weights = None
    patience_counter = 0
    start_time = time.time()

    cfg.checkpoints_dir.mkdir(parents=True, exist_ok=True)
    cfg.metadata_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting Two-View CNN training for {epochs} epochs (Early stopping patience={patience})...")

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        train_preds = []
        train_targets = []

        for global_x, local_x, y, _ in train_loader:
            global_x = global_x.to(device)
            local_x = local_x.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            logits = model(global_x, local_x)
            loss = criterion(logits, y)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item() * len(y)
            train_preds.extend(torch.sigmoid(logits).detach().cpu().numpy().flatten())
            train_targets.extend(y.cpu().numpy().flatten())

        avg_train_loss = train_loss / len(train_loader.dataset)
        train_auc = (
            float(roc_auc_score(train_targets, train_preds))
            if len(np.unique(train_targets)) > 1
            else 0.5
        )

        val_loss, val_auc, val_ap, val_y, val_probs = evaluate_epoch(
            model, val_loader, criterion, device
        )
        current_lr = float(optimizer.param_groups[0]["lr"])
        scheduler.step(val_auc)

        # Record metrics
        history["epoch"].append(epoch)
        history["train_loss"].append(round(avg_train_loss, 5))
        history["train_auc"].append(round(train_auc, 5))
        history["val_loss"].append(round(val_loss, 5))
        history["val_auc"].append(round(val_auc, 5))
        history["val_ap"].append(round(val_ap, 5))
        history["lr"].append(current_lr)

        logger.info(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {avg_train_loss:.4f} | Train AUC: {train_auc:.4f} | "
            f"Val Loss: {val_loss:.4f} | Val AUC: {val_auc:.4f} | Val AP: {val_ap:.4f}"
        )

        if progress_callback:
            progress_callback(epoch, epochs, {
                "train_loss": avg_train_loss,
                "val_loss": val_loss,
                "train_auc": train_auc,
                "val_auc": val_auc,
            })

        # Checkpoint if best
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            torch.save(best_weights, cfg.checkpoints_dir / "best_model.pth")
            patience_counter = 0
            logger.info(f"==> New best validation AUC: {best_val_auc:.4f} (Saved checkpoint)")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered after {epoch} epochs without validation improvement.")
                break

    training_duration = time.time() - start_time
    logger.info(f"Training completed in {training_duration:.1f}s. Best Val AUC: {best_val_auc:.4f}")

    # Reload best weights
    if best_weights is not None:
        model.load_state_dict(best_weights)

    # Compute optimal threshold on validation set
    _, _, _, final_val_y, final_val_probs = evaluate_epoch(model, val_loader, criterion, device)
    precisions, recalls, thresholds = precision_recall_curve(final_val_y, final_val_probs)
    f1s = np.zeros_like(thresholds)
    for i, t in enumerate(thresholds):
        p, r = precisions[i], recalls[i]
        f1s[i] = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

    best_idx = int(np.argmax(f1s)) if len(f1s) > 0 else 0
    optimal_thresh = float(thresholds[best_idx]) if len(thresholds) > 0 else 0.50
    optimal_thresh = max(0.1, min(0.9, optimal_thresh))

    # Save artifacts
    with open(cfg.metadata_dir / "classification_threshold.json", "w", encoding="utf-8") as f:
        json.dump({"threshold": optimal_thresh}, f, indent=2)

    with open(cfg.metadata_dir / "training_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    param_info = model.count_parameters()
    model_config = {
        "architecture": "DualViewExoplanetCNN",
        "global_length": cfg.cnn_global_length,
        "local_length": cfg.cnn_local_length,
        "parameters": param_info,
        "training_duration_seconds": round(training_duration, 2),
        "best_val_auc": round(best_val_auc, 5),
        "optimal_threshold": round(optimal_thresh, 4),
        "batch_size": cfg.cnn_batch_size,
        "learning_rate": lr,
        "weight_decay": weight_decay,
    }
    with open(cfg.metadata_dir / "model_config.json", "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)

    return model, {
        "history": history,
        "best_val_auc": best_val_auc,
        "optimal_threshold": optimal_thresh,
        "duration_seconds": training_duration,
    }

