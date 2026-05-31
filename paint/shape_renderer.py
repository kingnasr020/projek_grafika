from PyQt5.QtGui import QPainter, QPen, QPolygon
from PyQt5.QtCore import QPoint
from .tools import Tool
import math


class ShapeRenderer:
    """
    Menggambar semua bentuk geometri (shape) ke canvas.
    Dipanggil saat mouseRelease untuk shape yang sudah final.
    """

    def __init__(self, canvas_ref):
        self.ref = canvas_ref

    def _make_painter(self):
        painter = QPainter(self.ref.canvas)
        pen = QPen(self.ref.pen_color)
        pen.setWidth(self.ref.pen_size)
        painter.setPen(pen)
        return painter

    # ==================================================
    # DISPATCH
    # ==================================================

    def draw_shape(self, tool, x1, y1, x2, y2):
        """Entry point — pilih shape berdasarkan tool aktif."""

        if tool == Tool.LINE:
            self.ref.algorithms.draw_bresenham(x1, y1, x2, y2)

        elif tool == Tool.RECTANGLE:
            self._draw_rectangle(x1, y1, x2, y2)

        elif tool == Tool.ROUNDED_RECTANGLE:
            self._draw_rounded_rectangle(x1, y1, x2, y2)

        elif tool == Tool.ELLIPSE:
            self._draw_ellipse(x1, y1, x2, y2)

        elif tool == Tool.CIRCLE:
            self._draw_circle(x1, y1, x2, y2)

        elif tool == Tool.TRIANGLE:
            self._draw_triangle(x1, y1, x2, y2)

        elif tool == Tool.DIAMOND:
            self._draw_diamond(x1, y1, x2, y2)

        elif tool == Tool.PENTAGON:
            self._draw_polygon(x1, y1, x2, y2, sides=5, offset=-90)

        elif tool == Tool.HEXAGON:
            self._draw_polygon(x1, y1, x2, y2, sides=6, offset=0)

        elif tool == Tool.STAR:
            self._draw_star(x1, y1, x2, y2)

        elif tool in [Tool.ARROW_RIGHT, Tool.ARROW_LEFT,
                      Tool.ARROW_UP, Tool.ARROW_DOWN]:
            self._draw_arrow(tool, x1, y1, x2, y2)

    # ==================================================
    # BASIC SHAPES
    # ==================================================

    def _draw_rectangle(self, x1, y1, x2, y2):
        p = self._make_painter()
        p.drawRect(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))

    def _draw_rounded_rectangle(self, x1, y1, x2, y2):
        p = self._make_painter()
        p.drawRoundedRect(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1), 20, 20)

    def _draw_ellipse(self, x1, y1, x2, y2):
        p = self._make_painter()
        p.drawEllipse(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))

    def _draw_circle(self, x1, y1, x2, y2):
        # Center = tengah bounding box, radius = setengah sisi terpendek
        # sehingga lingkaran selalu pas di dalam area yang di-drag
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        radius = min(abs(x2 - x1), abs(y2 - y1)) // 2
        self.ref.algorithms.draw_circle(cx, cy, radius)

    # ==================================================
    # POLYGON SHAPES
    # ==================================================

    def _draw_triangle(self, x1, y1, x2, y2):
        p = self._make_painter()
        poly = QPolygon([
            QPoint((x1+x2)//2, y1),
            QPoint(x1, y2),
            QPoint(x2, y2),
        ])
        p.drawPolygon(poly)

    def _draw_diamond(self, x1, y1, x2, y2):
        p = self._make_painter()
        cx = (x1+x2)//2
        cy = (y1+y2)//2
        poly = QPolygon([
            QPoint(cx, y1),
            QPoint(x2, cy),
            QPoint(cx, y2),
            QPoint(x1, cy),
        ])
        p.drawPolygon(poly)

    def _draw_polygon(self, x1, y1, x2, y2, sides, offset):
        """Generic regular polygon dengan jumlah sisi dan sudut offset tertentu."""
        p = self._make_painter()
        cx = (x1+x2) / 2
        cy = (y1+y2) / 2
        r = min(abs(x2-x1), abs(y2-y1)) / 2

        pts = []
        for i in range(sides):
            angle = math.radians(i * (360/sides) + offset)
            pts.append(QPoint(int(cx + r*math.cos(angle)),
                               int(cy + r*math.sin(angle))))

        p.drawPolygon(QPolygon(pts))

    # ==================================================
    # STAR
    # ==================================================

    def _draw_star(self, x1, y1, x2, y2):
        p = self._make_painter()
        cx = (x1+x2) / 2
        cy = (y1+y2) / 2
        r_outer = min(abs(x2-x1), abs(y2-y1)) / 2
        r_inner = r_outer * 0.4

        pts = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append(QPoint(int(cx + r*math.cos(angle)),
                               int(cy + r*math.sin(angle))))

        p.drawPolygon(QPolygon(pts))

    # ==================================================
    # ARROWS
    # ==================================================

    def _draw_arrow(self, tool, x1, y1, x2, y2):
        p = self._make_painter()
        cx = (x1+x2) / 2
        cy = (y1+y2) / 2
        w = abs(x2-x1)
        h = abs(y2-y1)

        shaft_ratio = 0.4   # lebar batang relatif terhadap dimensi
        head_ratio  = 0.5   # panjang kepala relatif terhadap dimensi

        if tool == Tool.ARROW_RIGHT:
            pts = [
                QPoint(x1,                      int(cy - h*shaft_ratio/2)),
                QPoint(int(x2 - w*head_ratio),  int(cy - h*shaft_ratio/2)),
                QPoint(int(x2 - w*head_ratio),  y1),
                QPoint(x2,                      int(cy)),
                QPoint(int(x2 - w*head_ratio),  y2),
                QPoint(int(x2 - w*head_ratio),  int(cy + h*shaft_ratio/2)),
                QPoint(x1,                      int(cy + h*shaft_ratio/2)),
            ]

        elif tool == Tool.ARROW_LEFT:
            pts = [
                QPoint(x2,                      int(cy - h*shaft_ratio/2)),
                QPoint(int(x1 + w*head_ratio),  int(cy - h*shaft_ratio/2)),
                QPoint(int(x1 + w*head_ratio),  y1),
                QPoint(x1,                      int(cy)),
                QPoint(int(x1 + w*head_ratio),  y2),
                QPoint(int(x1 + w*head_ratio),  int(cy + h*shaft_ratio/2)),
                QPoint(x2,                      int(cy + h*shaft_ratio/2)),
            ]

        elif tool == Tool.ARROW_UP:
            pts = [
                QPoint(int(cx - w*shaft_ratio/2), y2),
                QPoint(int(cx - w*shaft_ratio/2), int(y1 + h*head_ratio)),
                QPoint(x1,                        int(y1 + h*head_ratio)),
                QPoint(int(cx),                   y1),
                QPoint(x2,                        int(y1 + h*head_ratio)),
                QPoint(int(cx + w*shaft_ratio/2), int(y1 + h*head_ratio)),
                QPoint(int(cx + w*shaft_ratio/2), y2),
            ]

        elif tool == Tool.ARROW_DOWN:
            pts = [
                QPoint(int(cx - w*shaft_ratio/2), y1),
                QPoint(int(cx - w*shaft_ratio/2), int(y2 - h*head_ratio)),
                QPoint(x1,                        int(y2 - h*head_ratio)),
                QPoint(int(cx),                   y2),
                QPoint(x2,                        int(y2 - h*head_ratio)),
                QPoint(int(cx + w*shaft_ratio/2), int(y2 - h*head_ratio)),
                QPoint(int(cx + w*shaft_ratio/2), y1),
            ]

        else:
            return

        p.drawPolygon(QPolygon(pts))