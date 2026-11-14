"""Unit tests for time-system validation, transit masking, detrending, and normalization."""
import numpy as np
import pytest

from src.preprocessing import (
    validate_and_align_time_system,
    compute_transit_mask,
    flatten_lightcurve,
    normalize_folded_view,
    KEPLER_TIME_OFFSET_BKJD,
)


def test_time_system_alignment():
    """Verify BJD to BKJD conversion when timestamps exceed 2400000."""
    bjd_times = np.array([2455000.0, 2455001.0, 2455002.0])
    bkjd_times = validate_and_align_time_system(bjd_times)
    expected = bjd_times - KEPLER_TIME_OFFSET_BKJD
    np.testing.assert_allclose(bkjd_times, expected)

    # Already in BKJD
    already_bkjd = np.array([130.0, 131.0, 132.0])
    aligned = validate_and_align_time_system(already_bkjd)
    np.testing.assert_allclose(aligned, already_bkjd)


def test_transit_masking():
    """Verify in-transit points are correctly identified around mid-transit."""
    period = 10.0  # days
    t0 = 100.0     # BKJD
    duration_hrs = 4.8  # 0.2 days

    times = np.array([99.8, 99.95, 100.0, 100.05, 100.2, 110.0])
    # Transit region: duration_days = 0.2, half = 0.1, with 1.2 factor = 0.12 days
    mask = compute_transit_mask(times, period=period, t0=t0, duration_hours=duration_hrs, mask_factor=1.2)

    # 99.95, 100.0, 100.05, and 110.0 (one orbit later) should be in-transit
    assert mask[1] is True or mask[1] == 1
    assert mask[2] is True or mask[2] == 1
    assert mask[3] is True or mask[3] == 1
    assert mask[5] is True or mask[5] == 1
    # 99.8 and 100.2 are out-of-transit (> 0.12 days from center)
    assert mask[0] is False or mask[0] == 0
    assert mask[4] is False or mask[4] == 0


def test_normalization_formula_and_bounds():
    """Verify normalized = (flux - median) / abs(min(flux - median)) centers at 0 and depths at -1."""
    # Synthetic transit with continuum at 1.0 and dip to 0.99 (depth = 0.01)
    flux = np.full(100, 1.0)
    flux[45:55] = 0.99

    norm = normalize_folded_view(flux)
    assert np.all(np.isfinite(norm))
    assert abs(np.median(norm)) < 1e-4  # Continuum centered at 0.0
    assert abs(np.min(norm) - (-1.0)) < 1e-4  # Maximum transit depth scaled to -1.0


def test_normalization_constant_and_zero_denominator():
    """Verify flat signals return zero without crashing or returning NaNs."""
    flat_flux = np.full(50, 1.0)
    norm = normalize_folded_view(flat_flux)
    assert not np.isnan(norm).any()
    assert (norm == 0.0).all()

