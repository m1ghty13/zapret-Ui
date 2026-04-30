"""QSS-стили: динамические темы с настраиваемым акцентом."""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Цветовые палитры
DARK = {
    "bg": "#1c1c1e",
    "sidebar": "#2c2c2e",
    "card": "#2c2c2e",
    "text": "#f2f2f7",
    "text_secondary": "#8e8e93",
    "border": "#3a3a3c",
    "input_bg": "#2c2c2e",
    "hover_bg": "rgba({accent_rgb}, 0.18)",
    "selected_bg": "rgba({accent_rgb}, 0.30)",
}

LIGHT = {
    "bg": "#f5f5f7",
    "sidebar": "#ebebf0",
    "card": "#ffffff",
    "text": "#1c1c1e",
    "text_secondary": "#8e8e93",
    "border": "#dcdce4",
    "input_bg": "#ffffff",
    "hover_bg": "rgba({accent_rgb}, 0.07)",
    "selected_bg": "rgba({accent_rgb}, 0.14)",
}


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Конвертирует #RRGGBB в (R, G, B)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _lighten(hex_color: str, factor: float = 1.2) -> str:
    """Осветляет цвет (для hover)."""
    r, g, b = _hex_to_rgb(hex_color)
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken(hex_color: str, factor: float = 0.8) -> str:
    """Затемняет цвет (для pressed)."""
    r, g, b = _hex_to_rgb(hex_color)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_qss(theme: str, accent_color: str) -> str:
    """
    Строит QSS для заданной темы и цвета акцента.

    Args:
        theme: "dark" | "light" | "system"
        accent_color: hex строка, например "#007aff"
    """
    # Определяем палитру
    if theme == "system":
        palette = DARK if _is_system_dark() else LIGHT
    elif theme == "light":
        palette = LIGHT
    else:  # dark
        palette = DARK

    # Генерируем производные цвета акцента
    accent_hover = _lighten(accent_color, 1.15)
    accent_pressed = _darken(accent_color, 0.85)
    accent_rgb = ", ".join(map(str, _hex_to_rgb(accent_color)))

    # Подставляем accent_rgb в hover/selected
    hover_bg = palette["hover_bg"].format(accent_rgb=accent_rgb)
    selected_bg = palette["selected_bg"].format(accent_rgb=accent_rgb)

    # Статусные цвета (одинаковые для обеих тем)
    if theme == "light" or (theme == "system" and not _is_system_dark()):
        success_fg = "#3B6D11"
        success_bg = "#eaf3de"
        warn_fg = "#7d4e00"
        warn_bg = "#fff4e0"
        error_fg = "#8b1a1a"
        error_bg = "#fde8e8"
        neutral_fg = "#555555"
        neutral_bg = "#f0f0f0"
        status_ok = success_fg
        status_err = "#e74c3c"
    else:
        success_fg = "#6abe3a"
        success_bg = "#1e3310"
        warn_fg = "#f0a500"
        warn_bg = "#3d2e00"
        error_fg = "#ff6b6b"
        error_bg = "#3d1010"
        neutral_fg = "#8e8e93"
        neutral_bg = "#2c2c2e"
        status_ok = "#6abe3a"
        status_err = "#ff6b6b"

    return f"""
/* ── Общие ── */
QMainWindow, QDialog, QWidget {{
    background-color: {palette["bg"]};
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 13px;
    color: {palette["text"]};
}}

/* ── Sidebar ── */
#Sidebar {{
    background-color: {palette["sidebar"]};
    border-right: 1px solid {palette["border"]};
}}
#SidebarButton {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    color: {palette["text"]};
}}
#SidebarButton:hover {{
    background-color: {hover_bg};
    color: {accent_color};
}}
#SidebarButton[active="true"] {{
    background-color: {selected_bg};
    color: {accent_color};
    font-weight: 600;
}}

/* ── Кнопки ── */
QPushButton {{
    background-color: {accent_color};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{ background-color: {accent_hover}; }}
QPushButton:pressed {{ background-color: {accent_pressed}; }}
QPushButton:disabled {{ background-color: {palette["border"]}; color: {palette["text_secondary"]}; }}

QPushButton#Secondary {{
    background-color: transparent;
    color: {accent_color};
    border: 1.5px solid {accent_color};
}}
QPushButton#Secondary:hover {{ background-color: {hover_bg}; }}
QPushButton#Secondary:pressed {{ background-color: {selected_bg}; }}

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
    background-color: {accent_color};
    color: white;
}}
QPushButton#ToggleBtn[running="true"] {{
    background-color: #e74c3c;
}}
QPushButton#ToggleBtn:hover {{ opacity: 0.85; }}

/* ── Поля ввода ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {palette["input_bg"]};
    border: 1.5px solid {palette["border"]};
    border-radius: 8px;
    padding: 6px 10px;
    color: {palette["text"]};
}}
QLineEdit:focus, QPlainTextEdit:focus {{
    border-color: {accent_color};
}}

/* ── Список стратегий ── */
QListWidget {{
    background-color: {palette["card"]};
    border: 1px solid {palette["border"]};
    border-radius: 10px;
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 36px;
}}
QListWidget::item:hover {{ background-color: {hover_bg}; }}
QListWidget::item:selected {{
    background-color: {selected_bg};
    color: {accent_color};
}}

/* ── Прогресс-бар ── */
QProgressBar {{
    border: none;
    border-radius: 6px;
    background-color: {palette["border"]};
    height: 8px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {accent_color};
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
    background: {palette["text_secondary"]};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Чекбоксы / переключатели ── */
QCheckBox {{
    spacing: 8px;
    color: {palette["text"]};
}}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border-radius: 5px;
    border: 1.5px solid {palette["text_secondary"]};
    background: {palette["input_bg"]};
}}
QCheckBox::indicator:checked {{
    background: {accent_color};
    border-color: {accent_color};
}}

/* ── Комбобоксы ── */
QComboBox {{
    background-color: {palette["input_bg"]};
    border: 1.5px solid {palette["border"]};
    border-radius: 8px;
    padding: 6px 10px;
    color: {palette["text"]};
}}
QComboBox:focus {{ border-color: {accent_color}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {palette["card"]};
    border: 1px solid {palette["border"]};
    selection-background-color: {selected_bg};
    selection-color: {accent_color};
}}

/* ── Спинбоксы ── */
QSpinBox {{
    background-color: {palette["input_bg"]};
    border: 1.5px solid {palette["border"]};
    border-radius: 8px;
    padding: 6px 10px;
    color: {palette["text"]};
}}
QSpinBox:focus {{ border-color: {accent_color}; }}

/* ── Разделители ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {palette["border"]};
}}

/* ── Лейблы-заголовки ── */
QLabel#SectionTitle {{
    font-size: 11px;
    font-weight: 600;
    color: {palette["text_secondary"]};
    letter-spacing: 0.5px;
}}
QLabel#StatusOk  {{ color: {status_ok}; font-weight: 600; }}
QLabel#StatusErr {{ color: {status_err}; font-weight: 600; }}

/* ── Бейдж стратегии ── */
QLabel#BadgeWorks   {{ color: {success_fg}; background: {success_bg}; border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgePartial {{ color: {warn_fg};    background: {warn_bg};    border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeFails   {{ color: {error_fg};   background: {error_bg};   border-radius: 5px; padding: 1px 7px; }}
QLabel#BadgeNone    {{ color: {neutral_fg}; background: {neutral_bg}; border-radius: 5px; padding: 1px 7px; }}

/* ── Скруглённая карточка ── */
QFrame#Card {{
    background: {palette["card"]};
    border: 1px solid {palette["border"]};
    border-radius: 12px;
}}
"""


def _is_system_dark() -> bool:
    """Определяет, используется ли системная тёмная тема."""
    try:
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Если фон окна тёмный (lightness < 128) - тёмная тема
            return palette.window().color().lightness() < 128
    except Exception:
        pass
    return False


def apply_theme(app: QApplication, theme: str = "dark", accent_color: str = "#007aff") -> None:
    """Применяет тему к приложению."""
    qss = build_qss(theme, accent_color)
    app.setStyleSheet(qss)
