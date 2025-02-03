import sys, cv2, random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout, QScrollArea
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt

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

class ThrustersWidget (QWidget) :
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.setMinimumSize (parent.width () // 3, parent.height () // 4)
        
        # Default colors
        self.square_color = QColor(0, 0, 0)  # Black for center square

        self.circle_colors = [
            QColor(0, 255, 0),  # Top
            QColor(0, 255, 0)
            # ,  # Bottom
            # # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
        ]

        self.rotated_square_colors = [
            QColor(0, 255, 0),  # Front-left
            QColor(0, 255, 0),  # Front-right
            QColor(0, 255, 0),  # Back-left
            QColor(0, 255, 0)   # Back-right
        ]

    def set_colors(self):
        """Allows changing colors dynamically"""

        frontRightSpeed = random.randint (0, 255)
        backRightSpeed = random.randint (0, 255)
        frontLeftSpeed = random.randint (0, 255)
        backLeftSpeed = random.randint (0, 255)
        upFrontSpeed = random.randint (0, 255)
        upBackSpeed = random.randint (0, 255)

        self.square_color = QColor(0, 0, 0)
        self.circle_colors = [
            QColor(upFrontSpeed, 255 - upFrontSpeed, 0),  # Top
            QColor(upBackSpeed, 255 - upBackSpeed, 0)
            # ,  # Bottom
            # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
        ]
        self.rotated_square_colors = [
            QColor(frontLeftSpeed, 255 - frontLeftSpeed, 0),  # Front-left
            QColor(frontRightSpeed, 255 - frontRightSpeed, 0),  # Front-right
            QColor(backLeftSpeed, 255 - backLeftSpeed, 0),  # Back-left
            QColor(backRightSpeed, 255 - backRightSpeed, 0)   # Back-right
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get parent size constraints
        max_width = self.parent.width() // 3
        max_height = self.parent.height() // 4
        size = min(max_width, max_height)

        # Central square (50% of size)
        square_size = int(size * 0.5)
        square_x = (self.width() - square_size) // 2
        square_y = (self.height() - square_size) // 2

        # Draw the black center square
        painter.setPen(QPen(self.square_color, 3))
        painter.setBrush(QBrush(Qt.NoBrush))
        painter.drawRect(square_x, square_y, square_size, square_size)

        # Circles' and Rotated Squares' Positions
        offsets = [
            (square_x + square_size // 2, square_y - square_size // 3),  # Top
            (square_x + square_size // 2, square_y + square_size + square_size // 3)
            # ,  # Bottom
            # (square_x - square_size // 3, square_y + square_size // 2),  # Left
            # (square_x + square_size + square_size // 3, square_y + square_size // 2)  # Right
        ]

        rotated_offsets = [
            (square_x - square_size // 3, square_y - square_size // 3),  # Top-left
            (square_x + square_size + square_size // 6, square_y - square_size // 3),  # Top-right
            (square_x - square_size // 3, square_y + square_size + square_size // 6),  # Bottom-left
            (square_x + square_size + square_size // 6, square_y + square_size + square_size // 6)  # Bottom-right
        ]

        circle_radius = int(square_size * 0.2)

        # Draw Circles with individual colors
        for i, (x, y) in enumerate(offsets):
            painter.setBrush(QBrush(self.circle_colors[i]))
            painter.drawEllipse(x - circle_radius, y - circle_radius, circle_radius * 2, circle_radius * 2)

        # Draw Rotated Squares with individual colors
        for i, (x, y) in enumerate(rotated_offsets):
            painter.setBrush(QBrush(self.rotated_square_colors[i]))
            painter.save()
            painter.translate(x, y)
            painter.rotate(45)  # Rotate by 45 degrees
            painter.drawRect(-circle_radius, -circle_radius, circle_radius * 2, circle_radius * 2)
            painter.restore()

    def update (self) :
        self.set_colors ()
        self.paintEvent (None)


        



class MainWindow (QMainWindow) :
    def __init__(self) :
        super().__init__()

        self.showMaximized ()
        self.setWindowTitle ("AU Robotics ROV GUI")

        self.state = self.windowState ()

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
        self.thrustersWidget = ThrustersWidget (self)
        self.tasksWidget = QScrollArea ()
        self.scriptsWidget = QScrollArea ()

        tasksScrollLayout = QVBoxLayout ()
        tasksScrollLayout.addWidget (QLabel ("Task 1"))
        tasksScrollLayout.addWidget (QLabel ("Task 2"))
        tasksScrollLayout.addWidget (QLabel ("Task 3"))
        tasksScrollLayout.addWidget (QLabel ("Task 4"))
        tasksScrollLayout.addWidget (QLabel ("Task 5"))
        tasksScrollLayout.addWidget (QLabel ("Task 6"))
        tasksScrollLayout.addWidget (QLabel ("Task 7"))
        tasksScrollLayout.addWidget (QLabel ("Task 8"))
        tasksScrollLayout.addWidget (QLabel ("Task 9"))
        tasksScrollLayout.addWidget (QLabel ("Task 10"))
        tasksScrollLayout.addWidget (QLabel ("Task 11"))
        tasksScrollLayout.addWidget (QLabel ("Task 12"))
        tasksScrollLayout.addWidget (QLabel ("Task 13"))
        tasksScrollLayout.addWidget (QLabel ("Task 14"))
        self.tasksWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tasksWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tasksWidget.setWidgetResizable(False)
        self.tasksWidget.setWidget (QWidget (self.tasksWidget).setLayout (tasksScrollLayout))

        scriptsScrollLayout = QVBoxLayout ()
        scriptsScrollLayout.addWidget (QLabel ("Script 1"))
        scriptsScrollLayout.addWidget (QLabel ("Script 2"))
        scriptsScrollLayout.addWidget (QLabel ("Script 3"))
        scriptsScrollLayout.addWidget (QLabel ("Script 4"))
        scriptsScrollLayout.addWidget (QLabel ("Script 5"))
        scriptsScrollLayout.addWidget (QLabel ("Script 6"))
        scriptsScrollLayout.addWidget (QLabel ("Script 7"))
        scriptsScrollLayout.addWidget (QLabel ("Script 8"))
        scriptsScrollLayout.addWidget (QLabel ("Script 9"))
        scriptsScrollLayout.addWidget (QLabel ("Script 10"))
        scriptsScrollLayout.addWidget (QLabel ("Script 11"))
        scriptsScrollLayout.addWidget (QLabel ("Script 12"))
        scriptsScrollLayout.addWidget (QLabel ("Script 13"))
        scriptsScrollLayout.addWidget (QLabel ("Script 14"))
        self.scriptsWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scriptsWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scriptsWidget.setWidgetResizable(False)
        self.scriptsWidget.setWidget (QWidget (self.scriptsWidget).setLayout (scriptsScrollLayout))
        
        grid = QGridLayout ()

        grid.setColumnMinimumWidth(0, self.width() // 3)
        grid.setColumnMinimumWidth(1, self.width() // 3)
        grid.setColumnMinimumWidth(2, self.width() // 3)

        grid.setRowMinimumHeight(0, self.height() // 4)
        grid.setRowMinimumHeight(1, self.height() // 4)
        grid.setRowMinimumHeight(2, self.height() // 4)
        grid.setRowMinimumHeight(3, self.height() // 4)



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
        if (self.state != self.windowState ()) :
            self.initUI ()
            self.state = self.windowState ()

        self.leftCameraWidget.update ()
        self.middleCameraWidget.update ()
        self.rightCameraWidget.update ()
        self.orientationsWidget.update ()


if __name__ == "__main__" :
    app = QApplication (sys.argv)
    mainWindow = MainWindow ()
    mainWindow.show ()
    sys.exit (app.exec_ ())