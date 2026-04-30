"""Панель «Настройки»."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QLineEdit, QPushButton, QFrame, QFileDialog, QScrollArea,
    QComboBox, QColorDialog, QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import core.config as cfg

log = logging.getLogger(__name__)


def _section(title: str) -> QLabel:
    lbl = QLabel(title.upper())
    lbl.setObjectName("SectionTitle")
    return lbl


def _separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    return sep


class _ToggleRow(QWidget):
    """Строка: описание + QCheckBox."""

    def __init__(self, label: str, description: str, config_key: str, parent=None):
        super().__init__(parent)
        self._key = config_key
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 6, 0, 6)

        text_col = QVBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
        text_col.addWidget(lbl)
        desc = QLabel(description)
        desc.setStyleSheet("color: #8e8e93; font-size: 11px;")
        text_col.addWidget(desc)
        lay.addLayout(text_col, stretch=1)

        self._chk = QCheckBox()
        self._chk.setChecked(bool(cfg.get(config_key, False)))
        self._chk.toggled.connect(self._save)
        lay.addWidget(self._chk)

    def _save(self, checked: bool) -> None:
        cfg.set(self._key, checked)
        if self._key == "autostart":
            try:
                from core.autostart import enable, disable
                if checked:
                    enable()
                else:
                    disable()
            except Exception as e:
                log.warning("Автозапуск: %s", e)
        elif self._key == "ping_monitor_enabled":
            # Управляем ping monitor через трей
            self._notify_ping_monitor_changed(checked)

    def _notify_ping_monitor_changed(self, enabled: bool) -> None:
        """Уведомляет трей об изменении настройки ping monitor."""
        # Получаем главное окно
        window = self.window()
        if window and hasattr(window, '_tray_icon'):
            tray = window._tray_icon
            if tray and hasattr(tray, '_ping_monitor'):
                if enabled:
                    tray._ping_monitor.start()
                else:
                    tray._ping_monitor.stop()


class _PathRow(QWidget):
    """Строка: метка + поле пути + кнопка обзора."""

    def __init__(self, label: str, config_key: str,
                 file_filter: str = "Все файлы (*)", parent=None):
        super().__init__(parent)
        self._key = config_key
        self._filter = file_filter

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; font-weight: 500;")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        self._edit = QLineEdit(str(cfg.get(config_key, "")))
        self._edit.editingFinished.connect(self._save)
        row.addWidget(self._edit, stretch=1)

        btn = QPushButton("…")
        btn.setFixedWidth(36)
        btn.setObjectName("Secondary")
        btn.clicked.connect(self._browse)
        row.addWidget(btn)
        lay.addLayout(row)

    def _save(self) -> None:
        cfg.set(self._key, self._edit.text())

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", self._filter)
        if path:
            self._edit.setText(path)
            self._save()


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(0)

        title = QLabel("Настройки")
        title.setStyleSheet("font-size: 22px; font-weight: 700; margin-bottom: 20px;")
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 16, 0)
        lay.setSpacing(8)

        # ── Поведение ─────────────────────────────────────────────────────
        lay.addWidget(_section("Поведение"))
        lay.addWidget(_ToggleRow(
            "Автозапуск с Windows",
            "Добавляет ZapretUI в HKCU\\...\\Run",
            "autostart",
        ))
        lay.addWidget(_ToggleRow(
            "Сворачивать в трей при закрытии",
            "Закрытие окна скрывает приложение в трей",
            "minimize_to_tray",
        ))
        lay.addWidget(_ToggleRow(
            "Авто-тест при первом запуске",
            "Автоматически запускает тест 20 стратегий при первом старте",
            "auto_test_on_first_run",
        ))
        lay.addWidget(_ToggleRow(
            "Показывать подсказку Secure DNS",
            "Рекомендует включить DoH/DoT для лучшего обхода",
            "secure_dns_hint",
        ))
        lay.addWidget(_ToggleRow(
            "Мониторинг подключения в трее",
            "Показывает индикатор статуса интернета на иконке трея (проверка каждые 5 сек)",
            "ping_monitor_enabled",
        ))
        lay.addWidget(_separator())

        # ── Внешний вид ───────────────────────────────────────────────────
        lay.addWidget(_section("Внешний вид"))

        # Выбор темы
        theme_row = QWidget()
        theme_lay = QHBoxLayout(theme_row)
        theme_lay.setContentsMargins(0, 6, 0, 6)

        theme_label = QLabel("Тема")
        theme_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        theme_lay.addWidget(theme_label, stretch=1)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Тёмная", "Светлая", "Системная"])
        current_theme = cfg.get("theme", "dark")
        theme_map = {"dark": 0, "light": 1, "system": 2}
        self._theme_combo.setCurrentIndex(theme_map.get(current_theme, 0))
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_lay.addWidget(self._theme_combo)

        lay.addWidget(theme_row)

        # Цвет акцента
        accent_row = QWidget()
        accent_lay = QHBoxLayout(accent_row)
        accent_lay.setContentsMargins(0, 6, 0, 6)

        accent_label = QLabel("Цвет акцента")
        accent_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        accent_lay.addWidget(accent_label, stretch=1)

        # Превью текущего цвета
        self._color_preview = QLabel("   ")
        self._color_preview.setFixedSize(24, 24)
        self._color_preview.setStyleSheet(f"background-color: {cfg.get('accent_color', '#007aff')}; border-radius: 12px; border: 1px solid #8e8e93;")
        accent_lay.addWidget(self._color_preview)

        # Кнопка выбора цвета
        color_btn = QPushButton("Выбрать цвет")
        color_btn.setObjectName("Secondary")
        color_btn.clicked.connect(self._pick_color)
        accent_lay.addWidget(color_btn)

        lay.addWidget(accent_row)

        # Пресеты цветов
        presets_label = QLabel("Быстрый выбор:")
        presets_label.setStyleSheet("color: #8e8e93; font-size: 11px; margin-top: 4px;")
        lay.addWidget(presets_label)

        presets_row = QWidget()
        presets_lay = QHBoxLayout(presets_row)
        presets_lay.setContentsMargins(0, 4, 0, 4)
        presets_lay.setSpacing(8)

        presets = [
            ("Синий", "#007aff"),
            ("Красный", "#ff3b30"),
            ("Зелёный", "#34c759"),
            ("Фиолетовый", "#af52de"),
            ("Оранжевый", "#ff9500"),
        ]

        for name, color in presets:
            btn = QPushButton(name)
            btn.setFixedHeight(28)
            btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 6px; padding: 4px 12px;")
            btn.clicked.connect(lambda checked, c=color: self._apply_accent(c))
            presets_lay.addWidget(btn)

        presets_lay.addStretch()
        lay.addWidget(presets_row)

        lay.addWidget(_separator())

        # ── Пути ──────────────────────────────────────────────────────────
        lay.addWidget(_section("Пути к файлам"))
        lay.addWidget(_PathRow(
            "Путь к winws.exe",
            "winws_path",
            "Исполняемый файл (winws.exe)",
        ))
        lay.addWidget(_PathRow(
            "Путь к hostlist.txt",
            "hostlist_path",
            "Текстовый файл (*.txt)",
        ))
        lay.addWidget(_separator())

        # ── Информация ────────────────────────────────────────────────────
        lay.addWidget(_section("О программе"))

        info_card = QFrame()
        info_card.setObjectName("Card")
        info_lay = QVBoxLayout(info_card)
        info_lay.setContentsMargins(16, 14, 16, 14)
        info_lay.setSpacing(6)

        for text in (
            "Zapret UI — графический интерфейс для zapret (winws.exe)",
            "Оригинальный zapret: github.com/bol-van/zapret",
            "Сборка для Discord/YouTube: github.com/Flowseal/zapret-discord-youtube",
        ):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #8e8e93; font-size: 12px;")
            info_lay.addWidget(lbl)

        lay.addWidget(info_card)
        lay.addStretch()

        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

    def _on_theme_changed(self, index: int) -> None:
        """Обработка изменения темы."""
        theme_map = {0: "dark", 1: "light", 2: "system"}
        theme = theme_map[index]
        cfg.set("theme", theme)

        # Применяем тему мгновенно
        self._apply_theme()

    def _pick_color(self) -> None:
        """Открывает диалог выбора цвета."""
        current_color = QColor(cfg.get("accent_color", "#007aff"))
        color = QColorDialog.getColor(current_color, self, "Выберите цвет акцента")

        if color.isValid():
            hex_color = color.name()
            self._apply_accent(hex_color)

    def _apply_accent(self, hex_color: str) -> None:
        """Применяет новый цвет акцента."""
        cfg.set("accent_color", hex_color)

        # Обновляем превью
        self._color_preview.setStyleSheet(
            f"background-color: {hex_color}; border-radius: 12px; border: 1px solid #8e8e93;"
        )

        # Применяем тему мгновенно
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Применяет текущую тему к приложению."""
        from ui.theme import apply_theme

        app = QApplication.instance()
        if app:
            theme = cfg.get("theme", "dark")
            accent = cfg.get("accent_color", "#007aff")
            apply_theme(app, theme, accent)
            log.info("Тема применена: %s, акцент: %s", theme, accent)
