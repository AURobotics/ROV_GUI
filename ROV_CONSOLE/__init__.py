from PySide6.QtWidgets import QApplication
import sys
from .gui import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    ret = app.exec()
    sys.exit(ret)