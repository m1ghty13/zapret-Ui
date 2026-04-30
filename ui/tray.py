"""Системный трей: иконка, меню, уведомления."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

import core.config as cfg
import core.strategies as strats

log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent


def _icon(name: str) -> QIcon:
    """Загружает иконку из assets/ или создаёт fallback."""
    path = ROOT / "assets" / name
    if path.exists():
        return QIcon(str(path))

    # Fallback: создаём простую цветную иконку
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    color = QColor("#00ff00") if "active" in name else QColor("#888888")
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()
    return QIcon(pixmap)


class TrayIcon:
    """Нативный Qt системный трей с меню стратегий."""

    def __init__(self, main_window, app: QApplication):
        self._win = main_window
        self._app = app
        self._tray: QSystemTrayIcon | None = None
        self._strategies_menu: QMenu | None = None

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

        # Статус (неактивный пункт)
        self._act_status = QAction("Статус: Выключено", menu)
        self._act_status.setEnabled(False)
        menu.addAction(self._act_status)

        menu.addSeparator()

        # Подменю стратегий
        self._strategies_menu = QMenu("⚡ Стратегии", menu)
        self._build_strategies_menu()
        menu.addMenu(self._strategies_menu)

        menu.addSeparator()

        # Включить/Выключить
        self._act_toggle = QAction("▶ Включить", menu)
        self._act_toggle.triggered.connect(self._toggle)
        menu.addAction(self._act_toggle)

        menu.addSeparator()

        # Открыть окно
        act_open = QAction("🪟 Открыть", menu)
        act_open.triggered.connect(self._show_window)
        menu.addAction(act_open)

        menu.addSeparator()

        # Выход
        act_quit = QAction("✕ Выход", menu)
        act_quit.triggered.connect(self._win.force_quit)
        menu.addAction(act_quit)

        self._tray.setContextMenu(menu)
        self._tray.show()

        # Подписываемся на статус runner
        self._win.runner.status_changed.connect(self._on_status_changed)

        log.info("Системный трей создан (Qt native)")

    def _build_strategies_menu(self) -> None:
        """Строит подменю со списком стратегий (первые 10)."""
        if not self._strategies_menu:
            return

        strategies = strats.list_strategies()[:10]  # Первые 10
        current = cfg.get("current_strategy", "")

        for name in strategies:
            action = QAction(name, self._strategies_menu)
            action.setCheckable(True)
            action.setChecked(name == current)
            action.triggered.connect(lambda checked, s=name: self._switch_strategy(s))
            self._strategies_menu.addAction(action)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Обработка кликов по иконке."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self) -> None:
        """Показывает и активирует главное окно."""
        self._win.show()
        self._win.activateWindow()
        self._win.raise_()

    def _on_status_changed(self, running: bool) -> None:
        """Обновление иконки и меню при изменении статуса."""
        if self._tray is None:
            return

        if running:
            strategy = self._win.runner.current_strategy()
            self._tray.setIcon(_icon("icon-active.ico"))
            self._tray.setToolTip(f"Zapret UI — Активно ({strategy})")
            self._act_status.setText(f"Статус: ✓ Активно ({strategy})")
            self._act_toggle.setText("⏹ Выключить")

            # Нативное Windows toast уведомление
            self._tray.showMessage(
                "Zapret UI",
                f"Запущено: {strategy}",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )
        else:
            self._tray.setIcon(_icon("icon-inactive.ico"))
            self._tray.setToolTip("Zapret UI — Выключено")
            self._act_status.setText("Статус: Выключено")
            self._act_toggle.setText("▶ Включить")

            self._tray.showMessage(
                "Zapret UI",
                "Остановлено",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )

        # Обновляем чекбоксы в меню стратегий
        self._update_strategies_menu()

    def _update_strategies_menu(self) -> None:
        """Обновляет чекбоксы в меню стратегий."""
        if not self._strategies_menu:
            return

        current = self._win.runner.current_strategy()
        for action in self._strategies_menu.actions():
            action.setChecked(action.text() == current)

    def _toggle(self) -> None:
        """Включить/выключить защиту."""
        runner = self._win.runner
        if runner.is_running():
            runner.stop()
        else:
            strategy = cfg.get("current_strategy", "ALT")
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            runner.start(strategy, hostlist)

    def _switch_strategy(self, strategy_name: str) -> None:
        """Переключение на другую стратегию."""
        runner = self._win.runner
        was_running = runner.is_running()

        if was_running:
            runner.stop()

        cfg.set("current_strategy", strategy_name)

        if was_running:
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            runner.start(strategy_name, hostlist)

            self._tray.showMessage(
                "Zapret UI",
                f"Стратегия изменена: {strategy_name}",
                QSystemTrayIcon.MessageIcon.Information,
                2000,
            )


def create_tray_icon(main_window, app: QApplication) -> TrayIcon:
    """Создаёт и настраивает системный трей."""
    tray = TrayIcon(main_window, app)
    tray.setup()
    return tray

