"""Exoplanet Detection Laboratory router: real neural inference, attributions, morphology."""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.schemas import PredictRequest, PredictResponse
from backend.services import get_predictor, get_candidates_df

router = APIRouter(prefix="/api/predict", tags=["Inference"])


@router.post("", response_model=PredictResponse)
def run_prediction(req: PredictRequest) -> PredictResponse:
    predictor = get_predictor()
    df = get_candidates_df()

    period = req.period
    t0 = req.t0
    duration_hours = req.duration_hours
    depth_ppm = req.depth_ppm

    # If any ephemeris parameters are missing, look them up in the catalog
    if period is None or t0 is None or duration_hours is None:
        matched = df[(df["kepid"] == req.kepid) & (df["tce_plnt_num"] == req.tce_plnt_num)]
        if matched.empty:
            matched = df[df["kepid"] == req.kepid]

        if not matched.empty:
            row = matched.iloc[0]
            period = period if period is not None else float(row.get("tce_period", 10.0))
            t0 = t0 if t0 is not None else float(row.get("tce_time0bk", 130.0))
            duration_hours = duration_hours if duration_hours is not None else float(row.get("tce_duration", 3.0))
            depth_ppm = depth_ppm if depth_ppm is not None else float(row.get("tce_depth", 500.0))
        else:
            period = period or 10.0
            t0 = t0 or 130.0
            duration_hours = duration_hours or 3.0
            depth_ppm = depth_ppm or 500.0

    try:
        pred = predictor.predict_candidate(
            kepid=req.kepid,
            period=period,
            t0=t0,
            duration_hours=duration_hours,
            depth_ppm=depth_ppm,
            force_refresh_lc=req.force_refresh or False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error on KIC {req.kepid}: {str(e)}")

    if pred.get("category") == "Insufficient Data":
        raise HTTPException(
            status_code=404,
            detail=pred.get("warning", f"Insufficient light curve observations for KIC {req.kepid}."),
        )

    # Convert numpy arrays to lists for JSON serialization
    global_view = pred.get("global_view")
    if isinstance(global_view, np.ndarray):
        global_view = global_view.tolist()

    local_view = pred.get("local_view")
    if isinstance(local_view, np.ndarray):
        local_view = local_view.tolist()

    ig_global = pred.get("ig_global")
    if isinstance(ig_global, np.ndarray):
        ig_global = ig_global.tolist()

    ig_local = pred.get("ig_local")
    if isinstance(ig_local, np.ndarray):
        ig_local = ig_local.tolist()

    return PredictResponse(
        kepid=req.kepid,
        tce_plnt_num=req.tce_plnt_num or 1,
        category=pred["category"],
        planet_probability=pred["planet_probability"],
        confidence=pred["confidence"],
        threshold=pred["threshold"],
        period=round(period, 5),
        duration_hours=round(duration_hours, 3),
        depth_ppm=round(depth_ppm, 2),
        global_view=global_view or [],
        local_view=local_view or [],
        ig_global=ig_global,
        ig_local=ig_local,
        morphology=pred.get("morphology", {}),
        lightcurve_meta=pred.get("lightcurve_meta", {}),
        warning=pred.get("warning"),
    )

