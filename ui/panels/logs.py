"""Панель «Логи»."""
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QFileDialog, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

log = logging.getLogger(__name__)
MAX_LINES = 2000


class LogsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)

        # ── Заголовок ──────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Логи")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_clear = QPushButton("  ✕  Очистить")
        btn_clear.setObjectName("Ghost")
        btn_clear.clicked.connect(self._clear)

        btn_save = QPushButton("  ↓  Сохранить")
        btn_save.setObjectName("Secondary")
        btn_save.clicked.connect(self._save)

        hdr.addWidget(btn_clear)
        hdr.addWidget(btn_save)
        root.addLayout(hdr)

        # ── Вывод ──────────────────────────────────────────────────────────
        self._out = QPlainTextEdit()
        self._out.setObjectName("LogOutput")
        self._out.setReadOnly(True)
        self._out.setMaximumBlockCount(MAX_LINES)
        root.addWidget(self._out, stretch=1)

        # ── Статус-строка ──────────────────────────────────────────────────
        self._status = QLabel("Ожидание...")
        self._status.setObjectName("StatKey")
        root.addWidget(self._status)

    def append_line(self, text: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._out.appendPlainText(f"[{ts}]  {text}")
        self._out.moveCursor(QTextCursor.MoveOperation.End)
        lines = self._out.blockCount()
        self._status.setText(f"{lines} строк")

    def _clear(self) -> None:
        self._out.clear()
        self._status.setText("Очищено")

    def _save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить лог", "zapret_log.txt", "Text files (*.txt)"
        )
        if path:
            Path(path).write_text(self._out.toPlainText(), encoding="utf-8")
            self._status.setText(f"Сохранено: {path}")
