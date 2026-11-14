"""Kepler light curve retrieval, stitching, validation, and persistent disk caching."""
import logging
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import numpy as np
import pandas as pd

from src.config import cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class LightCurveCache:
    """Manages persistent on-disk storage of stitched stellar light curves."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or cfg.lightcurves_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, kepid: int) -> Path:
        return self.cache_dir / f"kic_{kepid}.parquet"

    def exists(self, kepid: int) -> bool:
        path = self._get_path(kepid)
        return path.exists() and path.stat().st_size > 512

    def is_cached(self, kepid: int) -> bool:
        return self.exists(kepid)

    def save(self, kepid: int, time_arr: np.ndarray, flux_arr: np.ndarray, flux_err: Optional[np.ndarray] = None) -> Path:
        path = self._get_path(kepid)
        df = pd.DataFrame({
            "time": time_arr,
            "flux": flux_arr,
            "flux_err": flux_err if flux_err is not None else np.zeros_like(flux_arr),
        })
        # Save as compressed parquet
        df.to_parquet(path, compression="snappy", index=False)
        return path

    def load(self, kepid: int) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        if not self.exists(kepid):
            return None
        path = self._get_path(kepid)
        try:
            df = pd.read_parquet(path)
            time_arr = df["time"].to_numpy(dtype=np.float64)
            flux_arr = df["flux"].to_numpy(dtype=np.float64)
            flux_err = df["flux_err"].to_numpy(dtype=np.float64)
            # Remove any NaNs or infinities
            valid = np.isfinite(time_arr) & np.isfinite(flux_arr) & (flux_arr > 0)
            return time_arr[valid], flux_arr[valid], flux_err[valid]
        except Exception as e:
            logger.warning(f"Failed to read cached light curve for KIC {kepid}: {e}. Removing corrupt file.")
            path.unlink(missing_ok=True)
            return None

    def list_cached_stars(self) -> list[int]:
        cached = []
        for p in self.cache_dir.glob("kic_*.parquet"):
            try:
                kid = int(p.stem.replace("kic_", ""))
                cached.append(kid)
            except ValueError:
                continue
        return sorted(cached)


def download_stellar_lightcurve(
    kepid: int,
    cache: Optional[LightCurveCache] = None,
    force_refresh: bool = False,
    max_retries: int = 3,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Dict[str, Any]]:
    """Retrieve Kepler long-cadence observations using Lightkurve, stitch quarters, and cache locally.

    Returns:
        (time, flux, flux_err, metadata)
    """
    cache = cache or LightCurveCache()
    meta: Dict[str, Any] = {"kepid": kepid, "cached": False, "quarters": 0, "status": "unknown"}

    if not force_refresh and cache.exists(kepid):
        data = cache.load(kepid)
        if data is not None:
            t, f, fe = data
            meta["cached"] = True
            meta["status"] = "success_cache"
            meta["num_points"] = len(t)
            return t, f, fe, meta

    # Lightkurve retrieval
    try:
        import lightkurve as lk
    except ImportError:
        logger.error("lightkurve is not installed in current environment.")
        meta["status"] = "missing_dependency"
        meta["error"] = "Lightkurve library not installed."
        return None, None, None, meta

    logger.info(f"Querying MAST for KIC {kepid} long-cadence light curves...")
    for attempt in range(1, max_retries + 1):
        try:
            search_result = lk.search_lightcurve(
                f"KIC {kepid}",
                mission="Kepler",
                cadence="long",
                author="Kepler",
            )
            if len(search_result) == 0:
                logger.warning(f"No Kepler long-cadence data found for KIC {kepid}.")
                meta["status"] = "not_found"
                return None, None, None, meta

            meta["quarters"] = len(search_result)
            lc_collection = search_result.download_all()
            if lc_collection is None or len(lc_collection) == 0:
                meta["status"] = "download_empty"
                return None, None, None, meta

            stitched = lc_collection.stitch()
            cleaned = stitched.remove_nans().remove_outliers(sigma_lower=20, sigma_upper=5)

            # Extract time in BKJD
            # Lightkurve Kepler light curves store time in BKJD (BJD - 2454833.0)
            time_vals = cleaned.time.value.astype(np.float64)
            flux_vals = cleaned.flux.value.astype(np.float64)
            flux_err_vals = cleaned.flux_err.value.astype(np.float64) if cleaned.flux_err is not None else np.zeros_like(flux_vals)

            # Sanity filter
            valid = np.isfinite(time_vals) & np.isfinite(flux_vals) & (flux_vals > 0)
            time_vals = time_vals[valid]
            flux_vals = flux_vals[valid]
            flux_err_vals = flux_err_vals[valid]

            if len(time_vals) < 50:
                meta["status"] = "insufficient_cadences"
                return None, None, None, meta

            # Cache to disk
            cache.save(kepid, time_vals, flux_vals, flux_err_vals)
            meta["cached"] = False
            meta["status"] = "success_downloaded"
            meta["num_points"] = len(time_vals)
            logger.info(f"Successfully cached KIC {kepid}: {len(time_vals)} data points across {meta['quarters']} quarters.")
            return time_vals, flux_vals, flux_err_vals, meta

        except Exception as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed for KIC {kepid}: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                meta["status"] = "error"
                meta["error"] = str(e)
                return None, None, None, meta

    return None, None, None, meta

