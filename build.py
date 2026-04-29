"""Сборка Zapret UI в один .exe через PyInstaller."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def main() -> None:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=ZapretUI",
        "--icon=assets/icon.ico",
        "--add-data", "bin;bin",
        "--add-data", "lists;lists",
        "--add-data", "strategies;strategies",
        "--add-data", "assets;assets",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=httpx",
        "main.py",
    ]
    print("Запуск сборки:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode == 0:
        print("\n✓ Сборка успешна. Файл: dist/ZapretUI.exe")
    else:
        print("\n✗ Сборка завершилась с ошибкой")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
