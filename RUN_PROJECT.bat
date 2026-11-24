@echo off
title FloodShield-AI - Launching System...
color 0b

echo ===============================================================================
echo                FLOODSHIELD-AI : DECISION SUPPORT SYSTEM
echo               Yadgir District Real-Time Hydrological Monitoring
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Verify Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Python detected:
python --version
echo.

:: 2. Determine best Python executable
set PY_CMD=python

:: Check if the venv belongs to a different computer (e.g. Prajwal's laptop on Lab PC)
if exist "%~dp0backend\venv\pyvenv.cfg" (
    findstr /i "prajw" "%~dp0backend\venv\pyvenv.cfg" >nul 2>&1
    if %errorlevel% equ 0 (
        if not exist "C:\Users\prajw" (
            echo [2/3] Laptop virtual environment detected on Lab PC.
            echo Removing broken laptop venv so Lab Python 3.10 can run cleanly...
            rmdir /s /q "%~dp0backend\venv" >nul 2>&1
        )
    )
)

if exist "%~dp0backend\venv\Scripts\python.exe" (
    set PY_CMD="%~dp0backend\venv\Scripts\python.exe"
    echo [2/3] Using configured Python virtual environment.
) else (
    echo [2/3] Using system Python (3.10).
)

:: Test required packages
%PY_CMD% -c "import fastapi, uvicorn, sqlalchemy" >nul 2>&1
if %errorlevel% neq 0 (
    echo [2/3] Installing required packages for Python 3.10...
    %PY_CMD% -m pip install fastapi uvicorn sqlalchemy scikit-learn pandas numpy requests python-dotenv apscheduler joblib
) else (
    echo [2/3] All Python dependencies verified.
)
echo.

:: 3. Launch the Server and Open Browser
echo [3/3] Starting FloodShield-AI server on http://127.0.0.1:8000 ...
echo.
echo ===============================================================================
echo   PROJECT IS INITIALIZING AND RUNNING!
echo   Dashboard UI: http://127.0.0.1:8000
echo   API Docs:     http://127.0.0.1:8000/docs
echo   Press CTRL + C in this window to stop the server.
echo ===============================================================================
echo.

:: Automatically launch browser after 5 seconds to ensure server is ready
start "" cmd /c "timeout /t 5 /nobreak >nul & start http://127.0.0.1:8000"

:: Run the FastAPI application
cd /d "%~dp0backend"
%PY_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
