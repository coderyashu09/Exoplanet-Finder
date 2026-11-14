"""Light Curve Analysis Studio router: raw, detrended, and dual folded views."""
from typing import Optional
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from src.config import cfg
from src.lightcurve_downloader import download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve
from src.phase_folding import generate_two_views
from backend.schemas import LightCurveDataResponse, FoldedViewsResponse
from backend.services import get_cache, get_candidates_df, subsample_timeseries

router = APIRouter(prefix="/api/lightcurve", tags=["Lightcurves"])


@router.get("/{kepid}", response_model=LightCurveDataResponse)
def get_lightcurve(
    kepid: int,
    max_points: int = Query(3000, ge=500, le=20000, description="Max points to return for frontend performance"),
    force_refresh: bool = Query(False, description="Force re-download from MAST"),
) -> LightCurveDataResponse:
    cache = get_cache()
    df = get_candidates_df()

    # Retrieve candidate ephemeris for transit masking during detrending
    matched = df[df["kepid"] == kepid]
    period = 10.0
    t0 = 130.0
    duration_hours = 3.0

    if not matched.empty:
        row = matched.iloc[0]
        period = float(row.get("tce_period", 10.0))
        t0 = float(row.get("tce_time0bk", 130.0))
        duration_hours = float(row.get("tce_duration", 3.0))

    # Download or read from cache
    time_arr, flux_arr, flux_err, meta = download_stellar_lightcurve(
        kepid=kepid,
        cache=cache,
        force_refresh=force_refresh,
    )

    if time_arr is None or len(time_arr) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No light curve cadences found for star KIC {kepid}: {meta.get('error', 'MAST retrieval failed')}",
        )

    # Time alignment to BKJD
    t_aligned = validate_and_align_time_system(time_arr)

    # Detrending / Flattening
    detrended_flux, trend_flux, flat_meta = flatten_lightcurve(
        time_arr=t_aligned,
        flux_arr=flux_arr,
        period=period,
        t0=t0,
        duration_hours=duration_hours,
        window_length=cfg.flatten_window_length,
    )

    total_points = len(t_aligned)

    # Subsample for smooth UI responsiveness
    sub_time, sub_raw = subsample_timeseries(t_aligned, flux_arr, max_points)
    _, sub_detrended = subsample_timeseries(t_aligned, detrended_flux, max_points)
    _, sub_trend = subsample_timeseries(t_aligned, trend_flux, max_points)

    return LightCurveDataResponse(
        kepid=kepid,
        total_points=total_points,
        returned_points=len(sub_time),
        time=sub_time.tolist(),
        raw_flux=sub_raw.tolist(),
        detrended_flux=sub_detrended.tolist(),
        trend_flux=sub_trend.tolist(),
        transit_mask=None,
        status=meta.get("status", "success"),
        source=meta.get("source", "cache" if cache.is_cached(kepid) else "MAST"),
    )


@router.get("/views/{kepid}/{tce_plnt_num}", response_model=FoldedViewsResponse)
def get_folded_views(kepid: int, tce_plnt_num: int) -> FoldedViewsResponse:
    cache = get_cache()
    df = get_candidates_df()

    matched = df[(df["kepid"] == kepid) & (df["tce_plnt_num"] == tce_plnt_num)]
    if matched.empty:
        matched = df[df["kepid"] == kepid]
        if matched.empty:
            raise HTTPException(status_code=404, detail=f"Candidate KIC {kepid} not found.")

    row = matched.iloc[0]
    period = float(row.get("tce_period", 10.0))
    t0 = float(row.get("tce_time0bk", 130.0))
    duration_hours = float(row.get("tce_duration", 3.0))
    depth_ppm = float(row.get("tce_depth", 500.0))

    # Retrieve light curve
    time_arr, flux_arr, _, meta = download_stellar_lightcurve(kepid=kepid, cache=cache)
    if time_arr is None or len(time_arr) < 50:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient observation cadences for KIC {kepid}: {meta.get('error', 'Less than 50 points')}",
        )

    t_aligned = validate_and_align_time_system(time_arr)
    flat_flux, _, _ = flatten_lightcurve(
        time_arr=t_aligned,
        flux_arr=flux_arr,
        period=period,
        t0=t0,
        duration_hours=duration_hours,
    )

    global_view, local_view, _ = generate_two_views(
        time_arr=t_aligned,
        flux_arr=flat_flux,
        period=period,
        t0=t0,
        duration_hours=duration_hours,
        global_bins=cfg.cnn_global_length,
        local_bins=cfg.cnn_local_length,
        local_factor=cfg.local_duration_factor,
    )

    # Phase coordinates
    global_phase = np.linspace(-0.5, 0.5, cfg.cnn_global_length).tolist()
    local_window = (cfg.local_duration_factor * duration_hours) / (24.0 * period)
    local_phase = np.linspace(-local_window / 2.0, local_window / 2.0, cfg.cnn_local_length).tolist()

    return FoldedViewsResponse(
        kepid=kepid,
        tce_plnt_num=tce_plnt_num,
        global_phase=global_phase,
        global_view=global_view.tolist(),
        local_phase=local_phase,
        local_view=local_view.tolist(),
        period=round(period, 5),
        duration_hours=round(duration_hours, 3),
        depth_ppm=round(depth_ppm, 2),
    )

