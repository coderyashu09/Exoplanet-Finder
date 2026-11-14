"""Two-View 1D Convolutional Neural Network for Exoplanet Detection."""
from typing import Dict, Any, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.config import cfg


class Conv1DBlock(nn.Module):
    """Convolutional block: Conv1D -> BatchNorm1D -> ReLU -> MaxPool1D."""

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 5, pool_size: int = 2):
        super().__init__()
        self.conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            padding=kernel_size // 2,
            bias=False,
        )
        self.bn = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.pool = nn.MaxPool1d(kernel_size=pool_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.pool(self.relu(self.bn(self.conv(x))))


class DualViewExoplanetCNN(nn.Module):
    """Two-Branch 1D Convolutional Neural Network.

    Processes both the wide orbital Global View (2001 bins) and
    the zoomed high-resolution Local View (201 bins) through separate representation
    branches, concatenates feature embeddings, and outputs exoplanet transit probability.

    Shapes:
        Input A (Global): [batch_size, 1, 2001]
        Input B (Local):  [batch_size, 1, 201]
        Output:           [batch_size, 1] (raw logit)
    """

    def __init__(
        self,
        global_in_len: int = 2001,
        local_in_len: int = 201,
        dropout_rate: float = 0.3,
    ):
        super().__init__()
        self.global_in_len = global_in_len
        self.local_in_len = local_in_len

        # Branch A: Global View CNN (processes long baseline transit + variability)
        self.global_branch = nn.Sequential(
            Conv1DBlock(1, 16, kernel_size=7, pool_size=2),    # 2001 -> 1000
            Conv1DBlock(16, 32, kernel_size=5, pool_size=2),   # 1000 -> 500
            Conv1DBlock(32, 64, kernel_size=5, pool_size=2),   # 500 -> 250
            Conv1DBlock(64, 128, kernel_size=3, pool_size=2),  # 250 -> 125
            nn.AdaptiveAvgPool1d(8),                            # Fixed 8 spatial bins
        )
        self.global_fc = nn.Sequential(
            nn.Linear(128 * 8, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
        )

        # Branch B: Local View CNN (zoomed transit profile: ingress, egress, bottom flatness)
        self.local_branch = nn.Sequential(
            Conv1DBlock(1, 16, kernel_size=7, pool_size=2),    # 201 -> 100
            Conv1DBlock(16, 32, kernel_size=5, pool_size=2),   # 100 -> 50
            Conv1DBlock(32, 64, kernel_size=5, pool_size=2),   # 50 -> 25
            Conv1DBlock(64, 128, kernel_size=3, pool_size=2),  # 25 -> 12
            nn.AdaptiveAvgPool1d(8),                            # Fixed 8 spatial bins
        )
        self.local_fc = nn.Sequential(
            nn.Linear(128 * 8, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
        )

        # Feature Fusion & Classification Head
        # Concatenation of Global (256) + Local (256) = 512 dimensions
        self.classifier = nn.Sequential(
            nn.Linear(256 + 256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate / 2.0),
            nn.Linear(64, 1),  # Single logit output
        )

    def forward(self, global_x: torch.Tensor, local_x: torch.Tensor) -> torch.Tensor:
        """Forward pass accepting both Global and Local views.

        Args:
            global_x: Tensor of shape [batch_size, 1, 2001]
            local_x:  Tensor of shape [batch_size, 1, 201]

        Returns:
            Logits of shape [batch_size, 1]
        """
        # Ensure 3D tensors: [batch_size, channels=1, length]
        if global_x.dim() == 2:
            global_x = global_x.unsqueeze(1)
        if local_x.dim() == 2:
            local_x = local_x.unsqueeze(1)

        # Branch representations
        feat_global = self.global_branch(global_x)
        feat_global = feat_global.flatten(start_dim=1)
        emb_global = self.global_fc(feat_global)

        feat_local = self.local_branch(local_x)
        feat_local = feat_local.flatten(start_dim=1)
        emb_local = self.local_fc(feat_local)

        # Feature concatenation
        fusion = torch.cat([emb_global, emb_local], dim=1)

        # Classification logit
        logits = self.classifier(fusion)
        return logits

    def predict_proba(self, global_x: torch.Tensor, local_x: torch.Tensor) -> torch.Tensor:
        """Inference helper returning planet probabilities in [0.0, 1.0]."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(global_x, local_x)
            probs = torch.sigmoid(logits)
        return probs

    def count_parameters(self) -> Dict[str, int]:
        """Count trainable and total parameters."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total_parameters": total, "trainable_parameters": trainable}

