"""Unit tests for phase-folding, Global View (2001 bins) and Local View (201 bins) generation."""
import numpy as np
import pytest

from src.phase_folding import (
    fold_lightcurve,
    generate_global_view,
    generate_local_view,
    generate_two_views,
)


def test_fold_lightcurve_centering():
    """Verify phase formula centers transit at 0.0 in range [-period/2, +period/2]."""
    period = 10.0
    t0 = 50.0

    times = np.array([45.0, 50.0, 55.0, 60.0])
    phases, _ = fold_lightcurve(times, np.ones_like(times), period=period, t0=t0)

    # At t = 50.0 and t = 60.0, transit is centered at phase 0.0
    assert 0.0 in phases or np.isclose(phases, 0.0).any()
    assert (phases >= -period / 2.0).all()
    assert (phases <= period / 2.0).all()


def test_dual_view_dimensions_and_finite_values():
    """Verify exact output shapes: Global View (2001,), Local View (201,) with zero NaNs."""
    np.random.seed(42)
    # 200 days of observation, 30-min cadence (48 per day = 9600 points)
    times = np.linspace(100.0, 300.0, 9600)
    fluxes = 1.0 + np.random.normal(0, 0.001, size=len(times))

    # Inject periodic box transit
    period = 12.5
    t0 = 105.0
    duration_hrs = 4.0
    dur_days = duration_hrs / 24.0

    phases = ((times - t0 + period / 2.0) % period) - period / 2.0
    fluxes[np.abs(phases) < dur_days / 2.0] -= 0.005  # 5000 ppm dip

    global_v, local_v, meta = generate_two_views(
        time_arr=times,
        flux_arr=fluxes,
        period=period,
        t0=t0,
        duration_hours=duration_hrs,
        global_bins=2001,
        local_bins=201,
    )

    # Exact expected tensor dimensions
    assert global_v.shape == (2001,), f"Expected (2001,), got {global_v.shape}"
    assert local_v.shape == (201,), f"Expected (201,), got {local_v.shape}"

    # No NaNs or infinities
    assert np.all(np.isfinite(global_v)), "Global view contains NaNs or infs"
    assert np.all(np.isfinite(local_v)), "Local view contains NaNs or infs"

    # Transit dip should be at phase 0 in local view (index ~100)
    center_idx = len(local_v) // 2
    assert local_v[center_idx] < -0.5, "Transit dip was not captured in the center of local view!"

