"""Dataset & Cache Management router."""
import os
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter

from src.config import cfg
from backend.services import get_cache, get_candidates_df

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("/cache")
def get_cache_status() -> Dict[str, Any]:
    cache = get_cache()
    cached_stars = cache.list_cached_stars()

    file_details: List[Dict[str, Any]] = []
    total_bytes = 0

    for kepid in cached_stars:
        p = cfg.lightcurves_dir / f"kic_{kepid}.parquet"
        if p.exists():
            size = p.stat().st_size
            total_bytes += size
            file_details.append({
                "kepid": kepid,
                "file_name": p.name,
                "size_kb": round(size / 1024.0, 1),
                "modified": p.stat().st_mtime,
            })

    # Dataset file statistics
    raw_file = cfg.tce_catalog_file
    processed_file = cfg.processed_dir / "tce_cleaned.csv"

    dataset_stats = {
        "raw_dataset_present": raw_file.exists(),
        "raw_size_mb": round(raw_file.stat().st_size / (1024 * 1024), 2) if raw_file.exists() else 0,
        "processed_dataset_present": processed_file.exists(),
        "processed_size_mb": round(processed_file.stat().st_size / (1024 * 1024), 2) if processed_file.exists() else 0,
        "total_cache_mb": round(total_bytes / (1024 * 1024), 2),
        "cached_count": len(file_details),
    }

    return {
        "stats": dataset_stats,
        "cached_files": file_details,
    }
