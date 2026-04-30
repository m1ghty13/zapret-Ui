"""Главное окно приложения с sidebar и QStackedWidget."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QCloseEvent

import core.config as cfg
import core.domains as domains_mod
from core.runner import WinwsRunner
from core.tester import StrategyTester
from core.health_monitor import HealthMonitor
from ui.panels.home import HomePanel
from ui.panels.strategies import StrategiesPanel
from ui.panels.domains import DomainsPanel
from ui.panels.logs import LogsPanel
from ui.panels.settings import SettingsPanel

log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent

# Пункты sidebar: (имя, метка, иконка-эмодзи)
_NAV_ITEMS = [
    ("home",       "Главная",    "🏠"),
    ("strategies", "Стратегии",  "⚡"),
    ("domains",    "Домены",     "🌐"),
    ("logs",       "Логи",       "📋"),
    ("settings",   "Настройки",  "⚙"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Zapret UI — Выключено")
        self.setMinimumSize(960, 620)
        self.resize(cfg.get("window_width", 1100), cfg.get("window_height", 680))

        # Ядро
        self.runner = WinwsRunner(self)
        self.tester = StrategyTester(self)
        self.health_monitor = HealthMonitor(self.runner.is_running, self)

        # Сигналы runner
        self.runner.status_changed.connect(self._on_status_changed)

        # Сигналы health monitor
        self.health_monitor.health_changed.connect(self._on_health_changed)

        self._sidebar_btns: dict[str, QPushButton] = {}
        self._current_page = "home"

        self._build_ui()
        self._init_domains()

    # ── Построение UI ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        root_layout.addWidget(sep)

        # Контентная область
        self._stack = QStackedWidget()
        root_layout.addWidget(self._stack, stretch=1)

        # Создаём панели
        self._panels: dict[str, QWidget] = {
            "home":       HomePanel(self.runner, self.tester, self),
            "strategies": StrategiesPanel(self.runner, self.tester, self),
            "domains":    DomainsPanel(self),
            "logs":       LogsPanel(self),
            "settings":   SettingsPanel(self),
        }
        for panel in self._panels.values():
            self._stack.addWidget(panel)

        # Логи runner → панель Логи
        self.runner.log_line.connect(self._panels["logs"].append_line)

        # Сигналы tester → панель Стратегии
        sp: StrategiesPanel = self._panels["strategies"]  # type: ignore
        self.tester.progress.connect(sp.on_test_progress)
        self.tester.strategy_done.connect(sp.on_strategy_done)
        self.tester.finished.connect(sp.on_test_finished)
        self.tester.finished.connect(self._on_test_finished)

        self._navigate("home")

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(180)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(4)

        # Логотип / заголовок
        logo = QLabel("Zapret UI")
        logo.setStyleSheet("font-size: 15px; font-weight: 700; padding: 8px 6px 16px 6px;")
        layout.addWidget(logo)

        for key, label, icon in _NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("SidebarButton")
            btn.setCheckable(False)
            btn.setProperty("active", "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._sidebar_btns[key] = btn

        layout.addStretch()

        # Версия
        ver = QLabel("v1.0.0")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #8e8e93; font-size: 11px;")
        layout.addWidget(ver)

        return sidebar

    # ── Навигация ──────────────────────────────────────────────────────────

    def _navigate(self, key: str) -> None:
        # Сброс старой активной кнопки
        if old := self._sidebar_btns.get(self._current_page):
            old.setProperty("active", "false")
            old.style().unpolish(old)
            old.style().polish(old)

        self._current_page = key
        panel = self._panels.get(key)
        if panel:
            self._stack.setCurrentWidget(panel)

        btn = self._sidebar_btns.get(key)
        if btn:
            btn.setProperty("active", "true")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── Обработка событий ─────────────────────────────────────────────────

    def _on_status_changed(self, running: bool) -> None:
        status = "Активно" if running else "Выключено"
        self.setWindowTitle(f"Zapret UI — {status}")
        # Обновляем иконку трея через родителя (tray слушает runner напрямую)
        home: HomePanel = self._panels["home"]  # type: ignore
        home.on_status_changed(running)

        # Управляем health monitor
        if running:
            self.health_monitor.start()
        else:
            self.health_monitor.stop()

    def _on_health_changed(self, is_healthy: bool) -> None:
        """Обработка изменения статуса работоспособности."""
        if not is_healthy:
            log.warning("Стратегия перестала работать!")
            # Показываем уведомление через трей (если есть)
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Zapret UI - Проблема с обходом",
                "Текущая стратегия перестала работать.\n\n"
                "Запустить автоматический тест для поиска рабочей стратегии?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.trigger_auto_test()

    def _on_test_finished(self, best: str, scores: dict) -> None:
        if best:
            log.info("Авто-тест завершён. Лучшая стратегия: %s", best)
            self.runner.start(best, cfg.get("hostlist_path", "lists/hostlist.txt"))

    def _init_domains(self) -> None:
        """Пересобираем hostlist при запуске."""
        groups = cfg.get("enabled_groups", [])
        try:
            domains_mod.build_hostlist(groups, cfg.get("hostlist_path"))
        except Exception as e:
            log.warning("Не удалось собрать hostlist: %s", e)

    # ── Публичный API для main.py ──────────────────────────────────────────

    def trigger_auto_test(self) -> None:
        self._navigate("strategies")
        sp: StrategiesPanel = self._panels["strategies"]  # type: ignore
        sp.start_auto_test()

    # ── Закрытие окна ─────────────────────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        minimize_to_tray = cfg.get("minimize_to_tray", True)
        if minimize_to_tray:
            event.ignore()
            self.hide()
        else:
            self._shutdown(event)

    def force_quit(self) -> None:
        """Вызывается из трея при выборе «Выход»."""
        self._shutdown(None)

    def _shutdown(self, event) -> None:
        cfg.set("window_width", self.width())
        cfg.set("window_height", self.height())
        self.runner.stop()
        self.tester.cancel()
        if event:
            event.accept()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
