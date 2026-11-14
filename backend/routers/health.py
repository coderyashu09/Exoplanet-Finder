"""Health and system diagnostics router."""
import torch
from fastapi import APIRouter

from backend.schemas import HealthResponse
from backend.services import get_predictor, get_candidates_df, get_cache

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def get_system_health() -> HealthResponse:
    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"
    device_count = torch.cuda.device_count() if cuda_avail else 0

    predictor = get_predictor()
    cache = get_cache()
    df = get_candidates_df()

    return HealthResponse(
        status="healthy",
        torch_version=torch.__version__,
        cuda_available=cuda_avail,
        device_name=device_name,
        device_count=device_count,
        models_loaded={
            "cnn_two_view": predictor.is_model_loaded,
            "baseline_classifier": True
        },
        dataset_records=len(df),
        cached_stars=len(cache.list_cached_stars()),
    )

