@echo off
echo ============================================================
echo Building Zapret UI for Windows
echo ============================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>/dev/null
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable...
echo.

REM Build the executable
pyinstaller --noconfirm ^
    --name "ZapretUI" ^
    --windowed ^
    --onedir ^
    --icon=assets/icon.ico ^
    --add-data "dist;dist" ^
    --add-data "assets;assets" ^
    --add-data "core;core" ^
    --add-data "api;api" ^
    --add-data "config.json;." ^
    --hidden-import "flask" ^
    --hidden-import "flask_cors" ^
    --hidden-import "webview" ^
    --hidden-import "pystray" ^
    --hidden-import "PIL" ^
    --hidden-import "httpx" ^
    --hidden-import "core.config" ^
    --hidden-import "core.runner" ^
    --hidden-import "core.tester" ^
    --hidden-import "core.domains" ^
    --hidden-import "api.server" ^
    --hidden-import "api.bridge" ^
    --hidden-import "api.runner_wrapper" ^
    --hidden-import "api.tester_wrapper" ^
    --hidden-import "api.tray" ^
    main.py

echo.
echo ============================================================
echo Build complete!
echo ============================================================
echo.
echo Executable location: dist\ZapretUI\ZapretUI.exe
echo.
echo You can now distribute the entire dist\ZapretUI folder
echo.
pause
