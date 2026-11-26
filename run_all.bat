@echo off
echo ======================================================================
echo Starting AI Disease Prediction ^& Health Assistant (Backend + Frontend)
echo ======================================================================
cd /d "%~dp0"

echo Starting FastAPI Backend API on http://127.0.0.1:8000 ...
start "Backend API (FastAPI)" cmd /k "call .venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Streamlit Web UI on http://127.0.0.1:8501 ...
start "Frontend UI (Streamlit)" cmd /k "call .venv\Scripts\activate.bat && python -m streamlit run frontend\app.py --server.port 8501"

echo.
echo Both servers are launching in separate windows!
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo - Frontend Web App: http://127.0.0.1:8501
echo.
