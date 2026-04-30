"""QSS-стили: современный минималистичный дизайн."""
from PyQt6.QtWidgets import QApplication

ACCENT        = "#6366f1"
ACCENT_HOVER  = "#818cf8"
ACCENT_PRESS  = "#4f46e5"

BG      = "#0f0f11"
SURFACE = "#18181b"
CARD    = "#1e1e24"
CARD2   = "#27272a"
BORDER  = "#2e2e35"
BORDER2 = "#3f3f46"
TEXT    = "#fafafa"
TEXT2   = "#a1a1aa"
TEXT3   = "#71717a"
GREEN   = "#22c55e"
RED     = "#ef4444"
YELLOW  = "#f59e0b"


QSS = f"""
* {{
    font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    color: {TEXT};
    outline: none;
    box-sizing: border-box;
}}
QMainWindow, QDialog, QWidget {{
    background: {BG};
}}

/* ── Sidebar ── */
#Sidebar {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
    min-width: 220px;
    max-width: 220px;
}}
#SidebarLogo {{
    font-size: 16px;
    font-weight: 700;
    color: {TEXT};
    padding: 0;
}}
#SidebarSection {{
    font-size: 10px;
    font-weight: 700;
    color: {TEXT3};
    letter-spacing: 1px;
    padding: 0 4px;
}}
#NavBtn {{
    background: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    color: {TEXT2};
}}
#NavBtn:hover {{
    background: rgba(99,102,241,0.10);
    color: {TEXT};
}}
#NavBtn[active="true"] {{
    background: rgba(99,102,241,0.18);
    color: {ACCENT};
    font-weight: 600;
}}

/* ── Cards ── */
#Card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}
#Card2 {{
    background: {CARD2};
    border: 1px solid {BORDER2};
    border-radius: 10px;
}}

/* ── Buttons ── */
QPushButton {{
    background: {ACCENT};
    color: #fff;
    border: none;
    border-radius: 9px;
    padding: 9px 20px;
    font-weight: 600;
}}
QPushButton:hover   {{ background: {ACCENT_HOVER}; }}
QPushButton:pressed {{ background: {ACCENT_PRESS}; }}
QPushButton:disabled {{ background: {CARD2}; color: {TEXT3}; }}

QPushButton#Secondary {{
    background: rgba(99,102,241,0.12);
    color: {ACCENT};
    border: 1px solid rgba(99,102,241,0.28);
}}
QPushButton#Secondary:hover   {{ background: rgba(99,102,241,0.22); }}
QPushButton#Secondary:pressed {{ background: rgba(99,102,241,0.30); }}

QPushButton#Ghost {{
    background: transparent;
    color: {TEXT2};
    border: 1px solid {BORDER2};
}}
QPushButton#Ghost:hover {{ background: {CARD2}; color: {TEXT}; }}

QPushButton#Danger {{
    background: rgba(239,68,68,0.13);
    color: {RED};
    border: 1px solid rgba(239,68,68,0.28);
}}
QPushButton#Danger:hover {{ background: rgba(239,68,68,0.22); }}

/* ── Power Button ── */
#PowerBtn {{
    border-radius: 40px;
    min-width: 80px; max-width: 80px;
    min-height: 80px; max-height: 80px;
    font-size: 26px;
    padding: 0;
    background: rgba(99,102,241,0.12);
    color: {ACCENT};
    border: 2px solid rgba(99,102,241,0.30);
}}
#PowerBtn:hover {{
    background: rgba(99,102,241,0.22);
    border-color: {ACCENT};
}}
#PowerBtn[active="true"] {{
    background: rgba(34,197,94,0.12);
    color: {GREEN};
    border: 2px solid rgba(34,197,94,0.35);
}}
#PowerBtn[active="true"]:hover {{
    background: rgba(34,197,94,0.22);
}}

/* ── Inputs ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {CARD2};
    border: 1px solid {BORDER2};
    border-radius: 8px;
    padding: 7px 11px;
    color: {TEXT};
    selection-background-color: rgba(99,102,241,0.35);
}}
QLineEdit:focus, QPlainTextEdit:focus {{ border-color: {ACCENT}; }}

/* ── Log output ── */
#LogOutput {{
    background: #0a0a0d;
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px;
    font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 12px;
    color: #c9d1d9;
    line-height: 1.6;
}}

/* ── List ── */
QListWidget {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 38px;
    color: {TEXT2};
}}
QListWidget::item:hover    {{ background: rgba(99,102,241,0.10); color: {TEXT}; }}
QListWidget::item:selected {{ background: rgba(99,102,241,0.18); color: {ACCENT}; }}

/* ── Progress ── */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background: {CARD2};
    min-height: 6px;
    max-height: 6px;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 4px;
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    border: none; background: transparent; width: 5px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER2}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    border: none; background: transparent; height: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER2}; border-radius: 3px; min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Checkbox ── */
QCheckBox {{ spacing: 9px; color: {TEXT}; background: transparent; }}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1.5px solid {BORDER2};
    background: {CARD2};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QCheckBox::indicator:hover {{ border-color: {ACCENT}; }}

/* ── ComboBox ── */
QComboBox {{
    background: {CARD2}; border: 1px solid {BORDER2};
    border-radius: 8px; padding: 7px 11px; color: {TEXT};
}}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {CARD}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 4px;
    selection-background-color: rgba(99,102,241,0.18);
    selection-color: {ACCENT};
}}

/* ── SpinBox ── */
QSpinBox {{
    background: {CARD2}; border: 1px solid {BORDER2};
    border-radius: 8px; padding: 7px 11px; color: {TEXT};
}}
QSpinBox:focus {{ border-color: {ACCENT}; }}
QSpinBox::up-button, QSpinBox::down-button {{
    border: none; background: transparent; width: 18px;
}}

/* ── Separator ── */
QFrame[frameShape="4"] {{ color: {BORDER}; max-width: 1px; }}
QFrame[frameShape="5"] {{ color: {BORDER}; max-height: 1px; }}

/* ── Labels ── */
#PageTitle    {{ font-size: 20px; font-weight: 700; color: {TEXT}; }}
#SectionLabel {{ font-size: 11px; font-weight: 700; color: {TEXT3}; letter-spacing: 0.8px; }}
#StatKey      {{ font-size: 12px; color: {TEXT3}; }}
#StatVal      {{ font-size: 14px; font-weight: 600; color: {TEXT}; }}
#StatusOn     {{ color: {GREEN}; font-weight: 600; }}
#StatusOff    {{ color: {TEXT3}; font-weight: 500; }}
#StatusErr    {{ color: {RED};   font-weight: 600; }}

/* ── Badges ── */
#BadgeWorks   {{ color: {GREEN};  background: rgba(34,197,94,0.12);  border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700; }}
#BadgeFails   {{ color: {RED};    background: rgba(239,68,68,0.12);  border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700; }}
#BadgePartial {{ color: {YELLOW}; background: rgba(245,158,11,0.12); border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700; }}
#BadgeNone    {{ color: {TEXT3};  background: {CARD2};               border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 700; }}

/* ── Tooltip ── */
QToolTip {{
    background: {CARD2}; color: {TEXT};
    border: 1px solid {BORDER2};
    border-radius: 7px; padding: 5px 10px;
}}

/* ── MessageBox ── */
QMessageBox {{ background: {SURFACE}; }}
QMessageBox QPushButton {{ min-width: 80px; }}
"""


def apply_theme(app: QApplication, theme: str = "dark", accent_color: str = "#6366f1") -> None:
    app.setStyleSheet(QSS)
