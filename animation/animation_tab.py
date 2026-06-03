from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QFrame
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

# ===================================
# TAB (UI Refactored)
# ===================================

# ===================================
# ROMBAKAN TOTAL: NAVBAR RAMPING & PROPORSIONAL
# ===================================

class AnimationTab(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = AnimationCanvas()
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Layout utama menggunakan margin tipis agar clean
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 1. NAVBAR (Di-press biar tipis dan rapi)
        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("NavBar")
        self.nav_frame.setFixedHeight(55) # KUNCI UTAMA: Mengunci tinggi navbar biar gak maruk
        
        nav_layout = QHBoxLayout(self.nav_frame)
        nav_layout.setContentsMargins(15, 0, 15, 0) # Atas-bawah 0 biar elemen pas di tengah
        nav_layout.setSpacing(12)
        nav_layout.setAlignment(Qt.AlignVCenter) # Memastikan semua widget rata tengah secara vertikal

        # Elemen: Dropdown Animasi
        lbl_animasi = QLabel("Animasi:")
        lbl_animasi.setObjectName("NavLabel")
        nav_layout.addWidget(lbl_animasi)
        
        self.combo = QComboBox()
        self.combo.addItems(["Bola Memantul", "Mobil Bergerak", "Planet Berputar"])
        self.combo.currentTextChanged.connect(self.change_animation)
        self.combo.setCursor(Qt.PointingHandCursor)
        self.combo.setFixedHeight(32) # Tinggi drop-down yang ideal
        nav_layout.addWidget(self.combo)

        nav_layout.addSpacing(10)

        # Elemen: Tombol Kontrol
        btn_start = QPushButton("▶ Start")
        btn_start.setCursor(Qt.PointingHandCursor)
        btn_start.setObjectName("BtnStart")
        btn_start.setFixedHeight(32)
        
        btn_stop  = QPushButton("⏹ Stop")
        btn_stop.setCursor(Qt.PointingHandCursor)
        btn_stop.setObjectName("BtnStop")
        btn_stop.setFixedHeight(32)
        
        btn_start.clicked.connect(self.canvas.start_animation)
        btn_stop.clicked.connect(self.canvas.stop_animation)
        
        nav_layout.addWidget(btn_start)
        nav_layout.addWidget(btn_stop)

        nav_layout.addSpacing(15)

        # Elemen: Slider Kecepatan
        lbl_speed = QLabel("Speed:")
        lbl_speed.setObjectName("NavLabel")
        nav_layout.addWidget(lbl_speed)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setFixedWidth(130)
        self.speed_slider.setCursor(Qt.PointingHandCursor)
        self.speed_slider.valueChanged.connect(self.canvas.set_speed)
        nav_layout.addWidget(self.speed_slider)

        self.speed_label = QLabel("5")
        self.speed_label.setObjectName("NavLabel")
        self.speed_label.setFixedWidth(15)
        self.speed_slider.valueChanged.connect(
            lambda v: self.speed_label.setText(str(v))
        )
        nav_layout.addWidget(self.speed_label)

        # Mendorong semua elemen ke kiri, menyisakan space kosong di kanan jika layar melebar
        nav_layout.addStretch() 

        # 2. CANVAS ANIMASI
        # Beri nilai stretch=1 agar canvas mendominasi seluruh sisa ruang vertikal layar
        layout.addWidget(self.nav_frame)
        layout.addWidget(self.canvas, stretch=1) 

    def change_animation(self, text):
        self.canvas.animation_type = text
        self.canvas.update()

    def apply_styles(self):
        stylesheet = """
            /* Background Aplikasi Utama */
            AnimationTab {
                background-color: #0f172a; /* Slate 900 */
            }
            
            /* Canvas Tempat Animasi */
            AnimationCanvas {
                background-color: #1e1e2f;
                border-radius: 8px;
            }

            /* Styling Navbar modern & sleek */
            #NavBar {
                background-color: #1e293b; /* Slate 800 */
                border-radius: 8px;
                border: 1px solid #334155; /* Slate 700 */
            }

            /* Label Teks */
            #NavLabel {
                color: #cbd5e1; /* Slate 300 */
                font-weight: 600;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }

            /* Dropdown / ComboBox */
            QComboBox {
                background-color: #334155;
                color: white;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 2px 10px;
                font-size: 13px;
                min-width: 140px;
            }
            QComboBox:hover {
                background-color: #475569;
                border: 1px solid #64748b;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            /* Tombol Navigasi */
            QPushButton {
                background-color: #2563eb; /* Blue 600 */
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0px 14px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            
            /* Tombol Stop Khusus Merah */
            #BtnStop {
                background-color: #dc2626; /* Red 600 */
            }
            #BtnStop:hover {
                background-color: #ef4444;
            }
            #BtnStop:pressed {
                background-color: #b91c1c;
            }

            /* Track Slider Kecepatan */
            QSlider::groove:horizontal {
                border-radius: 3px;
                height: 6px;
                background: #334155;
            }
            /* Handle Slider Kecepatan */
            QSlider::handle:horizontal {
                background: #3b82f6;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #60a5fa;
            }
        """
        self.setStyleSheet(stylesheet)