"""Панель «Главная»."""
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt

import core.config as cfg
import core.domains as domains_mod

log = logging.getLogger(__name__)


def _card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("Card")
    return f


def _stat_card(key: str, value: str, parent=None) -> tuple[QFrame, QLabel]:
    card = _card(parent)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(20, 16, 20, 16)
    lay.setSpacing(6)

    lbl_key = QLabel(key)
    lbl_key.setObjectName("StatKey")

    lbl_val = QLabel(value)
    lbl_val.setObjectName("StatVal")
    lbl_val.setWordWrap(True)

    lay.addWidget(lbl_key)
    lay.addWidget(lbl_val)
    return card, lbl_val


class HomePanel(QWidget):
    def __init__(self, runner, tester, parent=None):
        super().__init__(parent)
        self._runner = runner
        self._tester = tester
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # ── Заголовок ──────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Главная")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        # ── Карточка управления ────────────────────────────────────────────
        ctrl_card = _card()
        ctrl_lay = QVBoxLayout(ctrl_card)
        ctrl_lay.setContentsMargins(32, 28, 32, 28)
        ctrl_lay.setSpacing(16)
        ctrl_lay.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._power_btn = QPushButton("⏻")
        self._power_btn.setObjectName("PowerBtn")
        self._power_btn.setProperty("active", "false")
        self._power_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._power_btn.setToolTip("Запустить / Остановить")
        self._power_btn.clicked.connect(self._toggle)

        self._status_lbl = QLabel("Остановлен")
        self._status_lbl.setObjectName("StatusOff")
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._strategy_lbl = QLabel("Стратегия не выбрана")
        self._strategy_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._strategy_lbl.setStyleSheet("color: #71717a; font-size: 12px;")

        ctrl_lay.addWidget(self._power_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ctrl_lay.addWidget(self._status_lbl)
        ctrl_lay.addWidget(self._strategy_lbl)

        root.addWidget(ctrl_card)

        # ── Стат-карточки ──────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(12)

        strategy = cfg.get("current_strategy", "—")
        self._card_strategy, self._val_strategy = _stat_card("Текущая стратегия", strategy or "—")

        hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
        count = self._count_domains(hostlist)
        self._card_domains, self._val_domains = _stat_card("Доменов в hostlist", str(count))

        autostart = "Включён" if cfg.get("autostart", False) else "Выключен"
        self._card_autostart, self._val_autostart = _stat_card("Автозапуск", autostart)

        recovery = "Включён" if cfg.get("auto_recovery_enabled", False) else "Выключен"
        self._card_recovery, self._val_recovery = _stat_card("Авто-восстановление", recovery)

        grid.addWidget(self._card_strategy,  0, 0)
        grid.addWidget(self._card_domains,   0, 1)
        grid.addWidget(self._card_autostart, 1, 0)
        grid.addWidget(self._card_recovery,  1, 1)

        root.addLayout(grid)

        # ── Кнопки действий ───────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_rebuild = QPushButton("  ◎  Пересобрать домены")
        btn_rebuild.setObjectName("Secondary")
        btn_rebuild.clicked.connect(self._rebuild_domains)

        btn_test = QPushButton("  ⚡  Авто-тест стратегий")
        btn_test.setObjectName("Secondary")
        btn_test.clicked.connect(self._start_test)

        btn_row.addWidget(btn_rebuild)
        btn_row.addWidget(btn_test)
        btn_row.addStretch()
        root.addLayout(btn_row)

        root.addStretch()

        self._refresh_strategy_label()

    # ── Вспомогательные ───────────────────────────────────────────────────

    def _count_domains(self, path: str) -> int:
        p = Path(path) if path else Path("lists/hostlist.txt")
        if not p.exists():
            return 0
        return sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip())

    def _refresh_strategy_label(self) -> None:
        s = cfg.get("current_strategy", "")
        self._strategy_lbl.setText(f"Стратегия: {s}" if s else "Стратегия не выбрана")
        self._val_strategy.setText(s or "—")

    # ── Слоты ─────────────────────────────────────────────────────────────

    def _toggle(self) -> None:
        if self._runner.is_running():
            self._runner.stop()
        else:
            strategy = cfg.get("current_strategy", "")
            if not strategy:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Zapret UI",
                    "Выберите стратегию во вкладке «Стратегии» перед запуском.")
                return
            hostlist = cfg.get("hostlist_path", "lists/hostlist.txt")
            self._runner.start(strategy, hostlist)

    def _rebuild_domains(self) -> None:
        groups = cfg.get("enabled_groups", [])
        try:
            domains_mod.build_hostlist(groups, cfg.get("hostlist_path"))
            count = self._count_domains(cfg.get("hostlist_path", "lists/hostlist.txt"))
            self._val_domains.setText(str(count))
        except Exception as e:
            log.error("Rebuild failed: %s", e)

    def _start_test(self) -> None:
        parent = self.parent()
        while parent and not hasattr(parent, "trigger_auto_test"):
            parent = parent.parent()
        if parent:
            parent.trigger_auto_test()

    def on_status_changed(self, running: bool) -> None:
        self._power_btn.setProperty("active", "true" if running else "false")
        self._power_btn.style().unpolish(self._power_btn)
        self._power_btn.style().polish(self._power_btn)

        if running:
            self._status_lbl.setText("Активно")
            self._status_lbl.setObjectName("StatusOn")
        else:
            self._status_lbl.setText("Остановлен")
            self._status_lbl.setObjectName("StatusOff")
        self._status_lbl.style().unpolish(self._status_lbl)
        self._status_lbl.style().polish(self._status_lbl)

        self._refresh_strategy_label()
        count = self._count_domains(cfg.get("hostlist_path", "lists/hostlist.txt"))
        self._val_domains.setText(str(count))
        autostart = "Включён" if cfg.get("autostart", False) else "Выключен"
        self._val_autostart.setText(autostart)
        recovery = "Включён" if cfg.get("auto_recovery_enabled", False) else "Выключен"
        self._val_recovery.setText(recovery)
