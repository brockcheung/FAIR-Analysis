@echo off
REM Wrapper script for FAIR Quick Risk Analysis on Windows
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
    echo This is required to run the FAIR Quick Risk Analysis Tool.
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
    echo Starting the tool now...
    echo.
    timeout /t 2 >nul
)

REM All checks passed - run the tool
python "%~dp0quick_risk_analysis.py" %*
