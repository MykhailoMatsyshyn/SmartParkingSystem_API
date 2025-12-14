@echo off
echo ========================================
echo   Sensor API Server - Запуск
echo ========================================
echo.

REM Перевірка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не знайдено! Встановіть Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Встановлення залежностей...
pip install -r requirements_api.txt

echo.
echo [INFO] Запуск сервера...
echo.
python sensor_api_server.py

pause

