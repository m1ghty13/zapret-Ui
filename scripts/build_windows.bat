@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo  Building Zapret UI for Windows
echo ============================================================
echo.

cd /d "%~dp0.."

if not exist "main.py" (
    echo ERROR: main.py not found. Run this script from the scripts\ folder.
    pause
    exit /b 1
)

echo Directory: %CD%
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo Done.
echo.

echo [2/3] Downloading zapret binaries...
python scripts\download_zapret.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to download zapret binaries.
    echo Download manually from https://github.com/bol-van/zapret/releases
    echo and place winws.exe, WinDivert.dll, WinDivert64.sys into the bin\ folder.
    pause
    exit /b 1
)
echo.

echo [3/3] Building ZapretUI.exe...
echo.
python scripts\build.py
set BUILD_EXIT=%errorlevel%

echo.
if %BUILD_EXIT% == 0 (
    echo ============================================================
    echo  SUCCESS: dist\ZapretUI.exe is ready!
    echo ============================================================
) else (
    echo ============================================================
    echo  FAILED: see errors above
    echo ============================================================
)

echo.
pause
exit /b %BUILD_EXIT%
