"""Панель «Домены» — группы с тогглами и тегами доменов."""
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QCheckBox, QFrame, QSizePolicy, QPushButton, QFlowLayout,
)
from PyQt6.QtCore import Qt

import core.config as cfg
import core.domains as domains_mod

log = logging.getLogger(__name__)


# PyQt6 не включает QFlowLayout — реализуем простой wrap-layout
class _FlowLayout(QVBoxLayout):
    """Упрощённая имитация flow-layout через обёртку в QHBoxLayout."""
    pass


class _DomainTag(QLabel):
    def __init__(self, domain: str, parent=None):
        super().__init__(domain, parent)
        self.setStyleSheet(
            "background: rgba(83,74,183,0.10); border-radius: 4px;"
            "padding: 2px 8px; color: #534AB7; font-size: 11px;"
        )


class _GroupCard(QFrame):
    def __init__(self, group_name: str, domains: list[str],
                 enabled: bool, on_toggle, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._group = group_name
        self._on_toggle = on_toggle

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)

        # Заголовок + переключатель
        hdr = QHBoxLayout()
        self._toggle = QCheckBox(group_name)
        self._toggle.setStyleSheet("font-size: 13px; font-weight: 600;")
        self._toggle.setChecked(enabled)
        self._toggle.toggled.connect(self._on_check)
        hdr.addWidget(self._toggle)
        hdr.addStretch()

        count = QLabel(f"{len(domains)} доменов")
        count.setStyleSheet("color: #8e8e93; font-size: 11px;")
        hdr.addWidget(count)
        lay.addLayout(hdr)

        # Теги доменов (первые 12)
        tag_wrap = QWidget()
        tag_lay = QHBoxLayout(tag_wrap)
        tag_lay.setContentsMargins(0, 0, 0, 0)
        tag_lay.setSpacing(6)
        tag_lay.setAlignment(Qt.AlignmentFlag.AlignLeft)

        shown = domains[:12]
        for d in shown:
            tag_lay.addWidget(_DomainTag(d))
        if len(domains) > 12:
            more = QLabel(f"+{len(domains) - 12} ещё")
            more.setStyleSheet("color: #8e8e93; font-size: 11px;")
            tag_lay.addWidget(more)
        tag_lay.addStretch()
        lay.addWidget(tag_wrap)

    def _on_check(self, checked: bool) -> None:
        self._on_toggle(self._group, checked)


class DomainsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)

        # Заголовок
        hdr = QHBoxLayout()
        title = QLabel("Домены")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        hdr.addWidget(title)
        hdr.addStretch()

        self._lbl_total = QLabel()
        self._lbl_total.setStyleSheet("color: #8e8e93; font-size: 12px;")
        hdr.addWidget(self._lbl_total)

        btn_rebuild = QPushButton("🔄 Пересобрать hostlist")
        btn_rebuild.setObjectName("Secondary")
        btn_rebuild.clicked.connect(self._rebuild)
        hdr.addWidget(btn_rebuild)

        root.addLayout(hdr)

        hint = QLabel(
            "Включите нужные группы. Итоговый hostlist.txt будет передан в winws.exe."
        )
        hint.setStyleSheet("color: #8e8e93; font-size: 12px;")
        root.addWidget(hint)

        # Прокручиваемая область с карточками групп
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._cards_layout = QVBoxLayout(container)
        self._cards_layout.setContentsMargins(0, 0, 8, 0)
        self._cards_layout.setSpacing(10)

        self._populate()

        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        self._update_total()

    def _populate(self) -> None:
        # Очистить
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        enabled_groups = set(cfg.get("enabled_groups", []))

        for group in domains_mod.get_all_groups():
            doms = domains_mod.load_group(group)
            card = _GroupCard(
                group, doms,
                enabled=(group in enabled_groups),
                on_toggle=self._on_group_toggle,
            )
            self._cards_layout.addWidget(card)

        self._cards_layout.addStretch()

    def _on_group_toggle(self, group: str, enabled: bool) -> None:
        groups: list[str] = list(cfg.get("enabled_groups", []))
        if enabled and group not in groups:
            groups.append(group)
        elif not enabled and group in groups:
            groups.remove(group)
        cfg.set("enabled_groups", groups)
        self._update_total()
        # Пересобираем hostlist сразу
        self._rebuild()

    def _rebuild(self) -> None:
        groups = cfg.get("enabled_groups", [])
        try:
            domains_mod.build_hostlist(groups, cfg.get("hostlist_path"))
            self._update_total()
        except Exception as e:
            log.error("Ошибка пересборки доменов: %s", e)

    def _update_total(self) -> None:
        from pathlib import Path
        hostlist = Path(cfg.get("hostlist_path", "lists/hostlist.txt"))
        count = 0
        if hostlist.exists():
            count = sum(1 for l in hostlist.read_text(encoding="utf-8").splitlines() if l.strip())
        self._lbl_total.setText(f"Итого доменов: {count}")
