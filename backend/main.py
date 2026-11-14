"""EXOPLANET FINDER — FastAPI Intelligence Backend.

Serves authentic NASA Kepler astronomical data, Lightkurve time series,
and PyTorch Two-View Convolutional Neural Network inference.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.services import get_predictor, get_candidates_df
from backend.routers import (
    health,
    stats,
    candidates,
    lightcurves,
    inference,
    models,
    kepler90,
    experiments,
    data_mgmt,
    catalog,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("exoplanet_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NASA Kepler Data & Neural Pipeline...")
    try:
        # Pre-warm candidate dataset
        get_candidates_df()
        # Pre-warm neural network predictor
        get_predictor()
        logger.info("Exoplanet Finder Backend initialized successfully.")
    except Exception as e:
        logger.error(f"Startup warning during pre-warming: {e}")
    yield
    logger.info("Shutting down Exoplanet Finder Backend.")


app = FastAPI(
    title="EXOPLANET FINDER — NASA AI Planet Detection Platform",
    description="Full-stack AI/ML platform powered by NASA Kepler DR24 data and PyTorch Two-View 1D CNN.",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js (port 3000) and other local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(stats.router)
app.include_router(candidates.router)
app.include_router(lightcurves.router)
app.include_router(inference.router)
app.include_router(models.router)
app.include_router(kepler90.router)
app.include_router(experiments.router)
app.include_router(data_mgmt.router)
app.include_router(catalog.router)


@app.get("/")
def root():
    return {
        "platform": "EXOPLANET FINDER",
        "tagline": "Discover New Worlds Beyond Our Solar System",
        "mission": "NASA Kepler DR24 AI Planet Detection Platform",
        "version": "2.0.0",
        "documentation": "/docs",
        "status": "operational",
    }

