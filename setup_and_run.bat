@echo off
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Starting Streamlit application...
python -m streamlit run app.py

pause

