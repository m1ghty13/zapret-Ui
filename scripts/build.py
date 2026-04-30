"""Сборка Zapret UI в один .exe через PyInstaller."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def main() -> None:
    # Проверяем существование main.py
    main_py = ROOT / "main.py"
    if not main_py.exists():
        print(f"✗ Ошибка: {main_py} не найден")
        print(f"  Текущая директория: {Path.cwd()}")
        print(f"  ROOT директория: {ROOT}")
        sys.exit(1)

    manifest_path = ROOT / "scripts" / "ZapretUI.manifest"
    icon_path = ROOT / "assets" / "icon-default.ico"

    # Проверяем иконку
    if not icon_path.exists():
        print(f"⚠ Предупреждение: иконка не найдена: {icon_path}")
        icon_arg = []
    else:
        icon_arg = ["--icon", str(icon_path)]

    # Собираем список папок для добавления
    data_folders = []
    for folder in ["bin", "lists", "strategies", "assets"]:
        folder_path = ROOT / folder
        if folder_path.exists():
            data_folders.extend(["--add-data", f"{folder};{folder}"])
        else:
            print(f"⚠ Предупреждение: папка {folder} не найдена, пропускаем")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=ZapretUI",
        *icon_arg,
        "--manifest", str(manifest_path),
        *data_folders,
        "--hidden-import=PyQt6.sip",
        "--hidden-import=psutil",
        str(main_py),
    ]

    print("=" * 60)
    print("Сборка Zapret UI")
    print("=" * 60)
    print(f"ROOT: {ROOT}")
    print(f"main.py: {main_py}")
    print(f"Запуск PyInstaller...")
    print()

    result = subprocess.run(cmd, cwd=str(ROOT))

    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✓ Сборка успешна!")
        print(f"  Файл: {ROOT / 'dist' / 'ZapretUI.exe'}")
    else:
        print("✗ Сборка завершилась с ошибкой")
    print("=" * 60)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
