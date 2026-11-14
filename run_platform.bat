@echo off
TITLE EXOPLANET FINDER - NASA AI Planet Detection Platform
COLOR 0B

echo ======================================================================
echo           EXOPLANET FINDER -- SPACE INTELLIGENCE PLATFORM
echo          Discover New Worlds Beyond Our Solar System (NASA DR24)
echo ======================================================================
echo.

:: 1. Check Python virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found!
    echo Please create it with 'uv venv' or 'python -m venv .venv'.
    pause
    exit /b 1
)

:: 2. Check Node.js and frontend directory
if not exist "frontend\package.json" (
    echo [ERROR] Frontend directory not found!
    pause
    exit /b 1
)

echo [INFO] Starting FastAPI AI/ML Backend on http://localhost:8000 ...
start "Exoplanet Backend (FastAPI)" cmd /k ".venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [INFO] Starting Next.js Mission Control Frontend on http://localhost:3000 ...
cd frontend
start "Exoplanet Frontend (Next.js)" cmd /k "npm run dev"
cd ..

echo.
echo ======================================================================
echo  Exoplanet Finder is launching!
echo  - Frontend: http://localhost:3000
echo  - API Docs: http://localhost:8000/docs
echo ======================================================================
echo.

