"""Панель «Стратегии» — список, авто-тест, прогресс-бар."""
import logging
from typing import Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QCheckBox, QSizePolicy,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

import core.config as cfg
import core.strategies as strats

log = logging.getLogger(__name__)

_STATUS_MAP = {
    "works":   ("Работает",      "BadgeWorks"),
    "partial": ("Частично",      "BadgePartial"),
    "fails":   ("Не работает",   "BadgeFails"),
    "error":   ("Ошибка",        "BadgeFails"),
    None:      ("Не проверено",  "BadgeNone"),
}

_TEST_DOMAINS = [
    "discord.com", "youtube.com", "faceit.com",
    "instagram.com", "twitch.tv", "spotify.com",
]


class _StrategyItem(QWidget):
    """Строка в списке: имя стратегии + бейдж статуса."""

    def __init__(self, name: str, status: str | None = None, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(4, 2, 4, 2)

        self._name_lbl = QLabel(name)
        self._name_lbl.setFont(QFont("Segoe UI Variable", 13))
        lay.addWidget(self._name_lbl, stretch=1)

        self._badge = QLabel()
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedWidth(110)
        lay.addWidget(self._badge)

        self.set_status(status)

    def set_status(self, status: str | None) -> None:
        text, obj_name = _STATUS_MAP.get(status, _STATUS_MAP[None])
        self._badge.setText(text)
        self._badge.setObjectName(obj_name)
        self._badge.style().unpolish(self._badge)
        self._badge.style().polish(self._badge)


class StrategiesPanel(QWidget):
    def __init__(self, runner, tester, parent=None):
        super().__init__(parent)
        self._runner = runner
        self._tester = tester
        self._items: dict[str, _StrategyItem] = {}
        self._list_items: dict[str, QListWidgetItem] = {}
        self._selected_test_domains: set[str] = set(cfg.get("test_domains", ["discord.com", "youtube.com"]))
        self._build()
        self._load_tested_results()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)

        # Заголовок
        hdr = QHBoxLayout()
        title = QLabel("Стратегии")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        hdr.addWidget(title)
        hdr.addStretch()

        self._lbl_active = QLabel()
        self._lbl_active.setStyleSheet("color: #8e8e93; font-size: 12px;")
        self._update_active_label()
        hdr.addWidget(self._lbl_active)
        root.addLayout(hdr)

        # Список стратегий
        self._list = QListWidget()
        self._list.setSpacing(2)
        self._list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._populate_list()
        root.addWidget(self._list, stretch=1)

        # ── Блок авто-теста ────────────────────────────────────────────────
        test_card = QFrame()
        test_card.setObjectName("Card")
        test_lay = QVBoxLayout(test_card)
        test_lay.setContentsMargins(16, 14, 16, 14)
        test_lay.setSpacing(10)

        test_title = QLabel("АВТО-ТЕСТ")
        test_title.setObjectName("SectionTitle")
        test_lay.addWidget(test_title)

        # Чипы доменов
        chip_lbl = QLabel("Тестовые домены:")
        chip_lbl.setStyleSheet("color: #8e8e93; font-size: 12px;")
        test_lay.addWidget(chip_lbl)

        chips_row = QHBoxLayout()
        chips_row.setSpacing(8)
        self._domain_chips: dict[str, QCheckBox] = {}
        for domain in _TEST_DOMAINS:
            chk = QCheckBox(domain)
            chk.setChecked(domain in self._selected_test_domains)
            chk.toggled.connect(lambda checked, d=domain: self._on_domain_chip(d, checked))
            chips_row.addWidget(chk)
        chips_row.addStretch()
        test_lay.addLayout(chips_row)

        # Прогресс-бар
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(strats.ALL_STRATEGIES))
        self._progress_bar.setValue(0)
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setTextVisible(False)
        test_lay.addWidget(self._progress_bar)

        self._progress_label = QLabel("Готов к тестированию")
        self._progress_label.setStyleSheet("color: #8e8e93; font-size: 12px;")
        test_lay.addWidget(self._progress_label)

        # Кнопки
        btn_row = QHBoxLayout()
        self._btn_test = QPushButton("⚡ Запустить тест всех 20 стратегий")
        self._btn_test.clicked.connect(self.start_auto_test)
        btn_row.addWidget(self._btn_test)

        self._btn_cancel = QPushButton("Отмена")
        self._btn_cancel.setObjectName("Secondary")
        self._btn_cancel.clicked.connect(self._tester.cancel)
        self._btn_cancel.setEnabled(False)
        btn_row.addWidget(self._btn_cancel)
        btn_row.addStretch()
        test_lay.addLayout(btn_row)

        root.addWidget(test_card)

    def _populate_list(self) -> None:
        self._list.clear()
        self._items.clear()
        self._list_items.clear()

        for group, members in strats.STRATEGY_GROUPS.items():
            # Заголовок группы
            grp_item = QListWidgetItem(group)
            grp_item.setFlags(Qt.ItemFlag.NoItemFlags)
            grp_item.setForeground(Qt.GlobalColor.gray)
            font = grp_item.font()
            font.setBold(True)
            font.setPointSize(10)
            grp_item.setFont(font)
            self._list.addItem(grp_item)

            for name in members:
                status = self._get_status(name)
                widget = _StrategyItem(name, status)
                item = QListWidgetItem()
                item.setSizeHint(QSize(0, 44))
                item.setData(Qt.ItemDataRole.UserRole, name)
                self._list.addItem(item)
                self._list.setItemWidget(item, widget)
                self._items[name] = widget
                self._list_items[name] = item

    def _get_status(self, name: str) -> str | None:
        tested = cfg.get("tested_strategies", {})
        return tested.get(name, {}).get("status")

    def _load_tested_results(self) -> None:
        tested = cfg.get("tested_strategies", {})
        for name, data in tested.items():
            if name in self._items:
                self._items[name].set_status(data.get("status"))

    def _update_active_label(self) -> None:
        current = cfg.get("current_strategy", "—")
        self._lbl_active.setText(f"Активна: {current}")

    # ── Слоты тестирования ────────────────────────────────────────────────

    def start_auto_test(self) -> None:
        if self._tester.is_running():
            return
        domains = list(self._selected_test_domains) or ["discord.com", "youtube.com"]
        self._btn_test.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск теста…")
        self._tester.run_async(strats.ALL_STRATEGIES, domains)

    def on_test_progress(self, current: int, total: int, name: str) -> None:
        self._progress_bar.setValue(current)
        self._progress_label.setText(f"[{current}/{total}] Тест: {name}")

    def on_strategy_done(self, name: str, score: int, total: int) -> None:
        tested = cfg.get("tested_strategies", {})
        status = tested.get(name, {}).get("status")
        if name in self._items:
            self._items[name].set_status(status)

    def on_test_finished(self, best: str, scores: dict) -> None:
        self._btn_test.setEnabled(True)
        self._btn_cancel.setEnabled(False)
        self._progress_bar.setValue(self._progress_bar.maximum())
        self._progress_label.setText(f"Тест завершён. Лучшая: {best}")
        self._load_tested_results()
        self._update_active_label()
        log.info("Авто-тест завершён. Лучшая стратегия: %s", best)

    # ── Слоты взаимодействия ──────────────────────────────────────────────

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        log.info("Выбрана стратегия: %s", name)
        cfg.set("current_strategy", name)
        self._update_active_label()
        if self._runner.is_running():
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            self._runner.start(name, hostlist)

    def _on_domain_chip(self, domain: str, checked: bool) -> None:
        if checked:
            self._selected_test_domains.add(domain)
        else:
            self._selected_test_domains.discard(domain)
        cfg.set("test_domains", list(self._selected_test_domains))
