from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QColorDialog, QFileDialog,
    QLabel, QSpinBox, QMessageBox, QInputDialog,
    QGroupBox, QGridLayout, QScrollArea,
    QSizePolicy, QFrame, QSlider, QToolButton
)
from PyQt5.QtGui import QPixmap, QKeySequence, QColor, QPainter, QPen
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt, QSize

from .canvas import Canvas
from .tools import Tool


# ══════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════

class ToolBtn(QPushButton):
    """Compact square tool button with tooltip."""
    def __init__(self, label, tooltip="", checkable=True, parent=None):
        super().__init__(label, parent)
        self.setCheckable(checkable)
        self.setFixedSize(38, 38)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._base_style())

    def _base_style(self):
        return (
            "QPushButton {"
            "  background: #F8FAFC;"
            "  color: #475569;"
            "  border: 1px solid #E2E8F0;"
            "  border-radius: 6px;"
            "  font-size: 14px;"
            "  padding: 0;"
            "}"
            "QPushButton:hover {"
            "  background: #EFF6FF;"
            "  color: #1E40AF;"
            "  border-color: #2563EB;"
            "}"
            "QPushButton:checked, QPushButton:pressed {"
            "  background: #2563EB;"
            "  color: #ffffff;"
            "  border-color: #1D4ED8;"
            "}"
        )


class WideBtn(QPushButton):
    """Wider button for actions like New/Save."""
    def __init__(self, label, tooltip="", parent=None):
        super().__init__(label, parent)
        self.setFixedHeight(34)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)


class ColorSwatch(QPushButton):
    """Active color preview swatch."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("#000000")
        self.setFixedSize(42, 42)
        self.setToolTip("Pilih warna")
        self.setCursor(Qt.PointingHandCursor)
        self._refresh()

    def set_color(self, color: QColor):
        self._color = color
        self._refresh()

    def _refresh(self):
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        luma = 0.299*r + 0.587*g + 0.114*b
        border = "#7AA7FF" if luma < 200 else "#8892AA"
        self.setStyleSheet(
            f"QPushButton {{"
            f"  background: rgb({r},{g},{b});"
            f"  border: 2px solid {border};"
            f"  border-radius: 8px;"
            f"}}"
            f"QPushButton:hover {{ border-color: #ffffff; }}"
        )


class RibbonGroup(QGroupBox):
    """Labelled ribbon section card."""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(
            "QGroupBox {"
            "  background: #FFFFFF;"
            "  border: 1px solid #E2E8F0;"
            "  border-radius: 8px;"
            "  margin-top: 18px;"
            "  padding: 6px 6px 4px 6px;"
            "  color: #94A3B8;"
            "  font-size: 10px;"
            "  font-weight: 600;"
            "  letter-spacing: 0.8px;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin;"
            "  left: 8px; top: 0px;"
            "  padding: 0 4px;"
            "  background: #FFFFFF;"
            "}"
        )


class VerticalSliderPanel(QWidget):
    """Left panel with vertical size + opacity sliders."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(52)
        self.setStyleSheet("background: #F1F5F9; border-right: 1px solid #E2E8F0;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignHCenter)

        # Size slider
        lbl_size = QLabel("≡")
        lbl_size.setAlignment(Qt.AlignCenter)
        lbl_size.setStyleSheet("color:#94A3B8; font-size:16px; background:transparent;")
        lbl_size.setToolTip("Ukuran brush")

        self.size_slider = QSlider(Qt.Vertical)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(3)
        self.size_slider.setFixedHeight(200)
        self.size_slider.setToolTip("Ukuran brush  ([ / ])")
        self.size_slider.setCursor(Qt.PointingHandCursor)
        self.size_slider.setStyleSheet(self._slider_style())

        self.size_dot = QLabel("●")
        self.size_dot.setAlignment(Qt.AlignCenter)
        self.size_dot.setStyleSheet("color:#2563EB; font-size:8px; background:transparent;")
        self.size_dot.setToolTip("Ukuran brush saat ini")

        # Opacity slider
        lbl_opacity = QLabel("◑")
        lbl_opacity.setAlignment(Qt.AlignCenter)
        lbl_opacity.setStyleSheet("color:#94A3B8; font-size:16px; background:transparent;")
        lbl_opacity.setToolTip("Opacity")

        self.opacity_slider = QSlider(Qt.Vertical)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedHeight(200)
        self.opacity_slider.setToolTip("Opacity brush")
        self.opacity_slider.setCursor(Qt.PointingHandCursor)
        self.opacity_slider.setStyleSheet(self._slider_style())

        self.opacity_dot = QLabel("●")
        self.opacity_dot.setAlignment(Qt.AlignCenter)
        self.opacity_dot.setStyleSheet("color:#2563EB; font-size:8px; background:transparent;")
        self.opacity_dot.setToolTip("Opacity saat ini")

        layout.addWidget(lbl_size, alignment=Qt.AlignHCenter)
        layout.addWidget(self.size_slider, alignment=Qt.AlignHCenter)
        layout.addWidget(self.size_dot, alignment=Qt.AlignHCenter)
        layout.addSpacing(8)
        layout.addWidget(lbl_opacity, alignment=Qt.AlignHCenter)
        layout.addWidget(self.opacity_slider, alignment=Qt.AlignHCenter)
        layout.addWidget(self.opacity_dot, alignment=Qt.AlignHCenter)
        layout.addStretch()

    def _slider_style(self):
        return (
            "QSlider::groove:vertical {"
            "  width: 4px;"
            "  background: #E2E8F0;"
            "  border-radius: 2px;"
            "}"
            "QSlider::handle:vertical {"
            "  background: #2563EB;"
            "  border: 2px solid #F8FAFC;"
            "  width: 14px; height: 14px;"
            "  margin: 0 -5px;"
            "  border-radius: 7px;"
            "}"
            "QSlider::handle:vertical:hover {"
            "  background: #1D4ED8;"
            "}"
            "QSlider::sub-page:vertical {"
            "  background: #E2E8F0;"
            "  border-radius: 2px;"
            "}"
            "QSlider::add-page:vertical {"
            "  background: #2563EB;"
            "  border-radius: 2px;"
            "}"
        )


# ══════════════════════════════════════════════════════════
#  PaintTab
# ══════════════════════════════════════════════════════════

class PaintTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self._tool_buttons: dict[Tool, ToolBtn] = {}
        self.init_ui()
        self._setup_shortcuts()

    # ── Build UI ──────────────────────────────────────────

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── RIBBON ────────────────────────────────────────
        ribbon = QFrame()
        ribbon.setFixedHeight(110)
        ribbon.setStyleSheet(
            "QFrame {"
            "  background: #FFFFFF;"
            "  border-bottom: 1px solid #E2E8F0;"
            "}"
        )
        ribbon_layout = QHBoxLayout(ribbon)
        ribbon_layout.setContentsMargins(10, 4, 10, 4)
        ribbon_layout.setSpacing(6)
        ribbon_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # ── Group: File ────────────────────────────────
        grp_file = RibbonGroup("File")
        file_layout = QVBoxLayout()
        file_layout.setSpacing(3)
        file_layout.setContentsMargins(4, 2, 4, 2)

        row_f1 = QHBoxLayout(); row_f1.setSpacing(3)
        row_f2 = QHBoxLayout(); row_f2.setSpacing(3)

        btn_new  = WideBtn("New",    "New canvas  (Ctrl+N)")
        btn_open = WideBtn("Open",   "Open image  (Ctrl+O)")
        btn_save = WideBtn("Save",   "Save image  (Ctrl+S)")
        btn_resize = WideBtn("Resize", "Resize canvas")
        for b in [btn_new, btn_open, btn_save, btn_resize]:
            b.setFixedWidth(56)

        btn_undo = ToolBtn("↩", "Undo  (Ctrl+Z)", checkable=False)
        btn_redo = ToolBtn("↪", "Redo  (Ctrl+Y)", checkable=False)

        row_f1.addWidget(btn_new); row_f1.addWidget(btn_open)
        row_f1.addWidget(btn_save); row_f1.addWidget(btn_resize)
        row_f2.addWidget(btn_undo); row_f2.addWidget(btn_redo)
        row_f2.addStretch()

        file_layout.addLayout(row_f1)
        file_layout.addLayout(row_f2)
        grp_file.setLayout(file_layout)

        btn_new.clicked.connect(self.new_canvas)
        btn_open.clicked.connect(self.open_image)
        btn_save.clicked.connect(self.save_image)
        btn_resize.clicked.connect(self.resize_canvas)
        btn_undo.clicked.connect(self.canvas.undo)
        btn_redo.clicked.connect(self.canvas.redo)

        # ── Group: Tools ───────────────────────────────
        grp_tools = RibbonGroup("Tools")
        tools_grid = QGridLayout()
        tools_grid.setSpacing(3)
        tools_grid.setContentsMargins(4, 2, 4, 2)

        draw_tools = [
            ("✏",  Tool.PENCIL,  "Pencil  (P)"),
            ("🖌",  Tool.BRUSH,   "Brush  (B)"),
            ("◻",  Tool.ERASER,  "Eraser  (E)"),
            ("🪣",  Tool.FILL,    "Fill  (F)"),
            ("T",   Tool.TEXT,    "Text  (T)"),
            ("⬡",  Tool.SELECT,  "Select  (V)"),
        ]

        for i, (icon, tool, tip) in enumerate(draw_tools):
            btn = ToolBtn(icon, tip)
            btn.clicked.connect(lambda _, t=tool: self.set_tool(t))
            tools_grid.addWidget(btn, i // 3, i % 3)
            self._tool_buttons[tool] = btn

        grp_tools.setLayout(tools_grid)

        # ── Group: Brushes ─────────────────────────────
        grp_brushes = RibbonGroup("Brushes")
        brushes_layout = QVBoxLayout()
        brushes_layout.setSpacing(4)
        brushes_layout.setContentsMargins(4, 2, 4, 2)
        brushes_layout.setAlignment(Qt.AlignTop)

        # Size spin (compact)
        size_row = QHBoxLayout(); size_row.setSpacing(4)
        lbl_s = QLabel("Size")
        lbl_s.setStyleSheet("color:#94A3B8; font-size:11px; background:transparent;")
        self.size_box = QSpinBox()
        self.size_box.setRange(1, 50)
        self.size_box.setValue(3)
        self.size_box.setFixedWidth(58)
        self.size_box.setToolTip("Ukuran brush  ([ / ])")
        self.size_box.valueChanged.connect(self._on_size_spinbox)
        size_row.addWidget(lbl_s); size_row.addWidget(self.size_box)

        brushes_layout.addLayout(size_row)
        grp_brushes.setLayout(brushes_layout)

        # ── Group: Shapes ──────────────────────────────
        grp_shapes = RibbonGroup("Shapes")
        shapes_grid = QGridLayout()
        shapes_grid.setSpacing(3)
        shapes_grid.setContentsMargins(4, 2, 4, 2)

        shapes = [
            ("─",  Tool.LINE,              "Line  (L)"),
            ("▭",  Tool.RECTANGLE,         "Rectangle  (R)"),
            ("▢",  Tool.ROUNDED_RECTANGLE, "Rounded Rect"),
            ("●",  Tool.CIRCLE,            "Circle  (C)"),
            ("◉",  Tool.ELLIPSE,           "Ellipse"),
            ("▲",  Tool.TRIANGLE,          "Triangle"),
            ("◆",  Tool.DIAMOND,           "Diamond"),
            ("⬠",  Tool.PENTAGON,          "Pentagon"),
            ("⬡",  Tool.HEXAGON,           "Hexagon"),
            ("★",  Tool.STAR,              "Star  (S)"),
            ("→",  Tool.ARROW_RIGHT,       "Arrow →"),
            ("←",  Tool.ARROW_LEFT,        "Arrow ←"),
            ("↑",  Tool.ARROW_UP,          "Arrow ↑"),
            ("↓",  Tool.ARROW_DOWN,        "Arrow ↓"),
            ("~",  Tool.CURVE,             "Curve"),
        ]

        for i, (icon, tool, tip) in enumerate(shapes):
            btn = ToolBtn(icon, tip)
            btn.clicked.connect(lambda _, t=tool: self.set_tool(t))
            shapes_grid.addWidget(btn, i // 5, i % 5)
            self._tool_buttons[tool] = btn

        grp_shapes.setLayout(shapes_grid)

        # ── Group: Colour ──────────────────────────────
        grp_colour = RibbonGroup("Colour")
        colour_layout = QVBoxLayout()
        colour_layout.setContentsMargins(6, 2, 6, 2)
        colour_layout.setSpacing(4)
        colour_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.color_swatch = ColorSwatch()
        self.color_swatch.clicked.connect(self.pick_color)

        self.active_color_lbl = QLabel("●  Black")
        self.active_color_lbl.setStyleSheet(
            "color:#94A3B8; font-size:10px; background:transparent;"
        )
        self.active_color_lbl.setAlignment(Qt.AlignCenter)

        colour_layout.addWidget(self.color_swatch, alignment=Qt.AlignHCenter)
        colour_layout.addWidget(self.active_color_lbl)
        grp_colour.setLayout(colour_layout)
        # ── Group: Animation ──────────────────────────

        grp_anim = RibbonGroup("Animation")

        anim_layout = QVBoxLayout()
        anim_layout.setContentsMargins(4, 2, 4, 2)
        anim_layout.setSpacing(3)

        btn_bounce = WideBtn("Bounce")
        btn_spin = WideBtn("Spin")
        btn_pulse = WideBtn("Pulse")
        btn_stop = WideBtn("Stop")

        btn_bounce.clicked.connect(
            self.canvas.start_bounce
        )

        btn_spin.clicked.connect(
            self.canvas.start_spin
        )

        btn_pulse.clicked.connect(
            self.canvas.start_pulse
        )

        btn_stop.clicked.connect(
            self.canvas.stop_animation
        )

        anim_layout.addWidget(btn_bounce)
        anim_layout.addWidget(btn_spin)
        anim_layout.addWidget(btn_pulse)
        anim_layout.addWidget(btn_stop)

        grp_anim.setLayout(anim_layout)

        # ── Status chip ────────────────────────────────
        self.tool_chip = QLabel("✏  Pencil")
        self.tool_chip.setStyleSheet(
            "color: #2563EB;"
            "font-size: 12px;"
            "font-weight: 700;"
            "background: #EFF6FF;"
            "border: 1px solid #BFDBFE;"
            "border-radius: 12px;"
            "padding: 4px 12px;"
        )
        self.tool_chip.setAlignment(Qt.AlignCenter)
        self.tool_chip.setFixedHeight(28)

        # ── Assemble ribbon ────────────────────────────
        ribbon_layout.addWidget(grp_file)
        ribbon_layout.addWidget(grp_tools)
        ribbon_layout.addWidget(grp_brushes)
        ribbon_layout.addWidget(grp_shapes)
        ribbon_layout.addWidget(grp_colour)
        ribbon_layout.addWidget(grp_anim)
        ribbon_layout.addStretch()
        ribbon_layout.addWidget(self.tool_chip, alignment=Qt.AlignBottom)

        # ── BODY (slider panel + canvas) ──────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.slider_panel = VerticalSliderPanel()
        self.slider_panel.size_slider.valueChanged.connect(self._on_size_slider)
        self.slider_panel.opacity_slider.valueChanged.connect(self._on_opacity_slider)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: #F1F5F9; }"
        )

        body.addWidget(self.slider_panel)
        body.addWidget(self.scroll_area)

        root.addWidget(ribbon)
        root.addLayout(body, 1)

        # Default tool
        self.set_tool(Tool.PENCIL)

    # ── Events ────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, '_did_fit'):
            self._did_fit = True
            w = max(self.scroll_area.viewport().width(), 400)
            h = max(self.scroll_area.viewport().height(), 300)
            self.canvas.resize_canvas(w, h)

    # ── Shortcuts ─────────────────────────────────────────

    def _setup_shortcuts(self):
        pairs = [
            ("Ctrl+Z",       self.canvas.undo),
            ("Ctrl+Y",       self.canvas.redo),
            ("Ctrl+Shift+Z", self.canvas.redo),
            ("Ctrl+S",       self.save_image),
            ("Ctrl+O",       self.open_image),
            ("Ctrl+N",       self.new_canvas),
            ("P",  lambda: self.set_tool(Tool.PENCIL)),
            ("B",  lambda: self.set_tool(Tool.BRUSH)),
            ("E",  lambda: self.set_tool(Tool.ERASER)),
            ("F",  lambda: self.set_tool(Tool.FILL)),
            ("T",  lambda: self.set_tool(Tool.TEXT)),
            ("L",  lambda: self.set_tool(Tool.LINE)),
            ("R",  lambda: self.set_tool(Tool.RECTANGLE)),
            ("C",  lambda: self.set_tool(Tool.CIRCLE)),
            ("S",  lambda: self.set_tool(Tool.STAR)),
            ("]",  lambda: self.size_box.setValue(min(self.size_box.value() + 1, 50))),
            ("[",  lambda: self.size_box.setValue(max(self.size_box.value() - 1, 1))),
        ]
        for key, slot in pairs:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

    # ── Slider sync ───────────────────────────────────────

    def _on_size_slider(self, val):
        self.size_box.blockSignals(True)
        self.size_box.setValue(val)
        self.size_box.blockSignals(False)
        self.canvas.pen_size = val
        # Update dot size
        px = max(4, min(val // 2, 20))
        self.slider_panel.size_dot.setStyleSheet(
            f"color:#2563EB; font-size:{px}px; background:transparent;"
        )

    def _on_size_spinbox(self, val):
        self.slider_panel.size_slider.blockSignals(True)
        self.slider_panel.size_slider.setValue(val)
        self.slider_panel.size_slider.blockSignals(False)
        self.canvas.pen_size = val

    def _on_opacity_slider(self, val):
        # Store opacity; apply to pen color alpha when drawing
        alpha = int(val * 2.55)
        c = QColor(self.canvas.pen_color)
        c.setAlpha(alpha)
        self.canvas.pen_color = c
        # Update dot opacity label
        self.slider_panel.opacity_dot.setStyleSheet(
            f"color: rgba(37,99,235,{val/100}); font-size:10px; background:transparent;"
        )

    # ── Tool management ───────────────────────────────────

    def set_tool(self, tool):
        self.canvas.current_tool = tool
        for t, btn in self._tool_buttons.items():
            checked = (t == tool)
            btn.setChecked(checked)

        name = tool.name.replace("_", " ").title()
        icons = {
            Tool.PENCIL: "✏", Tool.BRUSH: "🖌", Tool.ERASER: "◻",
            Tool.FILL: "🪣", Tool.TEXT: "T", Tool.SELECT: "⬡",
            Tool.LINE: "─", Tool.RECTANGLE: "▭", Tool.CIRCLE: "●",
            Tool.STAR: "★", Tool.CURVE: "~",
        }
        ico = icons.get(tool, "◆")
        self.tool_chip.setText(f"{ico}  {name}")

    # ── Actions ───────────────────────────────────────────

    def pick_color(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self, "Pilih Warna")
        if color.isValid():
            # Preserve current opacity
            alpha = self.canvas.pen_color.alpha()
            color.setAlpha(alpha)
            self.canvas.pen_color = color
            self.color_swatch.set_color(color)
            name = color.name().upper()
            self.active_color_lbl.setText(f"●  {name}")

    def new_canvas(self):
        reply = QMessageBox.question(
            self, "New Canvas", "Bersihkan canvas?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG (*.png);;JPG (*.jpg)"
        )
        if filename:
            self.canvas.canvas.save(filename)

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if filename:
            pixmap = QPixmap(filename)
            self.canvas.canvas = pixmap.scaled(
                self.canvas.width(), self.canvas.height()
            )
            self.canvas.update()

    def resize_canvas(self):
        width, ok = QInputDialog.getInt(
            self, "Canvas Width", "Width:", self.canvas.width(), 100, 5000
        )
        if not ok:
            return
        height, ok = QInputDialog.getInt(
            self, "Canvas Height", "Height:", self.canvas.height(), 100, 5000
        )
        if not ok:
            return
        self.canvas.resize_canvas(width, height)
