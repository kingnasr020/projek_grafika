"""
paint_tab.py  —  Windows 11 Paint-inspired UI
Fluent Design · Card-based · Accessible · Vibrant Palette · Left Toolbar Slider
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QColorDialog, QFileDialog,
    QLabel, QSpinBox, QMessageBox, QInputDialog,
    QGroupBox, QScrollArea, QSizePolicy,
    QFrame, QSlider, QToolButton, QButtonGroup,
    QGraphicsDropShadowEffect, QApplication, QSplitter,
    QStatusBar
)
from PyQt5.QtGui import (
    QPixmap, QKeySequence, QColor, QPainter, QPen,
    QFont, QFontDatabase, QIcon, QPainterPath,
    QLinearGradient, QBrush, QCursor
)
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup,
    pyqtProperty, QRect, QTimer, QPoint
)
from PyQt5.QtWidgets import QShortcut

from .canvas import Canvas
from .tools import Tool


# ══════════════════════════════════════════════════════════════
#  DESIGN TOKENS  (Windows 11 Fluent / vibrant)
# ══════════════════════════════════════════════════════════════

ACCENT      = "#0067C0"        # Win11 default accent blue
ACCENT_LITE = "#CCE4F7"
ACCENT_DARK = "#004E94"
SURFACE     = "#F3F3F3"        # Win11 mica-like surface
CARD_BG     = "#FFFFFF"
CARD_BORDER = "#E0E0E0"
ICON_FG     = "#202020"
TEXT_MUTED  = "#666666"
HOVER_BG    = "#E5E5E5"
ACTIVE_BG   = "#D9EBFA"
ACTIVE_FG   = "#003C87"
RADIUS_SM   = "6px"
RADIUS_MD   = "8px"
RADIUS_LG   = "12px"

# Vibrant palette — 40 colours, curated bright/saturated
PALETTE_COLORS = [
    # Row 1 — Warm spectrum
    "#FF1744", "#FF5722", "#FF9100", "#FFCA28", "#FFE57F",
    "#FFEB3B", "#C6FF00", "#76FF03", "#00E676", "#1DE9B6",
    # Row 2 — Cool spectrum
    "#00E5FF", "#00B0FF", "#2979FF", "#3D5AFE", "#651FFF",
    "#D500F9", "#FF1744", "#FF4081", "#F50057", "#EC407A",
    # Row 3 — Pastels
    "#FFCDD2", "#FFE0B2", "#FFF9C4", "#DCEDC8", "#B2EBF2",
    "#BBDEFB", "#E1BEE7", "#F8BBD0", "#D7CCC8", "#CFD8DC",
    # Row 4 — Deep / dark
    "#B71C1C", "#BF360C", "#E65100", "#F57F17", "#1B5E20",
    "#006064", "#0D47A1", "#311B92", "#880E4F", "#212121",
    # Row 5 — Neutrals + metallic
    "#FFFFFF", "#F5F5F5", "#BDBDBD", "#757575", "#424242",
    "#000000", "#795548", "#607D8B", "#546E7A", "#37474F",
]


# ══════════════════════════════════════════════════════════════
#  FLUENT TOOL BUTTON
# ══════════════════════════════════════════════════════════════

class FluentToolButton(QPushButton):
    """Icon + label pill button with Fluent hover/active micro-interactions."""

    def __init__(self, icon_char: str, label: str, tool: Tool,
                 shortcut_hint: str = "", parent=None):
        super().__init__(parent)
        self.tool = tool
        self._icon_char = icon_char
        self._label = label
        self._shortcut_hint = shortcut_hint
        self._active = False

        self.setCheckable(True)
        self.setFixedHeight(52)
        self.setMinimumWidth(64)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(f"{label}  {shortcut_hint}" if shortcut_hint else label)
        # Accessibility
        self.setAccessibleName(label)
        self.setAccessibleDescription(f"Select {label} tool")
        self._apply_style(False)

    def _apply_style(self, active: bool):
        bg   = ACTIVE_BG   if active else "transparent"
        fg   = ACTIVE_FG   if active else ICON_FG
        bord = ACCENT      if active else "transparent"
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: 2px solid {bord};
                border-radius: {RADIUS_MD};
                padding: 4px 6px 2px 6px;
                color: {fg};
                font-size: 11px;
                font-weight: {'600' if active else '400'};
                text-align: center;
            }}
            QPushButton:hover:!checked {{
                background: {HOVER_BG};
                border: 2px solid {CARD_BORDER};
            }}
            QPushButton:checked {{
                background: {ACTIVE_BG};
                border: 2px solid {ACCENT};
                color: {ACTIVE_FG};
                font-weight: 600;
            }}
            QPushButton:focus {{
                outline: none;
                border: 2px solid {ACCENT};
                box-shadow: 0 0 0 3px {ACCENT_LITE};
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        active = self.isChecked()
        color  = QColor(ACTIVE_FG if active else ICON_FG)

        icon_font = QFont("Segoe Fluent Icons", 18)
        if not icon_font.exactMatch():
            icon_font = QFont("Segoe MDL2 Assets", 18)
        if not icon_font.exactMatch():
            icon_font = QFont("Arial", 14)

        icon_font.setPointSize(16)
        painter.setFont(icon_font)
        painter.setPen(color)
        icon_rect = QRect(0, 4, self.width(), 26)
        painter.drawText(icon_rect, Qt.AlignHCenter | Qt.AlignVCenter,
                         self._icon_char)

        lbl_font = QFont("Segoe UI Variable", 9)
        if not lbl_font.exactMatch():
            lbl_font = QFont("Segoe UI", 9)
        lbl_font.setWeight(QFont.SemiBold if active else QFont.Normal)
        painter.setFont(lbl_font)
        lbl_rect = QRect(0, 28, self.width(), 20)
        painter.drawText(lbl_rect, Qt.AlignHCenter | Qt.AlignVCenter,
                         self._label)
        painter.end()


# ══════════════════════════════════════════════════════════════
#  COLOR SWATCH
# ══════════════════════════════════════════════════════════════

class ColorSwatch(QPushButton):
    """Single colour swatch — square with hover ring."""

    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.hex_color = hex_color
        self.setFixedSize(26, 26)
        self.setMaximumHeight(120)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(hex_color)
        self.setAccessibleName(f"Color {hex_color}")
        self._apply_style()

    def _apply_style(self):
        border = "#888" if self.hex_color in ("#FFFFFF", "#F5F5F5", "#FFF9C4",
                                               "#FFEB3B", "#FFCA28", "#FFE57F") \
                        else self.hex_color
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self.hex_color};
                border: 2px solid transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid {ACCENT};
                border-radius: 6px;
            }}
            QPushButton:focus {{
                border: 3px solid {ACCENT};
            }}
        """)


# ══════════════════════════════════════════════════════════════
#  SECTION CARD  (collapsible group box replacement)
# ══════════════════════════════════════════════════════════════

def _card(title: str = "") -> tuple[QFrame, QVBoxLayout]:
    """Returns (frame, inner_layout) — a styled card."""
    frame = QFrame()
    frame.setObjectName("toolCard")
    frame.setStyleSheet(f"""
        QFrame#toolCard {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: {RADIUS_LG};
        }}
    """)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(10, 8, 10, 10)
    layout.setSpacing(6)
    if title:
        lbl = QLabel(title)
        lbl.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        """)  # Section header role
        layout.addWidget(lbl)
    return frame, layout


# ══════════════════════════════════════════════════════════════
#  LEFT SIDEBAR  (vertical tool panel)
# ══════════════════════════════════════════════════════════════

class LeftSidebar(QWidget):
    """Vertical scrollable left panel — tools, size slider, color active."""

    toolSelected = None   # set from PaintTab after init

    def __init__(self, canvas: Canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setFixedWidth(80)
        self.setAccessibleName("Tool sidebar")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(6)

        # ---- Active colour indicator ----
        color_card, color_layout = _card()
        color_layout.setContentsMargins(6, 6, 6, 6)
        self.active_color_btn = QPushButton()
        self.active_color_btn.setFixedSize(48, 48)
        self.active_color_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.active_color_btn.setToolTip("Active color — click to change")
        self.active_color_btn.setAccessibleName("Active color picker")
        self._set_active_color_style(QColor("#000000"))
        self.active_color_btn.clicked.connect(self._pick_color)
        color_layout.addWidget(self.active_color_btn, alignment=Qt.AlignHCenter)
        outer.addWidget(color_card)

        # ---- Size slider ----
        size_card, size_layout = _card("SIZE")
        self.size_slider = QSlider(Qt.Vertical)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(3)
        self.size_slider.setFixedHeight(120)
        self.size_slider.setTickPosition(QSlider.TicksBothSides)
        self.size_slider.setTickInterval(10)
        self.size_slider.setAccessibleName("Brush size")
        self.size_slider.setToolTip("Brush / pen size")
        self.size_slider.setStyleSheet(f"""
            QSlider::groove:vertical {{
                background: {CARD_BORDER};
                width: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:vertical {{
                background: {ACCENT};
                border: 2px solid white;
                width: 18px; height: 18px;
                margin: 0 -6px;
                border-radius: 9px;
            }}
            QSlider::sub-page:vertical {{
                background: {ACCENT_LITE};
                width: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:vertical:hover {{
                background: {ACCENT_DARK};
            }}
        """)
        self.size_slider.valueChanged.connect(self._on_size_change)

        self.size_label = QLabel("3 px")
        self.size_label.setAlignment(Qt.AlignHCenter)
        self.size_label.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; font-weight: 600;")
        self.size_label.setAccessibleName("Current brush size")

        size_layout.addWidget(self.size_slider, alignment=Qt.AlignHCenter)
        size_layout.addWidget(self.size_label)
        outer.addWidget(size_card)

        # ---- Tool buttons (scrollable) ----
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        tool_container = QWidget()
        tool_container.setStyleSheet("background: transparent;")
        tool_grid = QGridLayout(tool_container)
        tool_grid.setContentsMargins(0, 0, 0, 0)
        tool_grid.setSpacing(4)

        # (unicode_char, label, Tool, shortcut)
        tools = [
            ("✏️", "Pencil",  Tool.PENCIL,  "P"),
            ("🖌️", "Brush",   Tool.BRUSH,   "B"),
            ("⬜", "Eraser",  Tool.ERASER,  "E"),
            ("🪣", "Fill",    Tool.FILL,    "F"),
            ("📝", "Text",    Tool.TEXT,    "T"),
            ("➡️", "Select",  Tool.SELECT,  ""),
            ("📏", "Line",    Tool.LINE,    "L"),
            ("▭",  "Rect",   Tool.RECTANGLE, "R"),
            ("▢",  "Rounded",Tool.ROUNDED_RECTANGLE,""),
            ("○",  "Circle", Tool.CIRCLE,   "C"),
            ("⬭",  "Ellipse",Tool.ELLIPSE,  ""),
            ("△",  "Triangle",Tool.TRIANGLE,""),
            ("◇",  "Diamond", Tool.DIAMOND, ""),
            ("⬠",  "Pentagon",Tool.PENTAGON,""),
            ("⬡",  "Hexagon", Tool.HEXAGON, ""),
            ("★",  "Star",    Tool.STAR,    "S"),
            ("→",  "Arrow→",  Tool.ARROW_RIGHT,""),
            ("←",  "Arrow←",  Tool.ARROW_LEFT, ""),
            ("↑",  "Arrow↑",  Tool.ARROW_UP,   ""),
            ("↓",  "Arrow↓",  Tool.ARROW_DOWN, ""),
            ("〜", "Curve",   Tool.CURVE,      ""),
        ]

        self._tool_btn_group = QButtonGroup(self)
        self._tool_btn_group.setExclusive(True)
        self._tool_buttons: dict[Tool, QPushButton] = {}

        for idx, (icon, label, tool, sc) in enumerate(tools):
            btn = self._make_sidebar_tool_btn(icon, label, tool, sc)
            row, col = divmod(idx, 1)
            tool_grid.addWidget(btn, row, col)
            self._tool_btn_group.addButton(btn)
            self._tool_buttons[tool] = btn

        scroll.setWidget(tool_container)
        outer.addWidget(scroll, stretch=1)

    def _make_sidebar_tool_btn(self, icon, label, tool, sc):
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setFixedHeight(44)
        btn.setMinimumWidth(62)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setToolTip(f"{label}  [{sc}]" if sc else label)
        btn.setAccessibleName(f"{label} tool")
        sc_part = f"  [{sc}]" if sc else ""
        btn.setText(f"{icon}  {label}{sc_part}")
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1.5px solid transparent;
                border-radius: {RADIUS_MD};
                padding: 4px 8px;
                font-size: 11px;
                color: {ICON_FG};
                text-align: left;
            }}
            QPushButton:hover:!checked {{
                background: {HOVER_BG};
                border: 1.5px solid {CARD_BORDER};
            }}
            QPushButton:checked {{
                background: {ACTIVE_BG};
                border: 1.5px solid {ACCENT};
                color: {ACTIVE_FG};
                font-weight: 600;
            }}
            QPushButton:focus {{
                border: 2px solid {ACCENT};
            }}
        """)
        btn.setProperty("tool", tool)
        btn.clicked.connect(lambda _, t=tool: self._tool_clicked(t))
        return btn

    def _tool_clicked(self, tool: Tool):
        self.canvas.current_tool = tool
        if self.toolSelected:
            self.toolSelected(tool)

    def _on_size_change(self, val: int):
        self.canvas.pen_size = val
        self.size_label.setText(f"{val} px")

    def _pick_color(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self,
                                      "Choose Color",
                                      QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.canvas.pen_color = color
            self._set_active_color_style(color)

    def _set_active_color_style(self, color: QColor):
        hex_c = color.name()
        contrast = "#FFFFFF" if color.lightness() < 128 else "#000000"
        self.active_color_btn.setStyleSheet(f"""
            QPushButton {{
                background: {hex_c};
                border: 3px solid white;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                border: 3px solid {ACCENT};
            }}
        """)

    def sync_active_color(self, color: QColor):
        self._set_active_color_style(color)

    def set_active_tool(self, tool: Tool):
        btn = self._tool_buttons.get(tool)
        if btn:
            btn.setChecked(True)

    def set_size(self, val: int):
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(val)
        self.size_slider.blockSignals(False)
        self.size_label.setText(f"{val} px")


# ══════════════════════════════════════════════════════════════
#  ANIMATION PANEL CARD
# ══════════════════════════════════════════════════════════════

class AnimationPanel(QFrame):
    def __init__(self, canvas: Canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setObjectName("animCard")
        self.setStyleSheet(f"""
            QFrame#animCard {{
                background: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: {RADIUS_LG};
            }}
        """)
        self.setVisible(False)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        icon = QLabel("✨")
        icon.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon)

        self.status = QLabel("Area terpilih — pilih efek animasi")
        self.status.setStyleSheet(f"font-size: 11px; color: {ACCENT}; font-weight: 600;")
        self.status.setAccessibleName("Animation status")
        layout.addWidget(self.status)

        layout.addStretch()

        anim_defs = [
            ("🏀", "Bounce",  "bounce",  "#E67E22"),
            ("💗", "Pulse",   "pulse",   "#E74C3C"),
            ("🌀", "Spin",    "spin",    "#8E44AD"),
        ]
        self._anim_btns: dict[str, QPushButton] = {}
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(False)

        for icon_c, label, mode, color in anim_defs:
            btn = QPushButton(f"{icon_c}  {label}")
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setAccessibleName(f"{label} animation")
            btn.setToolTip(f"Apply {label} animation to selection")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 2px solid {color};
                    border-radius: 16px;
                    padding: 2px 14px;
                    color: {color};
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {color}22;
                }}
                QPushButton:checked {{
                    background: {color};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda _, m=mode, b=btn: self._toggle(m, b))
            self._anim_btns[mode] = btn
            layout.addWidget(btn)
            self._btn_group.addButton(btn)

        stop_btn = QPushButton("⏹  Stop")
        stop_btn.setFixedHeight(32)
        stop_btn.setCursor(QCursor(Qt.PointingHandCursor))
        stop_btn.setAccessibleName("Stop animation")
        stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE};
                border: 1.5px solid {CARD_BORDER};
                border-radius: 16px;
                padding: 2px 12px;
                font-size: 12px;
                color: {ICON_FG};
            }}
            QPushButton:hover {{ background: {HOVER_BG}; }}
        """)
        stop_btn.clicked.connect(self.stop)
        layout.addWidget(stop_btn)

    def _toggle(self, mode: str, btn: QPushButton):
        for m, b in self._anim_btns.items():
            if b is not btn:
                b.setChecked(False)
        if btn.isChecked():
            self.canvas.start_animation(mode)
            self.status.setText(f"▶  {mode.capitalize()} berjalan...")
        else:
            self.stop()

    def stop(self):
        for b in self._anim_btns.values():
            b.setChecked(False)
        self.canvas.stop_animation()
        self.status.setText("Area terpilih — pilih efek animasi")

    def on_selection(self, has_sel: bool):
        self.setVisible(has_sel)
        if not has_sel:
            self.stop()


# ══════════════════════════════════════════════════════════════
#  COLOR PALETTE PANEL
# ══════════════════════════════════════════════════════════════

class ColorPalettePanel(QFrame):
    def __init__(self, canvas: Canvas, sidebar: LeftSidebar, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.canvas  = canvas
        self.sidebar = sidebar
        self.setObjectName("paletteCard")
        self.setStyleSheet(f"""
            QFrame#paletteCard {{
                background: {CARD_BG};
                border: 1px solid {CARD_BORDER};
                border-radius: {RADIUS_LG};
            }}
        """)
        self.setAccessibleName("Color palette")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        hdr = QHBoxLayout()
        title = QLabel("COLORS")
        title.setStyleSheet(f"color:{TEXT_MUTED};font-size:10px;font-weight:600;letter-spacing:0.8px;")
        hdr.addWidget(title)
        hdr.addStretch()
        custom_btn = QPushButton("+ Custom")
        custom_btn.setFixedHeight(22)
        custom_btn.setCursor(QCursor(Qt.PointingHandCursor))
        custom_btn.setAccessibleName("Open custom color dialog")
        custom_btn.setToolTip("Open color picker dialog")
        custom_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {ACCENT};
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 10px;
                color: {ACCENT};
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {ACCENT_LITE}; }}
        """)
        custom_btn.clicked.connect(self._custom_color)
        hdr.addWidget(custom_btn)
        layout.addLayout(hdr)

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        cols = 12
        for i, hex_c in enumerate(PALETTE_COLORS):
            row, col = divmod(i, cols)
            swatch = ColorSwatch(hex_c, self)
            swatch.clicked.connect(lambda _, c=hex_c: self._swatch_clicked(c))
            grid.addWidget(swatch, row, col)

        layout.addWidget(grid_widget)

    def _swatch_clicked(self, hex_c: str):
        color = QColor(hex_c)
        self.canvas.pen_color = color
        self.sidebar.sync_active_color(color)

    def _custom_color(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self,
                                      "Choose Color",
                                      QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.canvas.pen_color = color
            self.sidebar.sync_active_color(color)


# ══════════════════════════════════════════════════════════════
#  TITLE BAR  (Win11 style)
# ══════════════════════════════════════════════════════════════

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setAccessibleName("Application title bar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        app_icon = QLabel("🎨")
        app_icon.setStyleSheet("font-size: 18px;")
        app_icon.setAccessibleName("Paint application icon")
        layout.addWidget(app_icon)

        title = QLabel("Paint")
        title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {ICON_FG};
            font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        """)
        title.setAccessibleName("Paint application")
        layout.addWidget(title)
        layout.addStretch()


# ══════════════════════════════════════════════════════════════
#  COMMAND BAR  (top ribbon — file + history)
# ══════════════════════════════════════════════════════════════

def _cmd_btn(icon: str, label: str, shortcut: str = "") -> QPushButton:
    btn = QPushButton()
    tip = f"{label}  {shortcut}" if shortcut else label
    btn.setToolTip(tip)
    btn.setAccessibleName(label)
    btn.setFixedHeight(36)
    btn.setText(f"{icon}  {label}")
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: {RADIUS_MD};
            padding: 2px 12px;
            font-size: 12px;
            color: {ICON_FG};
        }}
        QPushButton:hover {{
            background: {HOVER_BG};
            border: 1px solid {CARD_BORDER};
        }}
        QPushButton:pressed {{
            background: {ACTIVE_BG};
        }}
        QPushButton:focus {{
            border: 2px solid {ACCENT};
        }}
    """)
    return btn


# ══════════════════════════════════════════════════════════════
#  STATUS BAR
# ══════════════════════════════════════════════════════════════

class PaintStatusBar(QWidget):
    def __init__(self, canvas: Canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setFixedHeight(24)
        self.setAccessibleName("Status bar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)

        self.pos_label = QLabel("0, 0")
        self.size_label = QLabel("1000 × 700")
        self.tool_label = QLabel("Pencil")

        for lbl in [self.pos_label, self.size_label, self.tool_label]:
            lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
            layout.addWidget(lbl)

        layout.addStretch()

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {CARD_BORDER};")
        layout.addWidget(sep)

        zoom_lbl = QLabel("100%")
        zoom_lbl.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED};")
        zoom_lbl.setAccessibleName("Zoom level 100 percent")
        layout.addWidget(zoom_lbl)

    def update_tool(self, tool: Tool):
        self.tool_label.setText(tool.name.title())
        self.tool_label.setAccessibleName(f"Current tool: {tool.name.title()}")

    def update_canvas_size(self, w: int, h: int):
        self.size_label.setText(f"{w} × {h}")


# ══════════════════════════════════════════════════════════════
#  MAIN PAINT TAB
# ══════════════════════════════════════════════════════════════

class PaintTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self._init_ui()
        self._setup_shortcuts()

    def _init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: {SURFACE};
                font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
            }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {SURFACE};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {CARD_BORDER};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {TEXT_MUTED};
            }}
            QScrollBar:horizontal {{
                background: {SURFACE};
                height: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {CARD_BORDER};
                border-radius: 4px;
                min-width: 30px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Title bar ──
        self.title_bar = TitleBar(self)
        self.title_bar.setStyleSheet(f"""
            background: {CARD_BG};
            border-bottom: 1px solid {CARD_BORDER};
        """)
        root.addWidget(self.title_bar)

        # ── Command bar ──
        cmd_bar = self._build_command_bar()
        root.addWidget(cmd_bar)

        # ── Body: sidebar + canvas area ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.sidebar = LeftSidebar(self.canvas, self)
        self.sidebar.toolSelected = self._on_tool_selected
        self.sidebar.setStyleSheet(f"""
            background: {CARD_BG};
            border-right: 1px solid {CARD_BORDER};
        """)
        body.addWidget(self.sidebar)

        # Canvas column
        canvas_col = QVBoxLayout()
        canvas_col.setContentsMargins(8, 8, 8, 0)
        canvas_col.setSpacing(6)

        # Anim panel (hidden until selection)
        self.anim_panel = AnimationPanel(self.canvas, self)
        canvas_col.addWidget(self.anim_panel)

        # Colour palette card
        self.palette_panel = ColorPalettePanel(self.canvas, self.sidebar, self)
        canvas_col.addWidget(self.palette_panel)

        # Canvas scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: {SURFACE};
                border: 1px solid {CARD_BORDER};
                border-radius: {RADIUS_LG};
            }}
        """)
        canvas_col.addWidget(self.scroll_area, stretch=1)

        body.addLayout(canvas_col, stretch=1)
        root.addLayout(body, stretch=1)

        # ── Status bar ──
        self.status_bar = PaintStatusBar(self.canvas, self)
        self.status_bar.setStyleSheet(f"""
            background: {CARD_BG};
            border-top: 1px solid {CARD_BORDER};
        """)
        root.addWidget(self.status_bar)

        # Wire canvas → tab
        self.canvas._notify_selection_changed = self._on_canvas_selection

        # Set default tool highlight
        self.sidebar.set_active_tool(Tool.PENCIL)

    # ── Command bar ──────────────────────────────────────────

    def _build_command_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("cmdBar")
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"""
            QFrame#cmdBar {{
                background: {CARD_BG};
                border-bottom: 1px solid {CARD_BORDER};
            }}
        """)
        bar.setAccessibleName("Command bar")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # File group
        file_frame, file_layout = _card()
        file_layout.setContentsMargins(4, 4, 4, 4)
        file_frame.setStyleSheet("")  # override card style for inline
        file_h = QHBoxLayout()
        file_h.setSpacing(2)
        file_frame_inner = QFrame()
        file_frame_inner.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE};
                border: 1px solid {CARD_BORDER};
                border-radius: {RADIUS_MD};
            }}
        """)
        fif_layout = QHBoxLayout(file_frame_inner)
        fif_layout.setContentsMargins(4, 2, 4, 2)
        fif_layout.setSpacing(2)

        for icon, label, sc, slot in [
            ("📄", "New",    "Ctrl+N", self.new_canvas),
            ("📂", "Open",   "Ctrl+O", self.open_image),
            ("💾", "Save",   "Ctrl+S", self.save_image),
            ("📐", "Resize", "",       self.resize_canvas),
        ]:
            b = _cmd_btn(icon, label, sc)
            b.clicked.connect(slot)
            fif_layout.addWidget(b)

        layout.addWidget(file_frame_inner)
        layout.addSpacing(8)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(28)
        sep.setStyleSheet(f"color: {CARD_BORDER};")
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Undo / Redo
        hist_frame = QFrame()
        hist_frame.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE};
                border: 1px solid {CARD_BORDER};
                border-radius: {RADIUS_MD};
            }}
        """)
        hist_layout = QHBoxLayout(hist_frame)
        hist_layout.setContentsMargins(4, 2, 4, 2)
        hist_layout.setSpacing(2)

        for icon, label, sc, slot in [
            ("↩", "Undo", "Ctrl+Z", self.canvas.undo),
            ("↪", "Redo", "Ctrl+Y", self.canvas.redo),
        ]:
            b = _cmd_btn(icon, label, sc)
            b.clicked.connect(slot)
            hist_layout.addWidget(b)

        layout.addWidget(hist_frame)
        layout.addStretch()

        # Tool label (right aligned)
        self.cmd_tool_label = QLabel("✏️  Pencil")
        self.cmd_tool_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {ACCENT};
            padding: 4px 12px;
            background: {ACTIVE_BG};
            border-radius: 14px;
        """)
        self.cmd_tool_label.setAccessibleName("Currently active tool indicator")
        layout.addWidget(self.cmd_tool_label)

        return bar

    # ── Callbacks ────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, '_did_fit'):
            self._did_fit = True
            self._fit_canvas()

    def _fit_canvas(self):
        w = max(self.scroll_area.viewport().width(), 400)
        h = max(self.scroll_area.viewport().height(), 300)
        self.canvas.resize_canvas(w, h)
        self.status_bar.update_canvas_size(w, h)

    def _on_tool_selected(self, tool: Tool):
        icons = {
            Tool.PENCIL: "✏️",   Tool.BRUSH: "🖌️",  Tool.ERASER: "⬜",
            Tool.FILL: "🪣",     Tool.TEXT: "📝",   Tool.SELECT: "➡️",
            Tool.LINE: "📏",     Tool.RECTANGLE: "▭", Tool.CIRCLE: "○",
            Tool.STAR: "★",      Tool.CURVE: "〜",
        }
        icon = icons.get(tool, "🖊️")
        self.cmd_tool_label.setText(f"{icon}  {tool.name.title()}")
        self.cmd_tool_label.setAccessibleName(f"Active tool: {tool.name.title()}")
        self.status_bar.update_tool(tool)

    def _on_canvas_selection(self, has_sel: bool):
        self.anim_panel.on_selection(has_sel)

    def on_selection_changed(self, has_sel: bool):
        self.anim_panel.on_selection(has_sel)

    # ── Shortcuts ────────────────────────────────────────────

    def _setup_shortcuts(self):
        bindings = [
            ("Ctrl+Z",       self.canvas.undo),
            ("Ctrl+Y",       self.canvas.redo),
            ("Ctrl+Shift+Z", self.canvas.redo),
            ("Ctrl+S",       self.save_image),
            ("Ctrl+O",       self.open_image),
            ("Ctrl+N",       self.new_canvas),
            ("P",  lambda: self._set_tool(Tool.PENCIL)),
            ("B",  lambda: self._set_tool(Tool.BRUSH)),
            ("E",  lambda: self._set_tool(Tool.ERASER)),
            ("F",  lambda: self._set_tool(Tool.FILL)),
            ("T",  lambda: self._set_tool(Tool.TEXT)),
            ("L",  lambda: self._set_tool(Tool.LINE)),
            ("R",  lambda: self._set_tool(Tool.RECTANGLE)),
            ("C",  lambda: self._set_tool(Tool.CIRCLE)),
            ("S",  lambda: self._set_tool(Tool.STAR)),
            ("]",  lambda: self._adj_size(+1)),
            ("[",  lambda: self._adj_size(-1)),
            ("Escape", self._on_escape),
        ]
        for key, slot in bindings:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

    def _set_tool(self, tool: Tool):
        self.canvas.current_tool = tool
        self.sidebar.set_active_tool(tool)
        self._on_tool_selected(tool)

    def _adj_size(self, delta: int):
        new_val = max(1, min(50, self.canvas.pen_size + delta))
        self.canvas.pen_size = new_val
        self.sidebar.set_size(new_val)

    def _on_escape(self):
        self.anim_panel.stop()
        self.canvas._select_rect.setRect(0, 0, 0, 0)
        self.anim_panel.on_selection(False)
        self.canvas.update()

    # ── File actions ─────────────────────────────────────────

    def new_canvas(self):
        reply = QMessageBox.question(self, "New Canvas",
                                     "Hapus canvas dan mulai baru?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
        if filename:
            self.canvas.canvas.save(filename)

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            pix = QPixmap(filename)
            self.canvas.canvas = pix.scaled(
                self.canvas.width(), self.canvas.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.canvas.update()

    def resize_canvas(self):
        w, ok = QInputDialog.getInt(self, "Canvas Width", "Width (px):",
                                    self.canvas.width(), 100, 8000)
        if not ok:
            return
        h, ok = QInputDialog.getInt(self, "Canvas Height", "Height (px):",
                                    self.canvas.height(), 100, 8000)
        if not ok:
            return
        self.canvas.resize_canvas(w, h)
        self.status_bar.update_canvas_size(w, h)