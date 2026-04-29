"""Системный трей: иконка, меню, уведомления."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

import core.config as cfg

log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent


def _icon(name: str) -> QIcon:
    path = ROOT / "assets" / name
    if path.exists():
        return QIcon(str(path))
    # Fallback: пустая иконка
    return QIcon()


class TrayIcon:
    def __init__(self, main_window, app: QApplication):
        self._win = main_window
        self._app = app
        self._tray: QSystemTrayIcon | None = None

    def setup(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            log.warning("Системный трей недоступен")
            return

        self._tray = QSystemTrayIcon(self._app)
        self._tray.setIcon(_icon("icon-inactive.ico"))
        self._tray.setToolTip("Zapret UI — Выключено")
        self._tray.activated.connect(self._on_activated)

        # Контекстное меню
        menu = QMenu()

        self._act_toggle = QAction("▶ Включить", menu)
        self._act_toggle.triggered.connect(self._toggle)
        menu.addAction(self._act_toggle)

        menu.addSeparator()

        act_open = QAction("🪟 Открыть", menu)
        act_open.triggered.connect(self._win.show)
        menu.addAction(act_open)

        menu.addSeparator()

        act_quit = QAction("✕ Выход", menu)
        act_quit.triggered.connect(self._win.force_quit)
        menu.addAction(act_quit)

        self._tray.setContextMenu(menu)
        self._tray.show()

        # Подписываемся на статус runner
        self._win.runner.status_changed.connect(self._on_status_changed)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._win.show()
            self._win.activateWindow()

    def _on_status_changed(self, running: bool) -> None:
        if self._tray is None:
            return
        if running:
            self._tray.setIcon(_icon("icon-active.ico"))
            self._tray.setToolTip(
                f"Zapret UI — Активно ({self._win.runner.current_strategy()})"
            )
            self._act_toggle.setText("⏹ Выключить")
            self._tray.showMessage(
                "Zapret UI",
                f"Запущено: {self._win.runner.current_strategy()}",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )
        else:
            self._tray.setIcon(_icon("icon-inactive.ico"))
            self._tray.setToolTip("Zapret UI — Выключено")
            self._act_toggle.setText("▶ Включить")
            self._tray.showMessage(
                "Zapret UI",
                "Остановлено",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )

    def _toggle(self) -> None:
        runner = self._win.runner
        if runner.is_running():
            runner.stop()
        else:
            strategy = cfg.get("current_strategy", "ALT")
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            runner.start(strategy, hostlist)
