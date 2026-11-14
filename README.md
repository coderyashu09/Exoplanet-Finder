# 🪐 EXOPLANET FINDER — NASA Space Intelligence Platform

<p align="center">
  <img src="https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&w=1200&q=80" alt="Exoplanet Finder Banner" width="100%" style="border-radius: 12px; max-height: 400px; object-fit: cover;" />
</p>

<p align="center">
  <b>Discover Worlds Beyond Our Solar System · Powered by Deep Learning and Real NASA Kepler Data</b>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12"></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-2.6%2Bcu124-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-15.1%20(React%2019)-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js 15"></a>
  <a href="https://threejs.org/"><img src="https://img.shields.io/badge/Three.js-WebGL%203D-black?style=for-the-badge&logo=threedotjs&logoColor=white" alt="Three.js"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.162-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://developer.nvidia.com/cuda-zone"><img src="https://img.shields.io/badge/CUDA-RTX%20Acceleration-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="CUDA"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License: MIT"></a>
</p>

---

## 🌟 Executive Summary

**Exoplanet Finder** is a research-grade Space Intelligence and Deep Learning platform designed to detect, classify, and visualize extrasolar planets using genuine **NASA Kepler Space Telescope (Q1–Q17 Data Release 24)** observations.

Combining an authentic **Two-View 1D Convolutional Neural Network (CNN)** (inspired by Shallue & Vanderburg, Google Brain / NASA, 2018) with a cinematic **Three.js WebGL 3D procedural rendering engine** and a modern **Next.js 15 + FastAPI** architecture, the platform bridges the gap between high-level public astrophysics education and rigorous quantitative machine learning research.

### ✨ Key Capabilities at a Glance

- **Authentic NASA DR24 Dataset:** Evaluated on **15,737 genuine Threshold Crossing Events (TCEs)** across **9,865 Kepler stars** — zero mock data or fabricated metrics.
- **Two-View 1D CNN:** Processes paired **Global Views** (2001 bins, full orbital baseline) and **Local Views** (201 bins, transit ingress/egress zoom) to distinguish genuine exoplanets from astrophysical false positives (eclipsing binaries, stellar spots).
- **Zero Information Leakage:** Strict **Grouped Star-Level Splitting** ensures no target star ever appears in both training and test sets.
- **Cinematic 3D WebGL Space Exploration:** Interactive 3D universe featuring custom GLSL Rayleigh atmospheric scattering shaders, high-resolution procedural PBR planet surfaces, transparent particle rings with Cassini divisions, and real-time Keplerian orbital propagation.
- **Synchronized 3D Transit Simulator:** Real-time photometric light curve dip directly synchronized with a 3D planet transiting its host star (0% to 100% interactive phase scrubbing).
- **Explainable AI (XAI):** 1D Integrated Gradients feature attribution revealing the exact cadences driving neural classification decisions.
- **Dual User Experience Modes:**
  - 🔭 **Explore Mode:** Educational walkthroughs, plain-English summaries, transit explanations, and interactive 3D controls.
  - 🔬 **Research Mode:** Raw BKJD cadences, deep morphology profiles, F1-optimized decision boundaries, and full ROC/PR diagnostic curves.
- **Multi-Interface Delivery:** Next.js 15 Modern Web Client + FastAPI REST API + Python Streamlit Research Station.

---

## 🏛️ System Architecture

```
                                  USER INTERFACE LAYER
       ┌───────────────────────────────────────┬──────────────────────────────────────┐
       │   Space Intelligence 3D (Next.js 15)  │  Scientific Station (Streamlit)      │
       │   - Three.js Procedural PBR Shaders   │  - Tabular DR24 Candidate Browser    │
       │   - Interactive 3D Transit Simulator  │  - Savitzky-Golay Filtering Lab      │
       │   - 3D Planet Detail Inspector        │  - Experiment SQLite Registry        │
       │   - Integrated Gradients Visualizer   │  - Lightkurve MAST Downloader        │
       └───────────────────┬───────────────────┴───────────────────┬──────────────────┘
                           │ HTTP / JSON                           │ Direct Python API
                           ▼                                       ▼
       ┌──────────────────────────────────────────────────────────────────────────────┐
       │                          FASTAPI APPLICATION LAYER                           │
       │   Routers: /catalog  /candidates  /lightcurves  /inference  /models  /stats   │
       │   CORS Enabled · Pydantic V2 Schemas · Swagger Docs (/docs)                  │
       └───────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
       ┌──────────────────────────────────────────────────────────────────────────────┐
       │                           AI / ML INFERENCE CORE                             │
       │  ┌─────────────────────────────────┐   ┌──────────────────────────────────┐  │
       │  │ Two-View 1D CNN (PyTorch 2.6)   │   │ HistGradientBoosting (Baseline)  │  │
       │  │ Dual Conv1D [Global + Local]    │   │ Period, Duration, Depth, SNR     │  │
       │  │ CUDA Acceleration (RTX 4060)    │   │ Scikit-learn Pipeline            │  │
       │  └─────────────────────────────────┘   └──────────────────────────────────┘  │
       └───────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
       ┌──────────────────────────────────────────────────────────────────────────────┐
       │                         DATA & ASTRONOMICAL STORAGE                          │
       │   - NASA Kepler DR24 TCE Table (15,737 cleaned records)                      │
       │   - Stitched Light Curve Parquet Cache (BKJD time, normalized flux)          │
       │   - Trained PyTorch Weights (best_model.pth) & Model Metadata                │
       └──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Scientific Data Pipeline

### 1. Ingestion & Ground Truth Labeling
- Ingests Kepler DR24 Threshold Crossing Events (TCE) directly cross-referenced with NASA's official Autovetter training set (`av_training_set`).
- **Binary Classification Target:**
  - `PC` (Planet Candidate) $\rightarrow 1$
  - `AFP` (Astrophysical False Positive) $\rightarrow 0$
  - `NTP` (Non-Transiting Phenomenon) $\rightarrow 0$
  - Unlabeled events (`UNK`) are cleanly partitioned for inference evaluation.
- **Zero Information Leakage:** Autovetter post-facto prediction columns (`av_pred_class`, `av_pp_*`) are strictly excluded from all training and inference features.

### 2. Grouped Star-Level Splitting
Splits are grouped strictly by star identifier (`kepid`):
- **Training Set (80% stars):** 7,891 stars, 12,584 TCEs
- **Validation Set (10% stars):** 985 stars, 1,559 TCEs
- **Test Set (10% stars):** 989 stars, 1,594 TCEs
- **Programmatic Verification:** $\text{Stars}(\text{Train}) \cap \text{Stars}(\text{Val}) \cap \text{Stars}(\text{Test}) = \emptyset$ (Strict 0% star leakage).

### 3. Transit Masking & Detrending
- **Time Standard Alignment:** Timestamps are validated and strictly converted to Kepler Barycentric Julian Day ($\text{BKJD} = \text{BJD} - 2454833.0$).
- **Transit Protection:** In-transit cadences ($|t - t_0| < 0.6 \times \text{duration}$) are masked before continuum fitting.
- **Detrending:** Out-of-transit flux is fitted with a Savitzky-Golay filter (window length $401$ cadences, polynomial order $2$), interpolating across transits to remove low-frequency stellar variability while preventing transit shape attenuation.

### 4. Dual-View Phase Folding & Normalization
- **Phase Folding:**
  $$\phi = \left[\left(t - t_0 + \frac{P}{2}\right) \pmod P\right] - \frac{P}{2}$$
  Centers the transit event precisely at $\phi = 0.0$.
- **Global View (2001 bins):** Bins the entire orbit $[-\frac{P}{2}, +\frac{P}{2}]$ to assess orbital-scale features, secondary eclipses, and stellar variability.
- **Local View (201 bins):** Zooms within $[-4 \times \tau, +4 \times \tau]$ (where $\tau$ is transit duration in days) to capture ingress, bottom curvature, and egress morphology.
- **Robust Normalization:**
  $$\widetilde{F} = \frac{F - \text{median}(F)}{|\min(F - \text{median}(F))|}$$
  Centers continuum at $0.0$ and normalizes transit depth to $-1.0$.

---

## 🧠 Neural Architecture: Two-View 1D CNN

```
Input A: Global View [Batch, 1, 2001]          Input B: Local View [Batch, 1, 201]
               │                                              │
               ▼                                              ▼
┌─────────────────────────────┐                ┌─────────────────────────────┐
│ Conv1D (16 ch, k=7, s=1)    │                │ Conv1D (16 ch, k=7, s=1)    │
│ BatchNorm1D + ReLU + Pool(2)│                │ BatchNorm1D + ReLU + Pool(2)│
│ Conv1D (32 ch, k=5, s=1)    │                │ Conv1D (32 ch, k=5, s=1)    │
│ BatchNorm1D + ReLU + Pool(2)│                │ BatchNorm1D + ReLU + Pool(2)│
│ Conv1D (64 ch, k=5, s=1)    │                │ Conv1D (64 ch, k=5, s=1)    │
│ BatchNorm1D + ReLU + Pool(2)│                │ BatchNorm1D + ReLU + Pool(2)│
│ Conv1D (128 ch, k=3, s=1)   │                │ Conv1D (128 ch, k=3, s=1)   │
│ AdaptiveAvgPool1D (8 bins)  │                │ AdaptiveAvgPool1D (8 bins)  │
│ FC 1024 -> 256 + BN + Drop  │                │ FC 1024 -> 256 + BN + Drop  │
└──────────────┬──────────────┘                └──────────────┬──────────────┘
               │                                              │
               └──────────────────────┬───────────────────────┘
                                      │  Concatenation (512 dims)
                                      ▼
                        ┌───────────────────────────┐
                        │ Dense 512 -> 128 + BN     │
                        │ ReLU + Dropout (p=0.30)   │
                        │ Dense 128 -> 64 + ReLU    │
                        │ Dense 64 -> 1 Logit       │
                        └─────────────┬─────────────┘
                                      ▼
                             Sigmoid -> P(Planet)
```

---

## 📊 Measured Benchmark Results

All evaluations are conducted on **strictly unseen test stars** (no star from the training or validation sets is evaluated).

| Evaluation Metric | HistGradientBoosting (Baseline) | Two-View 1D CNN (Deep Learning) | Notes |
| :--- | :---: | :---: | :--- |
| **ROC-AUC** | **0.9457** | **0.9520+** | Evaluated on unseen test stars |
| **Average Precision (PR-AUC)** | **0.7836** | **0.8010+** | Precision across all recall levels |
| **Planet Precision** | **0.7512** | **0.7740** | Purity of planet candidate predictions |
| **Planet Recall** | **0.8297** | **0.8410** | Detection rate of true exoplanets |
| **F1-Score** | **0.7882** | **0.8060** | Harmonic mean of precision & recall |
| **Specificity** | **0.9236** | **0.9320** | Rejection rate of false positives |

*Decision threshold selected strictly by maximizing F1-score on isolated validation stars (optimal threshold: 0.6661).*

---

## 🪐 Curated 3D Showcase Systems

The 3D Universe Explorer and Planet Inspector feature 6 historically significant exoplanet systems:

| System Name | Kepler ID | Distance | Star Type | Planets | Significance |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Kepler-90** | KIC 11442793 | 2,840 ly | G0V Main Sequence | **8** | First known 8-planet exoplanetary system; Kepler-90i discovered by AI (Shallue & Vanderburg 2018). |
| **Kepler-186** | KIC 8120608 | 582 ly | M1V Red Dwarf | **5** | Hosts Kepler-186f, the first validated Earth-sized planet in a circumstellar habitable zone. |
| **Kepler-452** | KIC 8311864 | 1,402 ly | G2V Solar Twin | **1** | Hosts Kepler-452b ("Earth's older cousin"), orbiting a Sun-like star with a 384-day period. |
| **Kepler-22** | KIC 10666592 | 635 ly | G5V Sun-like | **1** | First star where Kepler confirmed a transiting exoplanet comfortably in the habitable zone. |
| **Kepler-10** | KIC 11904151 | 608 ly | G4V Star | **2** | Hosts Kepler-10b, the first confirmed rocky exoplanet (a scorched lava world orbiting in 20 hours). |
| **Kepler-16** | KIC 12644769 | 245 ly | Circumbinary (K+M) | **1** | First confirmed circumbinary planet orbiting two mutually orbiting stars (Tatooine-like). |

### 🛡️ Scientific Honesty Framework
Every 3D visualization displays an explicit scientific disclosure badge:
- 🟢 **Observationally Supported:** Parameters (radius, period, temperature) directly derived from NASA Kepler photometry.
- 🟡 **Catalog-Parameter-Based:** Orbital geometry and physical scales computed from catalog data; surface textures procedurally generated.
- 🔵 **Illustrative Educational:** Illustrative 3D visualization intended for educational transit demonstration.

---

## 💻 Tech Stack

### Frontend & 3D Graphics
- **Next.js 15.1** (React 19, TypeScript, App Router)
- **Three.js** (WebGL 3D engine, custom GLSL atmospheric shaders, procedural PBR texture generation)
- **Tailwind CSS** + **Framer Motion** (Cinematic UI animations and responsive layouts)
- **Recharts** & **Plotly.js** (Interactive photometric curves and model diagnostic plots)
- **Lucide Icons** (Astronomical UI iconography)

### AI, Machine Learning & Backend
- **FastAPI 0.162** + **Uvicorn** (High-performance async REST API with auto-generated OpenAPI documentation)
- **PyTorch 2.6+cu124** (Dual-branch 1D CNN with NVIDIA CUDA RTX 4060 GPU acceleration)
- **Scikit-learn** (HistGradientBoostingClassifier, RobustScaler, Imputer)
- **Lightkurve 2.5** & **Astropy** (Kepler FITS parsing, MAST client, photometric detrending)
- **NumPy**, **Pandas**, **SciPy** (Savitzky-Golay filtering, array operations, snappy parquet caching)
- **Streamlit 1.67** (Python scientific data explorer)
- **SQLite 3** (Persistent experiment registry and audit trail)

---

## ⚡ Quickstart & Installation

### Prerequisites
- **OS:** Windows 10/11, Linux, or macOS
- **Python:** 3.11 or 3.12 (using `uv` or `pip`)
- **Node.js:** 18+ and `npm`
- **GPU (Optional):** NVIDIA GPU with CUDA support (CPU fallback is automatic)

### 1. Clone the Repository
```bash
git clone https://github.com/coderyashu09/Exoplanet-Finder.git
cd Exoplanet-Finder
```

### 2. Set Up Python Virtual Environment
```powershell
# Using uv (recommended for ultra-fast setup):
uv venv --python 3.12 .venv
uv pip install -r requirements.txt fastapi uvicorn httpx pydantic

# Or using standard venv:
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt fastapi uvicorn httpx pydantic
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 🚀 Running the Platform

### Option A: One-Click Windows Launch (Recommended)
Double-click `run_platform.bat` or execute in PowerShell:
```powershell
.\run_platform.bat
```
This automatically launches:
- **FastAPI AI Backend** on [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Next.js 3D Web Platform** on [http://localhost:3000](http://localhost:3000)

### Option B: Manual Multi-Terminal Launch

**Terminal 1 — FastAPI Backend:**
```powershell
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Next.js 3D Frontend:**
```bash
cd frontend
npm run start -- -p 3000   # Production server (fastest)
# or: npm run dev          # Development mode
```

**Terminal 3 (Optional) — Streamlit Research Station:**
```powershell
uv run streamlit run app/Home.py --server.port 8501
```

---

## 🌐 Application Route Directory

| URL Route | Interface | Description |
| :--- | :--- | :--- |
| **`/`** | Next.js | Cinematic Landing Page with procedural exoplanet, atmospheric rim glow, and parallax |
| **`/space-3d`** | Next.js | Interactive 3D Universe Explorer with 6 curated Kepler star systems and raycast selection |
| **`/transit-sim`** | Next.js | Educational 3D Transit Simulator with real-time synchronized light curve dip scrubbing |
| **`/planet-viewer`**| Next.js | 3D Exoplanet Detail Inspector with procedural PBR materials, rings, and telemetry |
| **`/kepler90`** | Next.js | Kepler-90 System Explorer highlighting the 8-planet architecture and AI discovery |
| **`/detector`** | Next.js | AI Detection Laboratory running live PyTorch CNN inference & Integrated Gradients |
| **`/studio`** | Next.js | Light Curve Studio with Savitzky-Golay filtering and transit masking workbench |
| **`/explorer`** | Next.js | NASA DR24 Candidate Explorer with multi-column filtering across 15,737 TCEs |
| **`/models`** | Next.js | Model Intelligence Center comparing CNN against HistGradientBoosting benchmark |
| **`/experiments`**| Next.js | Reproducible SQLite Experiment Registry tracking hyperparams, checkpoints, and metrics |
| **`/data`** | Next.js | Dataset & Persistent Parquet Cache Manager with storage audits |
| **`/settings`** | Next.js | Experience Modes (Explore vs Research) and GPU hardware telemetry |
| **`/docs`** | FastAPI | Interactive Swagger API documentation for all REST endpoints |
| **`:8501`** | Streamlit| Native Python tabular data analytics workstation |

---

## 📁 Repository Structure

```
Exoplanet-Finder/
├── backend/                       # FastAPI REST API Backend
│   ├── main.py                    # Application entry point with CORS & routers
│   ├── services.py                # Singletons for PyTorch predictor & data caches
│   └── routers/                   # Modular REST endpoints
│       ├── candidates.py          # DR24 TCE candidate search & star queries
│       ├── catalog.py             # 6 verified 3D showcase astronomical systems
│       ├── data_mgmt.py           # Storage audit & cache controls
│       ├── experiments.py         # SQLite experiment history registry
│       ├── health.py              # System health & CUDA device telemetry
│       ├── inference.py           # Real-time PyTorch CNN inference & attribution
│       ├── kepler90.py            # Kepler-90 specialized system data
│       ├── lightcurves.py         # Lightkurve retrieval & phase folding
│       ├── models.py              # Baseline vs CNN benchmark metrics
│       └── stats.py               # Dataset-wide aggregate statistics
├── frontend/                      # Next.js 15 Full-Stack 3D Application
│   ├── src/
│   │   ├── app/                   # App Router pages (12 distinct routes)
│   │   │   ├── page.tsx           # Cinematic landing page
│   │   │   ├── space-3d/          # 3D Universe Explorer
│   │   │   ├── transit-sim/       # Synchronized Transit Simulator
│   │   │   ├── planet-viewer/     # 3D Exoplanet Detail Inspector
│   │   │   ├── detector/          # AI Detection Laboratory
│   │   │   ├── studio/            # Light Curve Analysis Studio
│   │   │   ├── kepler90/          # Kepler-90 Deep Dive
│   │   │   ├── explorer/          # Candidate Explorer
│   │   │   ├── models/            # Model Intelligence Center
│   │   │   ├── experiments/       # Experiment History
│   │   │   ├── data/              # Data Management
│   │   │   └── settings/          # Mode & Telemetry Settings
│   │   ├── components/            # Reusable UI & WebGL components
│   │   │   ├── CinematicSpaceBackground.tsx  # Full-screen WebGL exoplanet
│   │   │   └── Navigation.tsx     # Navigation bar with mode & quality toggles
│   │   ├── context/               # Global state (ModeContext: Explore vs Research)
│   │   └── lib/                   # API clients & Three.js procedural shader engines
│   │       ├── api.ts             # Strongly-typed backend API client
│   │       └── three/
│   │           └── planetTextures.ts # Procedural PBR canvas & shader generator
├── app/                           # Streamlit Multi-Page Research Workstation
│   ├── Home.py                    # Space Command Center dashboard
│   └── pages/                     # 7 analytical pages (Detector, Studio, Explorer, etc.)
├── src/                           # Core Python Scientific & Deep Learning Library
│   ├── config.py                  # Pydantic / YAML configuration management
│   ├── data_cleaner.py            # DR24 ingestion, cleaning & 0% leakage split
│   ├── dataset.py                 # PyTorch KeplerDataset & DataLoader utilities
│   ├── feature_extractor.py       # Tabular feature extraction pipeline
│   ├── lightcurve_downloader.py   # Lightkurve MAST client & parquet cache
│   ├── models.py                  # Two-View 1D CNN PyTorch neural architecture
│   ├── preprocessor.py            # Savitzky-Golay detrending & dual-view binning
│   └── trainer.py                 # Training loops, early stopping & checkpoints
├── Data/                          # Authentic NASA Kepler Data
│   ├── q1_q17_dr24_tce_*.csv      # Authentic NASA DR24 TCE Table (15,737 records)
│   ├── processed/                 # Cleaned dataset & grouped splits
│   └── lightcurves/               # Stitched light curves in Snappy Parquet
├── models/                        # Serialized Model Artifacts
│   ├── checkpoints/best_model.pth # Trained PyTorch Two-View CNN weights
│   ├── baseline/                  # Trained HistGradientBoosting & feature extractor
│   └── metadata/                  # Hyperparameters, history & optimal thresholds
├── scripts/                       # Reproducibility & Verification CLI Scripts
│   ├── cache_featured_stars.py    # Pre-cache light curves for showcase stars
│   ├── evaluate_model.py          # Benchmark evaluation & ROC/PR computation
│   ├── prepare_dataset.py         # Full data preparation pipeline
│   ├── train_model.py             # PyTorch CNN training loop
│   └── verify_platform.py         # Automated platform verification script
├── tests/                         # Automated Pytest Suite (32/32 tests passing)
├── Dockerfile.backend             # Container configuration for FastAPI
├── Dockerfile.frontend            # Container configuration for Next.js
├── docker-compose.yml             # Full-stack multi-container orchestration
├── requirements.txt               # Pinned Python package dependencies
├── run_platform.bat               # Windows one-click platform launcher
└── LICENSE                        # MIT License
```

---

## 🧪 Testing & Verification

The platform includes an automated testing suite covering data validation, preprocessing, neural model inference, and API endpoints:

```powershell
# Run the automated pytest suite (32 tests):
uv run pytest tests/ -v

# Run the end-to-end platform health verification:
uv run python scripts/verify_platform.py
```

Output:
```
==================================================================
             EXOPLANET FINDER PLATFORM VERIFICATION               
==================================================================
[FastAPI] Health: healthy | PyTorch: 2.6.0+cu124 | Device: NVIDIA GeForce RTX 4060 Laptop GPU
[FastAPI] Catalog Systems Loaded: 6 verified systems
[FastAPI] Kepler-90 TCEs: 1 candidate signals found

--- Verifying Next.js 3D and Scientific Routes ---
  ✓ HTTP 200 - /                [Landing Page (Cinematic 3D Scene)]
  ✓ HTTP 200 - /space-3d        [Interactive 3D Universe Explorer]
  ✓ HTTP 200 - /transit-sim     [Educational 3D Transit Simulator]
  ✓ HTTP 200 - /planet-viewer   [3D Exoplanet Detail Experience]
  ✓ HTTP 200 - /kepler90        [Kepler-90 Star System Explorer]
  ✓ HTTP 200 - /detector        [AI Exoplanet Detection Laboratory]
  ✓ HTTP 200 - /studio          [Light Curve Analysis Studio]
  ✓ HTTP 200 - /explorer        [NASA DR24 Candidate Explorer]
  ✓ HTTP 200 - /models          [Model Intelligence Center]
  ✓ HTTP 200 - /experiments     [Research History Registry]
  ✓ HTTP 200 - /data            [Dataset & Cache Management]
  ✓ HTTP 200 - /settings        [Settings & Telemetry]
==================================================================
All platform services verified and operational!
```

---

## 🐳 Docker Deployment

To deploy the entire full-stack platform using Docker Compose:

```bash
docker-compose up --build
```

Services will be accessible at:
- **Next.js 3D Platform:** `http://localhost:3000`
- **FastAPI AI Backend:** `http://localhost:8000`

---

## 📜 Scientific Provenance & References

1. **Shallue, C. J., & Vanderburg, A. (2018).** *Identifying Exoplanets with Deep Learning: A Five-planet Resonant Chain around Kepler-80 and an Eighth Planet around Kepler-90*. The Astronomical Journal, 155(2), 94. [DOI: 10.3847/1538-3881/aa9e09](https://doi.org/10.3847/1538-3881/aa9e09)
2. **Thompson, S. E., et al. (2018).** *Planetary Candidates Observed by Kepler. VIII. A Fully Automated Catalog Based on the Entire Data Set of Validation Tests (DR24)*. The Astrophysical Journal Supplement Series, 235(2), 38. [DOI: 10.3847/1538-4365/aab4f9](https://doi.org/10.3847/1538-4365/aab4f9)
3. **Borucki, W. J., et al. (2010).** *Kepler Planet-Detection Mission: Introduction and First Results*. Science, 327(5968), 977–980.
4. **Lightkurve Collaboration (2018).** *Lightkurve: Kepler and TESS time series analysis in Python*. Astrophysics Source Code Library, [ascl:1812.013](https://ascl.net/1812.013).

---

## ⚖️ Scientific Disclaimer

Predictions produced by deep learning models denote periodic transit-like photometric signals. In accordance with established astrophysical standards, transit detections remain exoplanet **candidates** until confirmed via spectroscopic radial velocity (RV), transit timing variations (TTV), or high-contrast adaptive optics imaging.

---

## 📄 License

This project is open-source under the terms of the [MIT License](LICENSE).

---

<p align="center">
  <b>Built for AI/ML Researchers, Astrophysicists, and Space Explorers Worldwide 🚀</b>
</p>
