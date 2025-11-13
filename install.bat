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
echo ================================================================
echo              IMPORTANT: How to Run the Tools
echo ================================================================
echo.
echo OPTION 1 (Recommended - Works Immediately):
echo   Use the .bat wrapper scripts in this directory:
echo     fair-quick.bat    # Quick analysis tool
echo     fair-calc.bat     # Full calculator
echo     fair-app.bat      # Web application
echo.
echo   From this directory, just run:
echo     fair-quick.bat
echo.
echo OPTION 2 (Direct Python - Always Works):
echo     python quick_risk_analysis.py
echo     python fair_risk_calculator.py
echo     streamlit run fair_risk_app.py
echo.
echo OPTION 3 (Commands Anywhere - Requires PATH Setup):
echo   If you want to use 'fair-quick' from anywhere, add this to PATH:
echo     %%APPDATA%%\Python\Python%PYTHON_VERSION:~0,2%\Scripts
echo.
echo   To add to PATH permanently:
echo   1. Press Win+R, type: sysdm.cpl
echo   2. Go to Advanced tab ^> Environment Variables
echo   3. Under User Variables, select Path ^> Edit
echo   4. Click New and add: %%APPDATA%%\Python\Python%PYTHON_VERSION:~0,2%\Scripts
echo   5. Click OK on all windows
echo   6. Restart Command Prompt/PowerShell
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
echo ================================================================
echo              IMPORTANT: How to Run the Tools
echo ================================================================
echo.
echo OPTION 1 (Recommended - Works Immediately):
echo   Use the .bat wrapper scripts in this directory:
echo     fair-quick.bat    # Quick analysis tool
echo     fair-calc.bat     # Full calculator
echo     fair-app.bat      # Web application
echo.
echo   From this directory, just run:
echo     fair-quick.bat
echo.
echo OPTION 2 (Direct Python - Always Works):
echo     python quick_risk_analysis.py
echo     python fair_risk_calculator.py
echo     streamlit run fair_risk_app.py
echo.
echo OPTION 3 (Commands Anywhere - May Already Work):
echo   System-wide install usually adds Scripts to PATH automatically.
echo   Try running: fair-quick
echo   If it doesn't work, check if Python\Scripts is in your PATH.
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
echo QUICK START (From this directory):
echo   1. Quick analysis:   fair-quick.bat
echo   2. Web app:          fair-app.bat
echo   3. Full calculator:  fair-calc.bat
echo.
echo OR use Python directly:
echo   python quick_risk_analysis.py
echo.
echo TROUBLESHOOTING:
echo   - If commands don't work, use the .bat files
echo   - See TROUBLESHOOTING.md for PATH setup
echo   - Run test_validation.py to verify installation
echo.
pause
