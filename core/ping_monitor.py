"""Мониторинг подключения через TCP handshake к 1.1.1.1:443."""
import logging
import socket
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

log = logging.getLogger(__name__)


class PingMonitor(QObject):
    """Периодически проверяет доступность интернета через TCP к 1.1.1.1:443."""

    status_changed = pyqtSignal(bool)  # True = online, False = offline

    def __init__(self, interval_ms: int = 5000, parent=None):
        super().__init__(parent)
        self._interval = interval_ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._last_status: bool | None = None
        self._enabled = False

    def start(self) -> None:
        """Запускает мониторинг."""
        if self._enabled:
            return
        self._enabled = True
        self._last_status = None
        self._timer.start(self._interval)
        log.info("Ping monitor started (interval: %dms)", self._interval)
        # Первая проверка сразу
        self._check()

    def stop(self) -> None:
        """Останавливает мониторинг."""
        if not self._enabled:
            return
        self._enabled = False
        self._timer.stop()
        self._last_status = None
        log.info("Ping monitor stopped")

    def is_running(self) -> bool:
        return self._enabled

    def _check(self) -> None:
        """Проверяет доступность через TCP handshake."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect(("1.1.1.1", 443))
            sock.close()
            status = True
        except (socket.timeout, socket.error, OSError):
            status = False

        # Эмитим сигнал только при изменении статуса
        if status != self._last_status:
            self._last_status = status
            self.status_changed.emit(status)
            log.debug("Connection status changed: %s", "online" if status else "offline")
