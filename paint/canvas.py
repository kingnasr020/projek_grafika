from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QPolygon, QTransform
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, QRectF
import math


from .tools import Tool
from .drawing_algorithms import DrawingAlgorithms
from .shape_renderer import ShapeRenderer
from .flood_fill import FloodFill


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
        self.end_point   = QPoint()

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

        # --------------------------------------------------
        # SELECT tool — rubber-band selection
        # --------------------------------------------------
        self._select_start  = QPoint()
        self._select_rect   = QRect()        # normalized selection rect
        self._selecting     = False          # sedang drag

        # --------------------------------------------------
        # ANIMATION ENGINE
        # --------------------------------------------------
        # anim_mode: None | 'bounce' | 'pulse' | 'spin'
        self.anim_mode   = None
        self._anim_tick  = 0                 # frame counter (0..359)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)     # ~60 fps
        self._anim_timer.timeout.connect(self._on_anim_tick)

        # --------------------------------------------------
        # CURVE — state machine
        # --------------------------------------------------
        self._curve_phase = 0
        self._curve_p0    = QPoint()
        self._curve_p3    = QPoint()
        self._curve_cp1   = QPoint()
        self._curve_cp2   = QPoint()

    # ==================================================
    # ANIMATION CONTROL  (called from PaintTab)
    # ==================================================

    def start_animation(self, mode: str):
        """mode: 'bounce' | 'pulse' | 'spin'"""
        if self._select_rect.isNull():
            return
        self.anim_mode  = mode
        self._anim_tick = 0
        self._anim_timer.start()
        self.update()

    def stop_animation(self):
        self._anim_timer.stop()
        self.anim_mode = None
        self.update()

    def _on_anim_tick(self):
        self._anim_tick = (self._anim_tick + 2) % 360
        self.update()

    # ==================================================
    # PAINT
    # ==================================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)

        # --- Preview Curve ---
        if self.current_tool == Tool.CURVE and (
                self._curve_phase > 0 or self.drawing):
            self._paint_curve_preview(painter)
            return

        # --- Selection rectangle (dashed) ---
        if not self._select_rect.isNull():
            if self.anim_mode:
                self._paint_animated_selection(painter)
            else:
                pen = QPen(QColor("#0078d7"), 1, Qt.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(self._select_rect)
                # corner handles
                self._draw_handles(painter, self._select_rect)

        if not self.preview_shape:
            return

        # --- Shape preview ---
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
            pts = [QPoint(int(cx + r*math.cos(math.radians(i*72-90))),
                          int(cy + r*math.sin(math.radians(i*72-90)))) for i in range(5)]
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool == Tool.HEXAGON:
            pts = [QPoint(int(cx + r*math.cos(math.radians(i*60))),
                          int(cy + r*math.sin(math.radians(i*60)))) for i in range(6)]
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool == Tool.STAR:
            r_in = r * 0.4
            pts = []
            for i in range(10):
                angle = math.radians(i * 36 - 90)
                rad = r if i % 2 == 0 else r_in
                pts.append(QPoint(int(cx + rad*math.cos(angle)),
                                  int(cy + rad*math.sin(angle))))
            painter.drawPolygon(QPolygon(pts))

        elif self.current_tool in [Tool.ARROW_RIGHT, Tool.ARROW_LEFT,
                                    Tool.ARROW_UP,    Tool.ARROW_DOWN]:
            painter.drawRect(min(x1, x2), min(y1, y2), w, h)

    # --------------------------------------------------
    # ANIMATED SELECTION OVERLAY
    # --------------------------------------------------

    def _paint_animated_selection(self, painter: QPainter):
        """Render the selected region with Bounce / Pulse / Spin effect."""
        rect = self._select_rect
        if rect.isNull():
            return

        # Crop the selected pixels from canvas
        src_pixmap = self.canvas.copy(rect)

        cx = rect.center().x()
        cy = rect.center().y()
        t  = self._anim_tick  # 0-359

        painter.save()
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # ---- BOUNCE ----
        # Vertical sine wave offset + slight vertical squash/stretch
        if self.anim_mode == 'bounce':
            amplitude = rect.height() * 0.18
            offset_y  = -abs(math.sin(math.radians(t * 2))) * amplitude

            # squash when at bottom, stretch when at top
            phase = abs(math.sin(math.radians(t * 2)))  # 0=top 1=bottom
            scale_y = 1.0 - 0.12 * phase      # squash at bottom
            scale_x = 1.0 + 0.08 * phase      # widen at bottom

            transform = QTransform()
            transform.translate(cx, cy + offset_y)
            transform.scale(scale_x, scale_y)
            transform.translate(-rect.width() / 2, -rect.height() / 2)

            painter.setTransform(transform)
            painter.drawPixmap(0, 0, src_pixmap)

            # shadow (gets bigger/darker at bottom of bounce)
            shadow_alpha = int(80 + 80 * phase)
            shadow_h = max(4, int(8 * phase))
            shadow_w = int(rect.width() * (0.6 + 0.4 * phase))
            painter.resetTransform()
            shadow_color = QColor(0, 0, 0, shadow_alpha)
            painter.setBrush(shadow_color)
            painter.setPen(Qt.NoPen)
            shadow_x = cx - shadow_w // 2
            shadow_y = rect.bottom() + 4
            painter.drawEllipse(shadow_x, shadow_y, shadow_w, shadow_h)

        # ---- PULSE ----
        # Scale in/out from center with fade on the border
        elif self.anim_mode == 'pulse':
            scale = 1.0 + 0.12 * math.sin(math.radians(t * 3))
            glow_alpha = int(180 + 75 * math.sin(math.radians(t * 3)))

            transform = QTransform()
            transform.translate(cx, cy)
            transform.scale(scale, scale)
            transform.translate(-rect.width() / 2, -rect.height() / 2)

            painter.setTransform(transform)
            painter.drawPixmap(0, 0, src_pixmap)

            # Pulsing glow border
            painter.resetTransform()
            glow_color = QColor(0, 120, 215, glow_alpha)
            pen = QPen(glow_color, 3 + 2 * math.sin(math.radians(t * 3)))
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            margin = 4
            painter.drawRect(
                rect.adjusted(-margin, -margin, margin, margin)
            )

        # ---- SPIN ----
        # Full rotation around center
        elif self.anim_mode == 'spin':
            angle = t  # 0-359 degrees

            transform = QTransform()
            transform.translate(cx, cy)
            transform.rotate(angle)
            transform.translate(-rect.width() / 2, -rect.height() / 2)

            painter.setTransform(transform)
            painter.drawPixmap(0, 0, src_pixmap)

            # Spinning dashed border that counter-rotates for contrast
            painter.resetTransform()
            counter_transform = QTransform()
            counter_transform.translate(cx, cy)
            counter_transform.rotate(-angle * 0.5)
            counter_transform.translate(-rect.width() / 2, -rect.height() / 2)
            painter.setTransform(counter_transform)

            border_color = QColor("#ff6b35")
            pen = QPen(border_color, 2, Qt.DashLine)
            pen.setDashPattern([6, 4])
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(0, 0, rect.width(), rect.height())

        painter.restore()

        # Draw selection border hint (always visible)
        painter.setPen(QPen(QColor("#0078d7"), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)

    def _draw_handles(self, painter: QPainter, rect: QRect):
        """Draw 8 resize handles around selection rect."""
        painter.setPen(QPen(QColor("#0078d7"), 1))
        painter.setBrush(QColor("white"))
        hs = 6
        corners = [
            rect.topLeft(), rect.topRight(),
            rect.bottomLeft(), rect.bottomRight(),
            QPoint(rect.center().x(), rect.top()),
            QPoint(rect.center().x(), rect.bottom()),
            QPoint(rect.left(),  rect.center().y()),
            QPoint(rect.right(), rect.center().y()),
        ]
        for pt in corners:
            painter.drawRect(pt.x() - hs//2, pt.y() - hs//2, hs, hs)

    # --------------------------------------------------
    # CURVE PREVIEW
    # --------------------------------------------------

    def _paint_curve_preview(self, painter):
        dash_pen  = QPen(QColor("gray"), 1, Qt.DashLine)
        curve_pen = QPen(self.pen_color, self.pen_size)

        p0  = self._curve_p0
        p3  = self._curve_p3
        cp1 = self._curve_cp1
        cp2 = self._curve_cp2

        if self._curve_phase == 0:
            painter.setPen(dash_pen)
            painter.drawLine(p0, p3)

        elif self._curve_phase == 1:
            painter.setPen(dash_pen)
            painter.drawLine(p0, p3)
            mid = QPoint((p0.x()+p3.x())//2, (p0.y()+p3.y())//2)
            painter.setBrush(QColor("gray"))
            painter.drawEllipse(mid.x()-4, mid.y()-4, 8, 8)

        elif self._curve_phase == 2:
            painter.setPen(curve_pen)
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

            painter.setPen(dash_pen)
            painter.drawLine(p0, cp1)
            painter.drawLine(p3, cp2)
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
        self._select_rect = QRect()
        self.stop_animation()
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

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.current_tool == Tool.CURVE:
            self._curve_mouse_press(event)
            return

        if self.current_tool == Tool.SELECT:
            # reset animation & previous selection
            self.stop_animation()
            self._select_rect   = QRect()
            self._select_start  = event.pos()
            self._selecting     = True
            self.update()
            return

        self.save_state()
        self.drawing     = True
        self.start_point = event.pos()
        self.end_point   = event.pos()

        if self.current_tool == Tool.FILL:
            self.filler.flood_fill(event.x(), event.y())
            self.update()

    # --------------------------------------------------
    # MOVE
    # --------------------------------------------------

    def mouseMoveEvent(self, event):
        if self.current_tool == Tool.CURVE:
            self._curve_mouse_move(event)
            return

        if self.current_tool == Tool.SELECT and self._selecting:
            # rubber-band
            self._select_rect = QRect(
                self._select_start, event.pos()
            ).normalized()
            self.update()
            return

        if not self.drawing:
            return

        if self.current_tool in self._SHAPE_TOOLS:
            self.preview_shape = True
            self.preview_end   = event.pos()
            self.update()
            return

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
        if self.current_tool == Tool.CURVE:
            self._curve_mouse_release(event)
            return

        if self.current_tool == Tool.SELECT:
            self._selecting = False
            # Finalize selection rect
            if not self._select_rect.isNull():
                self._select_rect = QRect(
                    self._select_start, event.pos()
                ).normalized()
                # Notify PaintTab to show animation buttons
                self._notify_selection_changed()
            self.update()
            return

        self.drawing   = False
        self.end_point = event.pos()

        x1 = self.start_point.x()
        y1 = self.start_point.y()
        x2 = self.end_point.x()
        y2 = self.end_point.y()

        self.shapes.draw_shape(self.current_tool, x1, y1, x2, y2)

        self.preview_shape = False
        self.update()

    def _notify_selection_changed(self):
        """Signal parent PaintTab that a selection was made."""
        # Walk up to find PaintTab and call its on_selection_changed()
        parent = self.parent()
        while parent:
            if hasattr(parent, 'on_selection_changed'):
                parent.on_selection_changed(not self._select_rect.isNull())
                break
            parent = parent.parent()

    # ==================================================
    # CURVE STATE MACHINE
    # ==================================================

    def _curve_mouse_press(self, event):
        pos = event.pos()
        if self._curve_phase == 0:
            self.save_state()
            self.drawing   = True
            self._curve_p0 = pos
            self._curve_p3 = pos
        elif self._curve_phase == 1:
            self._curve_cp1   = pos
            self._curve_cp2   = pos
            self._curve_phase = 2
            self.update()
        elif self._curve_phase == 2:
            self._curve_cp2 = pos
            self._commit_curve()

    def _curve_mouse_move(self, event):
        pos = event.pos()
        if self._curve_phase == 0 and self.drawing:
            self._curve_p3 = pos
            self.update()
        elif self._curve_phase == 2:
            self._curve_cp2 = pos
            self.update()

    def _curve_mouse_release(self, event):
        if self._curve_phase == 0 and self.drawing:
            self.drawing      = False
            self._curve_p3    = event.pos()
            self._curve_phase = 1
            self.update()

    def _commit_curve(self):
        self.algorithms.draw_bezier([
            self._curve_p0,
            self._curve_cp1,
            self._curve_cp2,
            self._curve_p3,
        ])
        self._curve_phase = 0
        self.drawing      = False
        self.update()