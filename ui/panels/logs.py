"""Панель «Логи» — вывод stdout winws.exe в реальном времени."""
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QFileDialog,
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt

log = logging.getLogger(__name__)

MAX_LINES = 2000


class LogsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(12)

        # Заголовок + кнопки
        hdr = QHBoxLayout()
        title = QLabel("Логи")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_clear = QPushButton("🗑 Очистить")
        btn_clear.setObjectName("Secondary")
        btn_clear.clicked.connect(self._clear)
        hdr.addWidget(btn_clear)

        btn_save = QPushButton("💾 Сохранить")
        btn_save.setObjectName("Secondary")
        btn_save.clicked.connect(self._save)
        hdr.addWidget(btn_save)

        root.addLayout(hdr)

        # Текстовое поле
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        mono_font = QFont("Consolas", 11)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        self._text.setFont(mono_font)
        self._text.setMaximumBlockCount(MAX_LINES)
        root.addWidget(self._text, stretch=1)

        # Статус-строка
        self._status = QLabel("Ожидание логов…")
        self._status.setStyleSheet("color: #8e8e93; font-size: 11px;")
        root.addWidget(self._status)

    def append_line(self, line: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._text.appendPlainText(f"[{ts}] {line}")
        # Авто-скролл вниз
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text.setTextCursor(cursor)
        count = self._text.blockCount()
        self._status.setText(f"Строк: {count}")

    def _clear(self) -> None:
        self._text.clear()
        self._status.setText("Лог очищен")

    def _save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить лог",
            str(Path.home() / "zapret_log.txt"),
            "Текстовый файл (*.txt)",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._text.toPlainText())
                self._status.setText(f"Сохранено: {path}")
                log.info("Лог сохранён: %s", path)
            except Exception as e:
                log.error("Ошибка сохранения лога: %s", e)
