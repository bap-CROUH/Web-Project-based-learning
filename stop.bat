@echo off
title Dung Server Project-Based Learning
echo Dang tat server chay tren cong 5050...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [OK] Da tat tien trinh co PID: %%a
)
echo.
echo Server tren cong 5050 da duoc tat hoan toan!
pause
