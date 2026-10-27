@echo off
setlocal
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call "venv\Scripts\activate.bat"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
cd backend
python -m uvicorn main:app --reload --port 3000
pause
endlocal