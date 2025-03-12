import random
from .controlling import Controller
from .vision import Camera
from .esp32 import ESP32

from PySide6.QtWidgets import (
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
    QPainter,
    QColor,
    QPen,
    QBrush
)
from PySide6.QtCore import (
    QTimer,
    Qt
)
from .controller_widget import ControllerDisplay
from functools import partial
import requests

RASPBERY_PI_IP = "192.168.1.2"


class CameraWidget(QLabel):
    def __init__(self, parent, cam):
        super().__init__(parent)
        self.cam = Camera(cam)

    def update(self):
            frame = self.cam.frame
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showMaximized()
        self.setWindowTitle("AU Robotics ROV GUI")

        self.state = self.windowState()
        self.controller = Controller()
        self.esp = ESP32()
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(15)


    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        def is_url_reachable(url):
            try:
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            except requests.RequestException:
                return False
        left_camera_url = "http://" + RASPBERY_PI_IP + ":8081/stream"
        if is_url_reachable(left_camera_url):
            self.leftCameraWidget = CameraWidget(self, left_camera_url)
        else:
            self.leftCameraWidget = CameraWidget(self, 0)
        middle_camera_url = "http://" + RASPBERY_PI_IP + ":8080/stream"
        if is_url_reachable(middle_camera_url):
            self.middleCameraWidget = CameraWidget(self, middle_camera_url)
        else:
            self.middleCameraWidget = CameraWidget(self, 1)
        right_camera_url = "http://" + RASPBERY_PI_IP + ":8082/stream"
        if is_url_reachable(right_camera_url):
            self.rightCameraWidget = CameraWidget(self, right_camera_url)
        else:
            self.rightCameraWidget = CameraWidget(self, 2)
        self.orientationsWidget = OrientationsWidget(self)
        self.controllerWidget = ControllerDisplay(self.controller)
        self.thrustersWidget = ThrustersWidget(self)
        self.tasksWidget = QScrollArea(self)
        self.scriptsWidget = QScrollArea(self)

        self.menu_bar = self.menuBar()
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
        
    
    def createMenuBar(self):
        self.menu_bar.clear()
        port_menu = QMenu("Serial Port", self)
        port_is_from_choices = False
        self.menu_bar.addMenu(port_menu)
        for i in self.esp.available_ports:
            port_sel = port_menu.addAction(f'{i}')
            port_sel.setCheckable(True)
            if i == self.esp.port:
                port_sel.setChecked(True)
                port_is_from_choices = True
            port_sel.triggered.connect(partial(self.toggle_port, i))
        if self.esp.port is not None and not port_is_from_choices:
            port_sel = port_menu.addAction(f'{self.esp.port}')
            port_sel.setCheckable(True)
            port_sel.setChecked(True)
            port_sel.triggered.connect(partial(self.toggle_port, self.esp.port))
        port_menu.addSeparator()
        manual_port_selection = port_menu.addAction('Custom Port Selection')
        manual_port_selection.triggered.connect(partial(self.manual_port_selection))
        if self.esp.connected:
            reset_esp = port_menu.addAction('Reset ESP')
            reset_esp.triggered.connect(self.esp.reset)

        if not self.controller.gamepads:
            return
        controller_menu = QMenu("Controller", self)
        self.menu_bar.addMenu(controller_menu)
        for gp in self.controller.gamepads:
            gp_sel = controller_menu.addAction(f"{gp}")
            gp_sel.triggered.connect(partial(self.toggle_controller, gp))
            gp_sel.setCheckable(True)
            if self.controller.gamepad == gp:
                gp_sel.setChecked(True)


    def manual_port_selection(self):
        text, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                                        "Port Name (RFC2217 NOT FULLY SUPPORTED):", QLineEdit.EchoMode.Normal,
                                        "COM")
        if ok:
            self.toggle_port(text)

    def toggle_port(self, port):
        if self.esp.port == port:
            self.esp.disconnect()
            self.controller.payload_callback = None
        else:
            self.esp.connect(port)
            self.controller.payload_callback = self.esp.send

    def toggle_controller(self, indexed_name):
        if self.controller.connected:
            if indexed_name == self.controller.gamepad:
                self.controller.gamepad = None
                return
        i = indexed_name[:indexed_name.find(':')]
        self.controller.gamepad = int(i)

    def updateFrame(self):
        if (self.state != self.windowState()):
            self.state = self.windowState()
        self.orientationsWidget.update()
        self.thrustersWidget.updateThrusters()
        self.createMenuBar()
        self.leftCameraWidget.update()
        self.middleCameraWidget.update()
        self.rightCameraWidget.update()
        if self.esp.connected:
            while self.esp.incoming:
                print(self.esp.next_line)
        

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