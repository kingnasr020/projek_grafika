import cv2
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QComboBox, QSlider,
    QGroupBox, QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from .transform import apply_transform


def make_dark_figure():
    """Create a matplotlib figure styled for dark theme."""
    fig = Figure(figsize=(4, 2), tight_layout=True)
    fig.patch.set_facecolor("#FFFFFF")
    return fig


def plot_histogram(ax, image, title):
    ax.clear()
    ax.set_facecolor("#F8FAFC")
    colors = ("#2563EB", "#16A34A", "#DC2626")   # blue, green, red (more distinct)
    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        ax.plot(hist, color=color, linewidth=1.2, alpha=0.85)
    ax.set_title(title, color="#475569", fontsize=10, pad=4)
    ax.set_xlim([0, 256])
    ax.tick_params(colors="#94A3B8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#E2E8F0")
    ax.grid(True, color="#E2E8F0", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.set_facecolor("#F8FAFC")


class ImagePlaceholder(QLabel):
    """Styled empty-state placeholder for image panels."""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.placeholder_text = text
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(460, 320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._show_placeholder()

    def _show_placeholder(self):
        self.setText(f"<span style='color:#2A3048; font-size:32px;'>⬜</span>"
                     f"<br><span style='color:#5A6480; font-size:13px;'>{self.placeholder_text}</span>")
        self.setStyleSheet(
            "border: 2px dashed #E2E8F0;"
            "border-radius: 10px;"
            "background: #F8FAFC;"
            "padding: 20px;"
        )

    def set_pixmap_image(self, pixmap):
        self.setPixmap(
            pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.setStyleSheet(
            "border: 1px solid #E2E8F0;"
            "border-radius: 10px;"
            "background: #FFFFFF;"
            "padding: 4px;"
        )


class OperasiTab(QWidget):

    def __init__(self):
        super().__init__()
        self.original_image = None
        self.result_image = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ══════════════════════════════════════════
        # LEFT: Control Panel
        # ══════════════════════════════════════════
        control_group = QGroupBox("Transformasi")
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(10, 14, 10, 10)

        # Load button (primary)
        self.btn_load = QPushButton("📂  Pilih Gambar")
        self.btn_load.setProperty("class", "primary")
        self.btn_load.setCursor(Qt.PointingHandCursor)
        self.btn_load.setToolTip("Pilih file gambar untuk diproses")

        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.HLine)
        div1.setStyleSheet("color: #2A3048;")

        # Method combo
        lbl_method = QLabel("Metode")
        lbl_method.setStyleSheet("color:#64748B; font-size:11px; font-weight:600;")
        self.combo_method = QComboBox()
        self.combo_method.setToolTip("Pilih transformasi gambar")
        self.combo_method.addItems([
            "Negative", "Brightness", "Contrast", "Log Transform",
            "Color Filtering",
            "Gaussian Blur", "Salt & Pepper",
            "Grayscale", "Equalization",
            "Edge Detection",
            "Mirroring", "Rotate", "Translate",
            "Sharpen", "Emboss", "Sepia"
        ])

        # Color filter combo
        lbl_color = QLabel("Color Filter")
        lbl_color.setStyleSheet("color:#64748B; font-size:11px; font-weight:600;")
        self.combo_color = QComboBox()
        self.combo_color.addItems(["Red", "Green", "Blue"])

        # Parameter slider
        lbl_param = QLabel("Parameter")
        lbl_param.setStyleSheet("color:#64748B; font-size:11px; font-weight:600;")
        self.slider_label = QLabel("40")
        self.slider_label.setStyleSheet(
            "color:#2563EB; font-size:22px; font-weight:700; padding: 4px 0;"
        )
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 300)
        self.slider.setValue(40)
        self.slider.setToolTip("Atur nilai parameter transformasi")
        self.slider.valueChanged.connect(self._update_slider_label)

        # Action buttons
        self.btn_apply = QPushButton("⚙  Terapkan")
        self.btn_apply.setProperty("class", "primary")
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setToolTip("Jalankan transformasi  (Enter)")

        self.btn_save = QPushButton("💾  Simpan Hasil")
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setToolTip("Simpan gambar hasil transformasi")

        # Compose control layout
        control_layout.addWidget(self.btn_load)
        control_layout.addWidget(div1)
        control_layout.addWidget(lbl_method)
        control_layout.addWidget(self.combo_method)
        control_layout.addWidget(lbl_color)
        control_layout.addWidget(self.combo_color)
        control_layout.addWidget(lbl_param)
        control_layout.addWidget(self.slider_label)
        control_layout.addWidget(self.slider)
        control_layout.addSpacing(4)
        control_layout.addWidget(self.btn_apply)
        control_layout.addWidget(self.btn_save)
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        control_group.setFixedWidth(200)

        # ══════════════════════════════════════════
        # RIGHT: Image View + Histogram
        # ══════════════════════════════════════════
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)

        # Image panels (cards)
        image_row = QHBoxLayout()
        image_row.setSpacing(8)

        # Original card
        orig_card = QGroupBox("Gambar Asli")
        orig_inner = QVBoxLayout()
        orig_inner.setContentsMargins(6, 8, 6, 6)
        self.original_label = ImagePlaceholder("Belum ada gambar")
        orig_inner.addWidget(self.original_label)
        orig_card.setLayout(orig_inner)

        # Result card
        result_card = QGroupBox("Hasil Transformasi")
        result_inner = QVBoxLayout()
        result_inner.setContentsMargins(6, 8, 6, 6)
        self.result_label = ImagePlaceholder("Terapkan transformasi")
        result_inner.addWidget(self.result_label)
        result_card.setLayout(result_inner)

        image_row.addWidget(orig_card)
        image_row.addWidget(result_card)

        # Histogram panels (cards)
        hist_card = QGroupBox("Histogram")
        hist_row = QHBoxLayout()
        hist_row.setContentsMargins(6, 8, 6, 6)
        hist_row.setSpacing(8)

        self.fig1 = make_dark_figure()
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.set_facecolor("#F8FAFC")
        self.canvas_hist1 = FigureCanvas(self.fig1)
        self.canvas_hist1.setStyleSheet("background: #F8FAFC; border-radius: 6px;")
        self.canvas_hist1.setMinimumHeight(130)

        self.fig2 = make_dark_figure()
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor("#F8FAFC")
        self.canvas_hist2 = FigureCanvas(self.fig2)
        self.canvas_hist2.setStyleSheet("background: #F8FAFC; border-radius: 6px;")
        self.canvas_hist2.setMinimumHeight(130)

        hist_row.addWidget(self.canvas_hist1)
        hist_row.addWidget(self.canvas_hist2)
        hist_card.setLayout(hist_row)

        right_layout.addLayout(image_row, 3)
        right_layout.addWidget(hist_card, 1)

        # ══════════════════════════════════════════
        # Main assemble
        # ══════════════════════════════════════════
        main_layout.addWidget(control_group)
        main_layout.addLayout(right_layout, 1)

        # Signals
        self.btn_load.clicked.connect(self.load_image)
        self.btn_apply.clicked.connect(self.apply_image_transform)
        self.btn_save.clicked.connect(self.save_result)

    # ── Helpers ────────────────────────────────────

    def _update_slider_label(self):
        self.slider_label.setText(str(self.slider.value()))

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg)"
        )
        if not filename:
            return
        self.original_image = cv2.imread(filename)
        self._show_cv_image(self.original_image, self.original_label)
        plot_histogram(self.ax1, self.original_image, "Histogram Asli")
        self.canvas_hist1.draw()

    def _show_cv_image(self, image, label: ImagePlaceholder):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        label.set_pixmap_image(pixmap)

    def apply_image_transform(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Warning", "Pilih gambar terlebih dahulu!")
            return
        method = self.combo_method.currentText()
        color  = self.combo_color.currentText()
        param  = self.slider.value()
        self.result_image = apply_transform(self.original_image, method, color, param)
        self._show_cv_image(self.result_image, self.result_label)
        plot_histogram(self.ax2, self.result_image, "Histogram Hasil")
        self.canvas_hist2.draw()

    def save_result(self):
        if self.result_image is None:
            QMessageBox.warning(self, "Warning", "Belum ada hasil transformasi!")
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Result", "", "PNG (*.png);;JPG (*.jpg)"
        )
        if filename:
            cv2.imwrite(filename, self.result_image)
