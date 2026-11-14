"""Unified prediction pipeline for individual Kepler transit candidates."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
import torch

from src.config import cfg
from src.lightcurve_downloader import LightCurveCache, download_stellar_lightcurve
from src.preprocessing import validate_and_align_time_system, flatten_lightcurve
from src.phase_folding import generate_two_views
from src.model import DualViewExoplanetCNN
from src.explainability import compute_integrated_gradients_1d, analyze_transit_morphology

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ExoplanetPredictor:
    """Production predictor for Kepler transit candidates using the Two-View CNN."""

    def __init__(self, checkpoint_path: Optional[Path] = None, threshold_path: Optional[Path] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path or (cfg.checkpoints_dir / "best_model.pth")
        self.threshold_path = threshold_path or (cfg.metadata_dir / "classification_threshold.json")
        self.model: Optional[DualViewExoplanetCNN] = None
        self.threshold: float = cfg.default_threshold
        self.cache = LightCurveCache(cfg.lightcurves_dir)
        self._load_model_and_threshold()

    def _load_model_and_threshold(self) -> None:
        """Load trained PyTorch weights and optimal validation threshold."""
        if self.threshold_path.exists():
            try:
                with open(self.threshold_path, "r", encoding="utf-8") as f:
                    self.threshold = float(json.load(f).get("threshold", cfg.default_threshold))
            except Exception as e:
                logger.warning(f"Could not load threshold file: {e}")

        if self.checkpoint_path.exists():
            try:
                self.model = DualViewExoplanetCNN(
                    global_in_len=cfg.cnn_global_length,
                    local_in_len=cfg.cnn_local_length,
                )
                weights = torch.load(self.checkpoint_path, map_location=self.device, weights_only=True)
                self.model.load_state_dict(weights)
                self.model.to(self.device)
                self.model.eval()
                logger.info(f"Loaded CNN checkpoint from {self.checkpoint_path} onto {self.device}")
            except Exception as e:
                logger.error(f"Failed to load CNN checkpoint: {e}")
                self.model = None
        else:
            logger.info("CNN checkpoint not found. Predictor initialized without trained neural weights.")

    @property
    def is_model_loaded(self) -> bool:
        return self.model is not None

    def predict_from_lightcurve(
        self,
        time_arr: np.ndarray,
        flux_arr: np.ndarray,
        period: float,
        t0: float,
        duration_hours: float,
        depth_ppm: Optional[float] = None,
        compute_attributions: bool = True,
    ) -> Dict[str, Any]:
        """Process time-flux series and generate exoplanet prediction and explanation."""
        if len(time_arr) < 50:
            return {
                "category": "Insufficient Data",
                "planet_probability": 0.0,
                "confidence": 0.0,
                "threshold": self.threshold,
                "warning": "Fewer than 50 valid photometric cadences available.",
            }

        # 1. Time alignment (BKJD)
        t_aligned = validate_and_align_time_system(time_arr)

        # 2. Flattening with transit protection
        flat_flux, trend, flat_meta = flatten_lightcurve(
            time_arr=t_aligned,
            flux_arr=flux_arr,
            period=period,
            t0=t0,
            duration_hours=duration_hours,
            window_length=cfg.flatten_window_length,
        )

        # 3. Dual-View Phase Folding
        global_view, local_view, fold_meta = generate_two_views(
            time_arr=t_aligned,
            flux_arr=flat_flux,
            period=period,
            t0=t0,
            duration_hours=duration_hours,
            global_bins=cfg.cnn_global_length,
            local_bins=cfg.cnn_local_length,
            local_factor=cfg.local_duration_factor,
        )

        # 4. Neural Network Inference
        if not self.is_model_loaded:
            return {
                "category": "Model Uninitialized",
                "planet_probability": 0.0,
                "threshold": self.threshold,
                "global_view": global_view.tolist(),
                "local_view": local_view.tolist(),
                "flattened_flux": flat_flux.tolist(),
                "trend_flux": trend.tolist(),
                "warning": "CNN model has not been trained or checkpoint is missing. Train model first.",
            }

        g_tensor = torch.from_numpy(global_view).float().unsqueeze(0).to(self.device)
        l_tensor = torch.from_numpy(local_view).float().unsqueeze(0).to(self.device)

        with torch.no_grad():
            prob = float(self.model.predict_proba(g_tensor, l_tensor).item())

        # Prediction categorization
        uncertainty = cfg.uncertainty_window
        if prob >= self.threshold:
            category = "Planet-like Signal"
            confidence = min(1.0, (prob - self.threshold) / (1.0 - self.threshold + 1e-6))
        else:
            category = "Non-Planet Signal"
            confidence = min(1.0, (self.threshold - prob) / (self.threshold + 1e-6))

        # Integrated Gradients & morphology
        ig_global, ig_local = None, None
        if compute_attributions:
            try:
                ig_global, ig_local = compute_integrated_gradients_1d(
                    self.model, g_tensor, l_tensor, device=self.device
                )
            except Exception as e:
                logger.warning(f"Attribution calculation error: {e}")

        morphology = analyze_transit_morphology(global_view, local_view, period, duration_hours)

        return {
            "category": category,
            "planet_probability": round(prob, 4),
            "confidence": round(confidence, 4),
            "threshold": round(self.threshold, 4),
            "global_view": global_view,
            "local_view": local_view,
            "ig_global": ig_global,
            "ig_local": ig_local,
            "morphology": morphology,
            "flattening_meta": flat_meta,
            "folding_meta": fold_meta,
        }

    def predict_candidate(
        self,
        kepid: int,
        period: float,
        t0: float,
        duration_hours: float,
        depth_ppm: Optional[float] = None,
        force_refresh_lc: bool = False,
    ) -> Dict[str, Any]:
        """High-level pipeline: download/load lightcurve, process, infer, and explain."""
        time_arr, flux_arr, flux_err, lc_meta = download_stellar_lightcurve(
            kepid=kepid,
            cache=self.cache,
            force_refresh=force_refresh_lc,
        )

        if time_arr is None or len(time_arr) == 0:
            return {
                "kepid": kepid,
                "category": "Insufficient Data",
                "planet_probability": 0.0,
                "confidence": 0.0,
                "threshold": self.threshold,
                "lightcurve_status": lc_meta.get("status", "failed"),
                "warning": f"Unable to acquire Kepler observations for star KIC {kepid}: {lc_meta.get('error', 'No cadences')}",
            }

        pred = self.predict_from_lightcurve(
            time_arr=time_arr,
            flux_arr=flux_arr,
            period=period,
            t0=t0,
            duration_hours=duration_hours,
            depth_ppm=depth_ppm,
        )
        pred["kepid"] = kepid
        pred["lightcurve_meta"] = lc_meta
        return pred

