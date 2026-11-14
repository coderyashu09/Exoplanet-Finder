"""PyTorch Dataset and DataLoader constructors for two-view exoplanet transit observations."""
from typing import Dict, Any, Optional, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


class ExoplanetDualViewDataset(Dataset):
    """PyTorch Dataset holding paired Global (2001 bins) and Local (201 bins) transit curves.

    Tensors are provided as:
        - global_view: [1, 2001] FloatTensor
        - local_view:  [1, 201]  FloatTensor
        - label:       [1]       FloatTensor (1.0 for Planet Candidate, 0.0 for False Positive)
    """

    def __init__(
        self,
        global_views: np.ndarray,
        local_views: np.ndarray,
        labels: np.ndarray,
        kepids: Optional[np.ndarray] = None,
        tce_plnt_nums: Optional[np.ndarray] = None,
    ):
        assert len(global_views) == len(local_views) == len(labels), (
            f"Mismatched dataset lengths: {len(global_views)}, {len(local_views)}, {len(labels)}"
        )
        self.global_views = torch.from_numpy(np.asarray(global_views, dtype=np.float32)).unsqueeze(1)
        self.local_views = torch.from_numpy(np.asarray(local_views, dtype=np.float32)).unsqueeze(1)
        self.labels = torch.from_numpy(np.asarray(labels, dtype=np.float32)).unsqueeze(1)

        self.kepids = kepids if kepids is not None else np.zeros(len(labels), dtype=np.int64)
        self.tce_plnt_nums = tce_plnt_nums if tce_plnt_nums is not None else np.ones(len(labels), dtype=np.int32)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict[str, Any]]:
        meta = {
            "kepid": int(self.kepids[idx]),
            "tce_plnt_num": int(self.tce_plnt_nums[idx]),
        }
        return self.global_views[idx], self.local_views[idx], self.labels[idx], meta


def create_dataloaders(
    train_dataset: ExoplanetDualViewDataset,
    val_dataset: ExoplanetDualViewDataset,
    test_dataset: Optional[ExoplanetDualViewDataset] = None,
    batch_size: int = 32,
    num_workers: int = 0,
    pin_memory: bool = False,
) -> Tuple[DataLoader, DataLoader, Optional[DataLoader]]:
    """Build PyTorch DataLoaders with shuffle on training data."""
    # Avoid batch-size 1 in training to prevent BatchNorm1d single-element training failure
    drop_last_train = (len(train_dataset) > batch_size and len(train_dataset) % batch_size == 1)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last_train,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=False,
    )
    test_loader = None
    if test_dataset is not None:
        test_loader = DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=False,
        )

    return train_loader, val_loader, test_loader
