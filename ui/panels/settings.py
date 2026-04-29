"""Панель «Настройки»."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QLineEdit, QPushButton, QFrame, QFileDialog, QScrollArea,
)
from PyQt6.QtCore import Qt

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
