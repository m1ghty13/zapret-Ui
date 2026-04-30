"""Автоматический перезапуск winws.exe при падении."""
import logging
import psutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

log = logging.getLogger(__name__)


class AutoRecovery(QObject):
    """Мониторит процесс winws.exe и перезапускает при падении."""

    recovery_triggered = pyqtSignal(str)  # Эмитит имя стратегии при перезапуске

    def __init__(self, runner, interval_ms: int = 3000, parent=None):
        super().__init__(parent)
        self._runner = runner
        self._interval = interval_ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._enabled = False
        self._last_strategy: str | None = None
        self._last_hostlist: str | None = None
        self._was_running = False

    def start(self) -> None:
        """Запускает мониторинг."""
        if self._enabled:
            return
        self._enabled = True
        self._timer.start(self._interval)
        log.info("Auto-recovery started (interval: %dms)", self._interval)

    def stop(self) -> None:
        """Останавливает мониторинг."""
        if not self._enabled:
            return
        self._enabled = False
        self._timer.stop()
        self._last_strategy = None
        self._last_hostlist = None
        self._was_running = False
        log.info("Auto-recovery stopped")

    def is_running(self) -> bool:
        return self._enabled

    def _check(self) -> None:
        """Проверяет состояние процесса и перезапускает при необходимости."""
        runner_running = self._runner.is_running()

        # Сохраняем параметры запуска
        if runner_running:
            self._was_running = True
            self._last_strategy = self._runner.current_strategy()
            self._last_hostlist = self._runner._hostlist_path
        else:
            # Если runner говорит что не запущен, но мы помним что был запущен
            if self._was_running and self._last_strategy and self._last_hostlist:
                # Проверяем действительно ли процесс упал
                if not self._is_winws_alive():
                    log.warning("winws.exe crashed, triggering auto-recovery")
                    self._recover()
                else:
                    # Процесс жив, но runner потерял контроль - сбрасываем флаг
                    self._was_running = False

    def _is_winws_alive(self) -> bool:
        """Проверяет наличие процесса winws.exe."""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == 'winws.exe':
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return False

    def _recover(self) -> None:
        """Выполняет перезапуск."""
        if not self._last_strategy or not self._last_hostlist:
            log.error("Cannot recover: missing strategy or hostlist")
            return

        log.info("Recovering: %s", self._last_strategy)
        try:
            self._runner.start(self._last_strategy, self._last_hostlist)
            self.recovery_triggered.emit(self._last_strategy)
            self._was_running = True
        except Exception as e:
            log.error("Recovery failed: %s", e)
            self._was_running = False
