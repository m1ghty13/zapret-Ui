@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo  Building Zapret UI for Windows
echo ============================================================
echo.

REM Переходим в корень проекта (на уровень выше scripts/)
cd /d "%~dp0.."

REM Проверяем что мы в правильной директории
if not exist "main.py" (
    echo ERROR: main.py not found in current directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости из requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Устанавливаем psutil отдельно
echo Installing psutil...
pip install psutil --quiet

echo.
echo Building executable...
echo.

REM Запускаем build.py
python scripts\build.py
set BUILD_EXIT=%errorlevel%

echo.
if %BUILD_EXIT% == 0 (
    echo ============================================================
    echo  SUCCESS: ZapretUI.exe created in dist\ folder
    echo ============================================================
    echo.
    echo IMPORTANT: Copy zapret binaries into the bin\ folder next to
    echo            ZapretUI.exe before running:
    echo   - winws.exe
    echo   - WinDivert.dll
    echo   - WinDivert64.sys
    echo.
) else (
    echo ============================================================
    echo  FAILED: Build finished with errors
    echo ============================================================
)

pause
exit /b %BUILD_EXIT%
