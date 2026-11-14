"""Unit and integration tests for the FastAPI backend endpoints."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "EXOPLANET FINDER"
    assert data["status"] == "operational"


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "torch_version" in data
    assert "cuda_available" in data
    assert data["dataset_records"] >= 15000


def test_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_candidates"] == 15737
    assert data["unique_stars"] > 9000
    assert data["planet_candidates"] > 3000
    assert data["baseline_roc_auc"] > 0.90


def test_candidates_list():
    response = client.get("/api/candidates?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15737
    assert len(data["candidates"]) == 10
    assert "kepid" in data["candidates"][0]


def test_candidate_detail_kepler90():
    response = client.get("/api/candidates/11442793/1")
    assert response.status_code == 200
    data = response.json()
    assert data["kepid"] == 11442793
    assert data["tce_period"] is not None


def test_kepler90_system():
    response = client.get("/api/kepler90")
    assert response.status_code == 200
    data = response.json()
    assert data["star_name"].startswith("Kepler-90")
    assert len(data["planets"]) == 8
    ai_planet = [p for p in data["planets"] if p["letter"] == "i"][0]
    assert ai_planet["discovered_by_ai"] is True


def test_models_comparison():
    response = client.get("/api/models/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "comparison" in data
    assert "baseline_metrics" in data
    assert "cnn_metrics" in data


def test_experiments_list():
    response = client.get("/api/experiments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_data_cache():
    response = client.get("/api/data/cache")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert data["stats"]["cached_count"] >= 1


def test_catalog_objects():
    response = client.get("/api/catalog/objects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    k90 = [o for o in data if o["id"] == "kepler-90"][0]
    assert k90["confirmed_planets_count"] == 8
    assert "visualization_category" in k90


def test_candidate_tces():
    response = client.get("/api/candidates/11442793/tces")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_predict_endpoint_kepler90():
    # Test real neural prediction on cached Kepler-90 star
    payload = {
        "kepid": 11442793,
        "tce_plnt_num": 1,
        "period": 7.008,
        "t0": 134.0,
        "duration_hours": 3.0,
        "depth_ppm": 340.0,
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["kepid"] == 11442793
    assert "planet_probability" in data
    assert "category" in data
    assert len(data["global_view"]) == 2001
    assert len(data["local_view"]) == 201
    assert "morphology" in data

