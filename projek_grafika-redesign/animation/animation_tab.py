from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient, QFont
import math


class AnimationCanvas(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 550)
        self.animation_type = "Bola Memantul"
        self.speed = 5

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

        # Ball
        self.ball_x = 50
        self.ball_y = 100
        self.dx = 5
        self.dy = 4

        # Car
        self.car_x = -150

        # Planet
        self.angle = 0

    def start_animation(self):
        self.timer.start(self._interval())

    def stop_animation(self):
        self.timer.stop()

    def set_speed(self, value):
        self.speed = value
        if self.timer.isActive():
            self.timer.setInterval(self._interval())

    def _interval(self):
        return max(8, 90 - self.speed * 8)

    def animate(self):
        step = self.speed
        if self.animation_type == "Bola Memantul":
            self.ball_x += int(self.dx * step / 5)
            self.ball_y += int(self.dy * step / 5)
            if self.ball_x <= 0 or self.ball_x >= self.width() - 50:
                self.dx *= -1
            if self.ball_y <= 0 or self.ball_y >= self.height() - 50:
                self.dy *= -1
        elif self.animation_type == "Mobil Bergerak":
            self.car_x += int(step * 1.6)
            if self.car_x > self.width():
                self.car_x = -150
        elif self.animation_type == "Planet Berputar":
            self.angle = (self.angle + step * 0.6) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Gradient background
        bg_grad = QLinearGradient(0, 0, 0, self.height())
        bg_grad.setColorAt(0.0, QColor("#F0F4FF"))
        bg_grad.setColorAt(1.0, QColor("#E8EFFF"))
        painter.fillRect(self.rect(), bg_grad)

        if self.animation_type == "Bola Memantul":
            self._draw_ball(painter)
        elif self.animation_type == "Mobil Bergerak":
            self._draw_car(painter)
        elif self.animation_type == "Planet Berputar":
            self._draw_planet(painter)

    # ── Ball ─────────────────────────────────────
    def _draw_ball(self, painter):
        r = 28
        cx = self.ball_x + r
        cy = self.ball_y + r

        # Glow / shadow
        glow = QRadialGradient(cx, cy, r * 2.5)
        glow.setColorAt(0.0, QColor(91, 141, 239, 60))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(cx - r*2, cy - r*2, r*4, r*4)

        # Shadow
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawEllipse(cx - r + 8, cy - r + 10, r*2, r*2)

        # Ball gradient
        grad = QRadialGradient(cx - 8, cy - 8, r * 1.3)
        grad.setColorAt(0.0, QColor("#7ABAFF"))
        grad.setColorAt(0.5, QColor("#5B8DEF"))
        grad.setColorAt(1.0, QColor("#1A3D7C"))
        painter.setBrush(grad)
        painter.drawEllipse(self.ball_x, self.ball_y, r*2, r*2)

        # Specular highlight
        spec = QRadialGradient(cx - 10, cy - 10, 8)
        spec.setColorAt(0.0, QColor(255, 255, 255, 140))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(spec)
        painter.drawEllipse(cx - 16, cy - 16, 18, 18)

    # ── Car ──────────────────────────────────────
    def _draw_car(self, painter):
        x = self.car_x
        y = self.height() // 2 - 10

        # Road
        painter.setPen(Qt.NoPen)
        road_grad = QLinearGradient(0, y+28, 0, y+90)
        road_grad.setColorAt(0, QColor("#CBD5E1"))
        road_grad.setColorAt(1, QColor("#94A3B8"))
        painter.setBrush(road_grad)
        painter.drawRect(0, y + 28, self.width(), 65)

        # Road edge lines
        painter.setPen(QPen(QColor("#94A3B8"), 2))
        painter.drawLine(0, y + 29, self.width(), y + 29)
        painter.drawLine(0, y + 92, self.width(), y + 92)

        # Dashed center line
        pen = QPen(QColor("#CBD5E1"), 2, Qt.DashLine)
        pen.setDashPattern([20, 10])
        painter.setPen(pen)
        painter.drawLine(0, y + 60, self.width(), y + 60)

        # Car body (lower)
        painter.setPen(Qt.NoPen)
        body_grad = QLinearGradient(x, y, x, y + 50)
        body_grad.setColorAt(0, QColor("#3A5FA0"))
        body_grad.setColorAt(1, QColor("#1E3A6E"))
        painter.setBrush(body_grad)
        painter.drawRoundedRect(x, y, 145, 50, 8, 8)

        # Cabin
        cabin_grad = QLinearGradient(x+20, y-40, x+20, y+2)
        cabin_grad.setColorAt(0, QColor("#4A72B8"))
        cabin_grad.setColorAt(1, QColor("#2A4A8A"))
        painter.setBrush(cabin_grad)
        painter.drawRoundedRect(x + 22, y - 38, 88, 42, 8, 8)

        # Windows
        win_grad = QLinearGradient(0, y-34, 0, y)
        win_grad.setColorAt(0, QColor("#A8D8F0"))
        win_grad.setColorAt(1, QColor("#5AAFD4"))
        painter.setBrush(win_grad)
        painter.drawRoundedRect(x + 27, y - 34, 36, 32, 5, 5)
        painter.drawRoundedRect(x + 67, y - 34, 36, 32, 5, 5)

        # Headlight
        hl_grad = QRadialGradient(x + 136, y + 18, 12)
        hl_grad.setColorAt(0, QColor("#FFFDE0"))
        hl_grad.setColorAt(1, QColor("#F0C040"))
        painter.setBrush(hl_grad)
        painter.drawEllipse(x + 128, y + 13, 18, 13)

        # Wheels
        for wx in [x + 18, x + 100]:
            painter.setBrush(QColor(0, 0, 0, 60))
            painter.drawEllipse(wx + 3, y + 34, 31, 31)
            painter.setBrush(QColor("#111827"))
            painter.drawEllipse(wx, y + 30, 31, 31)
            painter.setBrush(QColor("#E2E8F0"))
            painter.drawEllipse(wx + 7, y + 37, 17, 17)
            painter.setBrush(QColor("#4A5568"))
            painter.drawEllipse(wx + 12, y + 42, 7, 7)

    # ── Planet ───────────────────────────────────
    def _draw_planet(self, painter):
        cx = self.width() // 2
        cy = self.height() // 2
        radius = min(self.width(), self.height()) // 3

        # Stars
        painter.setPen(QPen(QColor(100, 120, 200, 90), 1))
        import random
        rng = random.Random(42)
        for _ in range(80):
            sx = rng.randint(0, self.width())
            sy = rng.randint(0, self.height())
            sz = rng.random()
            if sz > 0.85:
                painter.setPen(QPen(QColor(80, 100, 200, 200), 2))
                painter.drawPoint(sx, sy)
            else:
                painter.setPen(QPen(QColor(100, 120, 200, 80), 1))
                painter.drawPoint(sx, sy)

        # Orbit ring
        painter.setPen(QPen(QColor(100, 130, 220, 60), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - radius, cy - radius, radius*2, radius*2)

        # Sun glow
        painter.setPen(Qt.NoPen)
        sun_glow = QRadialGradient(cx, cy, radius * 0.55)
        sun_glow.setColorAt(0.0, QColor(245, 197, 24, 30))
        sun_glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(sun_glow)
        painter.drawEllipse(cx - radius//2, cy - radius//2, radius, radius)

        # Sun
        sun_grad = QRadialGradient(cx - 12, cy - 12, 55)
        sun_grad.setColorAt(0.0, QColor("#FFF9C4"))
        sun_grad.setColorAt(0.4, QColor("#F5C518"))
        sun_grad.setColorAt(1.0, QColor("#E07B00"))
        painter.setBrush(sun_grad)
        painter.drawEllipse(cx - 48, cy - 48, 96, 96)

        # Planet
        px = int(cx + radius * math.cos(math.radians(self.angle)))
        py = int(cy + radius * math.sin(math.radians(self.angle)))

        # Planet glow
        pl_glow = QRadialGradient(px, py, 40)
        pl_glow.setColorAt(0, QColor(91, 141, 239, 50))
        pl_glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(pl_glow)
        painter.drawEllipse(px - 40, py - 40, 80, 80)

        # Planet shadow
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawEllipse(px - 18, py - 14, 44, 44)

        # Planet body
        planet_grad = QRadialGradient(px - 8, py - 8, 24)
        planet_grad.setColorAt(0.0, QColor("#7ABAFF"))
        planet_grad.setColorAt(0.5, QColor("#3A7ACC"))
        planet_grad.setColorAt(1.0, QColor("#0A2A50"))
        painter.setBrush(planet_grad)
        painter.drawEllipse(px - 22, py - 22, 44, 44)


# ══════════════════════════════════════════════════
# TAB
# ══════════════════════════════════════════════════

class AnimationTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = AnimationCanvas()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Toolbar card
        toolbar_frame = QFrame()
        toolbar_frame.setProperty("class", "toolbar-card")
        toolbar = QHBoxLayout(toolbar_frame)
        toolbar.setContentsMargins(10, 6, 10, 6)
        toolbar.setSpacing(10)

        # Animation selector
        lbl_anim = QLabel("Animasi")
        lbl_anim.setStyleSheet("color:#64748B; font-size:11px; font-weight:600;")
        toolbar.addWidget(lbl_anim)

        self.combo = QComboBox()
        self.combo.addItems(["Bola Memantul", "Mobil Bergerak", "Planet Berputar"])
        self.combo.setToolTip("Pilih jenis animasi")
        self.combo.setCursor(Qt.PointingHandCursor)
        self.combo.currentTextChanged.connect(self.change_animation)
        toolbar.addWidget(self.combo)

        toolbar.addSpacing(6)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color: #2A3048;")
        toolbar.addWidget(sep)
        toolbar.addSpacing(6)

        # Start / Stop
        btn_start = QPushButton("▶  Start")
        btn_stop  = QPushButton("⏹  Stop")
        btn_start.setToolTip("Mulai animasi")
        btn_stop.setToolTip("Hentikan animasi")
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_stop.setCursor(Qt.PointingHandCursor)
        btn_start.setProperty("class", "primary")
        btn_start.clicked.connect(self.canvas.start_animation)
        btn_stop.clicked.connect(self.canvas.stop_animation)
        toolbar.addWidget(btn_start)
        toolbar.addWidget(btn_stop)

        toolbar.addSpacing(6)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #2A3048;")
        toolbar.addWidget(sep2)
        toolbar.addSpacing(6)

        # Speed
        lbl_speed = QLabel("Speed")
        lbl_speed.setStyleSheet("color:#64748B; font-size:11px; font-weight:600;")
        toolbar.addWidget(lbl_speed)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setFixedWidth(140)
        self.speed_slider.setToolTip("Kecepatan animasi (1–10)")
        self.speed_slider.setCursor(Qt.PointingHandCursor)
        self.speed_slider.valueChanged.connect(self.canvas.set_speed)
        toolbar.addWidget(self.speed_slider)

        self.speed_label = QLabel("5")
        self.speed_label.setStyleSheet("color:#2563EB; font-weight:700; min-width:16px;")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(str(v)))
        toolbar.addWidget(self.speed_label)

        toolbar.addStretch()

        layout.addWidget(toolbar_frame)
        layout.addWidget(self.canvas)

    def change_animation(self, text):
        self.canvas.stop_animation()
        self.canvas.animation_type = text
        # Reset positions
        self.canvas.ball_x = 50
        self.canvas.ball_y = 100
        self.canvas.car_x = -150
        self.canvas.angle = 0
        self.canvas.update()
