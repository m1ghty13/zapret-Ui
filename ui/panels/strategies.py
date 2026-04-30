"""Панель «Стратегии»."""
import logging
from typing import Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QProgressBar, QFrame, QSplitter, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

import core.config as cfg
import core.strategies as strats

log = logging.getLogger(__name__)

_TEST_DOMAINS = [
    "youtube.com", "instagram.com", "twitter.com",
    "discord.com",  "telegram.org",  "twitch.tv",
]


def _card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("Card")
    return f


class StrategiesPanel(QWidget):
    def __init__(self, runner, tester, parent=None):
        super().__init__(parent)
        self._runner = runner
        self._tester = tester
        self._test_scores: dict[str, dict[str, Any]] = {}
        self._selected_test_domains: set[str] = set(_TEST_DOMAINS)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # ── Заголовок ──────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Стратегии")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        self._btn_test = QPushButton("  ⚡  Авто-тест")
        self._btn_test.clicked.connect(self.start_auto_test)

        self._btn_stop = QPushButton("  ✕  Стоп")
        self._btn_stop.setObjectName("Danger")
        self._btn_stop.clicked.connect(self._stop_test)
        self._btn_stop.setVisible(False)

        hdr.addWidget(self._btn_test)
        hdr.addWidget(self._btn_stop)
        root.addLayout(hdr)

        # ── Прогресс ───────────────────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, len(strats.ALL_STRATEGIES))
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)
        root.addWidget(self._progress_bar)

        self._progress_lbl = QLabel("")
        self._progress_lbl.setObjectName("StatKey")
        self._progress_lbl.setVisible(False)
        root.addWidget(self._progress_lbl)

        # ── Разделитель: список + детали ──────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #2e2e35; }")

        # Список стратегий
        list_card = _card()
        list_lay = QVBoxLayout(list_card)
        list_lay.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget()
        self._list.setSpacing(1)
        self._list.currentItemChanged.connect(self._on_item_changed)
        self._list.itemDoubleClicked.connect(self._on_double_click)
        list_lay.addWidget(self._list)
        splitter.addWidget(list_card)

        # Панель деталей
        detail_card = _card()
        self._detail_lay = QVBoxLayout(detail_card)
        self._detail_lay.setContentsMargins(24, 24, 24, 24)
        self._detail_lay.setSpacing(16)
        self._build_detail_empty()
        splitter.addWidget(detail_card)

        splitter.setSizes([380, 300])
        root.addWidget(splitter, stretch=1)

        self._populate_list()

    def _build_detail_empty(self) -> None:
        lbl = QLabel("Выберите стратегию\nиз списка слева")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #71717a; font-size: 14px;")
        self._detail_lay.addStretch()
        self._detail_lay.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        self._detail_lay.addStretch()

    def _populate_list(self) -> None:
        self._list.clear()
        current = cfg.get("current_strategy", "")
        scores = cfg.get("tested_strategies", {})

        for group, members in strats.STRATEGY_GROUPS.items():
            # Заголовок группы
            hdr = QListWidgetItem(f"  {group}")
            hdr.setFlags(Qt.ItemFlag.NoItemFlags)
            hdr.setForeground(QColor("#71717a"))
            font = hdr.font()
            font.setPointSize(10)
            font.setBold(True)
            hdr.setFont(font)
            hdr.setSizeHint(QSize(0, 32))
            self._list.addItem(hdr)

            for name in members:
                item = QListWidgetItem(f"    {name}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                item.setSizeHint(QSize(0, 42))
                if name == current:
                    item.setForeground(QColor("#6366f1"))
                self._list.addItem(item)

    def _on_item_changed(self, item: QListWidgetItem | None) -> None:
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        self._show_detail(name)

    def _on_double_click(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if name:
            self._apply_strategy(name)

    def _show_detail(self, name: str) -> None:
        while self._detail_lay.count():
            w = self._detail_lay.takeAt(0)
            if w.widget():
                w.widget().deleteLater()

        scores = cfg.get("tested_strategies", {})
        result = scores.get(name, {})

        # Название
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 16px; font-weight: 700;")
        self._detail_lay.addWidget(lbl_name)

        # Группа
        group = strats.get_group(name)
        lbl_group = QLabel(f"Группа: {group}")
        lbl_group.setObjectName("StatKey")
        self._detail_lay.addWidget(lbl_group)

        # Результат теста
        if result:
            score = result.get("score", 0)
            works = result.get("works", 0)
            total = result.get("total", 0)
            badge = QLabel()
            if score >= 0.7:
                badge.setText("✓  Работает")
                badge.setObjectName("BadgeWorks")
            elif score >= 0.3:
                badge.setText("~  Частично")
                badge.setObjectName("BadgePartial")
            else:
                badge.setText("✕  Не работает")
                badge.setObjectName("BadgeFails")
            self._detail_lay.addWidget(badge)

            stat = QLabel(f"Доменов: {works}/{total}")
            stat.setObjectName("StatKey")
            self._detail_lay.addWidget(stat)
        else:
            badge = QLabel("  Не протестировано")
            badge.setObjectName("BadgeNone")
            self._detail_lay.addWidget(badge)

        self._detail_lay.addStretch()

        # Кнопки
        btn_apply = QPushButton("  ▶  Запустить стратегию")
        btn_apply.clicked.connect(lambda: self._apply_strategy(name))
        self._detail_lay.addWidget(btn_apply)

        btn_select = QPushButton("  ✓  Выбрать (без запуска)")
        btn_select.setObjectName("Secondary")
        btn_select.clicked.connect(lambda: self._select_strategy(name))
        self._detail_lay.addWidget(btn_select)

    def _apply_strategy(self, name: str) -> None:
        cfg.set("current_strategy", name)
        hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
        self._runner.start(name, hostlist)
        self._populate_list()

    def _select_strategy(self, name: str) -> None:
        cfg.set("current_strategy", name)
        self._populate_list()

    def start_auto_test(self) -> None:
        if self._tester.is_running():
            return
        domains = list(self._selected_test_domains) or _TEST_DOMAINS
        self._btn_test.setVisible(False)
        self._btn_stop.setVisible(True)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self._progress_lbl.setVisible(True)
        self._progress_lbl.setText("Тестирование...")
        self._tester.run_async(strats.ALL_STRATEGIES, domains)

    def _stop_test(self) -> None:
        self._tester.cancel()
        self._reset_test_ui()

    def _reset_test_ui(self) -> None:
        self._btn_test.setVisible(True)
        self._btn_stop.setVisible(False)
        self._progress_bar.setVisible(False)
        self._progress_lbl.setVisible(False)

    # ── Слоты от tester ───────────────────────────────────────────────────

    def on_test_progress(self, current: int, total: int) -> None:
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)
        self._progress_lbl.setText(f"Протестировано: {current} / {total}")

    def on_strategy_done(self, name: str, score: float, details: dict) -> None:
        scores = cfg.get("tested_strategies", {})
        scores[name] = details
        cfg.set("tested_strategies", scores)

    def on_test_finished(self, best: str, scores: dict) -> None:
        cfg.set("tested_strategies", scores)
        if best:
            cfg.set("current_strategy", best)
            self._progress_lbl.setText(f"✓  Лучшая стратегия: {best}")
        else:
            self._progress_lbl.setText("Тест завершён — рабочих стратегий не найдено")
        self._btn_test.setVisible(True)
        self._btn_stop.setVisible(False)
        self._progress_bar.setVisible(False)
        self._populate_list()
