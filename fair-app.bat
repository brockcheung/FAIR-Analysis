@echo off
REM Wrapper script for fair-app command on Windows
REM This works regardless of PATH settings

streamlit run "%~dp0fair_risk_app.py" %*
