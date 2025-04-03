from __future__ import annotations

from functools import partial

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QInputDialog,
    QLineEdit, QMenuBar, QMenu, )
from plyer import notification

from ROV_CONSOLE.camera_widget import CameraWidget, CameraWidgetPosition
from ROV_CONSOLE.comms import CommunicationManager
from ROV_CONSOLE.conf import Config
from ROV_CONSOLE.controller_widget import ControllerDisplay
from ROV_CONSOLE.esp32 import ESP32
from ROV_CONSOLE.gamepad import Controller
from ROV_CONSOLE.orientation_widget import OrientationWidget
from ROV_CONSOLE.paths import APP_ICON
from ROV_CONSOLE.tasks_widget import TaskViewWidget
from ROV_CONSOLE.thrusters_widget import ThrustersWidget


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
        self._gp_menu_none_connected = QAction('No Controllers Connected')
        self._gp_menu_none_connected.setEnabled(False)
        self._gp_slots: dict[str:partial] = {}
        self._tasks_menu = self.addMenu('Tasks')
        self._migration_model = QAction('Invasive Carp Migration Model')
        self._migration_model.triggered.connect(lambda: notification.notify(
            title='Invasive Carp Migration Model',
            message='Invasive Carp Migration Model is not yet implemented.',
            timeout=2,
            app_name='AU Robotics - Console',
            app_icon=str(APP_ICON)
            ))
        self._tasks_menu.addAction(self._migration_model)

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
        # initialize pygame before setting window properties from Qt
        self.controller = Controller()
        conf = Config()

        self.esp = ESP32()
        self.esp.port = conf.com_port

        self.setWindowTitle('AU Robotics ROV GUI')
        self.setWindowIcon(QIcon(str(APP_ICON)))
        self.showMaximized()

        self.menu_bar = MenuBar(self, self.esp, self.controller)
        self.setMenuBar(self.menu_bar)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_camera_widget = CameraWidget(self, conf.main_camera, CameraWidgetPosition.MAIN)
        self.left_camera_widget = CameraWidget(self, conf.left_camera, CameraWidgetPosition.LEFT,
                                               self.main_camera_widget)
        self.right_camera_widget = CameraWidget(self, conf.right_camera, CameraWidgetPosition.RIGHT,
                                                self.main_camera_widget)
        self.orientationsWidget = OrientationWidget(self)
        self.controllerWidget = ControllerDisplay(self)
        self.thrustersWidget = ThrustersWidget(self)
        self.tasksWidget = TaskViewWidget(self, conf.tasks)

        self.comms_man = CommunicationManager(
            esp=self.esp, controller=self.controller,
            controller_widget=self.controllerWidget,
            thrusters_widget=self.thrustersWidget,
            orientation_widget=self.orientationsWidget,
            cameras=[self.main_camera_widget, self.left_camera_widget, self.right_camera_widget])

        grid = QGridLayout()

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)

        grid.addWidget(self.main_camera_widget, 0, 1, 2, 1)
        grid.addWidget(self.left_camera_widget, 0, 0, 1, 1)
        grid.addWidget(self.right_camera_widget, 0, 2, 1, 1)

        grid.addWidget(self.orientationsWidget, 1, 0, 2, 1)

        grid.addWidget(self.controllerWidget, 2, 1, 1, 1)
        grid.addWidget(self.thrustersWidget, 2, 2, 1, 1)
        grid.addWidget(self.tasksWidget, 1, 2, 1, 1)

        central_widget.setLayout(grid)
        self.setMinimumSize(self.size())
        self.timer = QTimer()
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(15)

    def main_loop(self):
        self.main_camera_widget.update()
        self.left_camera_widget.update()
        self.right_camera_widget.update()
        self.menu_bar.update()
        self.comms_man.update_widgets()
