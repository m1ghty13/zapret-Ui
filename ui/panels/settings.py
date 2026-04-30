"""Панель «Настройки»."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox, QComboBox,
    QFrame, QScrollArea, QFileDialog, QSpinBox,
)
from PyQt6.QtCore import Qt

import core.config as cfg
from core.autostart import enable as autostart_enable, disable as autostart_disable, is_enabled as is_autostart_enabled

log = logging.getLogger(__name__)


def _card(title: str, parent=None) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame(parent)
    card.setObjectName("Card")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(24, 20, 24, 20)
    lay.setSpacing(16)

    if title:
        lbl = QLabel(title.upper())
        lbl.setObjectName("SectionLabel")
        lay.addWidget(lbl)

    return card, lay


def _row(label: str, widget: QWidget, lay: QVBoxLayout) -> None:
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(200)
    lbl.setStyleSheet("color: #a1a1aa;")
    row.addWidget(lbl)
    row.addWidget(widget, stretch=1)
    lay.addLayout(row)


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 32, 32, 32)
        outer.setSpacing(0)

        title = QLabel("Настройки")
        title.setObjectName("PageTitle")
        outer.addWidget(title)
        outer.addSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(0, 0, 4, 0)
        root.setSpacing(16)

        # ── Запуск ─────────────────────────────────────────────────────────
        card, lay = _card("Запуск и стратегия")

        self._strategy_combo = QComboBox()
        from core.strategies import ALL_STRATEGIES
        self._strategy_combo.addItems(ALL_STRATEGIES)
        current = cfg.get("current_strategy", "")
        if current in ALL_STRATEGIES:
            self._strategy_combo.setCurrentText(current)
        _row("Стратегия по умолчанию", self._strategy_combo, lay)

        self._autostart_chk = QCheckBox("Запускать вместе с Windows")
        self._autostart_chk.setChecked(is_autostart_enabled())
        lay.addWidget(self._autostart_chk)

        self._autorun_chk = QCheckBox("Автозапуск стратегии при старте")
        self._autorun_chk.setChecked(cfg.get("autorun_on_start", False))
        lay.addWidget(self._autorun_chk)

        root.addWidget(card)

        # ── Пути ───────────────────────────────────────────────────────────
        card2, lay2 = _card("Пути к файлам")

        self._winws_edit = QLineEdit(cfg.get("winws_path", "bin/winws.exe"))
        row_winws = QHBoxLayout()
        row_winws.addWidget(self._winws_edit, stretch=1)
        btn_winws = QPushButton("…")
        btn_winws.setObjectName("Ghost")
        btn_winws.setFixedWidth(36)
        btn_winws.clicked.connect(self._browse_winws)
        row_winws.addWidget(btn_winws)
        lbl_winws = QLabel("Путь к winws.exe")
        lbl_winws.setFixedWidth(200)
        lbl_winws.setStyleSheet("color: #a1a1aa;")
        full_row = QHBoxLayout()
        full_row.addWidget(lbl_winws)
        full_row.addLayout(row_winws)
        lay2.addLayout(full_row)

        self._hostlist_edit = QLineEdit(cfg.get("hostlist_path", "lists/hostlist.txt"))
        row_hl = QHBoxLayout()
        row_hl.addWidget(self._hostlist_edit, stretch=1)
        btn_hl = QPushButton("…")
        btn_hl.setObjectName("Ghost")
        btn_hl.setFixedWidth(36)
        btn_hl.clicked.connect(self._browse_hostlist)
        row_hl.addWidget(btn_hl)
        lbl_hl = QLabel("Путь к hostlist.txt")
        lbl_hl.setFixedWidth(200)
        lbl_hl.setStyleSheet("color: #a1a1aa;")
        full_row2 = QHBoxLayout()
        full_row2.addWidget(lbl_hl)
        full_row2.addLayout(row_hl)
        lay2.addLayout(full_row2)

        root.addWidget(card2)

        # ── Поведение ──────────────────────────────────────────────────────
        card3, lay3 = _card("Поведение")

        self._tray_chk = QCheckBox("Сворачивать в трей при закрытии")
        self._tray_chk.setChecked(cfg.get("minimize_to_tray", True))
        lay3.addWidget(self._tray_chk)

        self._recovery_chk = QCheckBox("Авто-восстановление при сбое")
        self._recovery_chk.setChecked(cfg.get("auto_recovery_enabled", False))
        lay3.addWidget(self._recovery_chk)

        self._ping_chk = QCheckBox("Мониторинг соединения (ping)")
        self._ping_chk.setChecked(cfg.get("ping_monitor_enabled", False))
        lay3.addWidget(self._ping_chk)

        root.addWidget(card3)

        # ── Кнопки ─────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_save = QPushButton("  ✓  Сохранить настройки")
        btn_save.clicked.connect(self._save)
        btn_reset = QPushButton("  ↺  Сброс")
        btn_reset.setObjectName("Ghost")
        btn_reset.clicked.connect(self._reset)
        btn_row.addStretch()
        btn_row.addWidget(btn_reset)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

        root.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll, stretch=1)

        # Статус
        self._status = QLabel("")
        self._status.setObjectName("StatKey")
        outer.addWidget(self._status)

    def _browse_winws(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите winws.exe", "", "EXE (*.exe)")
        if path:
            self._winws_edit.setText(path)

    def _browse_hostlist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите hostlist", "", "Text (*.txt)")
        if path:
            self._hostlist_edit.setText(path)

    def _save(self) -> None:
        strategy = self._strategy_combo.currentText()
        cfg.set("current_strategy", strategy)
        cfg.set("winws_path", self._winws_edit.text())
        cfg.set("hostlist_path", self._hostlist_edit.text())
        cfg.set("minimize_to_tray", self._tray_chk.isChecked())
        cfg.set("auto_recovery_enabled", self._recovery_chk.isChecked())
        cfg.set("ping_monitor_enabled", self._ping_chk.isChecked())
        cfg.set("autorun_on_start", self._autorun_chk.isChecked())
        try:
            if self._autostart_chk.isChecked():
                autostart_enable()
            else:
                autostart_disable()
        except Exception as e:
            log.warning("Autostart error: %s", e)
        cfg.save()
        self._status.setText("✓  Настройки сохранены")

    def _reset(self) -> None:
        self._winws_edit.setText("bin/winws.exe")
        self._hostlist_edit.setText("lists/hostlist.txt")
        self._tray_chk.setChecked(True)
        self._recovery_chk.setChecked(False)
        self._ping_chk.setChecked(False)
        self._autorun_chk.setChecked(False)
        self._status.setText("Сброшено к значениям по умолчанию")
