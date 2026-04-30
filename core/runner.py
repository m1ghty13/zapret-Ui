"""Запуск и остановка winws.exe через QThread."""
import logging
import subprocess
import sys
import time
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtSignal

import core.config as cfg
import core.strategies as strats
import core.domains as domains_mod

log = logging.getLogger(__name__)

# Флаг для Windows: скрыть консольное окно процесса
CREATE_NO_WINDOW = 0x08000000


class _StdoutReader(QThread):
    """Читает stdout/stderr winws.exe и эмитит строки в основной поток."""

    line_received = pyqtSignal(str)

    def __init__(self, process: subprocess.Popen, parent: QObject | None = None):
        super().__init__(parent)
        self._proc = process

    def run(self) -> None:
        try:
            for raw in self._proc.stdout:  # type: ignore[union-attr]
                line = raw.rstrip()
                if line:
                    self.line_received.emit(line)
        except Exception as e:
            log.debug("Чтение stdout завершено: %s", e)


class WinwsRunner(QObject):
    """Менеджер процесса winws.exe."""

    log_line = pyqtSignal(str)           # новая строка лога
    status_changed = pyqtSignal(bool)    # True = запущен, False = остановлен

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._process: subprocess.Popen | None = None
        self._reader: _StdoutReader | None = None
        self._current_strategy: str = ""
        self._hostlist_path: str = ""

    # ── Публичный API ──────────────────────────────────────────────────────

    def start(self, strategy_name: str, hostlist_path: str) -> bool:
        """Запускает winws.exe с заданной стратегией."""
        if self.is_running():
            self.stop()

        winws_path = self._resolve_winws()
        if winws_path is None:
            self.log_line.emit("❌ winws.exe не найден. Проверьте путь в настройках.")
            return False

        args = strats.get_args(strategy_name)
        if not args:
            self.log_line.emit(f"❌ Стратегия «{strategy_name}» не содержит параметров.")
            return False

        self._current_strategy = strategy_name
        self._hostlist_path = hostlist_path

        # Подставляем путь к hostlist если аргумент использует плейсхолдер
        args = [a.replace("{hostlist}", hostlist_path) for a in args]

        cmd = [str(winws_path)] + args
        log.info("Запуск: %s", " ".join(cmd))
        self.log_line.emit(f"▶ Запуск: {strategy_name}")
        self.log_line.emit("  " + " ".join(cmd))

        try:
            flags = CREATE_NO_WINDOW if sys.platform == "win32" else 0
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=flags,
            )
        except PermissionError:
            self.log_line.emit("❌ Нет прав для запуска winws.exe. Запустите от администратора.")
            return False
        except FileNotFoundError:
            self.log_line.emit(f"❌ Файл не найден: {winws_path}")
            return False
        except Exception as e:
            self.log_line.emit(f"❌ Ошибка запуска: {e}")
            return False

        self._reader = _StdoutReader(self._process, self)
        self._reader.line_received.connect(self.log_line)
        self._reader.start()

        cfg.set("current_strategy", strategy_name)
        cfg.add_recent_strategy(strategy_name)  # Добавляем в recent
        self.status_changed.emit(True)
        return True

    def stop(self) -> None:
        """Останавливает winws.exe с корректным освобождением WinDivert."""
        if self._process is None:
            return

        log.info("Останавливаем winws.exe (PID: %d)", self._process.pid)

        try:
            if sys.platform == "win32":
                # На Windows используем CTRL_BREAK_EVENT для graceful shutdown
                import signal
                try:
                    self._process.send_signal(signal.CTRL_BREAK_EVENT)
                    log.debug("Отправлен CTRL_BREAK_EVENT")
                except Exception as e:
                    log.debug("CTRL_BREAK_EVENT не сработал: %s", e)
                    self._process.terminate()
            else:
                self._process.terminate()

            # Ждём до 3 секунд
            for _ in range(30):
                if self._process.poll() is not None:
                    log.info("winws.exe завершён корректно")
                    break
                time.sleep(0.1)
            else:
                # Если не завершился — kill
                log.warning("winws.exe не ответил на terminate, принудительная остановка")
                self._process.kill()
                self._process.wait(timeout=2)

        except Exception as e:
            log.error("Ошибка при остановке winws.exe: %s", e)
            try:
                self._process.kill()
            except Exception:
                pass

        self._process = None
        self._current_strategy = ""

        if self._reader and self._reader.isRunning():
            self._reader.wait(2000)

        self.log_line.emit("⏹ winws остановлен")
        self.status_changed.emit(False)

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def current_strategy(self) -> str:
        return self._current_strategy

    # ── Внутренние методы ─────────────────────────────────────────────────

    def _resolve_winws(self) -> Path | None:
        """Ищет winws.exe по пути из конфига и рядом с .exe."""
        candidates = [
            Path(cfg.get("winws_path", "bin/winws.exe")),
            Path(__file__).parent.parent / "bin" / "winws.exe",
        ]
        for p in candidates:
            if p.exists():
                return p
        return None
