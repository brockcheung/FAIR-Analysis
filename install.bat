@echo off
REM ###############################################################################
REM FAIR Risk Calculator - Windows Installation Script
REM ###############################################################################

echo ================================================================
echo       FAIR Risk Calculator - Installation Script
echo ================================================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check pip
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found. Please install pip.
    pause
    exit /b 1
)
echo [OK] pip found

echo.
echo Select installation type:
echo   1) User installation (recommended)
echo   2) System-wide installation
echo   3) Development installation (editable mode)
echo   4) Docker installation
echo.
set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" goto user_install
if "%choice%"=="2" goto system_install
if "%choice%"=="3" goto dev_install
if "%choice%"=="4" goto docker_install

echo [ERROR] Invalid choice
pause
exit /b 1

:user_install
echo.
echo Installing for current user...
pip install --user -r requirements.txt
if %errorlevel% neq 0 goto install_error

pip install --user -e .
if %errorlevel% neq 0 goto install_error

echo.
echo [OK] Installation complete!
echo.
echo You can now run:
echo   fair-quick    # Quick analysis tool
echo   fair-calc     # Full calculator
echo   fair-app      # Web application
echo.
goto end

:system_install
echo.
echo Installing system-wide...
pip install -r requirements.txt
if %errorlevel% neq 0 goto install_error

pip install .
if %errorlevel% neq 0 goto install_error

echo.
echo [OK] Installation complete!
echo.
echo You can now run:
echo   fair-quick    # Quick analysis tool
echo   fair-calc     # Full calculator
echo   fair-app      # Web application
echo.
goto end

:dev_install
echo.
echo Installing in development mode...
pip install --user -r requirements.txt
if %errorlevel% neq 0 goto install_error

pip install --user -e ".[dev]"
if %errorlevel% neq 0 goto install_error

echo.
echo [OK] Development installation complete!
echo.
echo You can now run:
echo   python fair_risk_calculator.py
echo   python quick_risk_analysis.py
echo   streamlit run fair_risk_app.py
echo.
goto end

:docker_install
echo.
echo Setting up Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Docker Compose not found.
        pause
        exit /b 1
    )
)

echo Building Docker image...
docker-compose build
if %errorlevel% neq 0 goto install_error

echo.
echo [OK] Docker installation complete!
echo.
echo To run the application:
echo   docker-compose up
echo.
echo Then open your browser to: http://localhost:8501
echo.
goto end

:install_error
echo.
echo [ERROR] Installation failed!
echo Please check the error messages above.
pause
exit /b 1

:end
echo.
echo ================================================================
echo              Installation Complete!
echo ================================================================
echo.
echo Quick Start:
echo   1. Try quick analysis:  fair-quick
echo   2. Run web app:         fair-app
echo   3. Full calculator:     fair-calc
echo.
echo For help, run any command with --help
echo.
pause
