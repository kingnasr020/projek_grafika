import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QAction,
    QMessageBox,
)

from paint.paint_tab import PaintTab
from image_processing.operasi_tab import OperasiTab
from animation.animation_tab import AnimationTab


LIGHT_PAINT_STYLE = """
QMainWindow {
    background-color: #f3f3f3;
}

QMenuBar {
    background-color: #f8f8f8;
    color: #202020;
    border-bottom: 1px solid #dddddd;
    padding: 2px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: #e5f1fb;
    border-radius: 4px;
}

QMenu {
    background-color: #ffffff;
    color: #202020;
    border: 1px solid #d0d0d0;
}

QMenu::item {
    padding: 7px 28px;
}

QMenu::item:selected {
    background-color: #e5f1fb;
}

/* TAB */
QTabWidget::pane {
    border: none;
    background-color: #f3f3f3;
}

QTabBar::tab {
    background-color: #f8f8f8;
    color: #202020;
    padding: 9px 18px;
    border: none;
    border-right: 1px solid #dddddd;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0078d4;
    border-bottom: 3px solid #0078d4;
}

QTabBar::tab:hover {
    background-color: #eaf4ff;
}

/* STATUS BAR */
QStatusBar {
    background-color: #f8f8f8;
    color: #404040;
    border-top: 1px solid #dddddd;
}
"""


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Grafika Studio")
        self.resize(1400, 900)

        self.init_ui()

    def init_ui(self):

        # ==============================
        # MENU BAR
        # ==============================
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        exit_action = QAction("Exit", self)
        about_action = QAction("About", self)

        exit_action.triggered.connect(self.close)
        about_action.triggered.connect(self.show_about)

        file_menu.addAction(exit_action)
        help_menu.addAction(about_action)

        # ==============================
        # TABS
        # ==============================
        self.tabs = QTabWidget()

        self.paint_tab = PaintTab()
        self.image_tab = OperasiTab()
        self.animation_tab = AnimationTab()

        self.tabs.addTab(self.paint_tab, "🎨 Paint")
        self.tabs.addTab(self.image_tab, "🖼 Operasi Gambar")
        self.tabs.addTab(self.animation_tab, "🎬 Animasi")

        self.setCentralWidget(self.tabs)

        self.statusBar().showMessage("Ready")

    def show_about(self):
        QMessageBox.information(
            self,
            "About",
            "Grafika Studio\n\n"
            "Fitur: Paint · Operasi Gambar · Animasi\n"
            "Dibuat dengan PyQt5, OpenCV, NumPy, Matplotlib"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Style Fusion membuat tampilan PyQt lebih modern dan ringan
    app.setStyle("Fusion")
    app.setStyleSheet(LIGHT_PAINT_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())