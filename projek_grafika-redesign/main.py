import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QAction, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt

from paint.paint_tab import PaintTab
from image_processing.operasi_tab import OperasiTab
from animation.animation_tab import AnimationTab
from stylesheet import DARK_MAROON


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grafika Studio")
        self.resize(1400, 900)
        self.init_ui()

    def init_ui(self):
        # ── Menu bar ──────────────────────────────
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        exit_action  = QAction("Exit",  self)
        about_action = QAction("About", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        about_action.triggered.connect(self.show_about)
        file_menu.addAction(exit_action)
        help_menu.addAction(about_action)

        # ── Tabs ──────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)   # removes outer border on macOS/some styles

        self.paint_tab     = PaintTab()
        self.image_tab     = OperasiTab()
        self.animation_tab = AnimationTab()

        self.tabs.addTab(self.paint_tab,     "🎨  Paint")
        self.tabs.addTab(self.image_tab,     "🖼  Operasi Gambar")
        self.tabs.addTab(self.animation_tab, "🎬  Animasi")

        self.setCentralWidget(self.tabs)

        # ── Status bar ────────────────────────────
        self.status = self.statusBar()
        self.status.showMessage("  Grafika Studio — Ready")

        # Tab change status update
        self.tabs.currentChanged.connect(self._on_tab_change)

    def _on_tab_change(self, idx):
        names = ["Paint", "Operasi Gambar", "Animasi"]
        self.status.showMessage(f"  {names[idx]}")

    def show_about(self):
        QMessageBox.information(
            self, "About Grafika Studio",
            "Grafika Studio\n\n"
            "Fitur: Paint · Operasi Gambar · Animasi\n"
            "Dibuat dengan PyQt5, OpenCV, NumPy, Matplotlib"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_MAROON)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
