"""Scientific explainability and feature attribution using Integrated Gradients and transit morphology analysis."""
import logging
from typing import Dict, Any, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_integrated_gradients_1d(
    model: nn.Module,
    global_x: torch.Tensor,
    local_x: torch.Tensor,
    baseline_global: Optional[torch.Tensor] = None,
    baseline_local: Optional[torch.Tensor] = None,
    m_steps: int = 25,
    device: Optional[torch.device] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate feature attributions using Integrated Gradients for 1D input signals.

    IG_i(x) = (x_i - x'_i) * (1/m) * sum_{k=1}^m grad_i(x' + (k/m)(x - x'))

    Returns:
        (global_attributions [2001], local_attributions [201])
    """
    model.eval()
    device = device or next(model.parameters()).device

    if global_x.dim() == 2:
        global_x = global_x.unsqueeze(1)
    if local_x.dim() == 2:
        local_x = local_x.unsqueeze(1)

    global_x = global_x.to(device)
    local_x = local_x.to(device)

    # Baselines: flat normalized continuum (0.0)
    if baseline_global is None:
        baseline_global = torch.zeros_like(global_x)
    if baseline_local is None:
        baseline_local = torch.zeros_like(local_x)

    baseline_global = baseline_global.to(device)
    baseline_local = baseline_local.to(device)

    # Scaled inputs along interpolation path
    alphas = torch.linspace(0.0, 1.0, m_steps + 1, device=device)

    grads_global = []
    grads_local = []

    for alpha in alphas[1:]:  # skip alpha=0
        interpolated_g = (baseline_global + alpha * (global_x - baseline_global)).detach().requires_grad_(True)
        interpolated_l = (baseline_local + alpha * (local_x - baseline_local)).detach().requires_grad_(True)

        logits = model(interpolated_g, interpolated_l)
        prob = torch.sigmoid(logits)

        # Compute gradient of probability with respect to interpolated inputs
        grad_g, grad_l = torch.autograd.grad(prob.sum(), [interpolated_g, interpolated_l])
        grads_global.append(grad_g.detach().cpu().numpy())
        grads_local.append(grad_l.detach().cpu().numpy())

    avg_grad_g = np.mean(grads_global, axis=0)
    avg_grad_l = np.mean(grads_local, axis=0)

    delta_g = (global_x - baseline_global).detach().cpu().numpy()
    delta_l = (local_x - baseline_local).detach().cpu().numpy()

    ig_g = delta_g * avg_grad_g
    ig_l = delta_l * avg_grad_l

    # Flatten to 1D
    return np.squeeze(ig_g), np.squeeze(ig_l)


def analyze_transit_morphology(
    global_view: np.ndarray,
    local_view: np.ndarray,
    period: float,
    duration_hours: float,
) -> Dict[str, Any]:
    """Examine transit morphology indicators to distinguish planetary candidates from astrophysical false positives."""
    n_local = len(local_view)
    center_idx = n_local // 2

    # Ingress / Egress symmetry check
    # Check 15% window on left vs right of center
    wing_span = max(5, int(n_local * 0.15))
    left_wing = local_view[center_idx - wing_span : center_idx]
    right_wing = local_view[center_idx + 1 : center_idx + 1 + wing_span]

    if len(left_wing) > 0 and len(right_wing) > 0:
        min_len = min(len(left_wing), len(right_wing))
        symmetry_diff = float(np.mean(np.abs(left_wing[-min_len:] - right_wing[:min_len][::-1])))
    else:
        symmetry_diff = 0.0

    # U-shape vs V-shape diagnostic
    # Ratio of transit bottom flatness (deepest 20% span) to overall transit span
    deepest_core = local_view[center_idx - 3 : center_idx + 4]
    core_variance = float(np.var(deepest_core)) if len(deepest_core) > 0 else 0.0
    is_u_shaped = core_variance < 0.05

    # Secondary Eclipse check in global view around phase 0.5 (opposite transit)
    n_global = len(global_view)
    # Phase 0.5 corresponds to the edges of the centered fold (near index 0 and index n_global-1)
    edge_depth_left = float(np.min(global_view[: int(n_global * 0.05)]))
    edge_depth_right = float(np.min(global_view[int(n_global * 0.95) :]))
    secondary_depth = min(edge_depth_left, edge_depth_right)
    has_secondary_eclipse = secondary_depth < -0.30  # Significant secondary dip

    diagnostics = {
        "symmetry_residual": round(symmetry_diff, 4),
        "is_symmetric": symmetry_diff < 0.35,
        "is_u_shaped": bool(is_u_shaped),
        "core_flatness_variance": round(core_variance, 4),
        "secondary_eclipse_detected": bool(has_secondary_eclipse),
        "secondary_depth_relative": round(secondary_depth, 4),
    }

    # Generate narrative bullet points
    reasons = []
    if is_u_shaped:
        reasons.append("Transit profile exhibits classic flat-bottomed U-shape indicative of a planetary disc transit.")
    else:
        reasons.append("Transit displays a tapered V-shape, which can be characteristic of grazing eclipsing binaries or high impact parameters.")

    if diagnostics["is_symmetric"]:
        reasons.append("Ingress and egress slopes are symmetric around phase zero.")
    else:
        reasons.append("Asymmetry detected between ingress and egress, which may stem from stellar variability or blending.")

    if has_secondary_eclipse:
        reasons.append("WARNING: Possible secondary eclipse detected near orbital phase 0.5, suggesting a binary star system.")

    diagnostics["morphology_reasons"] = reasons
    return diagnostics

