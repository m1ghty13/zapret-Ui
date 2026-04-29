"""Zapret UI — точка входа."""
import sys
import os
import logging
import logging.handlers
import subprocess
import threading
from pathlib import Path

# Добавляем корень проекта в sys.path (нужно для PyInstaller)
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def check_and_install_dependencies() -> bool:
    """Проверяем и устанавливаем недостающие зависимости."""
    required_packages = {
        'flask': 'flask>=3.0.0',
        'flask_cors': 'flask-cors>=4.0.0',
        'webview': 'pywebview>=5.0.0',
        'pystray': 'pystray>=0.19.0',
        'PIL': 'Pillow>=10.0.0',
        'httpx': 'httpx>=0.27.0',
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

import core.config as cfg
from api.server import start_server
from api.bridge import JSBridge


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


def build_react_app() -> bool:
    """Build React app if dist/ doesn't exist."""
    dist_dir = ROOT / "dist"
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        return True

    log = logging.getLogger(__name__)
    log.info("Building React app...")

    try:
        # Check if node_modules exists
        if not (ROOT / "node_modules").exists():
            log.info("Installing npm dependencies...")
            subprocess.run(["npm", "install"], cwd=ROOT, check=True)

        # Build the app
        subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True)
        log.info("React app built successfully")
        return True

    except subprocess.CalledProcessError as e:
        log.error("Failed to build React app: %s", e)
        return False
    except FileNotFoundError:
        log.error("npm not found. Please install Node.js")
        return False


def main() -> None:
    setup_logging()
    log = logging.getLogger(__name__)
    log.info("Zapret UI запускается")

    # Загружаем конфиг
    cfg.load()

    # Предупреждение о правах администратора
    if not check_admin():
        log.warning("Running without admin privileges")

    # Build React app if needed
    if not build_react_app():
        log.error("Cannot start: React app build failed")
        sys.exit(1)

    # Start Flask server
    port = start_server()
    url = f"http://127.0.0.1:{port}"

    log.info("Flask server started on port %d", port)

    # Initialize runner for tray
    from api.runner_wrapper import FlaskRunner
    from queue import Queue
    log_queue = Queue()
    runner = FlaskRunner(log_queue)

    # Create system tray icon
    from api.tray import TrayIcon
    tray = TrayIcon(runner, port)
    tray_icon = tray.create_icon()

    # Try to use pywebview (native window)
    use_webview = True

    if use_webview:
        try:
            import webview

            log.info("Starting pywebview window at %s", url)

            # Create JS bridge
            bridge = JSBridge()

            # Create webview window
            window = webview.create_window(
                title="Zapret UI",
                url=url,
                js_api=bridge,
                width=1100,
                height=680,
                min_size=(960, 620),
                resizable=True,
                frameless=False,
                on_top=False,
            )

            # Store window reference in tray
            if tray_icon:
                tray.window = window

            # Start tray icon in background thread
            if tray_icon:
                tray_thread = threading.Thread(target=tray.run, daemon=True)
                tray_thread.start()
                log.info("System tray icon started")

            # Handle window close event
            def on_closing():
                minimize_to_tray = cfg.get("minimize_to_tray", True)
                if minimize_to_tray and tray_icon:
                    log.info("Minimizing to tray")
                    window.hide()
                    if tray_icon:
                        tray_icon.notify("Zapret UI", "Свернуто в трей")
                    return False
                else:
                    log.info("Closing application")
                    if runner.is_running():
                        runner.stop()
                    if tray_icon:
                        tray.stop()
                    return True

            window.events.closing += on_closing

            log.info("UI инициализирован")
            webview.start(debug=False)

        except Exception as e:
            log.error("PyWebView error: %s", e)
            log.info("Falling back to browser mode")
            use_webview = False

    if not use_webview:
        # Browser mode (macOS or pywebview failed)
        log.info("Running in browser mode")
        log.info("=" * 60)
        log.info("Zapret UI запущен!")
        log.info("=" * 60)
        log.info("")
        log.info("Откройте в браузере: %s", url)
        log.info("")

        if tray_icon:
            log.info("Иконка в трее доступна для управления")
            log.info("")

        log.info("Нажмите Ctrl+C для остановки")
        log.info("=" * 60)

        # Open browser automatically on macOS
        if sys.platform == "darwin":
            try:
                subprocess.run(["open", url])
            except:
                pass

        # Start tray icon in background
        if tray_icon:
            tray_thread = threading.Thread(target=tray.run, daemon=True)
            tray_thread.start()
            log.info("System tray icon started")

        # Keep running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("\nStopping...")
            if runner.is_running():
                runner.stop()
            if tray_icon:
                tray.stop()

    # Cleanup on exit
    if runner.is_running():
        runner.stop()
    if tray_icon:
        tray.stop()


if __name__ == "__main__":
    main()
