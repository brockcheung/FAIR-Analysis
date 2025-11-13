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
    echo This is required to run the FAIR Risk Calculator Web App.
    echo.
    echo This script can automatically install them for you now.
    echo.
    set /p install_choice="Install dependencies now? [Y/n]: "

    if /i "%install_choice%"=="n" (
        echo.
        echo Installation cancelled. To install manually, run:
        echo   install.bat
        echo.
        pause
        exit /b 1
    )

    echo.
    echo ================================================================
    echo Installing dependencies...
    echo ================================================================
    echo.

    REM Try to install dependencies
    pip install -r "%~dp0requirements.txt"

    if %errorlevel% neq 0 (
        echo.
        echo ================================================================
        echo ERROR: Installation failed
        echo ================================================================
        echo.
        echo Please try running install.bat instead, or install manually:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )

    echo.
    echo ================================================================
    echo Installation complete!
    echo ================================================================
    echo.
    echo Starting the web app now...
    echo.
    timeout /t 2 >nul
)

REM Check if other dependencies are installed
python -c "import numpy, pandas, plotly" >nul 2>&1
if %errorlevel% neq 0 (
    echo ================================================================
    echo WARNING: Some dependencies may be missing
    echo ================================================================
    echo.
    echo Installing remaining dependencies...
    echo.

    pip install -r "%~dp0requirements.txt" >nul 2>&1

    echo Dependencies updated.
    echo.
    timeout /t 2 >nul
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
