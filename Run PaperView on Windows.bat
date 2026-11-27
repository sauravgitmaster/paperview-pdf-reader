@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Could not install PaperView requirements. Make sure Python is installed.
  pause
  exit /b 1
)
py PaperView.py
