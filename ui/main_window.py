"""Главное окно приложения."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QCloseEvent

import core.config as cfg
import core.domains as domains_mod
from core.runner import WinwsRunner
from core.tester import StrategyTester
from core.health_monitor import HealthMonitor
from core.auto_recovery import AutoRecovery
from ui.panels.home import HomePanel
from ui.panels.strategies import StrategiesPanel
from ui.panels.domains import DomainsPanel
from ui.panels.logs import LogsPanel
from ui.panels.settings import SettingsPanel

log = logging.getLogger(__name__)
ROOT = Path(__file__).parent.parent

_NAV = [
    ("home",       "  ⌂   Главная"),
    ("strategies", "  ⚡   Стратегии"),
    ("domains",    "  ◎   Домены"),
    ("logs",       "  ≡   Логи"),
    ("settings",   "  ✦   Настройки"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Zapret UI")
        self.setMinimumSize(980, 640)
        self.resize(cfg.get("window_width", 1140), cfg.get("window_height", 720))

        icon_path = ROOT / "assets" / "icon-default.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.runner = WinwsRunner(self)
        self.tester = StrategyTester(self)
        self.health_monitor = HealthMonitor(self.runner.is_running, self)
        self.auto_recovery = AutoRecovery(self.runner, interval_ms=3000, parent=self)

        self.runner.status_changed.connect(self._on_status_changed)
        self.health_monitor.health_changed.connect(self._on_health_changed)
        self.auto_recovery.recovery_triggered.connect(self._on_recovery_triggered)

        if cfg.get("auto_recovery_enabled", False):
            self.auto_recovery.start()

        self._sidebar_btns: dict[str, QPushButton] = {}
        self._current_page = "home"
        self._build_ui()
        self._init_domains()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        root.addWidget(sep)

        self._stack = QStackedWidget()
        root.addWidget(self._stack, stretch=1)

        self._panels: dict[str, QWidget] = {
            "home":       HomePanel(self.runner, self.tester, self),
            "strategies": StrategiesPanel(self.runner, self.tester, self),
            "domains":    DomainsPanel(self),
            "logs":       LogsPanel(self),
            "settings":   SettingsPanel(self),
        }
        for panel in self._panels.values():
            self._stack.addWidget(panel)

        self.runner.log_line.connect(self._panels["logs"].append_line)

        sp: StrategiesPanel = self._panels["strategies"]  # type: ignore
        self.tester.progress.connect(sp.on_test_progress)
        self.tester.strategy_done.connect(sp.on_strategy_done)
        self.tester.finished.connect(sp.on_test_finished)
        self.tester.finished.connect(self._on_test_finished)

        self._navigate("home")

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(16, 24, 16, 20)
        lay.setSpacing(2)

        logo = QLabel("Zapret UI")
        logo.setObjectName("SidebarLogo")
        lay.addWidget(logo)
        lay.addSpacing(20)

        for key, label in _NAV:
            btn = QPushButton(label)
            btn.setObjectName("NavBtn")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            lay.addWidget(btn)
            self._sidebar_btns[key] = btn

        lay.addStretch()

        ver = QLabel("v1.0.0")
        ver.setObjectName("SidebarVersion")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ver)

        return sidebar

    def _navigate(self, key: str) -> None:
        if old := self._sidebar_btns.get(self._current_page):
            old.setProperty("active", "false")
            old.style().unpolish(old)
            old.style().polish(old)

        self._current_page = key
        if panel := self._panels.get(key):
            self._stack.setCurrentWidget(panel)

        if btn := self._sidebar_btns.get(key):
            btn.setProperty("active", "true")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_status_changed(self, running: bool) -> None:
        status = "Активно" if running else "Выключено"
        self.setWindowTitle(f"Zapret UI — {status}")
        self._panels["home"].on_status_changed(running)  # type: ignore
        if running:
            self.health_monitor.start()
        else:
            self.health_monitor.stop()

    def _on_health_changed(self, is_healthy: bool) -> None:
        if not is_healthy:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "Zapret UI",
                "Текущая стратегия перестала работать.\n\nЗапустить авто-тест?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.trigger_auto_test()

    def _on_recovery_triggered(self, strategy_name: str) -> None:
        if hasattr(self, "_tray_icon") and self._tray_icon and self._tray_icon._tray:
            from PyQt6.QtWidgets import QSystemTrayIcon
            self._tray_icon._tray.showMessage(
                "Zapret UI",
                f"winws.exe перезапущен\nСтратегия: {strategy_name}",
                QSystemTrayIcon.MessageIcon.Warning,
                4000,
            )

    def _on_test_finished(self, best: str, scores: dict) -> None:
        if best:
            self.runner.start(best, cfg.get("hostlist_path", "lists/hostlist.txt"))

    def _init_domains(self) -> None:
        groups = cfg.get("enabled_groups", [])
        try:
            domains_mod.build_hostlist(groups, cfg.get("hostlist_path"))
        except Exception as e:
            log.warning("Не удалось собрать hostlist: %s", e)

    def trigger_auto_test(self) -> None:
        self._navigate("strategies")
        self._panels["strategies"].start_auto_test()  # type: ignore

    def force_quit(self) -> None:
        self._shutdown(None)

    def closeEvent(self, event: QCloseEvent) -> None:
        if cfg.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
        else:
            self._shutdown(event)

    def _shutdown(self, event) -> None:
        cfg.set("window_width", self.width())
        cfg.set("window_height", self.height())
        self.runner.stop()
        self.tester.cancel()
        if event:
            event.accept()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
