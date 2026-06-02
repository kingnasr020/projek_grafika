from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QToolButton,
    QColorDialog,
    QFileDialog,
    QLabel,
    QSpinBox,
    QMessageBox,
    QInputDialog,
    QGroupBox,
    QScrollArea,
    QSizePolicy,
    QFrame,
    QShortcut,
    QSlider,
)

from PyQt5.QtGui import (
    QPixmap,
    QKeySequence,
    QColor,
    QIcon,
    QPainter,
    QPen,
    QBrush,
    QPolygon,
    QFont,
)

from PyQt5.QtCore import Qt, QPoint, QSize

from .canvas import Canvas
from .tools import Tool


class PaintTab(QWidget):

    def __init__(self):
        super().__init__()

        self.canvas = Canvas()
        self.current_color = QColor("black")

        self.tool_buttons = {}
        self.shape_buttons = {}

        self.init_ui()
        self._setup_shortcuts()

        self.set_tool(Tool.PENCIL)
        self.change_size()

    # ==================================================
    # STYLE UTAMA
    # ==================================================

    def _style(self):
        return """
            QWidget {
                background-color: #f3f3f3;
                color: #202020;
                font-family: "Segoe UI";
                font-size: 11px;
            }

            QFrame#PaintRibbon {
                background-color: #f8f8f8;
                border-bottom: 1px solid #dddddd;
            }

            QFrame#RibbonGroup {
                background-color: #f8f8f8;
                border-right: 1px solid #e0e0e0;
            }

            QLabel#RibbonTitle {
                color: #555555;
                font-size: 11px;
                background-color: transparent;
            }

            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 2px;
                color: #202020;
            }

            QToolButton:hover {
                background-color: #eaf4ff;
                border: 1px solid #99d1ff;
            }

            QToolButton:pressed {
                background-color: #cce8ff;
                border: 1px solid #0078d4;
            }

            QToolButton:checked {
                background-color: #cce8ff;
                border: 1px solid #0078d4;
            }

            QPushButton {
                background-color: #f7f7f7;
                color: #000000;
                border: 1px solid #b8b8b8;
                border-radius: 2px;
                padding: 2px 8px;
                min-height: 18px;
            }

            QPushButton:hover {
                background-color: #eaf4ff;
                border: 1px solid #0078d7;
            }

            QPushButton:pressed {
                background-color: #cce8ff;
                border: 1px solid #0078d7;
            }

            QPushButton:disabled {
                background-color: #eeeeee;
                color: #b0b0b0;
                border: 1px solid #d0d0d0;
            }

            QLabel {
                background-color: transparent;
                color: #202020;
            }

            QSpinBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #b8b8b8;
                min-height: 19px;
            }

            QScrollArea#CanvasScrollArea {
                background-color: #efefef;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 15px;
                margin: 15px 0 15px 0;
                border: none;
            }

            QScrollBar::handle:vertical {
                background-color: #9f9f9f;
                min-height: 30px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #7f7f7f;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background-color: #e5e5e5;
                height: 15px;
            }

            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 15px;
                margin: 0 15px 0 15px;
                border: none;
            }

            QScrollBar::handle:horizontal {
                background-color: #c8c8c8;
                min-width: 30px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: #a8a8a8;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background-color: #e5e5e5;
                width: 15px;
            }

            QFrame#StatusBar {
                background-color: #f8f8f8;
                border-top: 1px solid #dddddd;
            }

            QFrame#StatusBar QLabel {
                color: #333333;
                font-size: 11px;
            }
        """

    # ==================================================
    # UI UTAMA
    # ==================================================

    def init_ui(self):
        self.setStyleSheet(self._style())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.size_box = QSpinBox(self)
        self.size_box.setRange(1, 50)
        self.size_box.setValue(3)
        self.size_box.valueChanged.connect(self.change_size)
        self.size_box.hide()

        ribbon = self._create_ribbon()

        self.anim_group = self._create_animation_group()
        self.anim_group.setVisible(False)

        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        self.side_panel = self._create_side_panel()
        workspace_layout.addWidget(self.side_panel)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("CanvasScrollArea")
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        workspace_layout.addWidget(self.scroll_area)

        status_bar = self._create_status_bar()

        main_layout.addWidget(ribbon)
        main_layout.addWidget(self.anim_group)
        main_layout.addLayout(workspace_layout, 1)
        main_layout.addWidget(status_bar)

    # ==================================================
    # CUSTOM ICON
    # ==================================================

    def _make_tool_icon(self, name, size=26):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        dark = QColor("#222222")
        blue = QColor("#0078d4")
        yellow = QColor("#f4c542")
        pink = QColor("#f2a2b8")

        painter.setPen(QPen(dark, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        if name == "select":
            painter.setPen(QPen(dark, 1, Qt.DashLine))
            painter.drawRect(5, 5, size - 10, size - 10)

        elif name == "pencil":
            body = QPolygon([
                QPoint(7, size - 7),
                QPoint(size - 9, 6),
                QPoint(size - 5, 10),
                QPoint(11, size - 4),
            ])
            painter.setBrush(QBrush(yellow))
            painter.setPen(QPen(dark, 1))
            painter.drawPolygon(body)

            painter.setBrush(QBrush(dark))
            tip = QPolygon([
                QPoint(size - 9, 6),
                QPoint(size - 4, 4),
                QPoint(size - 5, 10),
            ])
            painter.drawPolygon(tip)

        elif name == "brush":
            painter.setPen(QPen(dark, 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(10, 20, 20, 8)
            painter.setBrush(QBrush(QColor("#555555")))
            painter.setPen(QPen(dark, 1))
            painter.drawEllipse(5, 17, 9, 7)

        elif name == "fill":
            bucket = QPolygon([
                QPoint(8, 7),
                QPoint(18, 10),
                QPoint(15, 18),
                QPoint(5, 15),
            ])
            painter.setBrush(QBrush(QColor("#eeeeee")))
            painter.setPen(QPen(dark, 1))
            painter.drawPolygon(bucket)

            painter.setBrush(QBrush(blue))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(17, 17, 5, 7)

        elif name == "text":
            painter.setPen(QPen(dark, 1))
            font = QFont("Segoe UI", 17)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "A")

        elif name == "eraser":
            eraser = QPolygon([
                QPoint(7, 18),
                QPoint(15, 10),
                QPoint(22, 15),
                QPoint(14, 23),
            ])
            painter.setBrush(QBrush(pink))
            painter.setPen(QPen(dark, 1))
            painter.drawPolygon(eraser)
            painter.drawLine(11, 19, 18, 22)

        elif name == "palette":
            painter.setPen(Qt.NoPen)

            painter.setBrush(QColor("#22c55e"))
            painter.drawEllipse(4, 5, 8, 8)

            painter.setBrush(QColor("#3b82f6"))
            painter.drawEllipse(13, 5, 8, 8)

            painter.setBrush(QColor("#f97316"))
            painter.drawEllipse(7, 14, 8, 8)

            painter.setBrush(QColor("#a855f7"))
            painter.drawEllipse(16, 14, 6, 6)

            painter.setPen(QPen(QColor("#555555"), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(3, 4, size - 8, size - 8)

        elif name == "zoom":
            painter.setPen(QPen(dark, 2))
            painter.drawEllipse(5, 5, 12, 12)
            painter.drawLine(15, 15, 22, 22)

        else:
            painter.setPen(QPen(dark, 1))
            painter.drawText(pixmap.rect(), Qt.AlignCenter, str(name))

        painter.end()
        return QIcon(pixmap)

    # ==================================================
    # RIBBON
    # ==================================================

    def _create_ribbon(self):
        ribbon = QFrame()
        ribbon.setObjectName("PaintRibbon")
        ribbon.setFixedHeight(108)

        layout = QHBoxLayout(ribbon)
        layout.setContentsMargins(8, 6, 8, 4)
        layout.setSpacing(0)

        layout.addWidget(self._create_selection_group())
        layout.addWidget(self._create_image_group())
        layout.addWidget(self._create_tools_group())
        layout.addWidget(self._create_shapes_group())
        layout.addWidget(self._create_colours_group())
        layout.addStretch()

        return ribbon

    def _wrap_group(self, title, content_widget, width=None):
        group = QFrame()
        group.setObjectName("RibbonGroup")

        if width is not None:
            group.setFixedWidth(width)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(2)

        layout.addWidget(content_widget, 1)

        title_label = QLabel(title)
        title_label.setObjectName("RibbonTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(18)

        layout.addWidget(title_label)

        return group

    def _create_icon_button(
        self,
        icon,
        tooltip,
        slot=None,
        size=28,
        checkable=False,
    ):
        btn = QToolButton()
        btn.setToolTip(tooltip)
        btn.setFixedSize(size, size)
        btn.setCheckable(checkable)

        icon_names = {
            "select",
            "pencil",
            "brush",
            "fill",
            "text",
            "eraser",
            "palette",
            "zoom",
        }

        if icon in icon_names:
            btn.setIcon(self._make_tool_icon(icon, size - 4))
            btn.setIconSize(QSize(size - 8, size - 8))
        else:
            btn.setText(str(icon))

        if slot is not None:
            btn.clicked.connect(slot)

        return btn

    # ==================================================
    # GROUP SELECTION
    # ==================================================

    def _create_selection_group(self):
        content = QWidget()

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(2)

        btn_select = self._create_icon_button(
            "select",
            "Select",
            lambda: self.set_tool(Tool.SELECT),
            size=44,
            checkable=True,
        )

        self.tool_buttons[Tool.SELECT] = btn_select

        layout.addWidget(btn_select, alignment=Qt.AlignCenter)
        layout.addStretch()

        return self._wrap_group("Selection", content, 76)

    # ==================================================
    # GROUP IMAGE
    # ==================================================

    def _create_image_group(self):
        content = QWidget()

        grid = QGridLayout(content)
        grid.setContentsMargins(0, 4, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(4)

        buttons = [
            ("N", "New Canvas", self.new_canvas),
            ("O", "Open Image", self.open_image),
            ("S", "Save Image", self.save_image),
            ("⤢", "Resize Canvas", self.resize_canvas),
            ("↩", "Undo", self.canvas.undo),
            ("↪", "Redo", self.canvas.redo),
        ]

        for index, (icon, tooltip, slot) in enumerate(buttons):
            btn = self._create_icon_button(icon, tooltip, slot, size=26)
            grid.addWidget(btn, index // 3, index % 3)

        return self._wrap_group("Image", content, 156)

    # ==================================================
    # GROUP TOOLS
    # ==================================================

    def _create_tools_group(self):
        content = QWidget()

        grid = QGridLayout(content)
        grid.setContentsMargins(0, 2, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)

        tools = [
            ("pencil", "Pencil", Tool.PENCIL),
            ("brush", "Brush", Tool.BRUSH),
            ("fill", "Fill", Tool.FILL),
            ("eraser", "Eraser", Tool.ERASER),
            ("text", "Text", Tool.TEXT),
            ("zoom", "Zoom", None),
        ]

        for index, (icon_key, tooltip, tool) in enumerate(tools):
            if tool is None:
                btn = self._create_icon_button(
                    icon_key,
                    tooltip,
                    None,
                    size=30,
                    checkable=False,
                )
            else:
                btn = self._create_icon_button(
                    icon_key,
                    tooltip,
                    lambda checked=False, t=tool: self.set_tool(t),
                    size=30,
                    checkable=True,
                )
                self.tool_buttons[tool] = btn

            grid.addWidget(btn, index // 3, index % 3)

        return self._wrap_group("Tools", content, 136)

    # ==================================================
    # GROUP SHAPES
    # ==================================================

    def _create_shapes_group(self):
        content = QWidget()
        content.setFixedSize(190, 72)

        content.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }

            QFrame#ShapeBox {
                background-color: #ffffff;
                border: 1px solid #cfcfcf;
                border-radius: 3px;
            }

            QToolButton {
                background-color: #ffffff;
                border: 1px solid transparent;
                border-radius: 2px;
                padding: 0px;
                font-size: 16px;
                color: #222222;
            }

            QToolButton:hover {
                background-color: #eaf4ff;
                border: 1px solid #0078d7;
            }

            QToolButton:checked {
                background-color: #cce8ff;
                border: 1px solid #0078d7;
            }

            QScrollArea {
                background-color: #ffffff;
                border: none;
            }

            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 10px;
                border: none;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background-color: #a6a6a6;
                min-height: 20px;
                border-radius: 2px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
        """)

        outer = QVBoxLayout(content)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        shape_box = QFrame()
        shape_box.setObjectName("ShapeBox")

        shape_box_layout = QVBoxLayout(shape_box)
        shape_box_layout.setContentsMargins(2, 2, 2, 2)
        shape_box_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        grid_content = QWidget()

        grid = QGridLayout(grid_content)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setHorizontalSpacing(2)
        grid.setVerticalSpacing(2)

        shapes = [
            ("╲", "Line", Tool.LINE),
            ("⌒", "Curve", Tool.CURVE),
            ("○", "Circle", Tool.CIRCLE),
            ("▭", "Ellipse", Tool.ELLIPSE),
            ("□", "Rectangle", Tool.RECTANGLE),
            ("▱", "Rounded Rectangle", Tool.ROUNDED_RECTANGLE),
            ("△", "Triangle", Tool.TRIANGLE),
            ("◇", "Diamond", Tool.DIAMOND),
            ("⬟", "Pentagon", Tool.PENTAGON),
            ("⬢", "Hexagon", Tool.HEXAGON),
            ("→", "Arrow Right", Tool.ARROW_RIGHT),
            ("←", "Arrow Left", Tool.ARROW_LEFT),
            ("↑", "Arrow Up", Tool.ARROW_UP),
            ("↓", "Arrow Down", Tool.ARROW_DOWN),
            ("★", "Star", Tool.STAR),
            ("✩", "Star Alt", Tool.STAR),
            ("☁", "Cloud", Tool.ELLIPSE),
            ("◌", "Bubble", Tool.ROUNDED_RECTANGLE),
        ]

        for index, (icon, tooltip, tool) in enumerate(shapes):
            btn = QToolButton()
            btn.setText(icon)
            btn.setToolTip(tooltip)
            btn.setCheckable(True)
            btn.setFixedSize(24, 20)
            btn.clicked.connect(lambda checked=False, t=tool: self.set_tool(t))

            row = index // 6
            col = index % 6

            grid.addWidget(btn, row, col)
            self.shape_buttons[tool] = btn

        scroll_area.setWidget(grid_content)
        shape_box_layout.addWidget(scroll_area)

        outer.addWidget(shape_box)

        return self._wrap_group("Shapes", content, 230)

    # ==================================================
    # GROUP COLOURS
    # ==================================================

    def _create_colours_group(self):
        content = QWidget()
        content.setFixedSize(330, 72)

        layout = QHBoxLayout(content)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(8)

        self.current_color_btn = QPushButton()
        self.current_color_btn.setFixedSize(34, 34)
        self.current_color_btn.clicked.connect(self.pick_color)
        layout.addWidget(self.current_color_btn, alignment=Qt.AlignTop)

        palette = QWidget()
        palette_layout = QGridLayout(palette)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setHorizontalSpacing(5)
        palette_layout.setVerticalSpacing(5)

        colors = [
            "#000000", "#ffffff", "#7f7f7f", "#c3c3c3",
            "#880015", "#ed1c24", "#ff7f27", "#fff200",
            "#22b14c", "#00a2e8", "#3f48cc", "#a349a4",

            "#ffffff", "#f2f2f2", "#bfbfbf", "#808080",
            "#b97a57", "#ffaec9", "#ffc90e", "#efe4b0",
            "#b5e61d", "#99d9ea", "#7092be", "#c8bfe7",

            "#ffffff", "#ffffff", "#ffffff", "#ffffff",
            "#ffffff", "#ffffff", "#ffffff", "#ffffff",
            "#ffffff", "#ffffff", "#ffffff", "#ffffff",
        ]

        for index, color in enumerate(colors):
            btn = QPushButton()
            btn.setFixedSize(18, 18)
            btn.setToolTip(color)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #a0a0a0;
                    border-radius: 9px;
                    padding: 0px;
                }}

                QPushButton:hover {{
                    border: 2px solid #0078d4;
                }}
                """
            )
            btn.clicked.connect(lambda checked=False, c=color: self.set_color(QColor(c)))
            palette_layout.addWidget(btn, index // 12, index % 12)

        layout.addWidget(palette)

        more_color_btn = self._create_icon_button(
            "palette",
            "Pilih Warna",
            self.pick_color,
            size=32,
        )
        layout.addWidget(more_color_btn, alignment=Qt.AlignTop)

        self._update_current_color_preview()

        return self._wrap_group("Colours", content, 354)

    # ==================================================
    # SIDE PANEL SIZE & ZOOM
    # ==================================================

    def _create_side_panel(self):
        panel = QWidget()
        panel.setFixedWidth(62)

        panel.setStyleSheet("""
            QWidget {
                background-color: #f3f3f3;
            }

            QFrame#MiniBox {
                background-color: #fbfbfb;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }

            QLabel {
                color: #666666;
                background-color: transparent;
            }

            QSlider::groove:vertical {
                background: transparent;
                width: 18px;
            }

            QSlider::add-page:vertical {
                background: #0078d7;
                width: 4px;
                border-radius: 2px;
                margin-left: 7px;
                margin-right: 7px;
            }

            QSlider::sub-page:vertical {
                background: #9a9a9a;
                width: 4px;
                border-radius: 2px;
                margin-left: 7px;
                margin-right: 7px;
            }

            QSlider::handle:vertical {
                background: white;
                border: 4px solid #0078d7;
                width: 10px;
                height: 10px;
                margin: -6px 0px;
                border-radius: 9px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 22, 10, 8)
        layout.setSpacing(12)

        size_box = QFrame()
        size_box.setObjectName("MiniBox")
        size_box.setFixedSize(40, 292)

        size_layout = QVBoxLayout(size_box)
        size_layout.setContentsMargins(4, 8, 4, 8)
        size_layout.setSpacing(6)

        size_icon = QLabel("▤")
        size_icon.setAlignment(Qt.AlignCenter)

        self.size_slider = QSlider(Qt.Vertical)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(3)
        self.size_slider.setInvertedAppearance(False)
        self.size_slider.setInvertedControls(False)
        self.size_slider.valueChanged.connect(self._sync_size_from_slider)

        size_layout.addWidget(size_icon)
        size_layout.addWidget(self.size_slider)

        zoom_box = QFrame()
        zoom_box.setObjectName("MiniBox")
        zoom_box.setFixedSize(40, 292)

        zoom_layout = QVBoxLayout(zoom_box)
        zoom_layout.setContentsMargins(4, 8, 4, 8)
        zoom_layout.setSpacing(6)

        zoom_icon = QLabel("◓")
        zoom_icon.setAlignment(Qt.AlignCenter)

        self.zoom_slider_left = QSlider(Qt.Vertical)
        self.zoom_slider_left.setRange(50, 200)
        self.zoom_slider_left.setValue(100)
        self.zoom_slider_left.setInvertedAppearance(False)
        self.zoom_slider_left.setInvertedControls(False)
        self.zoom_slider_left.valueChanged.connect(self._on_zoom_changed)

        zoom_layout.addWidget(zoom_icon)
        zoom_layout.addWidget(self.zoom_slider_left)

        layout.addWidget(size_box)
        layout.addWidget(zoom_box)
        layout.addStretch()

        return panel

    # ==================================================
    # STATUS BAR
    # ==================================================

    def _create_status_bar(self):
        status = QFrame()
        status.setObjectName("StatusBar")
        status.setFixedHeight(34)

        layout = QHBoxLayout(status)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(14)

        pointer_label = QLabel("⌖")
        pointer_label.setFixedWidth(18)

        selection_label = QLabel("□")
        selection_label.setFixedWidth(18)

        self.canvas_size_label = QLabel("1152 × 648px")
        self.current_tool_label = QLabel("Tool: Pencil")

        layout.addWidget(pointer_label)
        layout.addSpacing(80)
        layout.addWidget(selection_label)
        layout.addSpacing(80)
        layout.addWidget(self.canvas_size_label)
        layout.addSpacing(20)
        layout.addWidget(self.current_tool_label)

        layout.addStretch()

        zoom_icon_left = QLabel("⊖")
        zoom_icon_right = QLabel("⊕")

        self.zoom_percent_label = QLabel("100%")
        self.zoom_percent_label.setFixedWidth(70)
        self.zoom_percent_label.setAlignment(Qt.AlignCenter)
        self.zoom_percent_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        self.zoom_slider_bottom = QSlider(Qt.Horizontal)
        self.zoom_slider_bottom.setRange(50, 200)
        self.zoom_slider_bottom.setValue(100)
        self.zoom_slider_bottom.setFixedWidth(130)
        self.zoom_slider_bottom.valueChanged.connect(self._on_zoom_changed)

        layout.addWidget(self.zoom_percent_label)
        layout.addWidget(zoom_icon_left)
        layout.addWidget(self.zoom_slider_bottom)
        layout.addWidget(zoom_icon_right)

        return status

    # ==================================================
    # ANIMATION GROUP
    # ==================================================

    def _create_animation_group(self):
        anim_group = QGroupBox("✨ Animasi Seleksi")

        anim_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078d7;
                border-radius: 4px;
                margin-top: 8px;
                padding: 6px;
                background-color: #f0f8ff;
                color: #0078d7;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 8px;
                padding: 0 4px;
                color: #0078d7;
                background-color: #f0f8ff;
            }
        """)

        anim_layout = QHBoxLayout()
        anim_layout.setContentsMargins(8, 6, 8, 6)
        anim_layout.setSpacing(8)

        self.anim_status = QLabel("Pilih area dengan Select, lalu pilih animasi:")
        self.anim_status.setStyleSheet(
            "color: #555555; font-weight: normal; background-color: transparent;"
        )

        anim_layout.addWidget(self.anim_status)
        anim_layout.addSpacing(16)

        self.btn_bounce = QPushButton("🏀 Bounce")
        self.btn_bounce.setCheckable(True)
        self.btn_bounce.setEnabled(False)
        self.btn_bounce.setFixedWidth(100)
        self.btn_bounce.setStyleSheet(self._anim_btn_style("#e67e22"))
        self.btn_bounce.clicked.connect(
            lambda: self._toggle_anim("bounce", self.btn_bounce)
        )
        anim_layout.addWidget(self.btn_bounce)

        self.btn_pulse = QPushButton("💗 Pulse")
        self.btn_pulse.setCheckable(True)
        self.btn_pulse.setEnabled(False)
        self.btn_pulse.setFixedWidth(90)
        self.btn_pulse.setStyleSheet(self._anim_btn_style("#e74c3c"))
        self.btn_pulse.clicked.connect(
            lambda: self._toggle_anim("pulse", self.btn_pulse)
        )
        anim_layout.addWidget(self.btn_pulse)

        self.btn_spin = QPushButton("🌀 Spin")
        self.btn_spin.setCheckable(True)
        self.btn_spin.setEnabled(False)
        self.btn_spin.setFixedWidth(80)
        self.btn_spin.setStyleSheet(self._anim_btn_style("#8e44ad"))
        self.btn_spin.clicked.connect(
            lambda: self._toggle_anim("spin", self.btn_spin)
        )
        anim_layout.addWidget(self.btn_spin)

        self.btn_stop_anim = QPushButton("⏹ Stop")
        self.btn_stop_anim.setEnabled(False)
        self.btn_stop_anim.setFixedWidth(80)
        self.btn_stop_anim.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px 12px;
                color: #2c3e50;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #d5dbdb;
            }

            QPushButton:disabled {
                color: #aaaaaa;
                background-color: #eeeeee;
            }
        """)
        self.btn_stop_anim.clicked.connect(self._stop_anim)
        anim_layout.addWidget(self.btn_stop_anim)

        anim_layout.addStretch()
        anim_group.setLayout(anim_layout)

        return anim_group

    def _anim_btn_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 6px;
                padding: 4px 14px;
                color: {color};
                font-weight: bold;
                font-size: 12px;
            }}

            QPushButton:hover {{
                background-color: {color};
                color: white;
            }}

            QPushButton:checked {{
                background-color: {color};
                color: white;
            }}

            QPushButton:disabled {{
                border-color: #cccccc;
                color: #cccccc;
                background-color: white;
            }}
        """

    # ==================================================
    # COLOR
    # ==================================================

    def set_color(self, color):
        if color.isValid():
            self.current_color = color
            self.canvas.pen_color = color
            self._update_current_color_preview()

    def _update_current_color_preview(self):
        if hasattr(self, "current_color_btn"):
            self.current_color_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self.current_color.name()};
                    border: 3px solid #0078d4;
                    border-radius: 17px;
                    padding: 0px;
                }}
                """
            )

    # ==================================================
    # ANIMATION CONTROL
    # ==================================================

    def on_selection_changed(self, has_selection: bool):
        self.anim_group.setVisible(has_selection)

        self.btn_bounce.setEnabled(has_selection)
        self.btn_pulse.setEnabled(has_selection)
        self.btn_spin.setEnabled(has_selection)

        if has_selection:
            self.anim_status.setText("Area terpilih! Pilih efek animasi:")
            self.anim_status.setStyleSheet(
                "color: #0078d7; font-weight: bold; background-color: transparent;"
            )
        else:
            self._stop_anim()
            self.anim_status.setText("Pilih area dengan Select, lalu pilih animasi:")
            self.anim_status.setStyleSheet(
                "color: #555555; font-weight: normal; background-color: transparent;"
            )

    def _toggle_anim(self, mode: str, btn: QPushButton):
        anim_btns = [self.btn_bounce, self.btn_pulse, self.btn_spin]

        for b in anim_btns:
            if b is not btn:
                b.setChecked(False)

        if btn.isChecked():
            self.canvas.start_animation(mode)
            self.btn_stop_anim.setEnabled(True)
            self.anim_status.setText(f"▶ Animasi '{mode}' berjalan...")
            self.anim_status.setStyleSheet(
                "color: #27ae60; font-weight: bold; background-color: transparent;"
            )
        else:
            self._stop_anim()

    def _stop_anim(self):
        self.canvas.stop_animation()

        self.btn_bounce.setChecked(False)
        self.btn_pulse.setChecked(False)
        self.btn_spin.setChecked(False)
        self.btn_stop_anim.setEnabled(False)

        if hasattr(self.canvas, "_select_rect") and not self.canvas._select_rect.isNull():
            self.anim_status.setText("Area terpilih! Pilih efek animasi:")
            self.anim_status.setStyleSheet(
                "color: #0078d7; font-weight: bold; background-color: transparent;"
            )
        else:
            self.anim_status.setText("Pilih area dengan Select, lalu pilih animasi:")
            self.anim_status.setStyleSheet(
                "color: #555555; font-weight: normal; background-color: transparent;"
            )

    # ==================================================
    # CANVAS AWAL
    # ==================================================

    def showEvent(self, event):
        super().showEvent(event)

        if not hasattr(self, "_initial_resize_done"):
            self._initial_resize_done = True
            self._fit_canvas_to_window()

    def _fit_canvas_to_window(self):
        width = 1152
        height = 648

        self.canvas.resize_canvas(width, height)
        self.canvas.setFixedSize(width, height)

        self._update_canvas_size_label()

    def _update_canvas_size_label(self):
        if hasattr(self, "canvas_size_label"):
            if hasattr(self.canvas, "canvas"):
                self.canvas_size_label.setText(
                    f"{self.canvas.canvas.width()} × {self.canvas.canvas.height()}px"
                )
            else:
                self.canvas_size_label.setText(
                    f"{self.canvas.width()} × {self.canvas.height()}px"
                )

    # ==================================================
    # SHORTCUTS
    # ==================================================

    def _setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+Z", self.canvas.undo),
            ("Ctrl+Y", self.canvas.redo),
            ("Ctrl+Shift+Z", self.canvas.redo),
            ("Ctrl+S", self.save_image),
            ("Ctrl+O", self.open_image),
            ("Ctrl+N", self.new_canvas),

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
            ("Escape", self._on_escape),
        ]

        for key, slot in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(slot)

    def _on_escape(self):
        self._stop_anim()

        if hasattr(self.canvas, "_select_rect"):
            self.canvas._select_rect.setRect(0, 0, 0, 0)

        self.on_selection_changed(False)
        self.canvas.update()

    def _increase_size(self):
        self.size_box.setValue(min(self.size_box.value() + 1, 50))

    def _decrease_size(self):
        self.size_box.setValue(max(self.size_box.value() - 1, 1))

    # ==================================================
    # TOOL
    # ==================================================

    def set_tool(self, tool):
        self.canvas.current_tool = tool

        if hasattr(self, "current_tool_label"):
            self.current_tool_label.setText(f"Tool: {tool.name.title()}")

        for tool_key, btn in self.tool_buttons.items():
            btn.setChecked(tool_key == tool)

        for shape_tool, btn in self.shape_buttons.items():
            btn.setChecked(shape_tool == tool)

    def pick_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        self.set_color(color)

    def change_size(self):
        value = self.size_box.value()
        self.canvas.pen_size = value

        if hasattr(self, "size_slider"):
            self.size_slider.blockSignals(True)
            self.size_slider.setValue(value)
            self.size_slider.blockSignals(False)

    def _sync_size_from_slider(self, value):
        self.size_box.blockSignals(True)
        self.size_box.setValue(value)
        self.size_box.blockSignals(False)

        self.canvas.pen_size = value

    def _on_zoom_changed(self, value):
        if hasattr(self, "zoom_percent_label"):
            self.zoom_percent_label.setText(f"{value}%")

        if hasattr(self, "zoom_slider_left"):
            self.zoom_slider_left.blockSignals(True)
            self.zoom_slider_left.setValue(value)
            self.zoom_slider_left.blockSignals(False)

        if hasattr(self, "zoom_slider_bottom"):
            self.zoom_slider_bottom.blockSignals(True)
            self.zoom_slider_bottom.setValue(value)
            self.zoom_slider_bottom.blockSignals(False)

    # ==================================================
    # FILE
    # ==================================================

    def new_canvas(self):
        reply = QMessageBox.question(
            self,
            "New Canvas",
            "Bersihkan canvas?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.clear_canvas()
            self._update_canvas_size_label()

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG (*.png);;JPG (*.jpg)"
        )

        if filename:
            self.canvas.canvas.save(filename)

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if filename:
            pixmap = QPixmap(filename)

            if pixmap.isNull():
                QMessageBox.warning(
                    self,
                    "Open Image",
                    "Gambar gagal dibuka."
                )
                return

            self.canvas.canvas = pixmap.scaled(
                self.canvas.canvas.width(),
                self.canvas.canvas.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.canvas.update()
            self._update_canvas_size_label()

    def resize_canvas(self):
        width, ok = QInputDialog.getInt(
            self,
            "Canvas Width",
            "Width:",
            self.canvas.canvas.width(),
            100,
            5000
        )

        if not ok:
            return

        height, ok = QInputDialog.getInt(
            self,
            "Canvas Height",
            "Height:",
            self.canvas.canvas.height(),
            100,
            5000
        )

        if not ok:
            return

        self.canvas.resize_canvas(width, height)
        self.canvas.setFixedSize(width, height)
        self._update_canvas_size_label()