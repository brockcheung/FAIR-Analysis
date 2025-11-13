@echo off
REM Wrapper script for fair-calc command on Windows
REM This works regardless of PATH settings

python "%~dp0fair_risk_calculator.py" %*
