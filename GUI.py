import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout
from PyQt5.QtGui import QImage, QPixmap, QFont

class MainWindow (QMainWindow) :
    def __init__(self) :
        super().__init__()

        self.showMaximized ()
        self.setWindowTitle ("AU Robotics ROV GUI")

        self.initUI ()

    def initUI (self) :
        
        centralWidget = QWidget ()
        self.setCentralWidget (centralWidget)

        leftCameraLabel = QLabel ("1", self)
        middleCameraLabel = QLabel ("2", self)
        rightCameraLabel = QLabel ("3", self)
        orientationsLabel = QLabel ("4", self)
        controllerLabel = QLabel ("5", self)
        thrustersLabel = QLabel ("6", self)
        tasksLabel = QLabel ("7", self)
        scriptsLabel = QLabel ("8", self)

        # leftCameraWidget.setGeometry (0, 0, self.width () // 3, self.height () // 2)
        # middleCameraWidget.setGeometry (self.width () // 3, 0, self.width () // 3, self.height () // 2)
        # rightCameraWidget.setGeometry (2 * self.width () // 3, 0, self.width () // 3, self.height () // 2)

        # orientationsWidget.setGeometry (0, self.height () // 2, self.width () // 3, self.height () // 2)

        # tasksWidget.setGeometry (self.width () // 3, self.height () // 2, self.width () // 3, self.height () // 4)
        # controllerWidget.setGeometry (self.width () // 3, self.height () // 4, self.width () // 3, self.height () // 4)

        # scriptsWidget.setGeometry (2 * self.width () // 3, self.height () // 2, self.width () // 3, self.height () // 4)
        # thrustersWidget.setGeometry (2 * self.width () // 3, self.height () // 4, self.width () // 3, self.height () // 4)

        grid = QGridLayout ()

        grid.setColumnMinimumWidth (self.width () // 3, 0)
        grid.setColumnMinimumWidth (self.width () // 3, 1)
        grid.setColumnMinimumWidth (self.width () // 3, 2)

        grid.setRowMinimumHeight (self.height () // 4, 0)
        grid.setRowMinimumHeight (self.height () // 4, 1)
        grid.setRowMinimumHeight (self.height () // 4, 2)
        grid.setRowMinimumHeight (self.height () // 4, 3)


        grid.addWidget (leftCameraLabel, 0, 0, 2, 1)
        grid.addWidget (middleCameraLabel, 0, 1, 2, 1)
        grid.addWidget (rightCameraLabel, 0, 2, 2, 1)

        grid.addWidget (orientationsLabel, 2, 0, 2, 1)

        grid.addWidget (tasksLabel, 2, 1, 1, 1)
        grid.addWidget (controllerLabel, 3, 1, 1, 1)

        grid.addWidget (scriptsLabel, 2, 2, 1, 1)
        grid.addWidget (thrustersLabel, 3, 2, 1, 1)

        centralWidget.setLayout (grid)


        

        

if __name__ == "__main__" :
    app = QApplication (sys.argv)
    mainWindow = MainWindow ()
    mainWindow.show ()
    sys.exit (app.exec_ ())