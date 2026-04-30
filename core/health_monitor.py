"""Фоновый мониторинг работоспособности стратегии."""
import logging
import socket
import ssl
from typing import Callable

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

log = logging.getLogger(__name__)

# Тестовые домены для проверки
TEST_DOMAINS = ["discord.com", "youtube.com"]
CHECK_INTERVAL_MS = 5 * 60 * 1000  # 5 минут
TEST_TIMEOUT = 5.0  # секунд


class HealthMonitor(QObject):
    """Периодически проверяет работоспособность текущей стратегии."""

    health_changed = pyqtSignal(bool)  # True = работает, False = сломалось

    def __init__(self, is_running_callback: Callable[[], bool], parent: QObject | None = None):
        super().__init__(parent)
        self._is_running_callback = is_running_callback
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_health)
        self._last_status = True  # Предполагаем что работает

    def start(self) -> None:
        """Запускает фоновый мониторинг."""
        log.info("Health monitor started (check every 5 min)")
        self._timer.start(CHECK_INTERVAL_MS)

    def stop(self) -> None:
        """Останавливает мониторинг."""
        self._timer.stop()
        log.info("Health monitor stopped")

    def _check_health(self) -> None:
        """Проверяет работоспособность стратегии."""
        # Проверяем только если winws запущен
        if not self._is_running_callback():
            return

        log.debug("Health check: testing %d domains", len(TEST_DOMAINS))
        working_count = 0

        for domain in TEST_DOMAINS:
            if self._test_domain(domain):
                working_count += 1

        # Считаем что стратегия работает если хотя бы 1 домен доступен
        is_healthy = working_count > 0

        # Эмитим сигнал только при изменении статуса
        if is_healthy != self._last_status:
            log.warning("Health status changed: %s -> %s", self._last_status, is_healthy)
            self._last_status = is_healthy
            self.health_changed.emit(is_healthy)
        else:
            log.debug("Health check OK: %d/%d domains working", working_count, len(TEST_DOMAINS))

    def _test_domain(self, domain: str) -> bool:
        """Проверяет доступность домена через TLS handshake."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TEST_TIMEOUT)
            sock.connect((domain, 443))

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return True

        except Exception as e:
            log.debug("Health check failed for %s: %s", domain, e)
            return False
        finally:
            try:
                sock.close()
            except:
                pass
