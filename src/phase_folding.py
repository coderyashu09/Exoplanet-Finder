"""Phase folding and dual-view (Global and Local) generation for Kepler exoplanet transit candidates."""
import logging
from typing import Tuple, Dict, Any, Optional

import numpy as np
from scipy.stats import binned_statistic

from src.config import cfg
from src.preprocessing import normalize_folded_view

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def fold_lightcurve(
    time_arr: np.ndarray,
    flux_arr: np.ndarray,
    period: float,
    t0: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute orbital phase relative to transit epoch and sort chronologically in phase space.

    Formula: phase = ((time - t0 + period / 2) % period) - period / 2
    This strictly centers the transit event at phase = 0.0.
    Range of phase: [-period / 2, +period / 2] in days.
    """
    time_clean = np.asarray(time_arr, dtype=np.float64)
    flux_clean = np.asarray(flux_arr, dtype=np.float64)

    phase = ((time_clean - t0 + period / 2.0) % period) - period / 2.0
    sort_idx = np.argsort(phase)
    return phase[sort_idx], flux_clean[sort_idx]


def median_bin_series(
    x_vals: np.ndarray,
    y_vals: np.ndarray,
    bin_edges: np.ndarray,
    default_fill: float = 1.0,
) -> Tuple[np.ndarray, int]:
    """Bin continuous series into discrete intervals using median statistics.

    Robustly handles empty bins through continuous linear interpolation between populated bins,
    falling back to nearest valid neighbor at boundaries to guarantee zero NaNs.

    Returns:
        (binned_array, empty_bins_count)
    """
    n_bins = len(bin_edges) - 1
    if len(x_vals) == 0:
        return np.full(n_bins, default_fill, dtype=np.float32), n_bins

    # Compute median within each bin
    binned_vals, _, _ = binned_statistic(x_vals, y_vals, statistic="median", bins=bin_edges)
    empty_mask = np.isnan(binned_vals)
    empty_count = int(np.sum(empty_mask))

    if empty_count == 0:
        return binned_vals.astype(np.float32), 0

    if empty_count == n_bins:
        # All bins empty (e.g. out of range data)
        fill = float(np.nanmedian(y_vals)) if len(y_vals) > 0 and np.any(np.isfinite(y_vals)) else default_fill
        return np.full(n_bins, fill, dtype=np.float32), empty_count

    # Linear interpolation for empty bins across bin centers
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    valid_idx = np.where(~empty_mask)[0]
    valid_x = bin_centers[valid_idx]
    valid_y = binned_vals[valid_idx]

    # Interpolate empty bins
    interp_y = np.interp(bin_centers, valid_x, valid_y)
    return interp_y.astype(np.float32), empty_count


def generate_global_view(
    phase: np.ndarray,
    flux: np.ndarray,
    period: float,
    n_bins: int = 2001,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate Global View covering the entire orbital period [-period/2, +period/2] in n_bins bins.

    Binned using median aggregation, imputed across gaps, and normalized to canonical exoplanet depth.
    Output shape: (n_bins,)
    """
    half_p = period / 2.0
    bin_edges = np.linspace(-half_p, half_p, n_bins + 1, endpoint=True)

    binned_flux, empty_count = median_bin_series(phase, flux, bin_edges, default_fill=1.0)
    norm_view = normalize_folded_view(binned_flux)

    meta = {
        "n_bins": n_bins,
        "empty_bins": empty_count,
        "phase_min": -half_p,
        "phase_max": half_p,
        "raw_median": float(np.nanmedian(binned_flux)),
    }
    return norm_view, meta


def generate_local_view(
    phase: np.ndarray,
    flux: np.ndarray,
    duration_hours: float,
    n_bins: int = 201,
    factor: float = 4.0,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Generate Local View zoomed around the transit region [-factor*duration, +factor*duration].

    Duration is converted from hours to days: duration_days = duration_hours / 24.0.
    Output shape: (n_bins,)
    """
    duration_days = duration_hours / 24.0
    local_window = factor * duration_days
    bin_edges = np.linspace(-local_window, local_window, n_bins + 1, endpoint=True)

    # Select phase points within a slightly wider window to aid edge interpolation
    in_local = (phase >= -local_window * 1.5) & (phase <= local_window * 1.5)
    loc_phase = phase[in_local]
    loc_flux = flux[in_local]

    binned_flux, empty_count = median_bin_series(loc_phase, loc_flux, bin_edges, default_fill=1.0)
    norm_view = normalize_folded_view(binned_flux)

    meta = {
        "n_bins": n_bins,
        "empty_bins": empty_count,
        "window_days": local_window,
        "duration_days": duration_days,
        "points_in_window": int(len(loc_phase)),
    }
    return norm_view, meta


def generate_two_views(
    time_arr: np.ndarray,
    flux_arr: np.ndarray,
    period: float,
    t0: float,
    duration_hours: float,
    global_bins: int = 2001,
    local_bins: int = 201,
    local_factor: float = 4.0,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Compute centered phase fold and generate both Global and Local normalized transit representations.

    Returns:
        (global_view [2001], local_view [201], metadata_dict)
    """
    phase, sorted_flux = fold_lightcurve(time_arr, flux_arr, period, t0)

    global_view, g_meta = generate_global_view(phase, sorted_flux, period, n_bins=global_bins)
    local_view, l_meta = generate_local_view(
        phase, sorted_flux, duration_hours, n_bins=local_bins, factor=local_factor
    )

    metadata = {
        "period_days": float(period),
        "t0_bkjd": float(t0),
        "duration_hours": float(duration_hours),
        "global_bins": global_bins,
        "local_bins": local_bins,
        "global_empty_bins": g_meta["empty_bins"],
        "local_empty_bins": l_meta["empty_bins"],
        "total_cadences": len(time_arr),
    }

    return global_view, local_view, metadata

