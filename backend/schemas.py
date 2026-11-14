"""Pydantic schemas for Exoplanet Finder FastAPI Backend."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    torch_version: str
    cuda_available: bool
    device_name: str
    device_count: int
    models_loaded: Dict[str, bool]
    dataset_records: int
    cached_stars: int


class StatsResponse(BaseModel):
    total_candidates: int
    unique_stars: int
    planet_candidates: int
    false_positives: int
    non_transiting: int
    split_counts: Dict[str, int]
    cached_lightcurves: int
    baseline_roc_auc: float
    baseline_avg_precision: float
    cnn_parameters: int


class CandidateSummary(BaseModel):
    kepid: int
    tce_plnt_num: int
    tce_period: Optional[float] = None
    tce_time0bk: Optional[float] = None
    tce_duration: Optional[float] = None
    tce_depth: Optional[float] = None
    tce_model_snr: Optional[float] = None
    tce_prad: Optional[float] = None
    tce_impact: Optional[float] = None
    av_training_set: Optional[str] = None
    radius_earth: Optional[float] = None


class CandidateListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    candidates: List[CandidateSummary]


class CandidateDetailResponse(BaseModel):
    kepid: int
    tce_plnt_num: int
    tce_period: Optional[float] = None
    tce_period_err: Optional[float] = None
    tce_time0bk: Optional[float] = None
    tce_time0bk_err: Optional[float] = None
    tce_duration: Optional[float] = None
    tce_duration_err: Optional[float] = None
    tce_depth: Optional[float] = None
    tce_depth_err: Optional[float] = None
    tce_model_snr: Optional[float] = None
    tce_prad: Optional[float] = None
    tce_impact: Optional[float] = None
    tce_steff: Optional[float] = None
    tce_sradius: Optional[float] = None
    tce_smass: Optional[float] = None
    tce_slogg: Optional[float] = None
    av_training_set: Optional[str] = None
    is_cached: bool


class LightCurveDataResponse(BaseModel):
    kepid: int
    total_points: int
    returned_points: int
    time: List[float]
    raw_flux: List[float]
    detrended_flux: Optional[List[float]] = None
    trend_flux: Optional[List[float]] = None
    transit_mask: Optional[List[bool]] = None
    status: str
    source: str


class FoldedViewsResponse(BaseModel):
    kepid: int
    tce_plnt_num: int
    global_phase: List[float]
    global_view: List[float]
    local_phase: List[float]
    local_view: List[float]
    period: float
    duration_hours: float
    depth_ppm: float


class PredictRequest(BaseModel):
    kepid: int
    tce_plnt_num: Optional[int] = 1
    period: Optional[float] = None
    t0: Optional[float] = None
    duration_hours: Optional[float] = None
    depth_ppm: Optional[float] = None
    force_refresh: Optional[bool] = False


class PredictResponse(BaseModel):
    kepid: int
    tce_plnt_num: int
    category: str
    planet_probability: float
    confidence: float
    threshold: float
    period: float
    duration_hours: float
    depth_ppm: float
    global_view: List[float]
    local_view: List[float]
    ig_global: Optional[List[float]] = None
    ig_local: Optional[List[float]] = None
    morphology: Dict[str, Any]
    lightcurve_meta: Dict[str, Any]
    warning: Optional[str] = None


class Kepler90Planet(BaseModel):
    name: str
    letter: str
    period_days: float
    semi_major_axis_au: float
    radius_earth: float
    temp_kelvin: int
    transit_depth_ppm: float
    discovery_year: int
    discovered_by_ai: bool
    eccentricity: float
    color: str


class Kepler90SystemResponse(BaseModel):
    star_name: str
    kepid: int
    spectral_type: str
    mass_solar: float
    radius_solar: float
    temperature_kelvin: int
    distance_ly: int
    constellation: str
    total_confirmed_planets: int
    ai_discovery_summary: str
    planets: List[Kepler90Planet]
    solar_system_comparison: Dict[str, Any]

