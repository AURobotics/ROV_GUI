from sys import argv, platform, exit

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from .constants import APP_ICON
from .gui import MainWindow


def main():
    app = QApplication(argv)
    QCoreApplication.setApplicationName('AU Robotics - Console')
    QCoreApplication.setOrganizationName("AURobotics")
    if platform.startswith('win'):
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            'AURobotics.Console')
    window = MainWindow()
    ret = app.exec()
    exit(ret)
