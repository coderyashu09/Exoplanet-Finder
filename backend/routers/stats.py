"""Global catalog and model statistics router."""
import json
from fastapi import APIRouter

from src.config import cfg
from backend.schemas import StatsResponse
from backend.services import get_candidates_df, get_cache, get_predictor

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("", response_model=StatsResponse)
def get_global_statistics() -> StatsResponse:
    df = get_candidates_df()
    cache = get_cache()
    predictor = get_predictor()

    total = len(df)
    unique_stars = int(df["kepid"].nunique())

    counts = df["av_training_set"].value_counts().to_dict() if "av_training_set" in df.columns else {}
    pc_count = int(counts.get("PC", 0))
    afp_count = int(counts.get("AFP", 0))
    ntp_count = int(counts.get("NTP", 0))

    # Splits count from star_splits.json if available
    split_path = cfg.splits_dir / "star_splits.json"
    splits = {"train": 12605, "val": 1570, "test": 1562}
    if split_path.exists():
        try:
            with open(split_path, "r", encoding="utf-8") as f:
                s_data = json.load(f)
                splits = {
                    "train": len(s_data.get("train", [])),
                    "val": len(s_data.get("val", [])),
                    "test": len(s_data.get("test", [])),
                }
        except Exception:
            pass

    # Model parameters count
    param_count = 0
    if predictor.model is not None:
        param_count = sum(p.numel() for p in predictor.model.parameters())

    # Baseline metrics from model_comparison.json
    baseline_auc = 0.9457
    baseline_ap = 0.7836
    comp_path = cfg.outputs_dir / "metrics" / "model_comparison.json"
    if comp_path.exists():
        try:
            with open(comp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                baseline_auc = data.get("roc_auc", {}).get("baseline", 0.9457)
                baseline_ap = data.get("average_precision", {}).get("baseline", 0.7836)
        except Exception:
            pass

    return StatsResponse(
        total_candidates=total,
        unique_stars=unique_stars,
        planet_candidates=pc_count,
        false_positives=afp_count,
        non_transiting=ntp_count,
        split_counts=splits,
        cached_lightcurves=len(cache.list_cached_stars()),
        baseline_roc_auc=round(baseline_auc, 4),
        baseline_avg_precision=round(baseline_ap, 4),
        cnn_parameters=param_count,
    )

