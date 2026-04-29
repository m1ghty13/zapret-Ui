"""Регистрация/удаление автозапуска через реестр Windows."""
import logging
import sys
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "ZapretUI"
REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str:
    if getattr(sys, "frozen", False):
        return sys.executable
    # В режиме разработки — путь к main.py через pythonw
    python = Path(sys.executable)
    main = Path(__file__).parent.parent / "main.py"
    return f'"{python}" "{main}"'


def enable() -> bool:
    """Добавляет ZapretUI в автозапуск. Возвращает True при успехе."""
    try:
        import winreg
        exe = _get_exe_path()
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe)
        log.info("Автозапуск включён: %s", exe)
        return True
    except Exception as e:
        log.error("Не удалось включить автозапуск: %s", e)
        return False


def disable() -> bool:
    """Удаляет ZapretUI из автозапуска. Возвращает True при успехе."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
        log.info("Автозапуск отключён")
        return True
    except FileNotFoundError:
        return True  # Уже не было
    except Exception as e:
        log.error("Не удалось отключить автозапуск: %s", e)
        return False


def is_enabled() -> bool:
    """Проверяет, зарегистрирован ли автозапуск."""
    try:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ
        ) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except Exception:
        return False
