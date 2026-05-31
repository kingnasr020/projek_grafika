from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient
import math


class AnimationCanvas(QWidget):

    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 600)
        self.animation_type = "Bola Memantul"
        self.speed = 5          # 1–10, dikontrol slider

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

        # Bola
        self.ball_x = 50
        self.ball_y = 100
        self.dx = 5
        self.dy = 4

        # Mobil
        self.car_x = -150

        # Planet
        self.angle = 0

    # ==================================================
    # START / STOP
    # ==================================================

    def start_animation(self):
        self.timer.start(self._interval())

    def stop_animation(self):
        self.timer.stop()

    def set_speed(self, value):
        """value: 1–10 dari slider."""
        self.speed = value
        if self.timer.isActive():
            self.timer.setInterval(self._interval())

    def _interval(self):
        # Speed 1 → 80ms, speed 10 → 8ms
        return max(8, 90 - self.speed * 8)

    # ==================================================
    # ANIMATE
    # ==================================================

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

    # ==================================================
    # PAINT
    # ==================================================

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background gelap
        painter.fillRect(self.rect(), QColor("#1a1a2e"))

        if self.animation_type == "Bola Memantul":
            self.draw_ball(painter)
        elif self.animation_type == "Mobil Bergerak":
            self.draw_car(painter)
        elif self.animation_type == "Planet Berputar":
            self.draw_planet(painter)

    # ==================================================
    # BALL
    # ==================================================

    def draw_ball(self, painter):
        r = 25
        cx = self.ball_x + r
        cy = self.ball_y + r

        # Shadow
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawEllipse(cx - r + 6, cy - r + 8, r*2, r*2)

        # Gradient bola
        grad = QRadialGradient(cx - 6, cy - 6, r * 1.2)
        grad.setColorAt(0.0, QColor("#ff6b8a"))
        grad.setColorAt(0.6, QColor("#8B0000"))
        grad.setColorAt(1.0, QColor("#3d0000"))
        painter.setBrush(grad)
        painter.drawEllipse(self.ball_x, self.ball_y, 50, 50)

    # ==================================================
    # CAR
    # ==================================================

    def draw_car(self, painter):
        x = self.car_x
        y = 250

        # Jalan
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#2d2d2d"))
        painter.drawRect(0, y + 30, self.width(), 60)

        # Marka jalan
        pen = QPen(QColor("#f0c040"), 3, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(0, y + 60, self.width(), y + 60)

        # Bodi bawah
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#8B0000"))
        painter.drawRoundedRect(x, y, 140, 50, 8, 8)

        # Bodi atas (kabin)
        painter.setBrush(QColor("#a31515"))
        painter.drawRoundedRect(x + 20, y - 38, 85, 42, 8, 8)

        # Kaca depan & belakang
        painter.setBrush(QColor("#a8d8f0"))
        painter.drawRoundedRect(x + 25, y - 34, 35, 34, 4, 4)
        painter.drawRoundedRect(x + 64, y - 34, 35, 34, 4, 4)

        # Lampu depan
        painter.setBrush(QColor("#fffacd"))
        painter.drawEllipse(x + 125, y + 12, 16, 12)

        # Roda
        for wx in [x + 18, x + 98]:
            # Shadow roda
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.drawEllipse(wx + 3, y + 34, 30, 30)
            # Roda
            painter.setBrush(QColor("#111"))
            painter.drawEllipse(wx, y + 30, 30, 30)
            # Velg
            painter.setBrush(QColor("#ccc"))
            painter.drawEllipse(wx + 7, y + 37, 16, 16)

    # ==================================================
    # PLANET
    # ==================================================

    def draw_planet(self, painter):
        cx = self.width() // 2
        cy = self.height() // 2
        radius = 150

        # Bintang-bintang di background
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1))
        import random
        rng = random.Random(42)
        for _ in range(60):
            sx = rng.randint(0, self.width())
            sy = rng.randint(0, self.height())
            painter.drawPoint(sx, sy)

        # Orbit
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(cx - radius, cy - radius, radius*2, radius*2)

        # Matahari — gradient
        painter.setPen(Qt.NoPen)
        sun_grad = QRadialGradient(cx - 10, cy - 10, 55)
        sun_grad.setColorAt(0.0, QColor("#fff5a0"))
        sun_grad.setColorAt(0.5, QColor("#f5c518"))
        sun_grad.setColorAt(1.0, QColor("#e07b00"))
        painter.setBrush(sun_grad)
        painter.drawEllipse(cx - 45, cy - 45, 90, 90)

        # Planet — posisi & gradient
        px = int(cx + radius * math.cos(math.radians(self.angle)))
        py = int(cy + radius * math.sin(math.radians(self.angle)))

        # Shadow planet
        painter.setBrush(QColor(0, 0, 0, 60))
        painter.drawEllipse(px - 17, py - 15, 40, 40)

        planet_grad = QRadialGradient(px - 6, py - 6, 22)
        planet_grad.setColorAt(0.0, QColor("#6ab0ff"))
        planet_grad.setColorAt(0.5, QColor("#1a6bb5"))
        planet_grad.setColorAt(1.0, QColor("#0a2a50"))
        painter.setBrush(planet_grad)
        painter.drawEllipse(px - 20, py - 20, 40, 40)


# ===================================
# TAB
# ===================================

class AnimationTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = AnimationCanvas()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        # Combo
        toolbar.addWidget(QLabel("Animasi:"))
        self.combo = QComboBox()
        self.combo.addItems(["Bola Memantul", "Mobil Bergerak", "Planet Berputar"])
        self.combo.currentTextChanged.connect(self.change_animation)
        toolbar.addWidget(self.combo)

        toolbar.addSpacing(8)

        # Start / Stop
        btn_start = QPushButton("▶ Start")
        btn_stop  = QPushButton("⏹ Stop")
        btn_start.clicked.connect(self.canvas.start_animation)
        btn_stop.clicked.connect(self.canvas.stop_animation)
        toolbar.addWidget(btn_start)
        toolbar.addWidget(btn_stop)

        toolbar.addSpacing(16)

        # Speed slider
        toolbar.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.canvas.set_speed)
        toolbar.addWidget(self.speed_slider)

        self.speed_label = QLabel("5")
        self.speed_label.setFixedWidth(20)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(str(v))
        )
        toolbar.addWidget(self.speed_label)

        toolbar.addStretch()

        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)

    def change_animation(self, text):
        self.canvas.animation_type = text
        self.canvas.update()