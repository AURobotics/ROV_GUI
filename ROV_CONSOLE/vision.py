import cv2
from threading import Thread
from time import sleep

from os import path
NO_VIDEO_INDICATOR = path.join(path.dirname(path.abspath(__file__)), 'assets', 'novideo.jpeg')

class Camera:
    def __init__(self, camera_fd):
        self._cam = cv2.VideoCapture(camera_fd)
        self._no_frame = cv2.imread(NO_VIDEO_INDICATOR)
        self._frame = self._no_frame
        self._killswitch = False
        self._frame_thread = Thread(target=self._frame_loop)
        self._frame_thread.start()

    def _frame_loop(self):
        while not self._killswitch:
            if self._cam.isOpened():
                _, f = self._cam.read()
                if _:
                    self._frame = f
            else:
                self._frame = self._no_frame
            sleep(0.015)

    @property
    def frame(self):
        return self._frame

    def discard(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._cam.isOpened():
            self._cam.release()

    def __del__(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._cam.isOpened():
            self._cam.release()
