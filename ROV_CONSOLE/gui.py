import random
from functools import partial
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QBrush, QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QPushButton,
    QInputDialog,
    QLineEdit, QMenuBar, QMenu, QToolButton,
    )

from .controller_widget import ControllerDisplay
from .cv_stream import VideoStream
from .esp32 import ESP32
from .gamepad import Controller
from .measurement_widget import MeasurementWindow

ASSETS_PATH = Path(__file__).resolve().parent / 'assets'
camera_toolbar_icons = {
    'hflip':       QIcon(str(ASSETS_PATH / 'flip-horizontal.svg')),
    'vflip':       QIcon(str(ASSETS_PATH / 'flip-vertical.svg')),
    'measurement': QIcon(str(ASSETS_PATH / 'ruler.svg')),
    'pano':        QIcon(str(ASSETS_PATH / 'pano.svg'))
    }
APP_ICON = ASSETS_PATH / 'appicon.png'


class CameraWidget(QWidget):

    def __init__(self, parent, cam):
        super().__init__(parent)
        self._stream = VideoStream(cam)
        self._view = QLabel(self)
        self._view.setScaledContents(True)
        self._empty_frame = self._pixmap_from_frame(self._stream.EMPTY_FRAME)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.bottom_buttons = {}
        for b in camera_toolbar_icons:
            pb = QPushButton(self)
            pb.setIcon(camera_toolbar_icons[b])
            pb.setIconSize(QSize(24, 24))
            pb.setVisible(False)
            self.bottom_buttons[b] = pb
        self.h_mirror = False
        self.v_mirror = False
        self.bottom_buttons['hflip'].clicked.connect(self.hflip)
        self.bottom_buttons['vflip'].clicked.connect(self.vflip)
        self.bottom_buttons['measurement'].clicked.connect(
            self._launch_length_measurement
            )
        self.camera_choice_button = QToolButton(self)
        self.camera_choice_button.setText('Cameras')
        self.camera_choice_menu = QMenu(self)
        self.camera_choice_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.camera_choice_button.setMenu(self.camera_choice_menu)
        cameras = self._stream.available_cameras
        for c in cameras:
            action = QAction(f'{c}:{cameras[c]}', self)
            self.camera_choice_menu.addAction(action)
            action.triggered.connect(partial(self.change_cam, int(c)))

    def hflip(self):
        self.h_mirror = not self.h_mirror

    def vflip(self):
        self.v_mirror = not self.v_mirror

    def enterEvent(self, event):
        w = self.width() // 4
        h = self.height() - self.height() // 10
        for b in self.bottom_buttons.values():
            b.move(w, h)
            b.setVisible(True)
            b.raise_()
            w += 36

    def leaveEvent(self, event):
        for b in self.bottom_buttons.values():
            b.setVisible(False)

    def _pixmap_from_frame(self, frame):
        return QPixmap(
            QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_BGR888))

    def _pixmap_from_stream(self):
        frame = self._stream.frame
        if frame is None:
            return self._empty_frame
        q_image = (
            QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                frame.strides[0],
                QImage.Format.Format_BGR888,
                )
            .mirrored(horizontally=self.h_mirror, vertically=self.v_mirror)
        )
        return QPixmap.fromImage(q_image)

    def _launch_length_measurement(self):
        self.measurement_window = MeasurementWindow(self, self._pixmap_from_stream())

    def resizeEvent(self, event):
        self._view.resize(event.size())

    def change_cam(self, cam):
        self._stream.source = cam

    def update(self):
        self._view.setPixmap(self._pixmap_from_stream())


class OrientationsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

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

        self.depthLabel.setText('Depth: ' + str(depthReading))
        self.yawLabel.setText('Yaw: ' + str(yawReading))
        self.pitchLabel.setText('Pitch: ' + str(pitchReading))
        self.rollLabel.setText('Roll: ' + str(rollReading))


class ThrustersWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

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
            QColor(0, 255, 0),
            # ,  # Bottom
            # # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
            ]

        self.rotated_square_colors = [
            QColor(0, 255, 0),  # Front-left
            QColor(0, 255, 0),  # Front-right
            QColor(0, 255, 0),  # Back-left
            QColor(0, 255, 0),  # Back-right
            ]

    def set_colors(self):
        '''Allows changing colors dynamically'''

        frontRightSpeed = 0
        backRightSpeed = 255
        frontLeftSpeed = 100
        backLeftSpeed = 200
        upFrontSpeed = 50
        upBackSpeed = 150

        self.frontLabel.setText(str(upFrontSpeed))
        self.backLabel.setText(str(upBackSpeed))
        self.leftfrontLabel.setText(str(frontLeftSpeed))
        self.rightfrontLabel.setText(str(frontRightSpeed))
        self.leftbackLabel.setText(str(backLeftSpeed))
        self.rightbackLabel.setText(str(backRightSpeed))

        self.square_color = QColor(0, 0, 0)
        self.circle_colors = [
            QColor(upFrontSpeed, 255 - upFrontSpeed, 0),  # Top
            QColor(upBackSpeed, 255 - upBackSpeed, 0),
            # ,  # Bottom
            # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
            ]
        self.rotated_square_colors = [
            QColor(frontLeftSpeed, 255 - frontLeftSpeed, 0),  # Front-left
            QColor(frontRightSpeed, 255 - frontRightSpeed, 0),  # Front-right
            QColor(backLeftSpeed, 255 - backLeftSpeed, 0),  # Back-left
            QColor(backRightSpeed, 255 - backRightSpeed, 0),  # Back-right
            ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get parent size constraints
        max_width = self.parent.width() // 3
        max_height = self.parent.height() // 4
        size = min(max_width, max_height)

        # Central square (70% of size)
        square_size = int(
            size * 0.7
            )  ###changing the ratio changes the thrusters size###
        square_x = (self.width() - square_size) // 2
        square_y = (self.height() - square_size) // 2

        # Draw the black center square
        painter.setPen(QPen(self.square_color, 3))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(square_x, square_y, square_size, square_size)

        # Circles' and Rotated Squares' Positions
        offsets = [
            (square_x + square_size // 2, square_y - square_size // 3),  # Top
            (square_x + square_size // 2, square_y + square_size + square_size // 3),
            # ,  # Bottom
            # (square_x - square_size // 3, square_y + square_size // 2),  # Left
            # (square_x + square_size + square_size // 3, square_y + square_size // 2)  # Right
            ]

        rotated_offsets = [
            (square_x - square_size // 3, square_y - square_size // 3),  # Top-left
            (
                square_x + square_size + square_size // 3,
                square_y - square_size // 3,
                ),  # Top-right
            (
                square_x - square_size // 3,
                square_y + square_size + square_size // 3,
                ),  # Bottom-left
            (
                square_x + square_size + square_size // 3,
                square_y + square_size + square_size // 3,
                ),  # Bottom-right
            ]

        self.frontLabel.setGeometry(
            offsets[0][0] - 10, offsets[0][1] - 15, 100, 30
            )  # (x, y, width, height)
        self.backLabel.setGeometry(offsets[1][0] - 10, offsets[1][1] - 15, 100, 30)
        self.leftfrontLabel.setGeometry(
            rotated_offsets[0][0] - 10, rotated_offsets[0][1] - 15, 100, 30
            )
        self.rightfrontLabel.setGeometry(
            rotated_offsets[1][0] - 10, rotated_offsets[1][1] - 15, 100, 30
            )
        self.leftbackLabel.setGeometry(
            rotated_offsets[2][0] - 10, rotated_offsets[2][1] - 15, 100, 30
            )
        self.rightbackLabel.setGeometry(
            rotated_offsets[3][0] - 10, rotated_offsets[3][1] - 15, 100, 30
            )

        circle_radius = int(square_size * 0.2)

        # Draw Circles with individual colors
        for i, (x, y) in enumerate(offsets):
            painter.setBrush(QBrush(self.circle_colors[i]))
            painter.drawEllipse(
                x - circle_radius,
                y - circle_radius,
                circle_radius * 2,
                circle_radius * 2,
                )

        # Draw Rotated Squares with individual colors
        for i, (x, y) in enumerate(rotated_offsets):
            painter.setBrush(QBrush(self.rotated_square_colors[i]))
            painter.save()
            painter.translate(x, y)
            painter.rotate(45)  # Rotate by 45 degrees
            painter.drawRect(
                -circle_radius, -circle_radius, circle_radius * 2, circle_radius * 2
                )
            painter.restore()

    def updateThrusters(self):
        self.set_colors()
        self.update()


class MenuBar(QMenuBar):
    _esp_menu: QMenu
    _controller_menu: QMenu
    _esp_actions: list[QAction]

    def __init__(self, parent, esp: ESP32, controller: Controller):
        super().__init__(parent)
        self._esp = esp
        self._esp_menu = self.addMenu('ESP')
        self._esp_menu_sep = self._esp_menu.addSeparator()
        self._esp_menu_add_custom = self._esp_menu.addAction('Custom Port')
        self._esp_menu_add_custom.triggered.connect(self.manual_port_selection)
        self._esp_menu_reset_esp = QAction('Reset ESP')
        self._esp_menu_reset_esp.triggered.connect(self._esp.reset)
        self._esp_menu_no_esp = QAction('No Serial Ports')
        self._esp_menu_no_esp.setEnabled(False)
        self._displayed_ports: list[QAction] = []
        self._port_slots: dict[str:partial] = {}
        self._stored_ports = []
        self._stored_custom_port = None
        self._controller = controller
        self._controller_menu = self.addMenu('Controller')
        self._displayed_controllers: list[QAction] = []
        self._stored_controllers: list[str] = []
        self._gp_menu_none_connected = QAction('No ControllerS Connected')
        self._gp_menu_none_connected.setEnabled(False)
        self._gp_slots: dict[str:partial] = {}

    def update(self):
        self._update_controller_menu()
        self._update_esp_menu()

    def _update_controller_menu(self):
        gamepads = self._controller.gamepads
        chosen = self._controller.gamepad
        new_gamepads = [gp for gp in gamepads if gp not in self._stored_controllers]
        removed_gamepads = [gp for gp in self._stored_controllers if gp not in gamepads]
        if len(gamepads) == 0:
            if len(removed_gamepads) != 0:
                self._controller_menu.addAction(self._gp_menu_none_connected)
        else:
            self._controller_menu.removeAction(self._gp_menu_none_connected)
        for gp in new_gamepads:
            option = QAction(f'{gp}')
            self._controller_menu.addAction(option)
            f = partial(self.toggle_controller, gp)
            self._gp_slots.update({gp: f})
            option.triggered.connect(f)
            self._displayed_controllers.append(option)
        for gp in removed_gamepads:
            for option in self._displayed_controllers:
                if option.text() == gp:
                    f = self._gp_slots.pop(gp)
                    option.triggered.disconnect(f)
                    self._controller_menu.removeAction(option)
                    self._displayed_controllers.remove(option)
        self._stored_controllers = gamepads
        for option in self._displayed_controllers:
            if chosen == option.text():
                option.setCheckable(True)
                option.setChecked(True)
            else:
                option.setChecked(False)
                option.setCheckable(False)

    def _update_esp_menu(self):
        # Tracking changes
        ports = self._esp.available_ports
        chosen = self._esp.port
        new_custom_port = chosen if chosen not in ports and chosen != self._stored_custom_port else None
        new_ports = [p for p in ports if p not in self._stored_ports]
        removed_ports = [p for p in self._stored_ports if p not in ports]
        if len(ports) == 0:
            if len(removed_ports) != 0:
                self._esp_menu.insertAction(self._esp_menu_sep, self._esp_menu_no_esp)
        else:
            self._esp_menu.removeAction(self._esp_menu_no_esp)
        for port in new_ports:
            option = QAction(f'{port}')
            self._esp_menu.insertAction(self._esp_menu_sep, option)
            f = partial(self.toggle_port, port)
            self._port_slots.update({port: f})
            option.triggered.connect(f)
            self._displayed_ports.append(option)
        if chosen is None and self._stored_custom_port is not None and new_custom_port is None:
            removed_ports.append(self._stored_custom_port)
        for port in removed_ports:
            for option in self._displayed_ports:
                if option.text() == port:
                    f = self._port_slots.pop(port)
                    option.triggered.disconnect(f)
                    self._esp_menu.removeAction(option)
                    self._displayed_ports.remove(option)
        self._stored_ports = ports
        if new_custom_port is not None:
            self._stored_custom_port = new_custom_port
            option = self._esp_menu.addAction(f'{new_custom_port}')
            f = partial(self.toggle_port, new_custom_port)
            self._port_slots.update({new_custom_port: f})
            option.triggered.connect(f)
            self._displayed_ports.append(option)

        for option in self._displayed_ports:
            if chosen == option.text():
                option.setCheckable(True)
                option.setChecked(True)
            else:
                option.setChecked(False)
                option.setCheckable(False)
        if chosen is not None:
            if new_custom_port is not None or len(new_ports) != 0:
                self._esp_menu.addAction(self._esp_menu_reset_esp)
        else:
            self._esp_menu.removeAction(self._esp_menu_reset_esp)

    def toggle_port(self, port):
        if self._esp.port == port:
            self._esp.disconnect()
            self._controller.payload_callback = None
        else:
            self._esp.connect(port)
            self._controller.payload_callback = self._esp.send

    def manual_port_selection(self):
        text, ok = QInputDialog.getText(
            self,
            'Custom Port',
            'Port Name (RFC2217 NOT FULLY SUPPORTED):',
            QLineEdit.EchoMode.Normal,
            'COM',
            )
        if ok:
            self.toggle_port(text)

    def toggle_controller(self, indexed_name):
        if self._controller.connected:
            if indexed_name == self._controller.gamepad:
                self._controller.gamepad = None
                return
        i = indexed_name[: indexed_name.find(':')]
        self._controller.gamepad = int(i)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.showMaximized()
        self.setWindowTitle('AU Robotics ROV GUI')
        self.setWindowIcon(QIcon(str(APP_ICON)))

        self.controller = Controller()
        self.esp = ESP32()
        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(15)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.leftCameraWidget = CameraWidget(self, 0)
        self.middleCameraWidget = CameraWidget(self, 0)
        self.rightCameraWidget = CameraWidget(self, 2)
        self.orientationsWidget = OrientationsWidget(self)
        self.controllerWidget = ControllerDisplay(self.controller)
        self.thrustersWidget = ThrustersWidget(self)

        self.menu_bar = MenuBar(self, self.esp, self.controller)
        self.setMenuBar(self.menu_bar)

        grid = QGridLayout()

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 1)

        grid.addWidget(self.leftCameraWidget, 0, 0, 2, 3)
        grid.addWidget(self.middleCameraWidget, 0, 3, 1, 1)
        grid.addWidget(self.rightCameraWidget, 1, 3, 1, 1)

        grid.addWidget(self.orientationsWidget, 2, 0, 2, 1)

        grid.addWidget(self.controllerWidget, 2, 1, 2, 2)
        grid.addWidget(self.thrustersWidget, 2, 2, 2, 2)

        central_widget.setLayout(grid)

    def updateFrame(self):
        self.orientationsWidget.update()
        self.thrustersWidget.updateThrusters()
        self.leftCameraWidget.update()
        self.middleCameraWidget.update()
        self.rightCameraWidget.update()
        self.menu_bar.update()
        if self.esp.connected:
            while self.esp.incoming:
                print(self.esp.next_line)
