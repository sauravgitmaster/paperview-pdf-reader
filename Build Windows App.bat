@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo Could not install build requirements. Make sure Python is installed.
  pause
  exit /b 1
)
py -m PyInstaller --noconfirm --clean --windowed --onefile --name PaperView --collect-all fitz PaperView.py
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
echo.
echo Done. Your app is at dist\PaperView.exe
pause
