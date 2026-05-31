# ============================================================
#  Grafika Studio — Light Minimal Theme
# ============================================================

ACCENT       = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
ACCENT_PRESS = "#1E40AF"
ACCENT_LIGHT = "#EFF6FF"

BG_BASE      = "#F8FAFC"
BG_SURFACE   = "#FFFFFF"
BG_ELEVATED  = "#F1F5F9"
BG_INPUT     = "#F8FAFC"
BG_BORDER    = "#E2E8F0"

TEXT_PRIMARY  = "#0F172A"
TEXT_SECONDARY= "#475569"
TEXT_MUTED    = "#94A3B8"

DARK_MAROON = f"""
QMainWindow, QWidget {{
    background-color: {BG_BASE};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}

QMenuBar {{
    background: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    border-bottom: 1px solid {BG_BORDER};
    padding: 2px 4px;
}}
QMenuBar::item {{
    padding: 4px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {ACCENT_LIGHT};
    color: {ACCENT};
}}
QMenu {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BG_BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {ACCENT};
    color: #ffffff;
}}

QTabWidget::pane {{
    border: none;
    background: {BG_BASE};
    border-top: 1px solid {BG_BORDER};
}}
QTabBar {{
    background: {BG_SURFACE};
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 10px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: 500;
    min-width: 100px;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    color: {TEXT_SECONDARY};
    background: {BG_ELEVATED};
}}

QPushButton {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    border: 1px solid {BG_BORDER};
    border-radius: 6px;
    padding: 5px 14px;
    min-height: 28px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT_LIGHT};
    color: {ACCENT};
}}
QPushButton[class="primary"] {{
    background-color: {ACCENT};
    color: #ffffff;
    border: none;
    font-weight: 600;
}}
QPushButton[class="primary"]:hover {{
    background-color: {ACCENT_HOVER};
    border: none;
}}

QGroupBox {{
    background: {BG_SURFACE};
    border: 1px solid {BG_BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    color: {TEXT_MUTED};
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    top: -1px;
    padding: 0 6px;
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
}}

QSpinBox {{
    background: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BG_BORDER};
    border-radius: 6px;
    padding: 4px 8px;
    selection-background-color: {ACCENT};
}}
QSpinBox:focus {{
    border-color: {ACCENT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {BG_ELEVATED};
    border: none;
    width: 18px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {ACCENT};
}}

QComboBox {{
    background: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BG_BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    min-width: 130px;
}}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox:hover {{ border-color: {TEXT_MUTED}; }}
QComboBox::drop-down {{ border: none; background: transparent; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BG_BORDER};
    border-radius: 6px;
    selection-background-color: {ACCENT};
    outline: none;
    padding: 4px;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {BG_BORDER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    border: 2px solid {BG_SURFACE};
    width: 16px; height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: {ACCENT_HOVER};
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

QScrollArea {{
    border: 1px solid {BG_BORDER};
    border-radius: 8px;
    background: {BG_BASE};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {BG_BORDER};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}

QLabel {{
    color: {TEXT_SECONDARY};
    background: transparent;
}}

QStatusBar {{
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
    border-top: 1px solid {BG_BORDER};
    font-size: 12px;
    padding: 2px 8px;
}}

QFrame[class="toolbar-card"] {{
    background: {BG_SURFACE};
    border: 1px solid {BG_BORDER};
    border-radius: 10px;
    padding: 4px;
}}

QToolTip {{
    background: {TEXT_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}}
"""
