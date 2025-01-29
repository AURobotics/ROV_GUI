import sys, cv2, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class CameraWidget (QLabel) :
    def __init__(self, parent, cam, w, h):
        super().__init__(parent)

        # self.setScaledContents (1)

        self.cam = cam
        self.w = w
        self.h = h

        self.update ()

    def update (self) :
        # cap = cv2.VideoCapture(self.cam)
        # if cap.isOpened () :
        #     ret, frame = cap.read ()
        #     if ret :
        #         frame = cv2.resize (frame, (self.w, self.h))
        #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #         q_image = QImage (frame.data, self.w, self.h, frame.strides[0], QImage.Format_RGB888)

        #         self.setPixmap (QPixmap.fromImage(q_image))
        # cap.release ()
        self.setText (str (self.cam))

class OrientationsWidget (QWidget) : 
    def __init__(self, parent):
        super().__init__(parent)

        self.setMinimumSize (parent.width () // 3, parent.height () // 2)

        layout = QVBoxLayout ()

        self.setLayout (layout)

        self.depthLabel = QLabel (self)
        self.yawLabel = QLabel (self)
        self.pitchLabel = QLabel (self)
        self.rollLabel = QLabel (self)

        layout.addWidget (self.depthLabel)
        layout.addWidget (self.yawLabel)
        layout.addWidget (self.pitchLabel)
        layout.addWidget (self.rollLabel)

        self.update ()

    def update (self) :
        # TODO: Change the randint to reading from RPi/ESP32 using PySerial
        depthReading = random.randint (0, 10)
        yawReading = random.randint (0, 10)
        pitchReading = random.randint (0, 10)
        rollReading = random.randint (0, 10)

        self.depthLabel.setText ("Depth: " + str (depthReading))
        self.yawLabel.setText ("Yaw: " + str (yawReading))
        self.pitchLabel.setText ("Pitch: " + str (pitchReading))
        self.rollLabel.setText ("Roll: " + str (rollReading))

class MainWindow (QMainWindow) :
    def __init__(self) :
        super().__init__()

        self.showMaximized ()
        self.setWindowTitle ("AU Robotics ROV GUI")

        self.initUI ()

        self.timer = QTimer ()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

    def initUI (self) :
        
        centralWidget = QWidget ()
        self.setCentralWidget (centralWidget)

        self.leftCameraWidget = CameraWidget (self, 0, self.width () // 3, self.height () // 4)
        self.middleCameraWidget = CameraWidget (self, 1, self.width () // 3, self.height () // 4)
        self.rightCameraWidget = CameraWidget (self, 2, self.width () // 3, self.height () // 4)
        self.orientationsWidget = OrientationsWidget (self)
        self.controllerWidget = QWidget ()
        self.thrustersWidget = QWidget ()
        self.tasksWidget = QWidget ()
        self.scriptsWidget = QWidget ()
        
        grid = QGridLayout ()

        grid.setColumnMinimumWidth (self.width () // 3, 0)
        grid.setColumnMinimumWidth (self.width () // 3, 1)
        grid.setColumnMinimumWidth (self.width () // 3, 2)

        grid.setRowMinimumHeight (self.height () // 4, 0)
        grid.setRowMinimumHeight (self.height () // 4, 1)
        grid.setRowMinimumHeight (self.height () // 4, 2)
        grid.setRowMinimumHeight (self.height () // 4, 3)


        grid.addWidget (self.leftCameraWidget, 0, 0, 2, 1)
        grid.addWidget (self.middleCameraWidget, 0, 1, 2, 1)
        grid.addWidget (self.rightCameraWidget, 0, 2, 2, 1)

        grid.addWidget (self.orientationsWidget, 2, 0, 2, 1)

        grid.addWidget (self.tasksWidget, 2, 1, 1, 1)
        grid.addWidget (self.controllerWidget, 3, 1, 1, 1)

        grid.addWidget (self.scriptsWidget, 2, 2, 1, 1)
        grid.addWidget (self.thrustersWidget, 3, 2, 1, 1)

        centralWidget.setLayout (grid)

    def updateFrame (self) :
        self.leftCameraWidget.update ()
        self.middleCameraWidget.update ()
        self.rightCameraWidget.update ()
        self.orientationsWidget.update ()


if __name__ == "__main__" :
    app = QApplication (sys.argv)
    mainWindow = MainWindow ()
    mainWindow.show ()
    sys.exit (app.exec_ ())