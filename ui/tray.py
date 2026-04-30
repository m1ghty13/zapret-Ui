"""Системный трей: иконка, меню, уведомления."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

import core.config as cfg
import core.strategies as strats
from core.ping_monitor import PingMonitor

log = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent


def _icon(name: str, connection_status: bool | None = None) -> QIcon:
    """Загружает иконку из assets/ или создаёт fallback с индикатором подключения."""
    path = ROOT / "assets" / name
    if path.exists():
        pixmap = QPixmap(str(path))
    else:
        # Fallback: создаём простую цветную иконку
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        color = QColor("#00ff00") if "active" in name else QColor("#888888")
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()

    # Добавляем индикатор подключения (маленький кружок в правом нижнем углу)
    if connection_status is not None:
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Цвет индикатора: зелёный = online, красный = offline
        indicator_color = QColor("#34c759") if connection_status else QColor("#ff3b30")

        # Рисуем кружок 16x16 в правом нижнем углу
        painter.setBrush(indicator_color)
        painter.setPen(QColor("#ffffff"))  # Белая обводка
        painter.drawEllipse(pixmap.width() - 20, pixmap.height() - 20, 16, 16)
        painter.end()

    return QIcon(pixmap)


class TrayIcon:
    """Нативный Qt системный трей с меню стратегий."""

    def __init__(self, main_window, app: QApplication):
        self._win = main_window
        self._app = app
        self._tray: QSystemTrayIcon | None = None
        self._strategies_menu: QMenu | None = None
        self._ping_monitor = PingMonitor(interval_ms=5000, parent=app)
        self._connection_status: bool | None = None

    def setup(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            log.warning("Системный трей недоступен")
            return

        self._tray = QSystemTrayIcon(self._app)
        self._tray.setIcon(_icon("icon-inactive.ico"))
        self._tray.setToolTip("Zapret UI — Выключено")
        self._tray.activated.connect(self._on_activated)

        # Контекстное меню (правый клик)
        self._context_menu = self._build_context_menu()
        self._tray.setContextMenu(self._context_menu)

        # Quick switcher меню (левый клик) - создаётся динамически
        self._quick_menu: QMenu | None = None

        self._tray.show()

        # Подписываемся на статус runner
        self._win.runner.status_changed.connect(self._on_status_changed)

        # Подписываемся на ping monitor
        self._ping_monitor.status_changed.connect(self._on_connection_changed)

        # Запускаем ping monitor если включено в настройках
        if cfg.get("ping_monitor_enabled", False):
            self._ping_monitor.start()

    def show(self) -> None:
        if self._tray:
            self._tray.show()

        log.info("Системный трей создан (Qt native)")

    def _build_context_menu(self) -> QMenu:
        """Строит полное контекстное меню (правый клик)."""
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

        return menu

    def _build_quick_switcher_menu(self) -> QMenu:
        """Строит компактное меню для быстрого переключения (левый клик)."""
        menu = QMenu()

        # Заголовок
        header = QAction("Быстрое переключение", menu)
        header.setEnabled(False)
        menu.addAction(header)

        menu.addSeparator()

        # Последние 5 стратегий
        recent = cfg.get("recent_strategies", [])
        current = self._win.runner.current_strategy()
        test_results = cfg.get("tested_strategies", {})

        if recent:
            for strategy_name in recent:
                # Формируем текст с результатами теста если есть
                text = strategy_name
                if strategy_name in test_results:
                    result = test_results[strategy_name]
                    score = result.get("score", 0)
                    total = result.get("total", 0)
                    text = f"{strategy_name} ({score}/{total})"

                action = QAction(text, menu)
                action.setCheckable(True)
                action.setChecked(strategy_name == current)
                action.triggered.connect(lambda checked, s=strategy_name: self._quick_switch(s))
                menu.addAction(action)

            menu.addSeparator()

        # "Все стратегии" - открывает окно на панели стратегий
        act_all = QAction("Все стратегии ►", menu)
        act_all.triggered.connect(self._open_strategies_panel)
        menu.addAction(act_all)

        return menu

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
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Левый клик - показываем quick switcher
            self._show_quick_switcher()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # Правый клик - контекстное меню (показывается автоматически)
            pass
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Двойной клик - показываем главное окно
            self._show_window()

    def _show_quick_switcher(self) -> None:
        """Показывает quick switcher меню рядом с курсором."""
        from PyQt6.QtGui import QCursor

        # Пересоздаём меню каждый раз для актуальности данных
        if self._quick_menu:
            self._quick_menu.deleteLater()

        self._quick_menu = self._build_quick_switcher_menu()
        self._quick_menu.exec(QCursor.pos())

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
            self._tray.setIcon(_icon("icon-active.ico", self._connection_status))
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
            self._tray.setIcon(_icon("icon-inactive.ico", self._connection_status))
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

    def _on_connection_changed(self, online: bool) -> None:
        """Обработка изменения статуса подключения."""
        self._connection_status = online

        # Обновляем иконку с новым индикатором
        if self._tray is None:
            return

        running = self._win.runner.is_running()
        icon_name = "icon-active.ico" if running else "icon-inactive.ico"
        self._tray.setIcon(_icon(icon_name, self._connection_status))

        # Показываем уведомление только если мониторинг включен
        if cfg.get("ping_monitor_enabled", False):
            if not online:
                self._tray.showMessage(
                    "Zapret UI",
                    "⚠️ Подключение к интернету потеряно",
                    QSystemTrayIcon.MessageIcon.Warning,
                    3000,
                )
            else:
                self._tray.showMessage(
                    "Zapret UI",
                    "✓ Подключение к интернету восстановлено",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000,
                )

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

    def _quick_switch(self, strategy_name: str) -> None:
        """Быстрое переключение стратегии из quick switcher."""
        current = self._win.runner.current_strategy()

        # Если выбрана текущая - ничего не делать
        if strategy_name == current:
            return

        self._switch_strategy(strategy_name)

    def _open_strategies_panel(self) -> None:
        """Открывает главное окно на панели стратегий."""
        self._show_window()
        # Переключаем на панель стратегий
        self._win._navigate("strategies")


def create_tray_icon(main_window, app: QApplication) -> TrayIcon:
    """Создаёт и настраивает системный трей."""
    tray = TrayIcon(main_window, app)
    tray.setup()
    return tray

