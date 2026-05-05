@echo off
title SIM-Chat Stop
echo ========================================
echo    SIM-Chat Project Stop
echo ========================================
echo.

echo Stopping services...
echo.

taskkill /F /FI "WINDOWTITLE eq SIM-Chat-Backend" >nul 2>&1
if errorlevel 1 (
    echo Backend not running
) else (
    echo Backend stopped
)

taskkill /F /FI "WINDOWTITLE eq SIM-Chat-Frontend" >nul 2>&1
if errorlevel 1 (
    echo Frontend not running
) else (
    echo Frontend stopped
)

timeout /t 2 /nobreak >nul

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo    Services stopped
echo ========================================
echo.
