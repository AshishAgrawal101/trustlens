@echo off
setlocal
cd /d "%~dp0"
if exist "local-python.cmd" call "local-python.cmd"
if not defined TRUSTLENS_PYTHON set "TRUSTLENS_PYTHON=python"
"%TRUSTLENS_PYTHON%" serve.py
if errorlevel 1 pause
