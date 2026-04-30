"""Zapret UI — точка входа (нативный PyQt6)."""
import sys
import os
import logging
import logging.handlers
import subprocess
from pathlib import Path

# Добавляем корень проекта в sys.path (нужно для PyInstaller)
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def check_and_install_dependencies() -> bool:
    """Проверяем и устанавливаем недостающие зависимости."""
    required_packages = {
        'PyQt6': 'PyQt6>=6.6.0',
        'pystray': 'pystray>=0.19.0',
        'PIL': 'Pillow>=10.0.0',
    }

    missing_packages = []

    # Проверяем какие пакеты отсутствуют
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if not missing_packages:
        return True

    print("=" * 60)
    print("Обнаружены недостающие зависимости!")
    print("=" * 60)
    print("\nУстанавливаю:", ", ".join(missing_packages))
    print("\nПожалуйста, подождите...\n")

    try:
        # Устанавливаем недостающие пакеты
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + missing_packages
        )
        print("\n✅ Все зависимости установлены успешно!")
        print("=" * 60)
        print("\nПерезапускаю приложение...\n")

        # Перезапускаем приложение
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при установке зависимостей: {e}")
        print("\nПопробуйте установить вручную:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return False


# Проверяем зависимости перед импортом
if not check_and_install_dependencies():
    input("\nНажмите Enter для выхода...")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
import core.config as cfg
from ui.main_window import MainWindow
from ui.tray import create_tray_icon


def setup_logging() -> None:
    appdata = Path(os.environ.get("APPDATA", Path.home())) / "ZapretUI"
    appdata.mkdir(parents=True, exist_ok=True)
    log_file = appdata / "app.log"

    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8"
    )
    console = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[handler, console],
    )


def check_admin() -> bool:
    """Проверяем права администратора (нужны для winws.exe)."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        # Не Windows — разрешаем запуск для разработки
        return True


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("Zapret UI запускается (PyQt6)")

    # Загружаем конфиг
    cfg.load()

    # Предупреждение о правах администратора
    if not check_admin():
        log.warning("Running without admin privileges")

    # Создаём Qt приложение
    app = QApplication(sys.argv)
    app.setApplicationName("Zapret UI")
    app.setQuitOnLastWindowClosed(False)  # Не выходим при закрытии окна (трей)

    # Single-instance lock
    socket = QLocalSocket()
    socket.connectToServer("ZapretUI_SingleInstance")
    if socket.waitForConnected(500):
        log.warning("Another instance is already running")
        QMessageBox.warning(
            None,
            "Zapret UI",
            "Приложение уже запущено.\nПроверьте системный трей."
        )
        sys.exit(0)

    server = QLocalServer()
    server.listen("ZapretUI_SingleInstance")
    log.info("Single-instance lock acquired")

    # Применяем тему
    from ui.theme import apply_theme
    apply_theme(app)

    # Главное окно
    window = MainWindow()

    # Системный трей
    tray_icon = create_tray_icon(window, app)
    if tray_icon:
        tray_icon.show()
        log.info("System tray icon created")

    # Показываем окно
    window.show()
    log.info("UI инициализирован")

    # Запускаем event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
