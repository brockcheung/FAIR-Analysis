@echo off
REM Wrapper script for FAIR Risk Calculator on Windows
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

REM Check if core dependencies are installed
python -c "import numpy, pandas, matplotlib" >nul 2>&1
if %errorlevel% neq 0 (
    echo ================================================================
    echo DEPENDENCIES NOT INSTALLED
    echo ================================================================
    echo.
    echo Required dependencies are not installed yet.
    echo.
    echo QUICK FIX - Run ONE of these commands:
    echo.
    echo Option 1 - Full Installation (Recommended):
    echo   install.bat
    echo.
    echo Option 2 - Install Dependencies Only:
    echo   pip install -r requirements.txt
    echo.
    echo After installation, run this script again.
    echo ================================================================
    echo.
    pause
    exit /b 1
)

REM All checks passed - run the tool
python "%~dp0fair_risk_calculator.py" %*
