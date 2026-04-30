"""Авто-тест всех стратегий с оценкой качества."""
import asyncio
import logging
import socket
import ssl
import time
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal

import core.config as cfg
import core.strategies as strats
from core.runner import WinwsRunner

log = logging.getLogger(__name__)

TEST_TIMEOUT = 10.0   # секунд на каждый домен (увеличено для медленных стратегий)
SETTLE_TIME = 5.0     # секунд ждём после запуска winws (увеличено)


class _TestWorker(QThread):
    """Рабочий поток: поочерёдно тестирует все стратегии."""

    progress = pyqtSignal(int, int, str)          # текущий, всего, имя стратегии
    strategy_done = pyqtSignal(str, int, int)     # имя, score, total_domains
    finished = pyqtSignal(str, dict)              # лучшая стратегия, все результаты

    def __init__(
        self,
        strategies: list[str],
        domains: list[str],
        hostlist_path: str,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._strategies = strategies
        self._domains = domains
        self._hostlist_path = hostlist_path
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        runner = WinwsRunner()   # локальный экземпляр без сигналов UI
        all_scores: dict[str, dict[str, Any]] = {}
        total = len(self._strategies)

        for idx, name in enumerate(self._strategies):
            if self._cancelled:
                break

            self.progress.emit(idx + 1, total, name)
            log.info("[Тест %d/%d] %s", idx + 1, total, name)

            # Запускаем winws с этой стратегией
            ok = runner.start(name, self._hostlist_path)
            if not ok:
                all_scores[name] = {"score": 0, "total": len(self._domains), "status": "error"}
                self.strategy_done.emit(name, 0, len(self._domains))
                continue

            time.sleep(SETTLE_TIME)

            score = self._test_domains()
            runner.stop()
            time.sleep(0.5)

            total_domains = len(self._domains)
            if score == total_domains:
                status = "works"
            elif score > 0:
                status = "partial"
            else:
                status = "fails"

            all_scores[name] = {"score": score, "total": total_domains, "status": status}
            self.strategy_done.emit(name, score, total_domains)

        runner.stop()

        # Обновляем конфиг с результатами тестов
        tested = cfg.get("tested_strategies", {})
        tested.update(all_scores)
        cfg.set("tested_strategies", tested)

        # Находим лучшую стратегию
        best = self._pick_best(all_scores)
        self.finished.emit(best, all_scores)

    def _test_domains(self) -> int:
        """Проверяет домены через TLS handshake. Возвращает количество успешных."""
        score = 0
        for domain in self._domains:
            if self._test_tls_handshake(domain):
                score += 1
                log.debug("  ✓ %s", domain)
            else:
                log.debug("  ✗ %s", domain)
        return score

    def _test_tls_handshake(self, domain: str) -> bool:
        """
        Проверяет TLS handshake с доменом.
        Это правильный способ проверки DPI bypass — проверяем именно ClientHello/ServerHello.
        """
        try:
            # Создаём raw TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TEST_TIMEOUT)

            # Подключаемся к 443
            sock.connect((domain, 443))

            # Оборачиваем в SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Выполняем TLS handshake с правильным SNI
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Если дошли сюда — handshake успешен
                return True

        except socket.timeout:
            log.debug("  ✗ %s: timeout", domain)
            return False
        except ConnectionRefusedError:
            log.debug("  ✗ %s: connection refused", domain)
            return False
        except ssl.SSLError as e:
            # SSL ошибка может быть из-за блокировки или проблем с сертификатом
            # Если получили ServerHello но сертификат невалиден — это ОК для нашей проверки
            if "certificate" in str(e).lower():
                log.debug("  ✓ %s: handshake ok (cert issue ignored)", domain)
                return True
            log.debug("  ✗ %s: SSL error: %s", domain, e)
            return False
        except Exception as e:
            log.debug("  ✗ %s: %s", domain, e)
            return False
        finally:
            try:
                sock.close()
            except:
                pass

    @staticmethod
    def _pick_best(scores: dict[str, dict[str, Any]]) -> str:
        """Возвращает имя стратегии с наибольшим score."""
        if not scores:
            return ""
        return max(scores, key=lambda n: scores[n].get("score", 0))


class StrategyTester(QObject):
    """Публичный API для запуска тестирования стратегий."""

    progress = pyqtSignal(int, int, str)       # current, total, name
    strategy_done = pyqtSignal(str, int, int)  # name, score, total
    finished = pyqtSignal(str, dict)           # best, all_scores

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._worker: _TestWorker | None = None

    def run_async(self, strategies: list[str], domains: list[str]) -> None:
        """Запускает тестирование в фоне."""
        if self._worker and self._worker.isRunning():
            return

        hostlist_path = cfg.get("hostlist_path", "lists/hostlist.txt")

        self._worker = _TestWorker(strategies, domains, hostlist_path, self)
        self._worker.progress.connect(self.progress)
        self._worker.strategy_done.connect(self.strategy_done)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def cancel(self) -> None:
        if self._worker:
            self._worker.cancel()

    def is_running(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    def _on_finished(self, best: str, scores: dict) -> None:
        self.finished.emit(best, scores)
