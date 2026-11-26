@echo off
echo =========================================================
echo Starting AI Disease Prediction ^& Health Assistant Frontend
echo =========================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m streamlit run frontend\app.py --server.port 8501
pause
