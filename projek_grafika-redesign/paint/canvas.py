from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QPolygon
from PyQt5.QtCore import Qt, QPoint

from .tools import Tool
from .drawing_algorithms import DrawingAlgorithms
from .shape_renderer import ShapeRenderer
from .flood_fill import FloodFill
from PyQt5.QtCore import Qt, QPoint, QRect
from .animation_engine import AnimationEngine

import math


class Canvas(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(1000, 700)

        self.canvas = QPixmap(1000, 700)
        self.canvas.fill(Qt.white)

        self.current_tool = Tool.PENCIL

        self.pen_color = QColor("black")
        self.pen_size = 3

        self.start_point = QPoint()
        self.end_point = QPoint()

        self.drawing = False

        self.undo_stack = []
        self.redo_stack = []

        # Preview Shape
        self.preview_shape = False
        self.preview_end = QPoint()

        # Text
        self.text_value = "Text"

        # Canvas Size
        self.canvas_width = 1000
        self.canvas_height = 700

        # Sub-modules
        self.algorithms = DrawingAlgorithms(self)
        self.shapes     = ShapeRenderer(self)
        self.filler     = FloodFill(self)
        # ==========================
        # SELECTION
        # ==========================

        self.selected_rect = QRect()
        self.selected_pixmap = None
        self.selecting = False

        # ==========================
        # ANIMATION
        # ==========================

        self.animation = AnimationEngine(self)

        # --------------------------------------------------
        # CURVE — state machine
        # Fase:
        #   0 = belum mulai
        #   1 = sudah drag garis awal (menunggu klik CP1)
        #   2 = sudah set CP1 (menunggu klik CP2)
        # --------------------------------------------------
        self._curve_phase  = 0
        self._curve_p0     = QPoint()   # titik awal
        self._curve_p3     = QPoint()   # titik akhir
        self._curve_cp1    = QPoint()   # control point 1
        self._curve_cp2    = QPoint()   # control point 2 (mouse saat ini)

    # ==================================================
    # PAINT
    # ==================================================

    def paintEvent(self, event):

        painter = QPainter(self)

        # gambar canvas utama
        painter.drawPixmap(0, 0, self.canvas)

        # gambar objek terseleksi dengan animasi
        if self.selected_pixmap:

            center = self.selected_rect.center()

            painter.save()

            painter.translate(
                center.x(),
                center.y() + self.animation.offset_y
            )

            painter.rotate(
                self.animation.rotation
            )

            painter.scale(
                self.animation.scale,
                self.animation.scale
            )

            painter.drawPixmap(
                -self.selected_pixmap.width() // 2,
                -self.selected_pixmap.height() // 2,
                self.selected_pixmap
            )

            painter.restore()

        # --- Preview Curve ---
        if self.current_tool == Tool.CURVE and (
                self._curve_phase > 0 or self.drawing):
            self._paint_curve_preview(painter)
            return

        if not self.preview_shape:
            return

        pen = QPen(QColor("gray"), 1, Qt.DashLine)
        painter.setPen(pen)

        x1 = self.start_point.x()
        y1 = self.start_point.y()
        x2 = self.preview_end.x()
        y2 = self.preview_end.y()

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        w  = abs(x2 - x1)
        h  = abs(y2 - y1)
        r  = min(w, h) / 2

        if self.current_tool == Tool.LINE:
            painter.drawLine(self.start_point, self.preview_end)

        elif self.current_tool == Tool.RECTANGLE:
            painter.drawRect(min(x1, x2), min(y1, y2), w, h)

        elif self.current_tool == Tool.ROUNDED_RECTANGLE:
            painter.drawRoundedRect(min(x1, x2), min(y1, y2), w, h, 20, 20)

        elif self.current_tool == Tool.ELLIPSE:
            painter.drawEllipse(min(x1, x2), min(y1, y2), w, h)

        elif self.current_tool == Tool.CIRCLE:
            # Preview lingkaran: dari center bounding box, radius = sisi terpendek / 2
            painter.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))

        elif self.current_tool == Tool.TRIANGLE:
            painter.drawPolygon(QPolygon([
                QPoint(int(cx), y1),
                QPoint(x1, y2),
                QPoint(x2, y2),
            ]))

        elif self.current_tool == Tool.DIAMOND:
            painter.drawPolygon(QPolygon([
                QPoint(int(cx), y1),
                QPoint(x2, int(cy)),
                QPoint(int(cx), y2),
                QPoint(x1, int(cy)),
            ]))

        elif self.current_tool == Tool.PENTAGON:
            import math as _m
            pts = [QPoint(int(cx + r*_m.cos(_m.radians(i*72-90))),
                          int(cy + r*_m.sin(_m.radians(i*72-90)))) for i in range(5)]
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool == Tool.HEXAGON:
            import math as _m
            pts = [QPoint(int(cx + r*_m.cos(_m.radians(i*60))),
                          int(cy + r*_m.sin(_m.radians(i*60)))) for i in range(6)]
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool == Tool.STAR:
            import math as _m
            r_in = r * 0.4
            pts = []
            for i in range(10):
                angle = _m.radians(i * 36 - 90)
                rad = r if i % 2 == 0 else r_in
                pts.append(QPoint(int(cx + rad*_m.cos(angle)), int(cy + rad*_m.sin(angle))))
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool in [Tool.ARROW_RIGHT, Tool.ARROW_LEFT,
                                    Tool.ARROW_UP,    Tool.ARROW_DOWN]:
            # Bounding box dashed sebagai preview arrow
            painter.drawRect(min(x1, x2), min(y1, y2), w, h)
        # tampilkan kotak seleksi
        if not self.selected_rect.isNull():

            pen = QPen(
                QColor(0, 120, 255),
                1,
                Qt.DashLine
            )

            painter.setPen(pen)

            painter.drawRect(
                self.selected_rect
            )

    def _paint_curve_preview(self, painter):
        """Gambar preview bezier + garis bantu control point."""
        dash_pen = QPen(QColor("gray"), 1, Qt.DashLine)
        curve_pen = QPen(self.pen_color, self.pen_size)

        p0 = self._curve_p0
        p3 = self._curve_p3
        cp1 = self._curve_cp1
        cp2 = self._curve_cp2

        if self._curve_phase == 0:
            # Sedang drag — preview garis lurus dari P0 ke posisi mouse (p3)
            painter.setPen(dash_pen)
            painter.drawLine(p0, p3)

        elif self._curve_phase == 1:
            # Drag selesai — preview garis lurus, tunggu klik CP1
            painter.setPen(dash_pen)
            painter.drawLine(p0, p3)
            # Tunjukkan hint: "klik untuk set control point"
            mid = QPoint((p0.x()+p3.x())//2, (p0.y()+p3.y())//2)
            painter.setBrush(QColor("gray"))
            painter.drawEllipse(mid.x()-4, mid.y()-4, 8, 8)

        elif self._curve_phase == 2:
            # CP1 sudah diklik, mouse = CP2 sementara
            # Gambar kurva bezier preview
            painter.setPen(curve_pen)
            pts = [p0, cp1, cp2, p3]
            prev = p0
            for i in range(1, 101):
                t = i / 100
                x = (
                    (1-t)**3 * p0.x()
                    + 3*(1-t)**2*t * cp1.x()
                    + 3*(1-t)*t**2 * cp2.x()
                    + t**3 * p3.x()
                )
                y = (
                    (1-t)**3 * p0.y()
                    + 3*(1-t)**2*t * cp1.y()
                    + 3*(1-t)*t**2 * cp2.y()
                    + t**3 * p3.y()
                )
                cur = QPoint(int(x), int(y))
                painter.drawLine(prev, cur)
                prev = cur

            # Garis bantu control point (tipis abu-abu)
            painter.setPen(dash_pen)
            painter.drawLine(p0, cp1)
            painter.drawLine(p3, cp2)

            # Titik control (kotak kecil)
            painter.setBrush(QColor("gray"))
            for pt in [cp1, cp2]:
                painter.drawRect(pt.x()-4, pt.y()-4, 8, 8)

    # ==================================================
    # UNDO / REDO
    # ==================================================

    def save_state(self):
        self.undo_stack.append(self.canvas.copy())
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self.canvas.copy())
        self.canvas = self.undo_stack.pop()
        self.update()

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self.canvas.copy())
        self.canvas = self.redo_stack.pop()
        self.update()

    # ==================================================
    # RESIZE CANVAS
    # ==================================================

    def resize_canvas(self, width, height):
        new_canvas = QPixmap(width, height)
        new_canvas.fill(Qt.white)
        painter = QPainter(new_canvas)
        painter.drawPixmap(0, 0, self.canvas)
        self.canvas = new_canvas
        self.canvas_width = width
        self.canvas_height = height
        self.setMinimumSize(width, height)
        self.update()

    # ==================================================
    # CLEAR
    # ==================================================

    def clear_canvas(self):
        self.save_state()
        self.canvas.fill(Qt.white)
        self.update()
    
    # ==================================================
    # MOUSE EVENTS
    # ==================================================

    _SHAPE_TOOLS = {
        Tool.LINE,
        Tool.RECTANGLE, Tool.ROUNDED_RECTANGLE,
        Tool.CIRCLE, Tool.ELLIPSE,
        Tool.TRIANGLE, Tool.DIAMOND,
        Tool.PENTAGON, Tool.HEXAGON,
        Tool.STAR,
        Tool.ARROW_RIGHT, Tool.ARROW_LEFT,
        Tool.ARROW_UP, Tool.ARROW_DOWN,
    }

    # --------------------------------------------------
    # PRESS
    # --------------------------------------------------
    def capture_selection(self):

        if self.selected_rect.isNull():
            return

        self.selected_pixmap = self.canvas.copy(
            self.selected_rect
        )

        self.update()
    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        # ---- CURVE state machine ----
        if self.current_tool == Tool.CURVE:
            self._curve_mouse_press(event)
            return

        self.save_state()
        self.drawing = True
        self.start_point = event.pos()
        self.end_point   = event.pos()

        if self.current_tool == Tool.FILL:
            self.filler.flood_fill(event.x(), event.y())
            self.update()

    # --------------------------------------------------
    # MOVE
    # --------------------------------------------------

    def mouseMoveEvent(self, event):

        # ---- CURVE ----
        if self.current_tool == Tool.CURVE:
            self._curve_mouse_move(event)
            return

        if not self.drawing:
            return
        # SELECT TOOL
        if self.current_tool == Tool.SELECT and self.selecting:

            self.selected_rect = QRect(
                self.start_point,
                event.pos()
            ).normalized()

            self.update()

            return
        # Preview shape tools
        if self.current_tool in self._SHAPE_TOOLS:
            self.preview_shape = True
            self.preview_end   = event.pos()
            self.update()
            return

        # Freehand
        if self.current_tool == Tool.PENCIL:
            self.algorithms.draw_dda(
                self.start_point.x(), self.start_point.y(),
                event.x(), event.y()
            )
            self.start_point = event.pos()
            self.update()

        elif self.current_tool == Tool.BRUSH:
            old_size = self.pen_size
            self.pen_size *= 3
            self.algorithms.draw_dda(
                self.start_point.x(), self.start_point.y(),
                event.x(), event.y()
            )
            self.pen_size = old_size
            self.start_point = event.pos()
            self.update()

        elif self.current_tool == Tool.ERASER:
            old_color = self.pen_color
            self.pen_color = QColor("white")
            self.algorithms.draw_dda(
                self.start_point.x(), self.start_point.y(),
                event.x(), event.y()
            )
            self.pen_color = old_color
            self.start_point = event.pos()
            self.update()

    # --------------------------------------------------
    # RELEASE
    # --------------------------------------------------

    def mouseReleaseEvent(self, event):
        # SELECT TOOL
        if self.current_tool == Tool.SELECT and self.selecting:

            self.selecting = False

            self.selected_rect = QRect(
                self.start_point,
                event.pos()
            ).normalized()

            self.capture_selection()

            return
        # ---- CURVE ----
        if self.current_tool == Tool.CURVE:
            self._curve_mouse_release(event)
            return

        self.drawing = False
        self.end_point = event.pos()
        # SELECT TOOL
        if self.current_tool == Tool.SELECT:

            self.selecting = True

            self.selected_rect = QRect(
                event.pos(),
                event.pos()
            )

            return
        x1 = self.start_point.x()
        y1 = self.start_point.y()
        x2 = self.end_point.x()
        y2 = self.end_point.y()

        self.shapes.draw_shape(self.current_tool, x1, y1, x2, y2)

        self.preview_shape = False
        self.update()

    # ==================================================
    # CURVE STATE MACHINE
    # ==================================================
    #
    # Alur penggunaan:
    #   1. Klik + drag  → tentukan P0 (awal) dan P3 (akhir)
    #   2. Release       → masuk fase 1, preview garis lurus
    #   3. Klik          → simpan CP1 di posisi klik, masuk fase 2
    #   4. Move          → preview kurva dengan CP2 = posisi mouse
    #   5. Klik          → simpan CP2, gambar kurva final, reset ke fase 0
    #
    # ==================================================

    def _curve_mouse_press(self, event):
        pos = event.pos()

        if self._curve_phase == 0:
            # Mulai drag garis awal
            self.save_state()
            self.drawing = True
            self._curve_p0 = pos
            self._curve_p3 = pos

        elif self._curve_phase == 1:
            # Klik pertama setelah drag: set CP1
            self._curve_cp1 = pos
            # CP2 default sama dengan CP1 dulu
            self._curve_cp2 = pos
            self._curve_phase = 2
            self.update()

        elif self._curve_phase == 2:
            # Klik kedua: set CP2 lalu commit kurva
            self._curve_cp2 = pos
            self._commit_curve()

    def _curve_mouse_move(self, event):
        pos = event.pos()

        if self._curve_phase == 0 and self.drawing:
            # Sedang drag garis awal
            self._curve_p3 = pos
            self.update()

        elif self._curve_phase == 2:
            # Gerakkan CP2
            self._curve_cp2 = pos
            self.update()

    def _curve_mouse_release(self, event):
        if self._curve_phase == 0 and self.drawing:
            self.drawing = False
            self._curve_p3 = event.pos()
            self._curve_phase = 1
            self.update()

    def _commit_curve(self):
        """Gambar kurva bezier final ke canvas lalu reset state."""
        self.algorithms.draw_bezier([
            self._curve_p0,
            self._curve_cp1,
            self._curve_cp2,
            self._curve_p3,
        ])
        self._curve_phase = 0
        self.drawing = False
        self.update()