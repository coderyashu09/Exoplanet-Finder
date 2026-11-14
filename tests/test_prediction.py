"""Unit tests for ExoplanetPredictor inference pipeline and invalid data handling."""
import numpy as np
import pytest

from src.predict import ExoplanetPredictor


def test_prediction_pipeline_synthetic_input():
    """Test full inference pipeline with synthetic photometric series."""
    predictor = ExoplanetPredictor()

    times = np.linspace(100.0, 150.0, 2400)
    fluxes = np.ones_like(times)
    # Transit dip
    period = 10.0
    t0 = 105.0
    duration_hrs = 3.0
    dur_days = duration_hrs / 24.0

    phases = ((times - t0 + period / 2.0) % period) - period / 2.0
    fluxes[np.abs(phases) < dur_days / 2.0] = 0.99

    res = predictor.predict_from_lightcurve(
        time_arr=times,
        flux_arr=fluxes,
        period=period,
        t0=t0,
        duration_hours=duration_hrs,
        depth_ppm=10000.0,
        compute_attributions=False,
    )

    assert "planet_probability" in res
    assert "threshold" in res
    assert "category" in res
    assert res["category"] in ["Planet-like Signal", "Non-Planet Signal", "Model Uninitialized"]
    assert "global_view" in res
    assert "local_view" in res
    assert len(res["global_view"]) == 2001
    assert len(res["local_view"]) == 201


def test_invalid_and_sparse_lightcurve_handling():
    """Verify that light curves with fewer than 50 points return 'Insufficient Data' gracefully."""
    predictor = ExoplanetPredictor()

    sparse_times = np.array([1.0, 2.0, 3.0])
    sparse_fluxes = np.array([1.0, 0.99, 1.0])

    res = predictor.predict_from_lightcurve(
        time_arr=sparse_times,
        flux_arr=sparse_fluxes,
        period=10.0,
        t0=1.0,
        duration_hours=2.0,
    )

    assert res["category"] == "Insufficient Data"
    assert res["planet_probability"] == 0.0
    assert "warning" in res

