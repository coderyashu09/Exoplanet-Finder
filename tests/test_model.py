"""Unit tests for Two-View 1D CNN architecture, forward pass shapes, probabilities, and checkpoint serialization."""
import tempfile
from pathlib import Path
import torch
import pytest

from src.model import DualViewExoplanetCNN


def test_cnn_forward_shapes():
    """Verify input/output shapes: Global [B, 1, 2001], Local [B, 1, 201] -> Logits [B, 1]."""
    model = DualViewExoplanetCNN(global_in_len=2001, local_in_len=201)
    batch_size = 4

    global_in = torch.randn(batch_size, 1, 2001)
    local_in = torch.randn(batch_size, 1, 201)

    logits = model(global_in, local_in)
    assert logits.shape == (batch_size, 1), f"Expected ({batch_size}, 1), got {logits.shape}"

    # Verify probability range
    probs = model.predict_proba(global_in, local_in)
    assert probs.shape == (batch_size, 1)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()


def test_cnn_2d_tensor_unsqueezing():
    """Verify model gracefully accepts 2D [B, L] inputs and unsqueezes to [B, 1, L]."""
    model = DualViewExoplanetCNN(global_in_len=2001, local_in_len=201)
    batch_size = 2

    global_2d = torch.randn(batch_size, 2001)
    local_2d = torch.randn(batch_size, 201)

    logits = model(global_2d, local_2d)
    assert logits.shape == (batch_size, 1)


def test_checkpoint_saving_and_loading():
    """Verify state dict can be saved to disk and reloaded identically."""
    model_orig = DualViewExoplanetCNN()
    x_g = torch.randn(2, 1, 2001)
    x_l = torch.randn(2, 1, 201)

    orig_probs = model_orig.predict_proba(x_g, x_l)

    with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        torch.save(model_orig.state_dict(), tmp_path)

        model_loaded = DualViewExoplanetCNN()
        model_loaded.load_state_dict(torch.load(tmp_path, weights_only=True))
        loaded_probs = model_loaded.predict_proba(x_g, x_l)

        torch.testing.assert_close(orig_probs, loaded_probs)
    finally:
        tmp_path.unlink(missing_ok=True)

