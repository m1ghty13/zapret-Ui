@echo off
echo ============================================================
echo Building Zapret UI for Windows
echo ============================================================
echo.

REM Переходим в корень проекта (на уровень выше scripts/)
cd /d "%~dp0.."

REM Проверяем что мы в правильной директории
if not exist "main.py" (
    echo ERROR: main.py not found in current directory
    echo Current directory: %CD%
    echo Please run this script from the scripts/ folder
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

REM Check if psutil is installed
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Installing psutil...
    pip install psutil
    echo.
)

echo Building executable...
echo.

REM Запускаем build.py
python scripts\build.py

echo.
pause
