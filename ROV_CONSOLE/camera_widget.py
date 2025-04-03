from __future__ import annotations

import enum
import time
from functools import partial
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon, QAction, QGuiApplication
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QGridLayout,
    QPushButton,
    QInputDialog,
    QLineEdit, QMenu, QToolButton, QSpacerItem, QSizePolicy, )
from plyer import notification

from ROV_CONSOLE.cv_stream import VideoStream, CapMetadata, CapType, ConnectionStatus, DisconnectReason
from ROV_CONSOLE.measurement_widget import MeasurementWindow
from ROV_CONSOLE.paths import APP_ICON, CAMERA_ICONS, PANO_SAVE


class CameraWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Window)
        # self.setWindowModality(Qt.WindowModality.WindowModal)
        width, height = QGuiApplication.primaryScreen().size().toTuple()
        width //= 2
        height //= 2
        self._view = QLabel(self)
        self.resize(width, height)
        self._view.setScaledContents(True)
        self.setWindowTitle("Video Stream")
        self.show()

    def resizeEvent(self, event):
        self._view.resize(event.size())

    def update_(self, pix):
        self._view.setPixmap(pix)


class CameraWidgetPosition(enum.Enum):
    MAIN = enum.auto()
    RIGHT = enum.auto()
    LEFT = enum.auto()


class CameraWidget(QWidget):
    _widget_position = CameraWidgetPosition
    _stream: VideoStream
    _view: QLabel
    _empty_frame: QPixmap
    _mirror_h: bool
    _mirror_v: bool
    _grid: QGridLayout
    _camera_dropdown: QToolButton
    _camera_menulist = QMenu
    _cam_menu_displayed_cams: list[QAction]
    _cam_menu_slots: dict[int | str:partial]
    _cam_menu_stored_cameras: list[CapMetadata]
    _cam_menu_no_cam_indicator = QAction
    _cam_menu_sep: QAction
    _cam_menu_add_custom: QAction
    _maximized_popup: Optional[CameraWindow]

    def __init__(self, parent, cam, widget_pos: CameraWidgetPosition, main_widget_ref: Optional[CameraWidget] = None):
        super().__init__(parent)
        self._parent = parent
        self._widget_position = widget_pos
        self._main_widget_ref = main_widget_ref
        self._stream = VideoStream(cam)
        self._last_known_url = str(cam)
        self._view = QLabel(self)
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        ef = VideoStream.EMPTY_FRAME
        self._empty_frame = QPixmap(
            QImage(ef.data, ef.shape[1], ef.shape[0], ef.strides[0], QImage.Format.Format_BGR888))
        self._mirror_h = False
        self._mirror_v = False
        self._photosphere_on = False

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._grid = QGridLayout()
        self.setLayout(self._grid)

        toolbar_buttons = {
            'hflip':       {'icon': QIcon(str(CAMERA_ICONS / 'flip-horizontal.svg')), 'function': self.hflip},
            'vflip':       {'icon': QIcon(str(CAMERA_ICONS / 'flip-vertical.svg')), 'function': self.vflip},
            'measurement': {'icon':     QIcon(str(CAMERA_ICONS / 'ruler.svg')),
                            'function': self._launch_length_measurement},
            'pano':        {'icon': QIcon(str(CAMERA_ICONS / 'pano.svg')), 'function': self._toggle_photosphere},
            'maximize':    {'icon': QIcon(str(CAMERA_ICONS / 'maximize.svg')), 'function': self.launch_maximized},
            }

        # Set up a grid layout with 10 evenly spaced rows
        for i in range(0, 9):
            self._grid.setRowStretch(i, 1)
        col = 0  # Utilize the 10th (forces it to be the bottom-most row)
        for b in toolbar_buttons:
            pb = QPushButton(toolbar_buttons[b]['icon'], '')
            pb.setIconSize(QSize(24, 24))
            pb.clicked.connect(toolbar_buttons[b]['function'])
            pb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            pb.setVisible(False)
            self._grid.addWidget(pb, 9, col, 1, 1)
            col += 1
            self._grid.addItem(
                QSpacerItem(24, 24, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding),
                9, col, 1, 1)
            col += 1
        if self._widget_position != CameraWidgetPosition.MAIN:
            self._swap_button = QPushButton(self)
            self._swap_button.setIcon(QIcon(str(CAMERA_ICONS / 'swap.svg')))
            self._swap_button.setVisible(False)
            self._swap_button.setIconSize(QSize(24, 24))
            self._swap_button.clicked.connect(self._swap)
            if self._widget_position == CameraWidgetPosition.RIGHT:
                self._grid.addWidget(self._swap_button, 4, 0, 1, 1)
            if self._widget_position == CameraWidgetPosition.LEFT:
                self._grid.addWidget(self._swap_button, 4, 11, 1, 1)

        self._camera_dropdown = QToolButton(self)
        self._camera_dropdown.setVisible(False)

        self._camera_dropdown.setText('No Cameras Found')
        self._camera_menulist = QMenu(self)  # Could be rewritten as a QComboBox
        self._camera_dropdown.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._camera_dropdown.setMenu(self._camera_menulist)
        self._camera_dropdown.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)

        self._cam_menu_displayed_cams = []
        self._cam_menu_slots = {}
        self._cam_menu_stored_cameras = []

        self._cam_menu_no_cam_indicator = QAction('No Cameras Found')
        self._cam_menu_no_cam_indicator.setEnabled(False)
        self._camera_menulist.addAction(self._cam_menu_no_cam_indicator)
        self._cam_menu_sep = self._camera_menulist.addSeparator()
        self._cam_menu_add_custom = self._camera_menulist.addAction('Custom URL')
        self._cam_menu_add_custom.triggered.connect(self.custom_camera_popup)
        self._grid.addWidget(self._camera_dropdown, 9, col, 1, 1)
        self.setLayout(self._grid)
        self._maximized_popup = None

    def _swap(self):
        main_src = self._main_widget_ref._stream.source
        my_src = self._stream.source
        if main_src == my_src:
            return
        self._main_widget_ref._stream.source = my_src
        self._stream.source = main_src

    def hflip(self):
        self._mirror_h = not self._mirror_h

    def vflip(self):
        self._mirror_v = not self._mirror_v

    def launch_maximized(self):
        if self._maximized_popup is None:
            self._maximized_popup = CameraWindow(self)

    def enterEvent(self, event):
        if self._widget_position != CameraWidgetPosition.MAIN:
            self._swap_button.setVisible(True)
        for i in range(self._grid.count()):
            item = self._grid.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(True)

    def leaveEvent(self, event):
        if self._camera_menulist.isVisible():
            return
        if self._widget_position != CameraWidgetPosition.MAIN:
            self._swap_button.setVisible(False)
        for i in range(self._grid.count()):
            item = self._grid.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(False)

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
            .mirrored(horizontally=self._mirror_h, vertically=self._mirror_v)
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

    def _toggle_photosphere(self):
        self._photosphere_on = not self._photosphere_on

    @property
    def photosphere_on(self):
        return self._photosphere_on

    def capture(self):
        frame = self._stream.frame
        if frame is None:
            frame = self._empty_frame
        q_image = (
            QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                frame.strides[0],
                QImage.Format.Format_BGR888,
                )
            .mirrored(horizontally=self._mirror_h, vertically=self._mirror_v)
        )
        q_image.save(str(PANO_SAVE / f'{time.time_ns()}.png'))

    def update(self):
        # Set frame
        frame_pixmap = self._pixmap_from_stream()
        frame_pixmap = frame_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self._view.setPixmap(frame_pixmap)

        # Check if a maximized view was launched
        if self._maximized_popup is not None:
            # Check if it was closed
            if not self._maximized_popup.isVisible():
                self._maximized_popup = None
            else:
                # Send the current frame
                self._maximized_popup.update_(frame_pixmap)

        # Handling connection status and switching cameras
        if self._stream.connection_status == ConnectionStatus.IN_PROGRESS:
            self._camera_dropdown.setText('Connecting..')
            return
        elif (self._stream.connection_status == ConnectionStatus.DISCONNECTED and self._stream.disconnect_reason is
              not DisconnectReason.DESIRED_DISCONNECT):
            notification.notify(
                title='Camera Disconnected',
                message=self._stream.disconnect_message,
                timeout=2,
                app_name='AU Robotics - Console',
                app_icon=str(APP_ICON)
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
        if new_custom is not None:
            self._last_known_url = new_custom
        new_cameras = [cam for cam in cameras if cam not in self._cam_menu_stored_cameras]
        old_cameras = [cam for cam in self._cam_menu_stored_cameras if cam not in cameras and cam != old_custom]

        if len(cameras) == 0:
            if len(old_cameras) != 0:
                self._camera_menulist.insertAction(self._cam_menu_sep, self._cam_menu_no_cam_indicator)
        else:
            self._camera_menulist.removeAction(self._cam_menu_no_cam_indicator)
        for cam in new_cameras:
            option = QAction(f'{cam["name"]}')

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
                if option.text() == f'{cam["name"]}':
                    f = self._cam_menu_slots.pop(cam['descriptor'])
                    option.triggered.disconnect(f)
                    self._camera_menulist.removeAction(option)
                    self._cam_menu_displayed_cams.remove(option)
                    self._cam_menu_stored_cameras.remove(cam)

        if new_custom is not None:
            self._cam_menu_stored_cameras.append(new_custom)
            option = QAction(f'{new_custom["name"]}')
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
                    self._camera_dropdown.setText(f'{chosen["name"]}')
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
            self._last_known_url,
            )
        if ok:
            self.change_cam(text)
