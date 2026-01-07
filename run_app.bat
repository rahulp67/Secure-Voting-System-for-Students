@echo off
title Student Voting System
color 0f
cls

echo ===================================================
echo     STUDENT VOTING SYSTEM - LAUNCHER
echo ===================================================
echo.
echo 1. Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

echo 2. Starting Server...
echo.
echo [INFO] Access the app at: http://127.0.0.1:5000
echo [INFO] Admin Login: shaikmaaz77zz@gmail.com
echo [INFO] To stop: Press Ctrl+C
echo.
echo ===================================================
echo    👇 OTP CODES WILL APPEAR BELOW 👇
echo ===================================================
echo.

python app.py
pause
