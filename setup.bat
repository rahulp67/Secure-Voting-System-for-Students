@echo off
title Voting System Setup
color 0f
cls

echo ===================================================
echo     STUDENT VOTING SYSTEM - FIRST TIME SETUP
echo ===================================================
echo.

echo [1/3] Installing Status...
pip install -r requirements.txt

echo.
echo [2/3] Initializing Database...
python init_db.py

echo.
echo [3/3] Setup Complete!
echo.
echo You can now run 'run_app.bat' to start the system.
echo.
pause
