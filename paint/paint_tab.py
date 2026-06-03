from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QToolButton, QColorDialog, QFileDialog, QLabel, QSpinBox,
    QMessageBox, QInputDialog, QFrame, QShortcut, QSlider,
    QMenuBar, QMenu, QAction, QActionGroup, QToolBar, QSizePolicy,
    QScrollArea, QScrollBar
)
from PyQt5.QtGui import (
    QPixmap, QKeySequence, QColor, QIcon, QPainter, QPen, QBrush,
    QPolygon, QFont, QPainterPath
)
from PyQt5.QtCore import Qt, QPoint, QSize, QEvent

from .canvas import Canvas
from .tools import Tool


class PaintTab(QWidget):
    """Modern Paint Tab with a premium minimalist UI and crisp vector icons"""

    def __init__(self) -> None:
        super().__init__()

        self.canvas = Canvas()
        self.current_color = QColor("#2c3e50")
        self.original_pixmap = None 

        self.tool_actions = {}
        self.shape_actions = {}

        self.init_ui()
        self._setup_shortcuts()

        self.set_tool(Tool.PENCIL)
        self.change_size()

        self.canvas.installEventFilter(self)

        if hasattr(self.canvas, 'selectionChanged'):
            self.canvas.selectionChanged.connect(self.on_selection_changed)

        self._store_original_pixmap()

    # ==================================================
    # MODERN PREMIUM STYLESHEET
    # ==================================================
    def _style(self) -> str:
        return """
            /* Base Application Styling */
            QWidget {
                background-color: #f8fafc;
                color: #334155;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 13px;
            }

            /* Elegant & Spacious Menu Bar */
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                min-height: 40px;
                padding: 0 12px;
                font-weight: 500;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                margin: 4px 2px;
                border-radius: 6px;
            }
            QMenuBar::item:selected {
                background-color: #f1f5f9;
                color: #0f172a;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 24px 6px 16px;
                border-radius: 4px;
                margin: 1px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }

            /* Sleek Floating-Style Toolbar */
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                spacing: 4px;
                padding: 6px 16px;
                min-height: 48px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 5px;
                margin: 0px 1px;
            }
            QToolBar QToolButton:hover {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
            }
            QToolBar QToolButton:checked {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
            }

            /* Custom Styling for Shapes Dropdown */
            QToolButton#ShapesBtn {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 12px;
                font-weight: 500;
                color: #475569;
            }
            QToolButton#ShapesBtn:hover {
                background-color: #e2e8f0;
                color: #1e293b;
            }

            /* Clean Canvas Workspace Scroll Area */
            QScrollArea {
                background-color: #cbd5e1;
                border: none;
            }

            /* Premium Minimal Slider */
            QSlider::groove:horizontal {
                height: 4px;
                background: #e2e8f0;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #3b82f6;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #3b82f6;
                width: 14px;
                height: 14px;
                margin: -5px 0;
            }

            /* Modern Input SpinBox */
            QSpinBox {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 6px;
                background: #ffffff;
                color: #334155;
                font-weight: 500;
            }
            QSpinBox:focus {
                border: 1px solid #3b82f6;
            }

            /* Status Bar Details */
            QFrame#StatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e2e8f0;
                padding: 6px 16px;
                min-height: 28px;
            }
            QFrame#StatusBar QLabel {
                color: #64748b;
                font-size: 12px;
            }
        """

    # ==================================================
    # VECTOR ICON GENERATOR (DYNAMIC & CRISP)
    # ==================================================
    def _create_vector_icon(self, name: str) -> QIcon:
        """Draws crisp geometric icons dynamically to replace ugly system emojis"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Icon base color configuration
        base_color = QColor("#475569")
        pen = QPen(base_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        if name == "new":
            path = QPainterPath()
            path.moveTo(8, 4)
            path.lineTo(18, 4)
            path.lineTo(24, 10)
            path.lineTo(24, 28)
            path.lineTo(8, 28)
            path.closeSubpath()
            painter.drawPath(path)
            painter.drawLine(18, 4, 18, 10)
            painter.drawLine(18, 10, 24, 10)
        elif name == "open":
            painter.drawRoundedRect(5, 10, 22, 16, 2, 2)
            painter.drawLine(7, 10, 10, 6)
            painter.drawLine(10, 6, 16, 6)
            painter.drawLine(16, 6, 18, 10)
        elif name == "save":
            painter.drawRoundedRect(6, 6, 20, 20, 3, 3)
            painter.fillRect(11, 6, 10, 6, base_color)
            painter.drawRect(10, 16, 12, 10)
        elif name == "undo":
            painter.drawLine(24, 16, 10, 16)
            painter.drawLine(10, 16, 15, 11)
            painter.drawLine(10, 16, 15, 21)
        elif name == "redo":
            painter.drawLine(8, 16, 22, 16)
            painter.drawLine(22, 16, 17, 11)
            painter.drawLine(22, 16, 17, 21)
        elif name == "select":
            pen.setStyle(Qt.DashLine)
            pen.setWidthF(1.5)
            painter.setPen(pen)
            painter.drawRoundedRect(6, 6, 20, 20, 2, 2)
        elif name == "pencil":
            painter.drawLine(8, 24, 22, 10)
            painter.setBrush(QBrush(base_color))
            painter.drawPolygon(QPolygon([QPoint(6, 26), QPoint(11, 25), QPoint(7, 21)]))
        elif name == "brush":
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(8, 24, 20, 12)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#ef4444"))) # Dynamic subtle color tip
            painter.drawEllipse(19, 8, 6, 6)
        elif name == "fill":
            painter.drawPolygon(QPolygon([QPoint(14, 6), QPoint(26, 18), QPoint(18, 26), QPoint(6, 14)]))
            painter.setBrush(QBrush(base_color))
            painter.drawEllipse(22, 24, 4, 6)
        elif name == "eraser":
            painter.drawRoundedRect(6, 10, 20, 12, 2, 2)
            painter.drawLine(15, 10, 15, 22)
            painter.fillRect(6, 10, 9, 12, QColor("#cbd5e1"))
        elif name == "text":
            font = QFont("Segoe UI", 15, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "A")
            
        painter.end()
        return QIcon(pixmap)

    # ==================================================
    # UI CONSTRUCTION
    # ==================================================
    def init_ui(self) -> None:
        self.setStyleSheet(self._style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Menu Bar
        self.menu_bar = self._create_menu_bar()
        layout.addWidget(self.menu_bar)

        # Main Toolbar
        self.toolbar = self._create_toolbar()
        layout.addWidget(self.toolbar)

        # Animation panel (hidden initially)
        self.anim_group = self._create_animation_group()
        layout.addWidget(self.anim_group)
        self.anim_group.setVisible(False)

        # Canvas with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False) 
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.scroll_area, 1)

        # Status Bar
        self.status_bar = self._create_status_bar()
        layout.addWidget(self.status_bar)

        self._fit_canvas_to_window()

    def _create_menu_bar(self) -> QMenuBar:
        menubar = QMenuBar()
        menubar.setFixedHeight(40)

        # File menu
        file_menu = menubar.addMenu("File")
        new_action = QAction("New Canvas", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_canvas)
        file_menu.addAction(new_action)
        self.addAction(new_action)

        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        self.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        self.addAction(save_action)

        file_menu.addSeparator()
        resize_action = QAction("Resize Canvas", self)
        resize_action.triggered.connect(self.resize_canvas)
        file_menu.addAction(resize_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.canvas.undo)
        edit_menu.addAction(undo_action)
        self.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.canvas.redo)
        edit_menu.addAction(redo_action)
        self.addAction(redo_action)

        return menubar

    def _create_toolbar(self) -> QToolBar:
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20)) # Perfect standard dimension for crisp look

        # File operations group
        toolbar.addAction(self._make_action(self._create_vector_icon("new"), "New", self.new_canvas))
        toolbar.addAction(self._make_action(self._create_vector_icon("open"), "Open", self.open_image))
        toolbar.addAction(self._make_action(self._create_vector_icon("save"), "Save", self.save_image))
        toolbar.addSeparator()

        # History action group
        toolbar.addAction(self._make_action(self._create_vector_icon("undo"), "Undo", self.canvas.undo))
        toolbar.addAction(self._make_action(self._create_vector_icon("redo"), "Redo", self.canvas.redo))
        toolbar.addSeparator()

        # Main structural tools group
        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)

        tools_config = [
            (Tool.SELECT, "select", "Selection Tool"),
            (Tool.PENCIL, "pencil", "Pencil"),
            (Tool.BRUSH, "brush", "Brush"),
            (Tool.FILL, "fill", "Fill Bucket"),
            (Tool.ERASER, "eraser", "Eraser"),
            (Tool.TEXT, "text", "Text Input"),
        ]

        for tool_key, icon_name, tip in tools_config:
            act = self._make_action(self._create_vector_icon(icon_name), tip, lambda checked, t=tool_key: self.set_tool(t))
            act.setCheckable(True)
            self.tool_group.addAction(act)
            self.tool_actions[tool_key] = act
            toolbar.addAction(act)

        toolbar.addSeparator()

        # Premium Custom Dropdown Shapes Button
        shapes_btn = QToolButton()
        shapes_btn.setObjectName("ShapesBtn")
        shapes_btn.setText("Shapes")
        shapes_btn.setPopupMode(QToolButton.InstantPopup)
        
        shapes_menu = QMenu()
        shapes_list = [
            ("Line", Tool.LINE), ("Curve", Tool.CURVE), ("Circle", Tool.CIRCLE),
            ("Ellipse", Tool.ELLIPSE), ("Rectangle", Tool.RECTANGLE),
            ("Rounded Rect", Tool.ROUNDED_RECTANGLE), ("Triangle", Tool.TRIANGLE),
            ("Diamond", Tool.DIAMOND), ("Star", Tool.STAR),
            ("Arrow →", Tool.ARROW_RIGHT), ("Arrow ←", Tool.ARROW_LEFT),
            ("Arrow ↑", Tool.ARROW_UP), ("Arrow ↓", Tool.ARROW_DOWN)
        ]
        for label, tool in shapes_list:
            act = QAction(label, self)
            act.triggered.connect(lambda checked, t=tool: self.set_tool(t))
            shapes_menu.addAction(act)
            self.shape_actions[tool] = act
        shapes_btn.setMenu(shapes_menu)
        toolbar.addWidget(shapes_btn)
        toolbar.addSeparator()

        # Circular Dynamic Color Picker Button
        self.color_btn = QToolButton()
        self.color_btn.setFixedSize(28, 28)
        self.color_btn.setToolTip("Select Color")
        self.color_btn.setStyleSheet(f"""
            background-color: {self.current_color.name()}; 
            border-radius: 14px; 
            border: 2px solid #ffffff;
            outline: none;
        """)
        # We wrap it gently to look perfectly floating
        color_container = QWidget()
        color_layout = QHBoxLayout(color_container)
        color_layout.setContentsMargins(4, 0, 4, 0)
        color_layout.addWidget(self.color_btn)
        self.color_btn.clicked.connect(self.pick_color)
        toolbar.addWidget(color_container)

        # Brush size layout controllers
        size_label = QLabel("Size")
        size_label.setStyleSheet("color: #64748b; font-weight: 500; margin-left: 4px;")
        toolbar.addWidget(size_label)

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(3)
        self.size_slider.setFixedWidth(100)
        self.size_slider.valueChanged.connect(self._sync_size_from_slider)
        toolbar.addWidget(self.size_slider)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 50)
        self.size_spin.setValue(3)
        self.size_spin.setFixedWidth(54)
        self.size_spin.valueChanged.connect(self._sync_size_from_spin)
        toolbar.addWidget(self.size_spin)

        return toolbar

    def _make_action(self, icon: QIcon, tooltip: str, slot) -> QAction:
        act = QAction(icon, "", self)
        act.setToolTip(tooltip)
        act.triggered.connect(slot)
        return act

    # --------------------------------------------------
    # Remaining UI Logic Methods (Unchanged Core Architecture)
    # --------------------------------------------------
    def _create_animation_group(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("AnimPanel")
        panel.setStyleSheet("background-color: #fff7ed; border-bottom: 1px solid #ffedd5;")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(16, 6, 16, 6)

        self.anim_status = QLabel("✨ Selection active — add motion")
        self.anim_status.setStyleSheet("font-weight: 600; color: #ea580c;")

        self.btn_bounce = QPushButton("Bounce")
        self.btn_bounce.setCheckable(True)
        self.btn_bounce.clicked.connect(lambda: self._toggle_anim("bounce", self.btn_bounce))

        self.btn_pulse = QPushButton("Pulse")
        self.btn_pulse.setCheckable(True)
        self.btn_pulse.clicked.connect(lambda: self._toggle_anim("pulse", self.btn_pulse))

        self.btn_spin = QPushButton("Spin")
        self.btn_spin.setCheckable(True)
        self.btn_spin.clicked.connect(lambda: self._toggle_anim("spin", self.btn_spin))

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self._stop_anim)
        self.btn_stop.setEnabled(False)

        layout.addWidget(self.anim_status)
        layout.addStretch()
        layout.addWidget(self.btn_bounce)
        layout.addWidget(self.btn_pulse)
        layout.addWidget(self.btn_spin)
        layout.addWidget(self.btn_stop)
        return panel

    def _create_status_bar(self) -> QFrame:
        status = QFrame()
        status.setObjectName("StatusBar")
        layout = QHBoxLayout(status)
        layout.setContentsMargins(16, 4, 16, 4)

        self.canvas_size_label = QLabel("1280 × 800 px")
        self.current_tool_label = QLabel("Tool: Pencil")
        self.cursor_pos_label = QLabel("📍 (0, 0)")

        layout.addWidget(self.canvas_size_label)
        layout.addSpacing(24)
        layout.addWidget(self.current_tool_label)
        layout.addSpacing(24)
        layout.addWidget(self.cursor_pos_label)
        layout.addStretch()

        zoom_label = QLabel("Zoom:")
        self.zoom_percent = QLabel("100%")
        self.zoom_percent.setFixedWidth(40)
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(120)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)

        layout.addWidget(zoom_label)
        layout.addWidget(self.zoom_slider)
        layout.addWidget(self.zoom_percent)
        return status

    def _on_zoom_changed(self, value: int) -> None:
        if self.original_pixmap is None:
            return
        percent = value
        self.zoom_percent.setText(f"{percent}%")
        scale = percent / 100.0

        orig = self.original_pixmap
        new_width = int(orig.width() * scale)
        new_height = int(orig.height() * scale)
        scaled_pixmap = orig.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.canvas.canvas = scaled_pixmap
        self.canvas.setFixedSize(scaled_pixmap.size())
        self._center_scroll_area()

    def _center_scroll_area(self) -> None:
        hbar = self.scroll_area.horizontalScrollBar()
        vbar = self.scroll_area.verticalScrollBar()
        hbar.setValue((hbar.maximum() - hbar.pageStep() + 1) // 2)
        vbar.setValue((vbar.maximum() - vbar.pageStep() + 1) // 2)

    def _adjust_zoom(self, delta: int) -> None:
        new_val = self.zoom_slider.value() + delta
        new_val = max(self.zoom_slider.minimum(), min(self.zoom_slider.maximum(), new_val))
        self.zoom_slider.setValue(new_val)

    def _store_original_pixmap(self) -> None:
        if hasattr(self.canvas, 'canvas') and self.canvas.canvas:
            self.original_pixmap = self.canvas.canvas.copy()
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(100)
            self.zoom_slider.blockSignals(False)
            self._on_zoom_changed(100)

    def _update_original_from_canvas(self) -> None:
        if hasattr(self.canvas, 'canvas') and self.canvas.canvas:
            self.original_pixmap = self.canvas.canvas.copy()
            current_zoom = self.zoom_slider.value()
            self._on_zoom_changed(current_zoom)

    def eventFilter(self, obj, event) -> bool:
        if obj == self.canvas and event.type() == QEvent.MouseMove:
            pos = event.pos()
            self.cursor_pos_label.setText(f"📍 ({pos.x()}, {pos.y()})")
        return super().eventFilter(obj, event)

    def set_tool(self, tool) -> None:
        self.canvas.current_tool = tool
        tool_name = tool.name.replace("_", " ").title()
        self.current_tool_label.setText(f"Tool: {tool_name}")
        for t, act in self.tool_actions.items():
            act.setChecked(t == tool)

    def set_color(self, color: QColor) -> None:
        if color.isValid():
            self.current_color = color
            self.canvas.pen_color = color
            self.color_btn.setStyleSheet(f"""
                background-color: {color.name()}; 
                border-radius: 14px; 
                border: 2px solid #ffffff;
                outline: none;
            """)

    def pick_color(self) -> None:
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        self.set_color(color)

    def change_size(self) -> None:
        size = self.size_spin.value()
        self.canvas.pen_size = size
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(size)
        self.size_slider.blockSignals(False)

    def _sync_size_from_slider(self, val: int) -> None:
        self.size_spin.blockSignals(True)
        self.size_spin.setValue(val)
        self.size_spin.blockSignals(False)
        self.canvas.pen_size = val

    def _sync_size_from_spin(self, val: int) -> None:
        self.size_slider.blockSignals(True)
        self.size_slider.setValue(val)
        self.size_slider.blockSignals(False)
        self.canvas.pen_size = val

    def _fit_canvas_to_window(self) -> None:
        self.canvas.resize_canvas(1280, 800)
        self.canvas.setFixedSize(1280, 800)
        self._store_original_pixmap()
        self._update_canvas_size_label()

    def _update_canvas_size_label(self) -> None:
        if self.original_pixmap:
            w = self.original_pixmap.width()
            h = self.original_pixmap.height()
            self.canvas_size_label.setText(f"{w} × {h} px")

    def new_canvas(self) -> None:
        reply = QMessageBox.question(self, "New Canvas", "Clear current canvas?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()
            self._store_original_pixmap()
            self._update_canvas_size_label()

    def open_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                QMessageBox.warning(self, "Error", "Could not load image.")
                return
            self.canvas.canvas = pixmap
            self.canvas.setFixedSize(pixmap.size())
            self._store_original_pixmap()
            self._update_canvas_size_label()

    def save_image(self) -> None:
        if self.original_pixmap is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG (*.png);;JPEG (*.jpg)")
        if path:
            self.original_pixmap.save(path)

    def resize_canvas(self) -> None:
        if self.original_pixmap is None:
            return
        w, ok = QInputDialog.getInt(self, "Canvas Width", "Width:", self.original_pixmap.width(), 100, 5000)
        if not ok: return
        h, ok = QInputDialog.getInt(self, "Canvas Height", "Height:", self.original_pixmap.height(), 100, 5000)
        if not ok: return
        self.canvas.resize_canvas(w, h)
        self._store_original_pixmap()
        self._update_canvas_size_label()

    def on_selection_changed(self, has_selection: bool) -> None:
        self.anim_group.setVisible(has_selection)
        for btn in (self.btn_bounce, self.btn_pulse, self.btn_spin):
            btn.setEnabled(has_selection)
        if not has_selection:
            self._stop_anim()

    def _toggle_anim(self, mode: str, btn: QPushButton) -> None:
        for b in (self.btn_bounce, self.btn_pulse, self.btn_spin):
            if b != btn: b.setChecked(False)
        if btn.isChecked():
            self.canvas.start_animation(mode)
            self.btn_stop.setEnabled(True)
            self.anim_status.setText(f"🎬 Animating: {mode}")
        else:
            self._stop_anim()

    def _stop_anim(self) -> None:
        self.canvas.stop_animation()
        self.btn_bounce.setChecked(False)
        self.btn_pulse.setChecked(False)
        self.btn_spin.setChecked(False)
        self.btn_stop.setEnabled(False)
        if hasattr(self.canvas, '_select_rect') and not self.canvas._select_rect.isNull():
            self.anim_status.setText("✨ Selection active — add motion")
        else:
            self.anim_status.setText("")

    def _setup_shortcuts(self):
        # List untuk menyimpan referensi objek shortcut agar tidak dihapus Python GC
        self.shortcut_objects = []

        shortcuts = [
            # Ctrl+Z, Y, S, O, N dkk SUDAH di-handle oleh Menu Bar di atas, 
            # Jadi jangan ditulis ulang di sini agar tidak konflik!
            
            ("Ctrl+Shift+Z", self.canvas.redo), 
            ("P", lambda: self.set_tool(Tool.PENCIL)), 
            ("B", lambda: self.set_tool(Tool.BRUSH)),
            ("E", lambda: self.set_tool(Tool.ERASER)), 
            ("F", lambda: self.set_tool(Tool.FILL)),
            ("T", lambda: self.set_tool(Tool.TEXT)), 
            ("L", lambda: self.set_tool(Tool.LINE)),
            ("R", lambda: self.set_tool(Tool.RECTANGLE)), 
            ("C", lambda: self.set_tool(Tool.CIRCLE)),
            ("S", lambda: self.set_tool(Tool.STAR)), 
            ("]", self._increase_size),
            ("[", self._decrease_size), 
            ("Escape", self._on_escape)
        ]

        for key, slot in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            # Mengatur agar shortcut aktif saat widget ini atau anaknya sedang fokus
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(slot)
            
            # Simpan referensi ke list instance
            self.shortcut_objects.append(shortcut)

    def _increase_size(self) -> None:
        self.size_spin.setValue(min(self.size_spin.value() + 1, 50))

    def _decrease_size(self) -> None:
        self.size_spin.setValue(max(self.size_spin.value() - 1, 1))

    def _on_escape(self) -> None:
        self._stop_anim()
        if hasattr(self.canvas, '_select_rect'):
            self.canvas._select_rect.setRect(0, 0, 0, 0)
        self.on_selection_changed(False)
        self.canvas.update()