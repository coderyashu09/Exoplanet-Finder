"""Shared backend services: data management, model predictor singleton, and light curve operations."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import numpy as np
import pandas as pd
import torch

from src.config import cfg
from src.predict import ExoplanetPredictor
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve
from src.phase_folding import generate_two_views

logger = logging.getLogger("exoplanet_backend")

# Global singleton holders
_predictor: Optional[ExoplanetPredictor] = None
_df_candidates: Optional[pd.DataFrame] = None
_cache: Optional[LightCurveCache] = None


def get_cache() -> LightCurveCache:
    global _cache
    if _cache is None:
        _cache = LightCurveCache(cfg.lightcurves_dir)
    return _cache


def get_predictor() -> ExoplanetPredictor:
    global _predictor
    if _predictor is None:
        logger.info("Initializing ExoplanetPredictor singleton...")
        _predictor = ExoplanetPredictor()
    return _predictor


def get_candidates_df() -> pd.DataFrame:
    global _df_candidates
    if _df_candidates is None:
        processed_path = cfg.processed_dir / "tce_cleaned.csv"
        raw_path = cfg.tce_catalog_file

        target_path = processed_path if processed_path.exists() else raw_path
        if not target_path.exists():
            raise FileNotFoundError(f"Neither {processed_path} nor {raw_path} exists.")

        logger.info(f"Loading candidate dataset from {target_path}...")
        df = pd.read_csv(target_path)

        # Standardize expected columns
        if "av_training_set" not in df.columns and "disposition" in df.columns:
            df["av_training_set"] = df["disposition"]

        # Ensure numeric types
        numeric_cols = [
            "kepid", "tce_plnt_num", "tce_period", "tce_time0bk",
            "tce_duration", "tce_depth", "tce_model_snr", "tce_prad", "tce_impact"
        ]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        _df_candidates = df
        logger.info(f"Loaded {len(_df_candidates)} candidate records.")
    return _df_candidates


def subsample_timeseries(
    time_arr: np.ndarray,
    flux_arr: np.ndarray,
    max_points: int = 3000
) -> Tuple[np.ndarray, np.ndarray]:
    """Subsamples a long time series uniformly for high-performance frontend charting."""
    n = len(time_arr)
    if n <= max_points:
        return time_arr, flux_arr
    step = int(np.ceil(n / max_points))
    return time_arr[::step], flux_arr[::step]
