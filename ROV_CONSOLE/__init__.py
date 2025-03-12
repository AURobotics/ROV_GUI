from PySide6.QtWidgets import QApplication
import sys
from .gui import MainWindow

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    ret = app.exec()
    main_window.leftCameraWidget.cam.discard()
    main_window.rightCameraWidget.cam.discard()
    main_window.middleCameraWidget.cam.discard()
    main_window.controller.discard()
    sys.exit(ret)