import cv2
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSlider,
    QGroupBox,
    QMessageBox
)

from PyQt5.QtGui import (
    QPixmap,
    QImage
)

from PyQt5.QtCore import Qt

from .transform import apply_transform


def plot_histogram(ax, image, title):

    ax.clear()

    colors = ("b", "g", "r")

    for i, color in enumerate(colors):

        hist = cv2.calcHist(
            [image],
            [i],
            None,
            [256],
            [0, 256]
        )

        ax.plot(hist, color=color)

    ax.set_title(title)
    ax.set_xlim([0, 256])

    ax.grid(True)


class OperasiTab(QWidget):

    def __init__(self):

        super().__init__()

        self.original_image = None
        self.result_image = None

        self.init_ui()

    def init_ui(self):

        main_layout = QHBoxLayout()

        # =====================================
        # CONTROL PANEL
        # =====================================

        control_group = QGroupBox(
            "Kontrol Transformasi"
        )

        control_layout = QVBoxLayout()

        self.btn_load = QPushButton(
            "📂 Pilih Gambar"
        )

        self.btn_save = QPushButton(
            "💾 Simpan Hasil"
        )

        self.combo_method = QComboBox()

        self.combo_method.addItems([

            "Negative",
            "Brightness",
            "Contrast",
            "Log Transform",

            "Color Filtering",

            "Gaussian Blur",
            "Salt & Pepper",

            "Grayscale",
            "Equalization",

            "Edge Detection",

            "Mirroring",
            "Rotate",
            "Translate",

            "Sharpen",
            "Emboss",
            "Sepia"
        ])

        self.combo_color = QComboBox()

        self.combo_color.addItems([
            "Red",
            "Green",
            "Blue"
        ])

        self.slider = QSlider(
            Qt.Horizontal
        )

        self.slider.setRange(
            0,
            300
        )

        self.slider.setValue(
            40
        )

        self.slider_label = QLabel(
            "Parameter : 40"
        )

        self.slider.valueChanged.connect(
            self.update_slider_label
        )

        self.btn_apply = QPushButton(
            "⚙ Terapkan Transformasi"
        )

        control_layout.addWidget(
            self.btn_load
        )

        control_layout.addWidget(
            QLabel("Metode")
        )

        control_layout.addWidget(
            self.combo_method
        )

        control_layout.addWidget(
            QLabel("Color Filter")
        )

        control_layout.addWidget(
            self.combo_color
        )

        control_layout.addWidget(
            self.slider_label
        )

        control_layout.addWidget(
            self.slider
        )

        control_layout.addWidget(
            self.btn_apply
        )

        control_layout.addWidget(
            self.btn_save
        )

        control_layout.addStretch()

        control_group.setLayout(
            control_layout
        )

        # =====================================
        # IMAGE VIEW
        # =====================================

        self.original_label = QLabel(
            "Gambar Asli"
        )

        self.original_label.setAlignment(
            Qt.AlignCenter
        )

        self.original_label.setMinimumSize(
            500,
            350
        )

        self.original_label.setStyleSheet(
            "border:1px solid gray;"
        )

        self.result_label = QLabel(
            "Hasil Transformasi"
        )

        self.result_label.setAlignment(
            Qt.AlignCenter
        )

        self.result_label.setMinimumSize(
            500,
            350
        )

        self.result_label.setStyleSheet(
            "border:1px solid gray;"
        )

        image_layout = QHBoxLayout()

        image_layout.addWidget(
            self.original_label
        )

        image_layout.addWidget(
            self.result_label
        )

        # =====================================
        # HISTOGRAM
        # =====================================

        self.fig1, self.ax1 = plt.subplots()

        self.canvas_hist1 = FigureCanvas(
            self.fig1
        )

        self.fig2, self.ax2 = plt.subplots()

        self.canvas_hist2 = FigureCanvas(
            self.fig2
        )

        hist_layout = QHBoxLayout()

        hist_layout.addWidget(
            self.canvas_hist1
        )

        hist_layout.addWidget(
            self.canvas_hist2
        )

        # =====================================
        # RIGHT SIDE
        # =====================================

        right_layout = QVBoxLayout()

        right_layout.addLayout(
            image_layout
        )

        right_layout.addLayout(
            hist_layout
        )

        # =====================================
        # MAIN LAYOUT
        # =====================================

        main_layout.addWidget(
            control_group,
            1
        )

        main_layout.addLayout(
            right_layout,
            3
        )

        self.setLayout(
            main_layout
        )

        # =====================================
        # SIGNAL
        # =====================================

        self.btn_load.clicked.connect(
            self.load_image
        )

        self.btn_apply.clicked.connect(
            self.apply_image_transform
        )

        self.btn_save.clicked.connect(
            self.save_result
        )

    # =========================================
    # LOAD IMAGE
    # =========================================

    def load_image(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Gambar",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not filename:
            return

        self.original_image = cv2.imread(
            filename
        )

        self.show_image(
            self.original_image,
            self.original_label
        )

        plot_histogram(
            self.ax1,
            self.original_image,
            "Histogram Asli"
        )

        self.canvas_hist1.draw()

    # =========================================
    # SHOW IMAGE
    # =========================================

    def show_image(
        self,
        image,
        label
    ):

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        qimg = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(
            qimg
        )

        label.setPixmap(
            pixmap.scaled(
                label.width(),
                label.height(),
                Qt.KeepAspectRatio
            )
        )

    # =========================================
    # APPLY
    # =========================================

    def apply_image_transform(self):

        if self.original_image is None:

            QMessageBox.warning(
                self,
                "Warning",
                "Pilih gambar terlebih dahulu!"
            )

            return

        method = self.combo_method.currentText()

        color = self.combo_color.currentText()

        param = self.slider.value()

        self.result_image = apply_transform(
            self.original_image,
            method,
            color,
            param
        )

        self.show_image(
            self.result_image,
            self.result_label
        )

        plot_histogram(
            self.ax2,
            self.result_image,
            "Histogram Hasil"
        )

        self.canvas_hist2.draw()

    # =========================================
    # SAVE RESULT
    # =========================================

    def save_result(self):

        if self.result_image is None:

            QMessageBox.warning(
                self,
                "Warning",
                "Belum ada hasil transformasi!"
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Result",
            "",
            "PNG (*.png);;JPG (*.jpg)"
        )

        if filename:

            cv2.imwrite(
                filename,
                self.result_image
            )

    # =========================================
    # SLIDER
    # =========================================

    def update_slider_label(self):

        self.slider_label.setText(
            f"Parameter : {self.slider.value()}"
        )