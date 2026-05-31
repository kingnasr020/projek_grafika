from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QFileDialog,
    QLabel, QSpinBox, QMessageBox, QInputDialog,
    QGroupBox, QGridLayout, QScrollArea,
    QSizePolicy, QFrame
)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt

from .canvas import Canvas
from .tools import Tool


class PaintTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = Canvas()
        self.init_ui()
        self._setup_shortcuts()

    def init_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # ==================================
        # BARIS 1 — File & History
        # ==================================

        row1 = QHBoxLayout()

        for label, slot in [
            ("New",           self.new_canvas),
            ("Open",          self.open_image),
            ("Save",          self.save_image),
            ("Resize Canvas", self.resize_canvas),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            row1.addWidget(btn)

        row1.addSpacing(16)

        btn_undo = QPushButton("↩ Undo")
        btn_redo = QPushButton("↪ Redo")
        btn_undo.clicked.connect(self.canvas.undo)
        btn_redo.clicked.connect(self.canvas.redo)
        row1.addWidget(btn_undo)
        row1.addWidget(btn_redo)
        row1.addStretch()

        # ==================================
        # BARIS 2 — Draw tools
        # ==================================

        row2 = QHBoxLayout()

        draw_tools = [
            ("Select", Tool.SELECT),
            ("Pencil", Tool.PENCIL),
            ("Brush",  Tool.BRUSH),
            ("Eraser", Tool.ERASER),
            ("Fill",   Tool.FILL),
            ("Text",   Tool.TEXT),
        ]

        for label, tool in draw_tools:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, t=tool: self.set_tool(t))
            row2.addWidget(btn)

        row2.addSpacing(16)

        btn_color = QPushButton("🎨 Color")
        btn_color.clicked.connect(self.pick_color)
        row2.addWidget(btn_color)

        row2.addWidget(QLabel("Size:"))
        self.size_box = QSpinBox()
        self.size_box.setRange(1, 50)
        self.size_box.setValue(3)
        self.size_box.valueChanged.connect(self.change_size)
        row2.addWidget(self.size_box)

        row2.addSpacing(16)

        self.current_tool_label = QLabel("Tool: Pencil")
        self.current_tool_label.setStyleSheet("font-weight: bold;")
        row2.addWidget(self.current_tool_label)
        row2.addStretch()

        # ==================================
        # BARIS 3 — Shapes
        # ==================================

        shape_group = QGroupBox("Shapes")
        shape_layout = QHBoxLayout()
        shape_layout.setSpacing(4)

        shapes = [
            ("Line",      Tool.LINE),
            ("Rect",      Tool.RECTANGLE),
            ("Rounded",   Tool.ROUNDED_RECTANGLE),
            ("Circle",    Tool.CIRCLE),
            ("Ellipse",   Tool.ELLIPSE),
            ("Triangle",  Tool.TRIANGLE),
            ("Diamond",   Tool.DIAMOND),
            ("Pentagon",  Tool.PENTAGON),
            ("Hexagon",   Tool.HEXAGON),
            ("Star",      Tool.STAR),
            ("Arrow →",   Tool.ARROW_RIGHT),
            ("Arrow ←",   Tool.ARROW_LEFT),
            ("Arrow ↑",   Tool.ARROW_UP),
            ("Arrow ↓",   Tool.ARROW_DOWN),
            ("Curve",     Tool.CURVE),
        ]

        for label, tool in shapes:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, t=tool: self.set_tool(t))
            shape_layout.addWidget(btn)

        shape_group.setLayout(shape_layout)

        # ==================================
        # CANVAS — scroll area
        # ==================================

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ==================================
        # Susun semua
        # ==================================

        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        main_layout.addWidget(shape_group)
        main_layout.addWidget(self.scroll_area)

    # ==================================================
    # Canvas mengikuti ukuran window saat pertama tampil
    # ==================================================

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, '_initial_resize_done'):
            self._initial_resize_done = True
            self._fit_canvas_to_window()

    def _fit_canvas_to_window(self):
        w = max(self.scroll_area.viewport().width(), 400)
        h = max(self.scroll_area.viewport().height(), 300)
        self.canvas.resize_canvas(w, h)


    # ==================================================
    # SHORTCUTS
    # ==================================================

    def _setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+Z",       self.canvas.undo),
            ("Ctrl+Y",       self.canvas.redo),
            ("Ctrl+Shift+Z", self.canvas.redo),
            ("Ctrl+S",       self.save_image),
            ("Ctrl+O",       self.open_image),
            ("Ctrl+N",       self.new_canvas),
            # Tools
            ("P",  lambda: self.set_tool(Tool.PENCIL)),
            ("B",  lambda: self.set_tool(Tool.BRUSH)),
            ("E",  lambda: self.set_tool(Tool.ERASER)),
            ("F",  lambda: self.set_tool(Tool.FILL)),
            ("T",  lambda: self.set_tool(Tool.TEXT)),
            ("L",  lambda: self.set_tool(Tool.LINE)),
            ("R",  lambda: self.set_tool(Tool.RECTANGLE)),
            ("C",  lambda: self.set_tool(Tool.CIRCLE)),
            ("S",  lambda: self.set_tool(Tool.STAR)),
            # Ukuran brush
            ("]",  self._increase_size),
            ("[",  self._decrease_size),
        ]

        for key, slot in shortcuts:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

    def _increase_size(self):
        self.size_box.setValue(min(self.size_box.value() + 1, 50))

    def _decrease_size(self):
        self.size_box.setValue(max(self.size_box.value() - 1, 1))

    # ==================================================
    # SLOTS
    # ==================================================

    def set_tool(self, tool):
        self.canvas.current_tool = tool
        self.current_tool_label.setText(f"Tool: {tool.name.title()}")

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.pen_color = color

    def change_size(self):
        self.canvas.pen_size = self.size_box.value()

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
            self, "Canvas Width", "Width:",
            self.canvas.width(), 100, 5000
        )
        if not ok:
            return
        height, ok = QInputDialog.getInt(
            self, "Canvas Height", "Height:",
            self.canvas.height(), 100, 5000
        )
        if not ok:
            return
        self.canvas.resize_canvas(width, height)