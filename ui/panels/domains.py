"""Панель «Домены»."""
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QCheckBox, QFrame, QPushButton,
)
from PyQt6.QtCore import Qt

import core.config as cfg
import core.domains as domains_mod

log = logging.getLogger(__name__)


def _card(parent=None) -> QFrame:
    f = QFrame(parent)
    f.setObjectName("Card")
    return f


class _GroupCard(QFrame):
    def __init__(self, group_name: str, domains: list[str], enabled: bool, on_toggle, parent=None):
        super().__init__(parent)
        self.setObjectName("Card2")
        self._group = group_name
        self._on_toggle = on_toggle

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        hdr = QHBoxLayout()

        self._toggle = QCheckBox(group_name)
        self._toggle.setStyleSheet("font-size: 13px; font-weight: 600;")
        self._toggle.setChecked(enabled)
        self._toggle.toggled.connect(self._on_check)
        hdr.addWidget(self._toggle)
        hdr.addStretch()

        count_lbl = QLabel(f"{len(domains)} доменов")
        count_lbl.setObjectName("StatKey")
        hdr.addWidget(count_lbl)

        lay.addLayout(hdr)

        # Превью доменов
        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)
        tags_row.setContentsMargins(0, 0, 0, 0)
        tags_row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for d in domains[:10]:
            tag = QLabel(d)
            tag.setStyleSheet(
                "background: rgba(99,102,241,0.10); color: #818cf8;"
                "border-radius: 5px; padding: 2px 8px; font-size: 11px;"
            )
            tags_row.addWidget(tag)

        if len(domains) > 10:
            more = QLabel(f"+{len(domains) - 10}")
            more.setObjectName("StatKey")
            tags_row.addWidget(more)

        tags_row.addStretch()
        lay.addLayout(tags_row)

    def _on_check(self, checked: bool) -> None:
        self._on_toggle(self._group, checked)


class DomainsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(20)

        # Заголовок
        hdr = QHBoxLayout()
        title = QLabel("Домены")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()

        self._lbl_total = QLabel()
        self._lbl_total.setObjectName("StatKey")
        hdr.addWidget(self._lbl_total)

        btn_rebuild = QPushButton("  ◎  Пересобрать hostlist")
        btn_rebuild.setObjectName("Secondary")
        btn_rebuild.clicked.connect(self._rebuild)
        hdr.addWidget(btn_rebuild)

        root.addLayout(hdr)

        hint = QLabel("Включите группы доменов. Итоговый hostlist.txt передаётся в winws.exe.")
        hint.setObjectName("StatKey")
        root.addWidget(hint)

        # Список карточек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._cards_layout = QVBoxLayout(container)
        self._cards_layout.setContentsMargins(0, 0, 4, 0)
        self._cards_layout.setSpacing(10)
        self._populate()

        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)
        self._update_total()

    def _populate(self) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        enabled = set(cfg.get("enabled_groups", []))
        for group in domains_mod.get_all_groups():
            doms = domains_mod.load_group(group)
            card = _GroupCard(group, doms, group in enabled, self._on_toggle)
            self._cards_layout.addWidget(card)

        self._cards_layout.addStretch()

    def _on_toggle(self, group: str, enabled: bool) -> None:
        groups: list[str] = list(cfg.get("enabled_groups", []))
        if enabled and group not in groups:
            groups.append(group)
        elif not enabled and group in groups:
            groups.remove(group)
        cfg.set("enabled_groups", groups)
        self._update_total()
        self._rebuild()

    def _rebuild(self) -> None:
        try:
            domains_mod.build_hostlist(cfg.get("enabled_groups", []), cfg.get("hostlist_path"))
            self._update_total()
        except Exception as e:
            log.error("Ошибка пересборки: %s", e)

    def _update_total(self) -> None:
        from pathlib import Path
        p = Path(cfg.get("hostlist_path", "lists/hostlist.txt"))
        count = 0
        if p.exists():
            count = sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip())
        self._lbl_total.setText(f"Итого: {count} доменов")
