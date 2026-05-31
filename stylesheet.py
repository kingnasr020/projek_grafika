DARK_MAROON = """
QMainWindow, QWidget {
    background-color: #0d1117;
    color: #cdd9e5;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #1f6feb;
    background: #0d1117;
}
QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 6px 18px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
}
QTabBar::tab:selected {
    background: #1f6feb;
    color: #ffffff;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #1c2a3a;
    color: #cdd9e5;
}

QPushButton {
    background-color: #161b22;
    color: #cdd9e5;
    border: 1px solid #30363d;
    border-radius: 5px;
    padding: 4px 12px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1f6feb;
    color: #ffffff;
    border-color: #388bfd;
}
QPushButton:pressed {
    background-color: #1158c7;
    border-color: #1f6feb;
}

QGroupBox {
    border: 1px solid #21262d;
    border-radius: 6px;
    margin-top: 6px;
    padding-top: 4px;
    color: #58a6ff;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}

QSpinBox {
    background: #161b22;
    color: #cdd9e5;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 4px;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: #21262d;
    border: none;
}

QComboBox {
    background: #161b22;
    color: #cdd9e5;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 3px 8px;
    min-width: 120px;
}
QComboBox::drop-down {
    border: none;
    background: #21262d;
}
QComboBox QAbstractItemView {
    background: #161b22;
    color: #cdd9e5;
    selection-background-color: #1f6feb;
}

QSlider::groove:horizontal {
    height: 5px;
    background: #21262d;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #1f6feb;
    border: 1px solid #388bfd;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #1f6feb;
    border-radius: 2px;
}

QScrollArea {
    border: 1px solid #21262d;
    background: #010409;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #161b22;
    width: 10px;
    height: 10px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #30363d;
    border-radius: 4px;
    min-height: 20px;
}

QLabel {
    color: #8b949e;
}

QMenuBar {
    background: #161b22;
    color: #cdd9e5;
    border-bottom: 1px solid #21262d;
}
QMenuBar::item:selected {
    background: #1f6feb;
    color: #ffffff;
}
QMenu {
    background: #161b22;
    color: #cdd9e5;
    border: 1px solid #30363d;
}
QMenu::item:selected {
    background: #1f6feb;
}

QStatusBar {
    background: #161b22;
    color: #8b949e;
    border-top: 1px solid #21262d;
}
"""