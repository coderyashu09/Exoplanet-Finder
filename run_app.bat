@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo           EXOPLANET FINDER — NASA DR24 AI DETECTION PLATFORM
echo ======================================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please run the following setup commands:
    echo   uv venv --python 3.12 .venv
    echo   .venv\Scripts\activate
    echo   uv pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Checking dataset status...
if not exist "Data\processed\tce_cleaned.csv" (
    echo [INFO] Preparing NASA DR24 TCE dataset...
    python scripts\prepare_dataset.py
)

echo [INFO] Starting Streamlit Mission Control Center...
echo Application URL: http://localhost:8501
echo.
streamlit run app\Home.py

pause

