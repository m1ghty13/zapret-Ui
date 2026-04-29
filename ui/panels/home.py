"""Панель «Главная» — кнопка-тоггл и статус-строки."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt

import core.config as cfg
import core.domains as domains_mod

log = logging.getLogger(__name__)


def _make_card() -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    return card


class _InfoRow(QWidget):
    """Строка: лейбл + значение."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        self._lbl = QLabel(label)
        self._lbl.setStyleSheet("color: #8e8e93; min-width: 160px;")
        self._val = QLabel("—")
        self._val.setObjectName("StatusOk")
        lay.addWidget(self._lbl)
        lay.addWidget(self._val, stretch=1)

    def set_value(self, text: str, ok: bool = True) -> None:
        self._val.setText(text)
        self._val.setObjectName("StatusOk" if ok else "StatusErr")
        self._val.style().unpolish(self._val)
        self._val.style().polish(self._val)


class HomePanel(QWidget):
    def __init__(self, runner, tester, parent=None):
        super().__init__(parent)
        self._runner = runner
        self._tester = tester
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(24)

        # ── Заголовок ──────────────────────────────────────────────────────
        title = QLabel("Главная")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        root.addWidget(title)

        # ── Кнопка-тоггл + подпись ─────────────────────────────────────────
        toggle_wrap = QHBoxLayout()
        toggle_wrap.setAlignment(Qt.AlignmentFlag.AlignLeft)

        toggle_col = QVBoxLayout()
        toggle_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toggle_col.setSpacing(8)

        self._toggle_btn = QPushButton("▶")
        self._toggle_btn.setObjectName("ToggleBtn")
        self._toggle_btn.setProperty("running", "false")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._on_toggle)
        toggle_col.addWidget(self._toggle_btn)

        self._toggle_label = QLabel("Нажмите для запуска")
        self._toggle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._toggle_label.setStyleSheet("color: #8e8e93; font-size: 12px;")
        toggle_col.addWidget(self._toggle_label)

        toggle_wrap.addLayout(toggle_col)
        toggle_wrap.addSpacing(32)

        # ── Карточка статуса ────────────────────────────────────────────────
        card = _make_card()
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(20, 16, 20, 16)
        card_lay.setSpacing(2)

        self._row_strategy = _InfoRow("Стратегия:")
        self._row_domains  = _InfoRow("Доменов в hostlist:")
        self._row_process  = _InfoRow("Процесс winws:")
        self._row_autorun  = _InfoRow("Автозапуск:")

        for row in (self._row_strategy, self._row_domains,
                    self._row_process, self._row_autorun):
            card_lay.addWidget(row)

        toggle_wrap.addWidget(card, stretch=1)
        root.addLayout(toggle_wrap)

        # ── Кнопки быстрых действий ─────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(12)

        self._btn_rebuild = QPushButton("🔄 Пересобрать домены")
        self._btn_rebuild.setObjectName("Secondary")
        self._btn_rebuild.clicked.connect(self._rebuild_domains)
        actions.addWidget(self._btn_rebuild)

        self._btn_autotest = QPushButton("⚡ Авто-тест стратегий")
        self._btn_autotest.setObjectName("Secondary")
        self._btn_autotest.clicked.connect(self._run_autotest)
        actions.addWidget(self._btn_autotest)

        actions.addStretch()
        root.addLayout(actions)
        root.addStretch()

        self._refresh_info()

    # ── Обновление UI ─────────────────────────────────────────────────────

    def _refresh_info(self) -> None:
        strategy = cfg.get("current_strategy", "—")
        self._row_strategy.set_value(strategy)

        hostlist = Path(cfg.get("hostlist_path", "lists/hostlist.txt"))
        count = 0
        if hostlist.exists():
            count = sum(1 for l in hostlist.read_text(encoding="utf-8").splitlines() if l.strip())
        self._row_domains.set_value(str(count), ok=count > 0)

        running = self._runner.is_running()
        self._row_process.set_value(
            "● Работает" if running else "○ Остановлен", ok=running
        )

        try:
            from core.autostart import is_enabled
            ar = is_enabled()
        except Exception:
            ar = cfg.get("autostart", False)
        self._row_autorun.set_value("Включён" if ar else "Выключен", ok=ar)

    def on_status_changed(self, running: bool) -> None:
        self._toggle_btn.setProperty("running", "true" if running else "false")
        self._toggle_btn.style().unpolish(self._toggle_btn)
        self._toggle_btn.style().polish(self._toggle_btn)
        self._toggle_btn.setText("⏹" if running else "▶")
        self._toggle_label.setText("Нажмите для остановки" if running else "Нажмите для запуска")
        self._refresh_info()

    # ── Действия ──────────────────────────────────────────────────────────

    def _on_toggle(self) -> None:
        if self._runner.is_running():
            self._runner.stop()
        else:
            strategy = cfg.get("current_strategy", "ALT")
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            self._runner.start(strategy, hostlist)
        self._refresh_info()

    def _rebuild_domains(self) -> None:
        groups = cfg.get("enabled_groups", [])
        try:
            out = domains_mod.build_hostlist(groups, cfg.get("hostlist_path"))
            log.info("Домены пересобраны: %s", out)
            self._refresh_info()
        except Exception as e:
            log.error("Ошибка сборки доменов: %s", e)

    def _run_autotest(self) -> None:
        # Переключаем на панель стратегий и запускаем тест
        main_win = self.window()
        if hasattr(main_win, "_navigate"):
            main_win._navigate("strategies")
        if hasattr(main_win, "trigger_auto_test"):
            main_win.trigger_auto_test()
