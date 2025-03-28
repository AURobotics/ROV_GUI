from functools import partial

from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon, QAction, QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QWidget,
    QGridLayout,
    QPushButton,
    QInputDialog,
    QLineEdit, QMenuBar, QMenu, QToolButton, QSpacerItem, QSizePolicy, )
from plyer import notification

from ROV_CONSOLE.comms import CommunicationManager
from ROV_CONSOLE.constants import APP_ICON, ASSETS_PATH
from ROV_CONSOLE.controller_widget import ControllerDisplay
from ROV_CONSOLE.cv_stream import VideoStream, CapMetadata, CapType, ConnectionStatus, DisconnectReason
from ROV_CONSOLE.esp32 import ESP32
from ROV_CONSOLE.gamepad import Controller
from ROV_CONSOLE.measurement_widget import MeasurementWindow
from ROV_CONSOLE.orientation_widget import OrientationWidget
from ROV_CONSOLE.thrusters_widget import ThrustersWidget


class CameraWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Window)
        # self.setWindowModality(Qt.WindowModality.WindowModal)
        width, height = QGuiApplication.primaryScreen().size().toTuple()
        width //= 2
        height //= 2
        self._frame = QLabel(self)
        self.resize(width, height)
        self._frame.setScaledContents(True)
        self.setWindowTitle("Video Stream")
        self.show()

    def resizeEvent(self, event):
        self._frame.resize(event.size())

    def update_(self, pix):
        self._frame.setPixmap(pix)


class CameraWidget(QWidget):
    def __init__(self, parent, cam):
        super().__init__(parent)
        self._stream = VideoStream(cam)
        self._view = QLabel(self)
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self._empty_frame = self._pixmap_from_frame(self._stream.EMPTY_FRAME)
        self.h_mirror = False
        self.v_mirror = False
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._bottom_toolbar = QGridLayout()
        self.setLayout(self._bottom_toolbar)

        toolbar_buttons = {
            'hflip':       {'icon': QIcon(str(ASSETS_PATH / 'flip-horizontal.svg')), 'function': self.hflip},
            'vflip':       {'icon': QIcon(str(ASSETS_PATH / 'flip-vertical.svg')), 'function': self.vflip},
            'measurement': {'icon': QIcon(str(ASSETS_PATH / 'ruler.svg')), 'function': self._launch_length_measurement},
            'pano':        {'icon': QIcon(str(ASSETS_PATH / 'pano.svg')), 'function': None},
            'maximize':    {'icon': QIcon(str(ASSETS_PATH / 'maximize.svg')), 'function': self.launch_maximized},
            }
        self._bottom_toolbar.setRowStretch(8, 1)  # Add 9 empty rows
        pos = [9, 0]  # Utilize the 10th (forces it to be the bottom-most row)
        for b in toolbar_buttons:
            pb = QPushButton(toolbar_buttons[b]['icon'], '')
            pb.setIconSize(QSize(24, 24))
            pb.clicked.connect(toolbar_buttons[b]['function'])
            pb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            pb.setVisible(False)
            self._bottom_toolbar.addWidget(pb, *pos, 1, 1)
            pos[1] += 1
            self._bottom_toolbar.addItem(
                QSpacerItem(24, 24, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding),
                *pos, 1, 1)
            pos[1] += 1
        self._camera_dropdown = QToolButton(self)
        self._camera_dropdown.setVisible(False)

        self._camera_dropdown.setText('Camera Disconnected')
        self._camera_menulist = QMenu(self)  # Could be rewritten as a QComboBox
        self._camera_dropdown.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._camera_dropdown.setMenu(self._camera_menulist)
        self._camera_dropdown.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)

        self._cam_menu_displayed_cams: list[QAction] = []
        self._cam_menu_slots: dict[int | str:partial] = {}
        self._cam_menu_stored_cameras: list[CapMetadata] = []

        self._cam_menu_no_cam_indicator = QAction('Camera Disconnected')
        self._cam_menu_no_cam_indicator.setEnabled(False)
        self._camera_menulist.addAction(self._cam_menu_no_cam_indicator)
        self._cam_menu_sep = self._camera_menulist.addSeparator()
        self._cam_menu_add_custom = self._camera_menulist.addAction('Custom URL')
        self._cam_menu_add_custom.triggered.connect(self.custom_camera_popup)
        self._bottom_toolbar.addWidget(self._camera_dropdown, *pos, 1, 1)
        self.setLayout(self._bottom_toolbar)
        self._maximized_popup = None

    def hflip(self):
        self.h_mirror = not self.h_mirror

    def vflip(self):
        self.v_mirror = not self.v_mirror

    def launch_maximized(self):
        if self._maximized_popup is None:
            self._maximized_popup = CameraWindow(self)

    def enterEvent(self, event):
        for i in range(self._bottom_toolbar.count()):
            item = self._bottom_toolbar.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(True)

    def leaveEvent(self, event):
        for i in range(self._bottom_toolbar.count()):
            item = self._bottom_toolbar.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(False)

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
        current_cam = self._stream.source
        if current_cam is not None:
            if current_cam['descriptor'] == cam:
                self._stream.source = None
                return
        self._stream.source = cam

    def update(self):
        pix = self._pixmap_from_stream()
        pix = pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self._view.setPixmap(pix)
        if self._maximized_popup is not None:
            if not self._maximized_popup.isVisible():
                self._maximized_popup = None
            else:
                self._maximized_popup.update_(pix)
        if self._stream.connection_status == ConnectionStatus.IN_PROGRESS:
            self._camera_dropdown.setText('Connecting..')
            return
        elif (self._stream.connection_status == ConnectionStatus.DISCONNECTED and self._stream.disconnect_reason is
              not DisconnectReason.DESIRED_DISCONNECT):
            notification.notify(
                title='Camera Disconnected',
                message=self._stream.disconnect_message,
                timeout=2,
                app_name='AU Robotics ROV GUI'
                )
        _devices = self._stream.available_cameras
        cameras = [CapMetadata(descriptor=cam, name=_devices[cam], type=CapType.DEVICE) for cam in _devices]
        old_custom = None
        for cam in self._cam_menu_stored_cameras:
            if cam not in cameras:
                old_custom = cam
                break
        chosen = self._stream.source
        if chosen is not None:
            chosen = chosen.copy()
        new_custom = chosen if chosen not in cameras and chosen != old_custom else None
        new_cameras = [cam for cam in cameras if cam not in self._cam_menu_stored_cameras]
        old_cameras = [cam for cam in self._cam_menu_stored_cameras if cam not in cameras and cam != old_custom]

        if len(cameras) == 0:
            if len(old_cameras) != 0:
                self._camera_menulist.insertAction(self._cam_menu_sep, self._cam_menu_no_cam_indicator)
        else:
            self._camera_menulist.removeAction(self._cam_menu_no_cam_indicator)
        for cam in new_cameras:
            option = QAction(f'{cam['name']}')

            self._camera_menulist.insertAction(self._cam_menu_sep, option)
            f = partial(self.change_cam, cam['descriptor'])
            self._cam_menu_slots.update({cam['descriptor']: f})
            option.triggered.connect(f)
            self._cam_menu_displayed_cams.append(option)
            self._cam_menu_stored_cameras.append(cam)

        if chosen != old_custom and old_custom is not None:
            old_cameras.append(old_custom)

        for cam in old_cameras:
            for option in self._cam_menu_displayed_cams:
                if option.text() == f'{cam['name']}':
                    f = self._cam_menu_slots.pop(cam['descriptor'])
                    option.triggered.disconnect(f)
                    self._camera_menulist.removeAction(option)
                    self._cam_menu_displayed_cams.remove(option)
                    self._cam_menu_stored_cameras.remove(cam)

        if new_custom is not None:
            self._cam_menu_stored_cameras.append(new_custom)
            option = QAction(f'{new_custom['name']}')
            self._camera_menulist.insertAction(self._cam_menu_add_custom, option)
            f = partial(self.change_cam, new_custom['descriptor'])
            self._cam_menu_slots.update({new_custom['descriptor']: f})
            option.triggered.connect(f)
            self._cam_menu_displayed_cams.append(option)

        for option in self._cam_menu_displayed_cams:
            if chosen is not None:
                if chosen['name'] == option.text():
                    option.setCheckable(True)
                    option.setChecked(True)
                    self._camera_dropdown.setText(f'{chosen['name']}')
                else:
                    option.setChecked(False)
                    option.setCheckable(False)
            else:
                self._camera_dropdown.setText('No Camera Selected')
                option.setChecked(False)
                option.setCheckable(False)

    def custom_camera_popup(self):
        text, ok = QInputDialog.getText(
            self,
            'Choose Camera by URL',
            'URL:',
            QLineEdit.EchoMode.Normal,
            'http://',
            )
        if ok:
            self.change_cam(text)


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
        else:
            self._esp.connect(port)

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

        self.menu_bar = MenuBar(self, self.esp, self.controller)
        self.setMenuBar(self.menu_bar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_camera_widget = CameraWidget(self, 0)
        self.secondary_camera_widget = CameraWidget(self, 0)
        self.tertiary_camera_widget = CameraWidget(self, 2)
        self.orientationsWidget = OrientationWidget(self)
        self.controllerWidget = ControllerDisplay(self)
        self.thrustersWidget = ThrustersWidget(self)

        self.comms_man = CommunicationManager(
            esp=self.esp, controller=self.controller,
            controller_widget=self.controllerWidget,
            thrusters_widget=self.thrustersWidget,
            orientation_widget=self.orientationsWidget
            )

        grid = QGridLayout()

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 1)

        grid.addWidget(self.main_camera_widget, 0, 0, 2, 3)
        grid.addWidget(self.secondary_camera_widget, 0, 3, 1, 1)
        grid.addWidget(self.tertiary_camera_widget, 1, 3, 1, 1)

        grid.addWidget(self.orientationsWidget, 2, 0, 2, 1)

        grid.addWidget(self.controllerWidget, 2, 1, 2, 2)
        grid.addWidget(self.thrustersWidget, 2, 2, 2, 2)

        central_widget.setLayout(grid)
        self.setMinimumSize(self.size())
        self.timer = QTimer()
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(15)

    def main_loop(self):
        self.main_camera_widget.update()
        self.secondary_camera_widget.update()
        self.tertiary_camera_widget.update()
        self.menu_bar.update()
        self.comms_man.update_widgets()
