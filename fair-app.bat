@echo off
REM Wrapper script for FAIR Risk Web App on Windows
REM Checks for dependencies and provides helpful guidance

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ================================================================
    echo ERROR: Python not found
    echo ================================================================
    echo.
    echo Python is required to run the FAIR Risk Calculator.
    echo Please install Python 3.7 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ================================================================
    echo DEPENDENCIES NOT INSTALLED
    echo ================================================================
    echo.
    echo Streamlit and other dependencies are not installed yet.
    echo.
    echo QUICK FIX - Run ONE of these commands:
    echo.
    echo Option 1 - Full Installation (Recommended):
    echo   install.bat
    echo.
    echo Option 2 - Install Dependencies Only:
    echo   pip install -r requirements.txt
    echo.
    echo Option 3 - Install Just Streamlit:
    echo   pip install streamlit
    echo.
    echo After installation, run this script again.
    echo ================================================================
    echo.
    pause
    exit /b 1
)

REM Check if other dependencies are installed
python -c "import numpy, pandas, plotly" >nul 2>&1
if %errorlevel% neq 0 (
    echo ================================================================
    echo WARNING: Some dependencies may be missing
    echo ================================================================
    echo.
    echo For best results, run the full installation:
    echo   install.bat
    echo.
    echo Or install all dependencies:
    echo   pip install -r requirements.txt
    echo.
    echo Attempting to start anyway...
    echo ================================================================
    echo.
    timeout /t 3 >nul
)

REM All checks passed - run the web app
echo ================================================================
echo Starting FAIR Risk Calculator Web App...
echo ================================================================
echo.
echo The web app will open in your browser automatically.
echo If it doesn't open, navigate to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server when done.
echo ================================================================
echo.

REM Use python -m streamlit instead of streamlit command
REM This is more reliable and works even if Scripts folder isn't in PATH
python -m streamlit run "%~dp0fair_risk_app.py" %*
