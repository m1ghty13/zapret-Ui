@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo  Building Zapret UI for Windows
echo ============================================================
echo.

REM Переходим в корень проекта (на уровень выше scripts/)
cd /d "%~dp0.."

if not exist "main.py" (
    echo ERROR: main.py not found. Run this script from the scripts\ folder.
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

REM Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости
echo [1/3] Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
pip install psutil --quiet
echo Done.
echo.

REM Скачиваем zapret бинарники если bin\ пуст
echo [2/3] Checking zapret binaries...
dir /b "bin\winws.exe" >nul 2>&1
if errorlevel 1 (
    echo   winws.exe not found, downloading from GitHub...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$ErrorActionPreference = 'Stop';" ^
        "try {" ^
        "  $rel = Invoke-RestMethod 'https://api.github.com/repos/bol-van/zapret/releases/latest';" ^
        "  $zip = ($rel.assets | Where-Object { $_.name -like '*.zip' } | Select-Object -First 1).browser_download_url;" ^
        "  Write-Host \"  Downloading $($rel.tag_name)...\";" ^
        "  $tmp = [System.IO.Path]::GetTempFileName() + '.zip';" ^
        "  Invoke-WebRequest -Uri $zip -OutFile $tmp -UseBasicParsing;" ^
        "  Add-Type -AssemblyName System.IO.Compression.FileSystem;" ^
        "  $arc = [System.IO.Compression.ZipFile]::OpenRead($tmp);" ^
        "  $files = @('winws.exe','WinDivert.dll','WinDivert64.sys');" ^
        "  foreach ($entry in $arc.Entries) {" ^
        "    if ($entry.FullName -match 'windows-x86_64' -and $files -contains $entry.Name) {" ^
        "      $dest = Join-Path 'bin' $entry.Name;" ^
        "      [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $dest, $true);" ^
        "      Write-Host \"  Extracted: $($entry.Name)\";" ^
        "    }" ^
        "  }" ^
        "  $arc.Dispose();" ^
        "  Remove-Item $tmp;" ^
        "  Write-Host '  Done.';" ^
        "} catch { Write-Host \"  ERROR: $_\"; exit 1 }"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to download zapret binaries.
        echo Please download manually from:
        echo   https://github.com/bol-van/zapret/releases
        echo and place winws.exe, WinDivert.dll, WinDivert64.sys into the bin\ folder.
        pause
        exit /b 1
    )
) else (
    echo   Found existing binaries, skipping download.
)
echo.

REM Собираем exe
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
