"""Candidate Explorer endpoints: search, filtering, pagination, and candidate details."""
from typing import Optional, List
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.schemas import CandidateListResponse, CandidateSummary, CandidateDetailResponse
from backend.services import get_candidates_df, get_cache

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.get("", response_model=CandidateListResponse)
def list_candidates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=5, le=200, description="Items per page"),
    kepid: Optional[int] = Query(None, description="Filter by exact KIC ID"),
    disposition: Optional[str] = Query("ALL", description="Filter by label: ALL, PC, AFP, NTP"),
    min_period: Optional[float] = Query(None, description="Minimum period in days"),
    max_period: Optional[float] = Query(None, description="Maximum period in days"),
    min_snr: Optional[float] = Query(None, description="Minimum SNR"),
    sort_by: str = Query("kepid", description="Column to sort by"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
) -> CandidateListResponse:
    df = get_candidates_df()
    filtered = df

    # Search by KIC ID (partial string match or exact int)
    if kepid is not None:
        filtered = filtered[filtered["kepid"] == kepid]

    # Filter by disposition
    if disposition and disposition.upper() != "ALL":
        filtered = filtered[filtered["av_training_set"].str.upper() == disposition.upper()]

    # Period filter
    if min_period is not None:
        filtered = filtered[filtered["tce_period"] >= min_period]
    if max_period is not None:
        filtered = filtered[filtered["tce_period"] <= max_period]

    # SNR filter
    if min_snr is not None and "tce_model_snr" in filtered.columns:
        filtered = filtered[filtered["tce_model_snr"] >= min_snr]

    total = len(filtered)
    total_pages = max(1, int(np.ceil(total / page_size)))

    # Sorting
    ascending = sort_dir.lower() == "asc"
    valid_sort_cols = ["kepid", "tce_plnt_num", "tce_period", "tce_depth", "tce_model_snr", "tce_prad", "tce_duration"]
    if sort_by in valid_sort_cols and sort_by in filtered.columns:
        filtered = filtered.sort_values(by=sort_by, ascending=ascending)

    # Pagination slice
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    sliced = filtered.iloc[start_idx:end_idx]

    candidates: List[CandidateSummary] = []
    for _, row in sliced.iterrows():
        candidates.append(
            CandidateSummary(
                kepid=int(row["kepid"]),
                tce_plnt_num=int(row.get("tce_plnt_num", 1)),
                tce_period=float(row["tce_period"]) if pd.notnull(row.get("tce_period")) else None,
                tce_time0bk=float(row["tce_time0bk"]) if pd.notnull(row.get("tce_time0bk")) else None,
                tce_duration=float(row["tce_duration"]) if pd.notnull(row.get("tce_duration")) else None,
                tce_depth=float(row["tce_depth"]) if pd.notnull(row.get("tce_depth")) else None,
                tce_model_snr=float(row["tce_model_snr"]) if pd.notnull(row.get("tce_model_snr")) else None,
                tce_prad=float(row["tce_prad"]) if pd.notnull(row.get("tce_prad")) else None,
                tce_impact=float(row["tce_impact"]) if pd.notnull(row.get("tce_impact")) else None,
                av_training_set=str(row["av_training_set"]) if pd.notnull(row.get("av_training_set")) else None,
                radius_earth=float(row["tce_prad"]) if pd.notnull(row.get("tce_prad")) else None,
            )
        )

    return CandidateListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        candidates=candidates,
    )


@router.get("/{kepid}", response_model=List[CandidateSummary])
def get_candidate_tces(kepid: int) -> List[CandidateSummary]:
    """Retrieve all Threshold Crossing Events (TCEs) recorded for a given KIC star."""
    df = get_candidates_df()
    matched = df[df["kepid"] == kepid]
    if matched.empty:
        raise HTTPException(status_code=404, detail=f"No TCE records found for KIC {kepid}")
    
    results = []
    for _, row in matched.iterrows():
        results.append(
            CandidateSummary(
                kepid=int(row["kepid"]),
                tce_plnt_num=int(row.get("tce_plnt_num", 1)),
                tce_period=float(row["tce_period"]) if pd.notnull(row.get("tce_period")) else None,
                tce_time0bk=float(row["tce_time0bk"]) if pd.notnull(row.get("tce_time0bk")) else None,
                tce_duration=float(row["tce_duration"]) if pd.notnull(row.get("tce_duration")) else None,
                tce_depth=float(row["tce_depth"]) if pd.notnull(row.get("tce_depth")) else None,
                tce_model_snr=float(row["tce_model_snr"]) if pd.notnull(row.get("tce_model_snr")) else None,
                tce_prad=float(row["tce_prad"]) if pd.notnull(row.get("tce_prad")) else None,
                tce_impact=float(row["tce_impact"]) if pd.notnull(row.get("tce_impact")) else None,
                av_training_set=str(row["av_training_set"]) if pd.notnull(row.get("av_training_set")) else None,
                radius_earth=float(row["tce_prad"]) if pd.notnull(row.get("tce_prad")) else None,
            )
        )
    return results


@router.get("/{kepid}/tces", response_model=List[CandidateSummary])
def get_candidate_tces_alias(kepid: int) -> List[CandidateSummary]:
    return get_candidate_tces(kepid)


@router.get("/{kepid}/{tce_plnt_num}", response_model=CandidateDetailResponse)
def get_candidate_detail(kepid: int, tce_plnt_num: int) -> CandidateDetailResponse:
    df = get_candidates_df()
    cache = get_cache()

    matched = df[(df["kepid"] == kepid) & (df["tce_plnt_num"] == tce_plnt_num)]
    if matched.empty:
        # Fall back to matching just kepid if specific plant num is not present
        matched = df[df["kepid"] == kepid]
        if matched.empty:
            raise HTTPException(status_code=404, detail=f"Candidate KIC {kepid} not found.")

    row = matched.iloc[0]

    def _safe_float(val):
        return float(val) if pd.notnull(val) else None

    return CandidateDetailResponse(
        kepid=int(row["kepid"]),
        tce_plnt_num=int(row.get("tce_plnt_num", 1)),
        tce_period=_safe_float(row.get("tce_period")),
        tce_period_err=_safe_float(row.get("tce_period_err")),
        tce_time0bk=_safe_float(row.get("tce_time0bk")),
        tce_time0bk_err=_safe_float(row.get("tce_time0bk_err")),
        tce_duration=_safe_float(row.get("tce_duration")),
        tce_duration_err=_safe_float(row.get("tce_duration_err")),
        tce_depth=_safe_float(row.get("tce_depth")),
        tce_depth_err=_safe_float(row.get("tce_depth_err")),
        tce_model_snr=_safe_float(row.get("tce_model_snr")),
        tce_prad=_safe_float(row.get("tce_prad")),
        tce_impact=_safe_float(row.get("tce_impact")),
        tce_steff=_safe_float(row.get("tce_steff")),
        tce_sradius=_safe_float(row.get("tce_sradius")),
        tce_smass=_safe_float(row.get("tce_smass")),
        tce_slogg=_safe_float(row.get("tce_slogg")),
        av_training_set=str(row.get("av_training_set", "UNKNOWN")),
        is_cached=cache.is_cached(kepid),
    )

