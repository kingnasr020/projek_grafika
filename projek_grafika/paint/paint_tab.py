"""
paint_tab.py — Windows 11 Paint UI clone (FULL WHITE + FULLSCREEN CANVAS)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QColorDialog, QFileDialog,
    QLabel, QSpinBox, QMessageBox, QInputDialog,
    QScrollArea, QSizePolicy, QFrame, QSlider,
    QButtonGroup, QApplication, QShortcut, QToolButton
)
from PyQt5.QtGui import (
    QPixmap, QKeySequence, QColor, QPainter, QPen,
    QFont, QIcon, QCursor, QResizeEvent
)
from PyQt5.QtCore import Qt, QSize, QRect, QTimer, QPoint

from .canvas import Canvas
from .tools import Tool

# ─── Design tokens (FULL WHITE) ───────────────────────────────
BG          = "#FFFFFF"
RIBBON_BG   = "#FFFFFF"
RIBBON_BORD = "#D6D6D6"
ACCENT      = "#0067C0"
ACCENT_LITE = "#CCE4F7"
ACTIVE_BG   = "#D9EBFA"
ACTIVE_FG   = "#003C87"
HOVER_BG    = "#E8E8E8"
CANVAS_BG   = "#FFFFFF"      # background area canvas putih
ICON_FG     = "#1A1A1A"
TEXT_MUTED  = "#666"
RADIUS      = "4px"

# ─── Standard Win11 Paint palette ────────────────────────────
PALETTE_COLORS = [
    "#000000","#7F7F7F","#880015","#ED1C24","#FF7F27","#FFF200",
    "#22B14C","#00A2E8","#3F48CC","#A349A4",
    "#FFFFFF","#C3C3C3","#B97A57","#FFAEC9","#FFC90E","#EFE4B0",
    "#B5E61D","#99D9EA","#7092BE","#C8BFE7",
]

SHAPE_TOOLS = [
    ("Line",     "╱",  Tool.LINE),
    ("Rect",     "□",  Tool.RECTANGLE),
    ("RndRect",  "▢",  Tool.ROUNDED_RECTANGLE),
    ("Ellipse",  "○",  Tool.ELLIPSE),
    ("Circle",   "◯",  Tool.CIRCLE),
    ("Triangle", "△",  Tool.TRIANGLE),
    ("Diamond",  "◇",  Tool.DIAMOND),
    ("Pentagon", "⬠",  Tool.PENTAGON),
    ("Hexagon",  "⬡",  Tool.HEXAGON),
    ("Star",     "★",  Tool.STAR),
    ("Arrow→",   "→",  Tool.ARROW_RIGHT),
    ("Arrow←",   "←",  Tool.ARROW_LEFT),
    ("Arrow↑",   "↑",  Tool.ARROW_UP),
    ("Arrow↓",   "↓",  Tool.ARROW_DOWN),
    ("Curve",    "〜", Tool.CURVE),
]

def _rib_btn(icon_text: str, label: str, w=64, h=68, checkable=False) -> QPushButton:
    btn = QPushButton()
    btn.setCheckable(checkable)
    btn.setFixedSize(w, h)
    btn.setCursor(QCursor(Qt.PointingHandCursor))
    btn.setToolTip(label)
    btn.setText(f"{icon_text}\n{label}")
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: {RADIUS};
            color: {ICON_FG};
            font-size: 11px;
            padding: 4px;
            text-align: center;
        }}
        QPushButton:hover:!checked {{
            background: {HOVER_BG};
            border: 1px solid {RIBBON_BORD};
        }}
        QPushButton:checked, QPushButton:pressed {{
            background: {ACTIVE_BG};
            border: 1px solid {ACCENT};
            color: {ACTIVE_FG};
            font-weight: 600;
        }}
    """)
    return btn

def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFixedHeight(60)
    f.setStyleSheet(f"color: {RIBBON_BORD}; margin: 4px 2px;")
    return f

class ColorSwatch(QPushButton):
    def __init__(self, hex_color: str, parent=None):
        super().__init__(parent)
        self.hex_color = hex_color
        self.setFixedSize(24, 24)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(hex_color)
        border = "#888" if hex_color in ("#FFFFFF","#FFF200","#EFE4B0","#FFC90E") else hex_color
        self.setStyleSheet(f"""
            QPushButton {{
                background: {hex_color};
                border: 1px solid {border};
                border-radius: 3px;
            }}
            QPushButton:hover {{ border: 2px solid {ACCENT}; }}
        """)

def _section(title: str) -> tuple:
    frame = QFrame()
    frame.setStyleSheet("background: transparent; border: none;")
    vbox = QVBoxLayout(frame)
    vbox.setContentsMargins(4, 2, 4, 2)
    vbox.setSpacing(2)
    inner = QWidget()
    inner.setStyleSheet("background: transparent;")
    inner_layout = QHBoxLayout(inner)
    inner_layout.setContentsMargins(0, 0, 0, 0)
    inner_layout.setSpacing(4)
    vbox.addWidget(inner, stretch=1)
    lbl = QLabel(title)
    lbl.setAlignment(Qt.AlignHCenter)
    lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; border-bottom: 1px solid {RIBBON_BORD};")
    vbox.addWidget(lbl)
    return frame, inner_layout

class PaintTab(QWidget):
    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self._init_ui()
        self._setup_shortcuts()
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._fit_canvas)

    def _init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{ background: {BG}; font-family: 'Segoe UI', sans-serif; }}
            QScrollArea {{ background: {CANVAS_BG}; border: none; }}
            QScrollBar:vertical {{ background: {BG}; width: 10px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: #B0B0B0; border-radius: 4px; min-height: 24px; }}
            QScrollBar:horizontal {{ background: {BG}; height: 10px; border-radius: 4px; }}
            QScrollBar::handle:horizontal {{ background: #B0B0B0; border-radius: 4px; min-width: 24px; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ height:0; width:0; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        ribbon = self._build_ribbon()
        root.addWidget(ribbon)

        # ── Canvas area: FULLSCREEN (resizable) ──
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(True)   # INI PENTING: biar canvas bisa di-resize otomatis
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setStyleSheet(f"background: {CANVAS_BG}; border: none;")
        root.addWidget(self.scroll_area, stretch=1)

        status = self._build_status()
        root.addWidget(status)

        self.canvas._notify_selection_changed = lambda has: None
        self._set_tool(Tool.PENCIL)

    def _build_ribbon(self) -> QFrame:
        ribbon = QFrame()
        ribbon.setObjectName("ribbon")
        ribbon.setFixedHeight(100)
        ribbon.setStyleSheet(f"""
            QFrame#ribbon {{
                background: {RIBBON_BG};
                border-bottom: 1px solid {RIBBON_BORD};
            }}
        """)

        h = QHBoxLayout(ribbon)
        h.setContentsMargins(6, 2, 6, 2)
        h.setSpacing(0)

        # FILE
        sec_f, lay_f = _section("File")
        for ico, lbl, sc, slot in [
            ("📄", "New",  "Ctrl+N", self.new_canvas),
            ("📂", "Open", "Ctrl+O", self.open_image),
            ("💾", "Save", "Ctrl+S", self.save_image),
        ]:
            b = _rib_btn(ico, lbl)
            b.clicked.connect(slot)
            lay_f.addWidget(b)
        h.addWidget(sec_f)
        h.addWidget(_sep())

        # EDIT
        sec_h, lay_h = _section("Edit")
        for ico, lbl, slot in [
            ("↩", "Undo", self.canvas.undo),
            ("↪", "Redo", self.canvas.redo),
            ("🗑️","Clear", self.canvas.clear_canvas),
        ]:
            b = _rib_btn(ico, lbl)
            b.clicked.connect(slot)
            lay_h.addWidget(b)
        h.addWidget(sec_h)
        h.addWidget(_sep())

        # TOOLS
        sec_t, lay_t = _section("Tools")
        self._tool_btn_group = QButtonGroup(self)
        self._tool_btn_group.setExclusive(True)
        self._tool_buttons = {}
        draw_tools = [
            ("✏️", "Pencil",  Tool.PENCIL,  "P"),
            ("🖌️", "Brush",   Tool.BRUSH,   "B"),
            ("⬜", "Eraser",  Tool.ERASER,  "E"),
            ("🪣", "Fill",    Tool.FILL,    "F"),
            ("📝", "Text",    Tool.TEXT,    "T"),
            ("⬚",  "Select",  Tool.SELECT,  ""),
            ("📐", "Resize",  None,         ""),
        ]
        for ico, lbl, tool, sc in draw_tools:
            tip = f"{lbl} [{sc}]" if sc else lbl
            b = _rib_btn(ico, lbl, checkable=(tool is not None))
            b.setToolTip(tip)
            if tool is not None:
                b.clicked.connect(lambda _, t=tool: self._set_tool(t))
                self._tool_btn_group.addButton(b)
                self._tool_buttons[tool] = b
            else:
                b.clicked.connect(self.resize_canvas)
            lay_t.addWidget(b)
        h.addWidget(sec_t)
        h.addWidget(_sep())

        # SHAPES
        sec_s, lay_s = _section("Shapes")
        scroll_shapes = QScrollArea()
        scroll_shapes.setFixedSize(280, 80)
        scroll_shapes.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_shapes.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_shapes.setWidgetResizable(True)
        scroll_shapes.setStyleSheet("background: transparent; border: none; QScrollBar:horizontal{height:8px;}")
        shapes_widget = QWidget()
        shapes_widget.setStyleSheet("background: transparent;")
        shapes_h = QHBoxLayout(shapes_widget)
        shapes_h.setContentsMargins(0, 0, 0, 0)
        shapes_h.setSpacing(2)
        for lbl, ico, tool in SHAPE_TOOLS:
            b = _rib_btn(ico, lbl, w=52, h=68, checkable=True)
            b.clicked.connect(lambda _, t=tool: self._set_tool(t))
            self._tool_btn_group.addButton(b)
            self._tool_buttons[tool] = b
            shapes_h.addWidget(b)
        scroll_shapes.setWidget(shapes_widget)
        lay_s.addWidget(scroll_shapes)
        h.addWidget(sec_s)
        h.addWidget(_sep())

        # SIZE
        sec_sz, lay_sz = _section("Size")
        size_widget = QWidget()
        size_widget.setStyleSheet("background: transparent;")
        size_vbox = QVBoxLayout(size_widget)
        size_vbox.setContentsMargins(4, 0, 4, 0)
        size_vbox.setSpacing(2)
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(3)
        self.size_slider.setFixedWidth(100)
        self.size_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height:4px; background:{RIBBON_BORD}; border-radius:2px; }}
            QSlider::handle:horizontal {{ background:{ACCENT}; border:1px solid white; width:14px; height:14px; margin:-5px 0; border-radius:7px; }}
            QSlider::sub-page:horizontal {{ background:{ACCENT}; border-radius:2px; }}
        """)
        self.size_label = QLabel("3 px")
        self.size_label.setAlignment(Qt.AlignHCenter)
        self.size_label.setStyleSheet(f"font-size:11px; color:{TEXT_MUTED};")
        self.size_slider.valueChanged.connect(self._on_size)
        size_vbox.addWidget(self.size_slider)
        size_vbox.addWidget(self.size_label)
        lay_sz.addWidget(size_widget)
        h.addWidget(sec_sz)
        h.addWidget(_sep())

        # COLORS
        sec_c, lay_c = _section("Colors")
        colors_widget = QWidget()
        colors_widget.setStyleSheet("background: transparent;")
        col_vbox = QVBoxLayout(colors_widget)
        col_vbox.setContentsMargins(0, 0, 0, 0)
        col_vbox.setSpacing(3)
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        self.color1_btn = QPushButton()
        self.color1_btn.setFixedSize(32, 32)
        self.color1_btn.setToolTip("Color 1 (foreground) — click to change")
        self.color1_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._set_color_btn_style(self.color1_btn, QColor("#000000"))
        self.color1_btn.clicked.connect(self._pick_color1)
        top_row.addWidget(self.color1_btn)
        self.color2_btn = QPushButton()
        self.color2_btn.setFixedSize(32, 32)
        self.color2_btn.setToolTip("Color 2 (background) — click to change")
        self.color2_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._set_color_btn_style(self.color2_btn, QColor("#FFFFFF"))
        top_row.addWidget(self.color2_btn)
        edit_btn = QPushButton("Edit\ncolors")
        edit_btn.setFixedSize(56, 32)
        edit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border:1px solid {RIBBON_BORD};
                border-radius:{RADIUS}; font-size:10px; color:{ICON_FG};
            }}
            QPushButton:hover {{ background:{HOVER_BG}; }}
        """)
        edit_btn.clicked.connect(self._pick_color1)
        top_row.addWidget(edit_btn)
        col_vbox.addLayout(top_row)
        palette_grid = QGridLayout()
        palette_grid.setContentsMargins(0, 0, 0, 0)
        palette_grid.setSpacing(2)
        for i, hex_c in enumerate(PALETTE_COLORS):
            row, col = divmod(i, 10)
            sw = ColorSwatch(hex_c, self)
            sw.clicked.connect(lambda _, c=hex_c: self._swatch_click(c))
            palette_grid.addWidget(sw, row, col)
        col_vbox.addLayout(palette_grid)
        lay_c.addWidget(colors_widget)
        h.addWidget(sec_c)
        h.addStretch()
        return ribbon

    def _build_status(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(26)
        bar.setStyleSheet(f"background:{BG}; border-top:1px solid {RIBBON_BORD};")
        h = QHBoxLayout(bar)
        h.setContentsMargins(10, 0, 10, 0)
        h.setSpacing(12)
        self.pos_lbl  = QLabel("0, 0")
        self.size_lbl = QLabel("1000 × 700")
        self.tool_lbl = QLabel("Pencil")
        for lb in [self.pos_lbl, self.size_lbl, self.tool_lbl]:
            lb.setStyleSheet(f"font-size:11px; color:{TEXT_MUTED};")
            h.addWidget(lb)
        h.addStretch()
        zoom = QLabel("100%")
        zoom.setStyleSheet(f"font-size:11px; color:{TEXT_MUTED};")
        h.addWidget(zoom)
        return bar

    def _set_color_btn_style(self, btn: QPushButton, color: QColor):
        hex_c = color.name()
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {hex_c};
                border: 2px solid #888;
                border-radius: 3px;
            }}
            QPushButton:hover {{ border: 2px solid {ACCENT}; }}
        """)

    def _swatch_click(self, hex_c: str):
        color = QColor(hex_c)
        self.canvas.pen_color = color
        self._set_color_btn_style(self.color1_btn, color)

    def _pick_color1(self):
        color = QColorDialog.getColor(self.canvas.pen_color, self, "Choose Color",
                                      QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.canvas.pen_color = color
            self._set_color_btn_style(self.color1_btn, color)

    def _on_size(self, val: int):
        self.canvas.pen_size = val
        self.size_label.setText(f"{val} px")

    def _set_tool(self, tool: Tool):
        self.canvas.current_tool = tool
        btn = self._tool_buttons.get(tool)
        if btn:
            btn.setChecked(True)
        self.tool_lbl.setText(tool.name.title())

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._fit_canvas)

    # ──────────────────────────────────────────
    # FULLSCREEN CANVAS: resize mengikuti window
    # ──────────────────────────────────────────
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        # Gunakan timer untuk menghindari resize berulang terlalu cepat
        self._resize_timer.start(50)

    def _fit_canvas(self):
        """Resize canvas agar memenuhi seluruh area scroll (full screen)"""
        if not self.scroll_area:
            return
        viewport = self.scroll_area.viewport()
        if viewport:
            w = max(viewport.width(), 10)
            h = max(viewport.height(), 10)
            # Hanya resize jika ukuran berbeda (mencegah infinite loop)
            if self.canvas.width() != w or self.canvas.height() != h:
                self.canvas.resize_canvas(w, h)
                self.size_lbl.setText(f"{w} × {h}")

    def _setup_shortcuts(self):
        bindings = [
            ("Ctrl+Z", self.canvas.undo),
            ("Ctrl+Y", self.canvas.redo),
            ("Ctrl+S", self.save_image),
            ("Ctrl+O", self.open_image),
            ("Ctrl+N", self.new_canvas),
            ("P", lambda: self._set_tool(Tool.PENCIL)),
            ("B", lambda: self._set_tool(Tool.BRUSH)),
            ("E", lambda: self._set_tool(Tool.ERASER)),
            ("F", lambda: self._set_tool(Tool.FILL)),
            ("T", lambda: self._set_tool(Tool.TEXT)),
            ("L", lambda: self._set_tool(Tool.LINE)),
            ("R", lambda: self._set_tool(Tool.RECTANGLE)),
            ("C", lambda: self._set_tool(Tool.CIRCLE)),
            ("S", lambda: self._set_tool(Tool.STAR)),
            ("]", lambda: self._adj_size(+1)),
            ("[", lambda: self._adj_size(-1)),
        ]
        for key, slot in bindings:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

    def _adj_size(self, d):
        new_val = max(1, min(50, self.canvas.pen_size + d))
        self.canvas.pen_size = new_val
        self.size_slider.setValue(new_val)

    def new_canvas(self):
        if QMessageBox.question(self, "New", "Hapus canvas?",
                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # Perbarui ukuran canvas agar tetap full screen setelah clear
            self._fit_canvas()
            self.canvas.clear_canvas()

    def save_image(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save", "",
                    "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)")
        if fn:
            self.canvas.canvas.save(fn)

    def open_image(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open", "",
                    "Images (*.png *.jpg *.jpeg *.bmp)")
        if fn:
            pix = QPixmap(fn)
            # Resize canvas ke ukuran gambar yang dibuka
            self.canvas.resize_canvas(pix.width(), pix.height())
            self.canvas.canvas = pix
            self.canvas.update()
            self._fit_canvas()  # pastikan full screen setelah buka

    def resize_canvas(self):
        # Override: karena canvas sudah full screen, mungkin tidak diperlukan
        # Tapi tetap biarkan manual jika user mau
        w, ok = QInputDialog.getInt(self, "Width", "Width (px):",
                    self.canvas.width(), 100, 8000)
        if not ok: return
        h, ok = QInputDialog.getInt(self, "Height", "Height (px):",
                    self.canvas.height(), 100, 8000)
        if not ok: return
        self.canvas.resize_canvas(w, h)
        self.size_lbl.setText(f"{w} × {h}")