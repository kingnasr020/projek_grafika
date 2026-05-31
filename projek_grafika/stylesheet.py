# Windows 11 Paint - light theme
PAINT_LIGHT = """
QMainWindow, QWidget {
    background-color: #F3F3F3;
    color: #1A1A1A;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}

QTabWidget::pane {
    border: none;
    background: #F3F3F3;
}
QTabBar::tab {
    background: #E8E8E8;
    color: #444;
    padding: 5px 16px;
    border: 1px solid #D0D0D0;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    min-width: 90px;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #000000;
    font-weight: 600;
    border-bottom: 2px solid #0067C0;
}
QTabBar::tab:hover:!selected {
    background: #EFEFEF;
}

QPushButton {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    padding: 3px 10px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #E5F0FB;
    border-color: #0067C0;
}
QPushButton:pressed {
    background-color: #CCE4F7;
}

QGroupBox {
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    margin-top: 6px;
    padding-top: 4px;
    color: #333;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}

QSpinBox {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    padding: 2px 4px;
}

QComboBox {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    padding: 3px 8px;
    min-width: 100px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #1A1A1A;
    selection-background-color: #CCE4F7;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #C0C0C0;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #0067C0;
    border: 1px solid #0067C0;
    width: 14px; height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #0067C0;
    border-radius: 2px;
}

QScrollArea {
    border: 1px solid #C8C8C8;
    background: #808080;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #F0F0F0;
    width: 10px; height: 10px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #B0B0B0;
    border-radius: 4px;
    min-height: 20px;
}

QLabel { color: #1A1A1A; }

QMenuBar {
    background: #F3F3F3;
    color: #1A1A1A;
    border-bottom: 1px solid #D0D0D0;
}
QMenuBar::item:selected {
    background: #CCE4F7;
    color: #000;
}
QMenu {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #D0D0D0;
}
QMenu::item:selected { background: #CCE4F7; }

QStatusBar {
    background: #F3F3F3;
    color: #555;
    border-top: 1px solid #D0D0D0;
}
"""

# Keep old name as alias
DARK_MAROON = PAINT_LIGHT
