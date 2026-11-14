"""Unit tests for scientific explainability: Integrated Gradients and transit morphology diagnostics."""
import numpy as np
import torch
import pytest

from src.model import DualViewExoplanetCNN
from src.explainability import compute_integrated_gradients_1d, analyze_transit_morphology


def test_integrated_gradients_shape_and_attribution():
    """Verify that Integrated Gradients returns attribution arrays matching input view shapes."""
    model = DualViewExoplanetCNN(global_in_len=2001, local_in_len=201)
    model.eval()

    g_in = torch.randn(1, 1, 2001)
    l_in = torch.randn(1, 1, 201)

    ig_g, ig_l = compute_integrated_gradients_1d(
        model, g_in, l_in, m_steps=10, device=torch.device("cpu")
    )

    assert ig_g.shape == (2001,), f"Expected shape (2001,), got {ig_g.shape}"
    assert ig_l.shape == (201,), f"Expected shape (201,), got {ig_l.shape}"
    assert np.all(np.isfinite(ig_g)), "Integrated Gradients global attributions contain NaNs"
    assert np.all(np.isfinite(ig_l)), "Integrated Gradients local attributions contain NaNs"


def test_transit_morphology_u_shape_detection():
    """Verify that a flat-bottomed synthetic transit is diagnosed as U-shaped."""
    local_view = np.zeros(201, dtype=np.float32)
    # Inject flat bottom between index 90 and 110
    local_view[80:90] = np.linspace(0.0, -1.0, 10)     # Ingress
    local_view[90:111] = -1.0                           # Flat core bottom
    local_view[111:121] = np.linspace(-1.0, 0.0, 10)   # Egress

    global_view = np.zeros(2001, dtype=np.float32)
    global_view[950:1051] = -1.0

    diag = analyze_transit_morphology(
        global_view=global_view,
        local_view=local_view,
        period=10.0,
        duration_hours=4.0,
    )

    assert "is_u_shaped" in diag
    assert "symmetry_residual" in diag
    assert "morphology_reasons" in diag
    assert diag["is_u_shaped"] is True
    assert diag["is_symmetric"] is True
    assert diag["secondary_eclipse_detected"] is False


def test_transit_morphology_secondary_eclipse_detection():
    """Verify that a secondary dip at orbital phase 0.5 triggers the secondary eclipse warning."""
    local_view = np.zeros(201, dtype=np.float32)
    local_view[95:106] = -1.0  # Primary transit

    global_view = np.zeros(2001, dtype=np.float32)
    # Inject secondary dip near phase 0.5 (edges of centered fold)
    global_view[:20] = -0.5
    global_view[-20:] = -0.5

    diag = analyze_transit_morphology(
        global_view=global_view,
        local_view=local_view,
        period=10.0,
        duration_hours=4.0,
    )

    assert diag["secondary_eclipse_detected"] is True
    assert any("secondary eclipse" in r.lower() for r in diag["morphology_reasons"])

