"""Scientific Preprocessing for Kepler Light Curves.

Implements transit masking, Savitzky-Golay / polynomial flattening with transit protection,
time-system validation (BKJD), and depth-preserving normalization.
"""
import logging
from typing import Tuple, Dict, Any, Optional

import numpy as np
from scipy.signal import savgol_filter

from src.config import cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

KEPLER_TIME_OFFSET_BKJD = 2454833.0


def validate_and_align_time_system(time_arr: np.ndarray) -> np.ndarray:
    """Ensure the light curve time series is strictly in Kepler Barycentric Julian Day (BKJD).

    BKJD = BJD - 2454833.0.
    If the input time values are in full BJD (> 2400000), align them to BKJD.
    """
    time_clean = np.asarray(time_arr, dtype=np.float64)
    if len(time_clean) == 0:
        return time_clean

    median_t = float(np.median(time_clean))
    if median_t > 2400000.0:
        logger.info(f"Input time detected in full BJD (~{median_t:.1f}). Converting to BKJD (-{KEPLER_TIME_OFFSET_BKJD}).")
        time_clean = time_clean - KEPLER_TIME_OFFSET_BKJD
    return time_clean


def compute_transit_mask(
    time_arr: np.ndarray,
    period: float,
    t0: float,
    duration_hours: float,
    mask_factor: float = 1.2,
) -> np.ndarray:
    """Calculate boolean mask indicating transit points that MUST BE PROTECTED during flattening.

    Args:
        time_arr: Array of observation timestamps in BKJD.
        period: Orbital period in days.
        t0: Transit epoch in BKJD.
        duration_hours: Transit duration in hours.
        mask_factor: Scaling factor to ensure transit ingress/egress wings are fully protected.

    Returns:
        Boolean array where True indicates in-transit points to mask out.
    """
    duration_days = duration_hours / 24.0
    half_transit_window = (duration_days / 2.0) * mask_factor

    # Phase relative to transit center in range [-period/2, period/2]
    phase = ((time_arr - t0 + period / 2.0) % period) - period / 2.0
    in_transit = np.abs(phase) < half_transit_window
    return in_transit


def flatten_lightcurve(
    time_arr: np.ndarray,
    flux_arr: np.ndarray,
    period: float,
    t0: float,
    duration_hours: float,
    window_length: int = 401,
    polyorder: int = 2,
    mask_factor: float = 1.2,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Flatten stellar variability and instrumental trends while strictly protecting transits.

    1. Computes transit mask.
    2. Interpolates stellar trend across masked transits using out-of-transit flux.
    3. Fits low-frequency trend using Savitzky-Golay / polynomial filter.
    4. Divides original flux by trend to produce flattened relative flux (median ~ 1.0).

    Returns:
        (flattened_flux, trend_flux, metadata)
    """
    meta: Dict[str, Any] = {
        "window_length": window_length,
        "polyorder": polyorder,
        "mask_factor": mask_factor,
        "status": "success",
    }

    n_points = len(time_arr)
    if n_points < 50:
        meta["status"] = "too_few_points"
        return flux_arr, np.ones_like(flux_arr), meta

    # Guarantee odd window length <= n_points
    if window_length % 2 == 0:
        window_length += 1
    if window_length >= n_points:
        window_length = n_points - 1 if (n_points - 1) % 2 != 0 else n_points - 2
    if window_length <= polyorder:
        window_length = polyorder + 2 if (polyorder + 2) % 2 != 0 else polyorder + 3

    meta["effective_window_length"] = window_length

    # Compute transit mask
    in_transit = compute_transit_mask(
        time_arr=time_arr,
        period=period,
        t0=t0,
        duration_hours=duration_hours,
        mask_factor=mask_factor,
    )
    meta["in_transit_points"] = int(np.sum(in_transit))

    # Construct out-of-transit flux array for trend estimation
    flux_for_trend = flux_arr.copy()
    if np.any(in_transit) and np.any(~in_transit):
        # Linearly interpolate across in-transit regions using out-of-transit neighbors
        flux_for_trend[in_transit] = np.interp(
            time_arr[in_transit],
            time_arr[~in_transit],
            flux_arr[~in_transit],
        )

    # Apply Savitzky-Golay filtering to obtain smooth continuum
    try:
        trend = savgol_filter(flux_for_trend, window_length=window_length, polyorder=polyorder)
        # Protect against non-positive trend values
        trend = np.where(trend <= 0, np.nanmedian(flux_arr), trend)
        flattened_flux = flux_arr / trend
    except Exception as e:
        logger.warning(f"Flattening fallback triggered: {e}")
        trend = np.ones_like(flux_arr) * np.nanmedian(flux_arr)
        flattened_flux = flux_arr / trend
        meta["status"] = f"fallback_{e}"

    return flattened_flux, trend, meta


def normalize_folded_view(view_flux: np.ndarray) -> np.ndarray:
    """Normalize folded phase-binned flux profile following the canonical NASA exoplanet formulation.

    normalized = (flux - median(flux)) / abs(min(flux - median(flux)))

    Centers the out-of-transit continuum around 0.0 and scales maximum transit depth to -1.0.
    Defensively guards against zero denominators, constant signals, NaNs, and extreme outliers.
    """
    view = np.asarray(view_flux, dtype=np.float32)

    # Check for NaNs or infinities
    if not np.all(np.isfinite(view)):
        # Impute invalid values with median of valid entries
        valid_vals = view[np.isfinite(view)]
        fill_val = float(np.median(valid_vals)) if len(valid_vals) > 0 else 1.0
        view = np.nan_to_num(view, nan=fill_val, posinf=fill_val, neginf=fill_val)

    med = float(np.median(view))
    shifted = view - med
    min_val = float(np.min(shifted))
    denom = abs(min_val)

    # Guard against zero/near-zero denominator (flat/constant signal or inverted spike)
    if denom < 1e-7:
        return np.zeros_like(view)

    normalized = shifted / denom
    # Clip any extreme numerical anomalies to scientific bounds [-5.0, 5.0]
    normalized = np.clip(normalized, -5.0, 5.0)
    return normalized

