"""Non-Qt wrapper for WinwsRunner."""
import logging
import subprocess
import sys
import threading
from pathlib import Path
from queue import Queue

import core.config as cfg
import core.strategies as strats

log = logging.getLogger(__name__)

CREATE_NO_WINDOW = 0x08000000


class FlaskRunner:
    """Manages winws.exe process without Qt dependencies."""

    def __init__(self, log_queue: Queue):
        self._process: subprocess.Popen | None = None
        self._current_strategy: str = ""
        self._log_queue = log_queue
        self._reader_thread: threading.Thread | None = None

    def start(self, strategy_name: str, hostlist_path: str) -> bool:
        """Start winws.exe with the given strategy."""
        if self.is_running():
            self.stop()

        winws_path = self._resolve_winws()
        if winws_path is None:
            self._log("❌ winws.exe не найден. Проверьте путь в настройках.")
            return False

        args = strats.get_args(strategy_name)
        if not args:
            self._log(f"❌ Стратегия «{strategy_name}» не содержит параметров.")
            return False

        args = [a.replace("{hostlist}", hostlist_path) for a in args]
        cmd = [str(winws_path)] + args

        log.info("Запуск: %s", " ".join(cmd))
        self._log(f"▶ Запуск: {strategy_name}")
        self._log("  " + " ".join(cmd))

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
            self._log("❌ Нет прав для запуска winws.exe. Запустите от администратора.")
            return False
        except FileNotFoundError:
            self._log(f"❌ Файл не найден: {winws_path}")
            return False
        except Exception as e:
            self._log(f"❌ Ошибка запуска: {e}")
            return False

        self._current_strategy = strategy_name

        # Start reader thread
        self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self._reader_thread.start()

        cfg.set("current_strategy", strategy_name)
        return True

    def stop(self) -> None:
        """Stop winws.exe."""
        if self._process is None:
            return

        try:
            self._process.terminate()
            self._process.wait(timeout=5)
        except Exception:
            try:
                self._process.kill()
            except Exception:
                pass

        self._process = None
        self._current_strategy = ""
        self._log("⏹ winws остановлен")

    def is_running(self) -> bool:
        """Check if winws is running."""
        return self._process is not None and self._process.poll() is None

    def current_strategy(self) -> str:
        """Get current strategy name."""
        return self._current_strategy

    def get_pid(self) -> int | None:
        """Get process PID."""
        if self._process and self.is_running():
            return self._process.pid
        return None

    def _read_output(self) -> None:
        """Read stdout/stderr in background thread."""
        try:
            if self._process and self._process.stdout:
                for line in self._process.stdout:
                    line = line.rstrip()
                    if line:
                        self._log(line)
        except Exception as e:
            log.debug("Чтение stdout завершено: %s", e)

    def _log(self, message: str) -> None:
        """Add log message to queue."""
        try:
            self._log_queue.put_nowait(message)
        except:
            pass

    def _resolve_winws(self) -> Path | None:
        """Find winws.exe."""
        candidates = [
            Path(cfg.get("winws_path", "bin/winws.exe")),
            Path(__file__).parent.parent / "bin" / "winws.exe",
        ]
        for p in candidates:
            if p.exists():
                return p
        return None
