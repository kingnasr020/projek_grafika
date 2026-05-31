from PyQt5.QtGui import QPainter, QPen


class DrawingAlgorithms:
    """
    Kumpulan algoritma menggambar garis dan kurva:
    - DDA (Digital Differential Analyzer)
    - Bresenham Line
    - Midpoint Circle
    - Bezier Cubic
    """

    def __init__(self, canvas_ref):
        # canvas_ref: objek Canvas yang punya atribut canvas, pen_color, pen_size
        self.ref = canvas_ref

    # ==================================================
    # DDA
    # ==================================================

    def draw_dda(self, x1, y1, x2, y2):

        painter = QPainter(self.ref.canvas)

        pen = QPen(self.ref.pen_color)
        pen.setWidth(self.ref.pen_size)
        painter.setPen(pen)

        dx = x2 - x1
        dy = y2 - y1

        steps = int(max(abs(dx), abs(dy)))

        if steps == 0:
            painter.drawPoint(x1, y1)
            return

        x_inc = dx / steps
        y_inc = dy / steps

        x = x1
        y = y1

        for _ in range(steps):
            painter.drawPoint(round(x), round(y))
            x += x_inc
            y += y_inc

    # ==================================================
    # BRESENHAM
    # ==================================================

    def draw_bresenham(self, x1, y1, x2, y2):

        painter = QPainter(self.ref.canvas)

        pen = QPen(self.ref.pen_color)
        pen.setWidth(self.ref.pen_size)
        painter.setPen(pen)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        err = dx - dy

        while True:
            painter.drawPoint(x1, y1)

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err

            if e2 > -dy:
                err -= dy
                x1 += sx

            if e2 < dx:
                err += dx
                y1 += sy

    # ==================================================
    # MIDPOINT CIRCLE
    # ==================================================

    def draw_circle(self, cx, cy, radius):

        painter = QPainter(self.ref.canvas)

        pen = QPen(self.ref.pen_color)
        pen.setWidth(self.ref.pen_size)
        painter.setPen(pen)

        x = radius
        y = 0
        p = 1 - radius

        while x >= y:
            pts = [
                (cx+x, cy+y), (cx-x, cy+y),
                (cx+x, cy-y), (cx-x, cy-y),
                (cx+y, cy+x), (cx-y, cy+x),
                (cx+y, cy-x), (cx-y, cy-x),
            ]

            for px, py in pts:
                painter.drawPoint(px, py)

            y += 1

            if p <= 0:
                p += 2*y + 1
            else:
                x -= 1
                p += 2*y - 2*x + 1

    # ==================================================
    # BEZIER CUBIC
    # ==================================================

    def draw_bezier(self, points):
        """points: list of 4 QPoint (P0, P1, P2, P3)"""

        if len(points) < 4:
            return

        painter = QPainter(self.ref.canvas)

        pen = QPen(self.ref.pen_color)
        pen.setWidth(self.ref.pen_size)
        painter.setPen(pen)

        for i in range(101):
            t = i / 100

            x = (
                (1-t)**3 * points[0].x()
                + 3*(1-t)**2 * t * points[1].x()
                + 3*(1-t) * t**2 * points[2].x()
                + t**3 * points[3].x()
            )

            y = (
                (1-t)**3 * points[0].y()
                + 3*(1-t)**2 * t * points[1].y()
                + 3*(1-t) * t**2 * points[2].y()
                + t**3 * points[3].y()
            )

            painter.drawPoint(int(x), int(y))