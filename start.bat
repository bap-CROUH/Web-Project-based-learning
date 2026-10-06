@echo off
title Project-Based Learning Explorer (GUI Localhost)
echo ========================================================
echo   PROJECT-BASED LEARNING EXPLORER - LOCALHOST GUI
echo ========================================================
echo.
echo [1/2] Kiem tra du lieu va khoi tao server...
python scripts/parse_to_json.py
echo.
echo [2/2] Dang khoi dong web server tren cong 5050...
start http://localhost:5050
python server.py
pause
