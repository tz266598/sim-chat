@echo off
title SIM-Chat Start
echo ========================================
echo    SIM-Chat Project Start
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo [0/4] Cleaning old processes...
taskkill /F /FI "WINDOWTITLE eq SIM-Chat-Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq SIM-Chat-Frontend" >nul 2>&1
timeout /t 2 /nobreak >nul
echo Done

echo.
echo [1/4] Starting Backend (FastAPI)...
start "SIM-Chat-Backend" cmd /c "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 && pause"

echo Waiting for backend...
set RETRY=0
:WAIT_BACKEND
timeout /t 2 /nobreak >nul
set /a RETRY+=1
if %RETRY% GTR 10 (
    echo Warning: Backend timeout, continuing anyway...
    goto START_FRONTEND
)
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 goto WAIT_BACKEND
echo Backend ready

:START_FRONTEND
echo.
echo [2/4] Starting Frontend (Streamlit)...
start "SIM-Chat-Frontend" cmd /c "cd /d %~dp0frontend && streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false && pause"

echo Waiting for frontend...
set RETRY=0
:WAIT_FRONTEND
timeout /t 2 /nobreak >nul
set /a RETRY+=1
if %RETRY% GTR 15 (
    echo Warning: Frontend timeout
    goto FINISH
)
curl -s -o nul http://localhost:8501 2>&1
if errorlevel 1 goto WAIT_FRONTEND
echo Frontend ready

:FINISH
echo.
echo ========================================
echo    Start Complete!
echo ========================================
echo.
echo URLs:
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8001
echo   API Docs: http://localhost:8001/docs
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8501
echo.
echo NOTE: Keep the two black windows open!
echo To stop: run stop.bat or close those windows
echo.
pause
