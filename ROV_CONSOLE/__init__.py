from PySide6.QtWidgets import QApplication
import sys
from .gui import MainWindow

def main():
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())