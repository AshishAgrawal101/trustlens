@echo off
setlocal
cd /d "%~dp0"
rem Demo recording only: allows the app to appear inside static/phone-demo.html.
set "TRUSTLENS_DEMO_FRAME=1"
if exist "local-python.cmd" call "local-python.cmd"
if not defined TRUSTLENS_PYTHON set "TRUSTLENS_PYTHON=python"
echo When it says ready, open that address with  static/phone-demo.html  added to the end.
"%TRUSTLENS_PYTHON%" serve.py
if errorlevel 1 pause
