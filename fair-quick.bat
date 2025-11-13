@echo off
REM Wrapper script for fair-quick command on Windows
REM This works regardless of PATH settings

python "%~dp0quick_risk_analysis.py" %*
