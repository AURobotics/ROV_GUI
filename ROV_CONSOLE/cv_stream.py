"""
    Fault-tolerant video stream handler using opencv.
"""
import enum
from os import name as os_name
from pathlib import Path
from threading import Thread
from time import sleep

import cv2
import requests
from cv2_enumerate_cameras import enumerate_cameras


class ConnectionStatus(enum.Enum):
    CONNECTED = enum.auto()
    DISCONNECTED = enum.auto()
    IN_PROGRESS = enum.auto()


class VideoStream:
    _ENUMERATION_APIS = {
        'nt':    cv2.CAP_MSMF,
        'posix': cv2.CAP_GSTREAMER
        }
    _ENUM_API = _ENUMERATION_APIS[os_name]
    _EMPTY_FRAME = cv2.imread(str(Path(__file__).resolve().parent / 'assets' / 'novideo.jpeg'))

    _cap: cv2.VideoCapture
    _cap_name: str | None
    _cap_index: int | None
    _connection_status: ConnectionStatus
    _cameras: dict[int:str]  # {index: name}
    _frame_thread: Thread
    _killswitch: bool

    def __init__(self, descriptor: int | str | None):
        self._cap = cv2.VideoCapture()
        self._cap_name = None
        self._cap_index = None
        self._connection_status = ConnectionStatus.DISCONNECTED
        if descriptor is not None:
            self.source = descriptor
        self._frame = self._EMPTY_FRAME
        self._killswitch = False
        self._frame_thread = Thread(target=self._frame_loop, daemon=True)
        self._frame_thread.start()
        self._cameras = []

    @property
    def available_cameras(self):
        self._cameras = {cam.index: cam.name for cam in enumerate_cameras(self._ENUM_API)}
        return self._cameras

    @property
    def connection_status(self):
        return self._connection_status

    def _try_connect_to_url(self, url: str):
        def url_reachable():
            ok = False
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    ok = True
            except requests.RequestException:
                ok = False
            if not ok:
                self._connection_status = ConnectionStatus.DISCONNECTED
                self.source = None
            else:
                self._connection_status = ConnectionStatus.CONNECTED
                self._cap_name = url
                self._cap_index = None
                self._cap.open(url)

        connection_thread = Thread(target=url_reachable, daemon=True)
        connection_thread.start()

    @property
    def source(self):
        return {'index': self._cap_index, 'name': self._cap_name, 'connection_status': self._connection_status}

    @source.setter
    def source(self, descriptor: dict | int | str | None):

        if self._connection_status == ConnectionStatus.IN_PROGRESS:
            return

        if descriptor is None:
            self._cap_index = None
            self._cap_name = None
            self._connection_status = ConnectionStatus.DISCONNECTED
            self._cap.release()
            return

        self._connection_status = ConnectionStatus.IN_PROGRESS

        if type(descriptor) is dict:
            if descriptor['index'] is not None:
                descriptor = descriptor['index']
            else:
                descriptor = descriptor['name']

        if type(descriptor) == int:
            if descriptor not in self.available_cameras:
                self.source = None
                return
            ok = self._cap.open(descriptor)
            if not ok:
                self.source = None
                return
            self._cap_index = descriptor
            self._cap_name = self.available_cameras[descriptor]
            self._connection_status = ConnectionStatus.CONNECTED

        elif type(descriptor) == str:
            filepath = Path(descriptor).resolve()
            if filepath.exists():
                ok = self._cap.open(str(filepath))
                if not ok:
                    self.source = None
                    return
                self._cap_index = None
                self._cap_name = filepath.name
                self._connection_status = ConnectionStatus.CONNECTED
            else:
                self._try_connect_to_url(descriptor)
        else:
            self.source = None

    @property
    def frame(self):
        return self._frame

    def _frame_loop(self):
        try:
            while not self._killswitch:
                if self._cap.isOpened() and self._connection_status == ConnectionStatus.CONNECTED:
                    _, f = self._cap.read()
                    if _:
                        self._frame = f
                else:
                    self._frame = self._EMPTY_FRAME
                sleep(0.015)
        except SystemExit:
            self.kill()

    def kill(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._cap.isOpened():
            self._cap.release()

    def __del__(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._cap.isOpened():
            self._cap.release()
