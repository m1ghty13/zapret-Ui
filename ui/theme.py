"""QSS-стили: light + dark тема с фиолетовым акцентом."""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette
from PyQt6.QtCore import Qt

ACCENT = "#534AB7"
ACCENT_HOVER = "#6559CC"
ACCENT_PRESSED = "#3E3690"

SUCCESS_BG = "#eaf3de"
SUCCESS_FG = "#3B6D11"
WARN_BG = "#fff4e0"
WARN_FG = "#7d4e00"
ERROR_BG = "#fde8e8"
ERROR_FG = "#8b1a1a"
NEUTRAL_BG = "#f0f0f0"
NEUTRAL_FG = "#555555"

_LIGHT_QSS = f"""
/* ── Общие ── */
QMainWindow, QDialog, QWidget {{
    background-color: #f5f5f7;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #1c1c1e;
}}

/* ── Sidebar ── */
#Sidebar {{
    background-color: #ebebf0;
    border-right: 1px solid #dcdce4;
}}
#SidebarButton {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    color: #3a3a3c;
}}
#SidebarButton:hover {{
    background-color: rgba(83, 74, 183, 0.10);
    color: {ACCENT};
}}
#SidebarButton[active="true"] {{
    background-color: rgba(83, 74, 183, 0.15);
    color: {ACCENT};
    font-weight: 600;
}}

/* ── Кнопки ── */
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
QPushButton:disabled {{ background-color: #c7c7cc; color: #8e8e93; }}

QPushButton#Secondary {{
    background-color: transparent;
    color: {ACCENT};
    border: 1.5px solid {ACCENT};
}}
QPushButton#Secondary:hover {{ background-color: rgba(83,74,183,0.08); }}
QPushButton#Secondary:pressed {{ background-color: rgba(83,74,183,0.15); }}

QPushButton#Danger {{
    background-color: #e74c3c;
}}
QPushButton#Danger:hover {{ background-color: #c0392b; }}

/* ── Большая кнопка toggle ── */
QPushButton#ToggleBtn {{
    border-radius: 36px;
    min-width: 72px;
    min-height: 72px;
    max-width: 72px;
    max-height: 72px;
    font-size: 26px;
    padding: 0;
    background-color: {ACCENT};
    color: white;
}}
QPushButton#ToggleBtn[running="true"] {{
    background-color: #e74c3c;
}}
QPushButton#ToggleBtn:hover {{ opacity: 0.85; }}

/* ── Поля ввода ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #ffffff;
    border: 1.5px solid #dcdce4;
    border-radius: 8px;
    padding: 6px 10px;
    color: #1c1c1e;
}}
QLineEdit:focus, QPlainTextEdit:focus {{
    border-color: {ACCENT};
}}

/* ── Список стратегий ── */
QListWidget {{
    background-color: #ffffff;
    border: 1px solid #dcdce4;
    border-radius: 10px;
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 36px;
}}
QListWidget::item:hover {{ background-color: rgba(83,74,183,0.07); }}
QListWidget::item:selected {{
    background-color: rgba(83,74,183,0.14);
    color: {ACCENT};
}}

/* ── Прогресс-бар ── */
QProgressBar {{
    border: none;
    border-radius: 6px;
    background-color: #e5e5ea;
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 6px;
}}

/* ── Скроллбар ── */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #c7c7cc;
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Чекбоксы / переключатели ── */
QCheckBox {{
    spacing: 8px;
    color: #1c1c1e;
}}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1.5px solid #8e8e93;
    background: white;
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* ── Разделители ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: #dcdce4;
}}

/* ── Лейблы-заголовки ── */
QLabel#SectionTitle {{
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
    letter-spacing: 0.5px;
}}
QLabel#StatusOk  {{ color: {SUCCESS_FG}; font-weight: 600; }}
QLabel#StatusErr {{ color: #e74c3c; font-weight: 600; }}

/* ── Бейдж стратегии ── */
QLabel#BadgeWorks   {{ color: {SUCCESS_FG}; background: {SUCCESS_BG}; border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgePartial {{ color: {WARN_FG};    background: {WARN_BG};    border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeFails   {{ color: {ERROR_FG};   background: {ERROR_BG};   border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeNone    {{ color: {NEUTRAL_FG}; background: {NEUTRAL_BG}; border-radius: 5px; padding: 1px 7px; }}

/* ── Скруглённая карточка ── */
QFrame#Card {{
    background: #ffffff;
    border: 1px solid #dcdce4;
    border-radius: 12px;
}}
"""

_DARK_QSS = f"""
QMainWindow, QDialog, QWidget {{
    background-color: #1c1c1e;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #f2f2f7;
}}
#Sidebar {{
    background-color: #2c2c2e;
    border-right: 1px solid #3a3a3c;
}}
#SidebarButton {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    color: #ebebf0;
}}
#SidebarButton:hover {{ background-color: rgba(83,74,183,0.20); color: #a89fe8; }}
#SidebarButton[active="true"] {{
    background-color: rgba(83,74,183,0.30);
    color: #c4bef5;
    font-weight: 600;
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
QPushButton:pressed {{ background-color: {ACCENT_PRESSED}; }}
QPushButton:disabled {{ background-color: #3a3a3c; color: #636366; }}
QPushButton#Secondary {{
    background-color: transparent;
    color: #a89fe8;
    border: 1.5px solid #534AB7;
}}
QPushButton#Danger {{ background-color: #c0392b; }}
QPushButton#ToggleBtn {{
    border-radius: 36px;
    min-width: 72px; min-height: 72px;
    max-width: 72px; max-height: 72px;
    font-size: 26px; padding: 0;
    background-color: {ACCENT};
    color: white;
}}
QPushButton#ToggleBtn[running="true"] {{ background-color: #c0392b; }}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: #2c2c2e;
    border: 1.5px solid #3a3a3c;
    border-radius: 8px;
    padding: 6px 10px;
    color: #f2f2f7;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QListWidget {{
    background-color: #2c2c2e;
    border: 1px solid #3a3a3c;
    border-radius: 10px;
    outline: none;
    padding: 4px;
    color: #f2f2f7;
}}
QListWidget::item {{ border-radius: 6px; padding: 6px 10px; min-height: 36px; }}
QListWidget::item:hover {{ background-color: rgba(83,74,183,0.18); }}
QListWidget::item:selected {{ background-color: rgba(83,74,183,0.30); color: #c4bef5; }}
QProgressBar {{
    border: none; border-radius: 6px;
    background-color: #3a3a3c; height: 8px;
}}
QProgressBar::chunk {{ background-color: {ACCENT}; border-radius: 6px; }}
QScrollBar:vertical {{
    border: none; background: transparent; width: 6px; margin: 0;
}}
QScrollBar::handle:vertical {{ background: #636366; border-radius: 3px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QCheckBox {{ spacing: 8px; color: #f2f2f7; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 5px;
    border: 1.5px solid #636366; background: #3a3a3c;
}}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QFrame[frameShape="4"], QFrame[frameShape="5"] {{ color: #3a3a3c; }}
QLabel#SectionTitle {{ font-size: 11px; font-weight: 600; color: #636366; letter-spacing: 0.5px; }}
QLabel#StatusOk {{ color: #6abe3a; font-weight: 600; }}
QLabel#StatusErr {{ color: #ff6b6b; font-weight: 600; }}
QLabel#BadgeWorks   {{ color: #6abe3a; background: #1e3310; border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgePartial {{ color: #f0a500; background: #3d2e00; border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeFails   {{ color: #ff6b6b; background: #3d1010; border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeNone    {{ color: #8e8e93; background: #2c2c2e; border-radius: 5px; padding: 1px 7px; }}
QFrame#Card {{ background: #2c2c2e; border: 1px solid #3a3a3c; border-radius: 12px; }}
"""


def _is_dark() -> bool:
    try:
        hints = QApplication.styleHints()
        from PyQt6.QtCore import Qt
        return hints.colorScheme() == Qt.ColorScheme.Dark
    except Exception:
        return False


def apply_theme(app: QApplication) -> None:
    qss = _DARK_QSS if _is_dark() else _LIGHT_QSS
    app.setStyleSheet(qss)
