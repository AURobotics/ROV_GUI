import sys, random
import threading
from .controlling import Controller
from .vision import Camera

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QCheckBox,
    QPushButton,
    QMenu,
    QInputDialog,
    QLineEdit
)
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QFont,
    QPainter,
    QColor,
    QPen,
    QBrush
)
from PySide6.QtCore import (
    QThread,
    Signal,
    QTimer,
    Qt
)
from trying_shit import PS4ControllerSimulation

import serial.tools.list_ports
import serial
from functools import partial


class CameraWidget(QLabel):
    def __init__(self, parent, cam):
        super().__init__(parent)
        self._cam = Camera(cam)

    def update(self):
            frame = self._cam.frame
            if frame is not None:
                q_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_BGR888).smoothScaled(self.width(), self.height())
                self.setPixmap(QPixmap.fromImage(q_image))


class OrientationsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setMinimumSize(parent.width() // 3, parent.height() // 2)

        layout = QVBoxLayout()

        self.setLayout(layout)

        self.depthLabel = QLabel(self)
        self.yawLabel = QLabel(self)
        self.pitchLabel = QLabel(self)
        self.rollLabel = QLabel(self)

        layout.addWidget(self.depthLabel)
        layout.addWidget(self.yawLabel)
        layout.addWidget(self.pitchLabel)
        layout.addWidget(self.rollLabel)

        self.update()

    def update(self):
        # TODO: Change the randint to reading from RPi/ESP32 using PySerial
        depthReading = random.randint(0, 10)
        yawReading = random.randint(0, 10)
        pitchReading = random.randint(0, 10)
        rollReading = random.randint(0, 10)

        self.depthLabel.setText("Depth: " + str(depthReading))
        self.yawLabel.setText("Yaw: " + str(yawReading))
        self.pitchLabel.setText("Pitch: " + str(pitchReading))
        self.rollLabel.setText("Roll: " + str(rollReading))


class ThrustersWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.setMinimumSize(parent.width() // 3, parent.height() // 4)

        self.frontLabel = QLabel(self)
        self.backLabel = QLabel(self)
        self.leftfrontLabel = QLabel(self)
        self.rightfrontLabel = QLabel(self)
        self.leftbackLabel = QLabel(self)
        self.rightbackLabel = QLabel(self)

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
            QColor(0, 255, 0)  # Back-right
        ]

    def set_colors(self):
        """Allows changing colors dynamically"""

        frontRightSpeed = 0
        backRightSpeed = 255
        frontLeftSpeed = 100
        backLeftSpeed = 200
        upFrontSpeed = 50
        upBackSpeed = 150

        self.frontLabel.setText( str(upFrontSpeed))
        self.backLabel.setText(str(upBackSpeed))
        self.leftfrontLabel.setText( str(frontLeftSpeed))
        self.rightfrontLabel.setText(str(frontRightSpeed))
        self.leftbackLabel.setText( str(backLeftSpeed))
        self.rightbackLabel.setText( str(backRightSpeed))
       



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
            QColor(backRightSpeed, 255 - backRightSpeed, 0)  # Back-right
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get parent size constraints
        max_width = self.parent.width() // 3
        max_height = self.parent.height() // 4
        size = min(max_width, max_height)

        # Central square (70% of size)
        square_size = int(size * 0.7)           ###changing the ratio changes the thrusters size### 
        square_x = (self.width() - square_size) // 2
        square_y = (self.height() - square_size) // 2

        # Draw the black center square
        painter.setPen(QPen(self.square_color, 3))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
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
            (square_x + square_size + square_size // 3, square_y - square_size // 3),  # Top-right
            (square_x - square_size // 3, square_y + square_size + square_size // 3),  # Bottom-left
            (square_x + square_size + square_size // 3, square_y + square_size + square_size // 3)  # Bottom-right
        ]

        self.frontLabel.setGeometry(offsets[0][0]-10, offsets[0][1]-15, 100, 30)  # (x, y, width, height)
        self.backLabel.setGeometry(offsets[1][0]-10, offsets[1][1]-15, 100, 30)
        self.leftfrontLabel.setGeometry(rotated_offsets[0][0]-10,rotated_offsets[0][1]-15, 100, 30)
        self.rightfrontLabel.setGeometry(rotated_offsets[1][0]-10,rotated_offsets[1][1]-15, 100, 30)
        self.leftbackLabel.setGeometry(rotated_offsets[2][0]-10,rotated_offsets[2][1]-15, 100, 30)  
        self.rightbackLabel.setGeometry(rotated_offsets[3][0]-10,rotated_offsets[3][1]-15, 100, 30)
      

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

    def updateThrusters(self):
        self.set_colors()
        self.update()


class ScriptWidget(QWidget):
    def __init__(self, desc):
        super().__init__()

        self.desc = desc

        hbox = QHBoxLayout(self)

        hbox.addWidget(QLabel(self.desc))

        self.button = QPushButton("Run", self)
        self.button.clicked.connect(self.runScript)

        hbox.addWidget(self.button)

    def runScript(self):
        print(self.desc)
        
class ControllerWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller_sim = PS4ControllerSimulation()
        layout = QVBoxLayout()
        layout.addWidget(self.controller_sim)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showMaximized()
        self.setWindowTitle("AU Robotics ROV GUI")

        self.state = self.windowState()

        self.initUI()

        # ser = serial.Serial('COM8', baudrate=115200)
        self.controller = Controller()
        self.ser: serial.Serial|None = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(15)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.leftCameraWidget = CameraWidget(self, 0)
        self.middleCameraWidget = CameraWidget(self, 2)
        self.rightCameraWidget = CameraWidget(self, 1)
        self.orientationsWidget = OrientationsWidget(self)
        self.controllerWidget = ControllerWidget(self)
        self.thrustersWidget = ThrustersWidget(self)
        self.tasksWidget = QScrollArea(self)
        self.scriptsWidget = QScrollArea(self)

        self.initTasks()
        self.initScripts()
        
        grid = QGridLayout()

        # grid.setColumnMinimumWidth(0, self.width() // 3)
        # grid.setColumnMinimumWidth(1, self.width() // 3)
        # grid.setColumnMinimumWidth(2, self.width() // 3)

        # grid.setRowMinimumHeight(0, self.height() // 4)
        # grid.setRowMinimumHeight(1, self.height() // 4)
        # grid.setRowMinimumHeight(2, self.height() // 4)
        # grid.setRowMinimumHeight(3, self.height() // 4)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 2)

        grid.addWidget(self.leftCameraWidget, 0, 0, 2, 1)
        grid.addWidget(self.middleCameraWidget, 0, 1, 2, 1)
        grid.addWidget(self.rightCameraWidget, 0, 2, 2, 1)

        grid.addWidget(self.orientationsWidget, 2, 0, 2, 1)

        grid.addWidget(self.tasksWidget, 2, 1, 1, 1)
        grid.addWidget(self.controllerWidget, 3, 1, 1, 1)

        grid.addWidget(self.scriptsWidget, 2, 2, 1, 1)
        grid.addWidget(self.thrustersWidget, 3, 2, 1, 1)

        central_widget.setLayout(grid)
        self._cameras_thread = threading.Thread(target=self.cameras_thread, daemon=True)
        self._cameras_thread.start()
        
    
    def createMenuBar(self):
        ports = serial.tools.list_ports.comports()
        # 'com_list' contains list of all com ports
        com_list = []
        for p in ports:
            com_list.append(p.device)

        menuBar = self.menuBar()
        #  Clear existing menus
        menuBar.clear()
        # Creating menus using a QMenu object
        fileMenu = QMenu("Serial Port", self)
        menuBar.addMenu(fileMenu)
        for i in com_list:
            port_selected = fileMenu.addAction(f"{i}")
            port_selected.triggered.connect(partial(self.portSelected, i))
        fileMenu.addSeparator()
        manual_port_selection = fileMenu.addAction('Manual Port Selection')
        manual_port_selection.triggered.connect(partial(self.manual_port_selection))

    def manual_port_selection(self):
        text, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                                        "Port or URL:", QLineEdit.EchoMode.Normal,
                                        "COM")
        print(text)
        self.portSelected(text)
    def portSelected(self, port):
        print(f"Selected port: {port}")
        if self.ser is not None:
            self.ser.close()
        if port.startswith("rfc"):
            self.ser = serial.serial_for_url(port, baudrate=115200)
        else:
            self.ser = serial.Serial(port , baudrate=115200)
        self.controller.payload_callback = self.ser.write
        

    def updateFrame(self):
        if (self.state != self.windowState()):
            self.state = self.windowState()
        self.orientationsWidget.update()
        self.thrustersWidget.updateThrusters()
        self.createMenuBar()
        if self.ser is not None:
            try:
                while self.ser.in_waiting:
                    print(self.ser.readline())
            except serial.SerialException:
                self.ser = None
        
        
    def cameras_thread(self):
        while True:
            self.leftCameraWidget.update()
            self.middleCameraWidget.update()
            self.rightCameraWidget.update()
    def initTasks(self):
        tasksContainer = QWidget()
        tasksScrollLayout = QVBoxLayout(tasksContainer)

        tasksScrollLayout.addWidget(QCheckBox("Task 1"))
        tasksScrollLayout.addWidget(QCheckBox("Task 2"))
        tasksScrollLayout.addWidget(QCheckBox("Task 3"))
        tasksScrollLayout.addWidget(QCheckBox("Task 4"))
        tasksScrollLayout.addWidget(QCheckBox("Task 5"))
        tasksScrollLayout.addWidget(QCheckBox("Task 6"))
        tasksScrollLayout.addWidget(QCheckBox("Task 7"))
        tasksScrollLayout.addWidget(QCheckBox("Task 8"))
        tasksScrollLayout.addWidget(QCheckBox("Task 9"))
        tasksScrollLayout.addWidget(QCheckBox("Task 10"))
        tasksScrollLayout.addWidget(QCheckBox("Task 11"))
        tasksScrollLayout.addWidget(QCheckBox("Task 12"))
        tasksScrollLayout.addWidget(QCheckBox("Task 13"))

        self.tasksWidget.setWidget(tasksContainer)

    def initScripts(self):
        scriptsContainer = QWidget()
        scriptsScrollLayout = QVBoxLayout(scriptsContainer)

        scriptsScrollLayout.addWidget(ScriptWidget("Script 1"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 2"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 3"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 4"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 5"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 6"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 7"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 8"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 9"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 10"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 11"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 12"))
        scriptsScrollLayout.addWidget(ScriptWidget("Script 13"))

        self.scriptsWidget.setWidget(scriptsContainer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
