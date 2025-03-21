"""
    Fault-tolerant video stream handler using opencv.
"""

import cv2
from threading import Thread
from time import sleep

from os import path
NO_VIDEO_INDICATOR = path.join(path.dirname(path.abspath(__file__)), 'assets', 'novideo.jpeg')

class VideoStream:
    def __init__(self, descriptor: int | str | None):
        self._source = cv2.VideoCapture()
        if descriptor is not None:
            self._source.open(descriptor)
        self._no_frame = cv2.imread(NO_VIDEO_INDICATOR)
        self._frame = self._no_frame
        self._killswitch = False
        self._frame_thread = Thread(target=self._frame_loop, daemon=True)
        self._frame_thread.start()

    @property
    def frame(self):
        return self._frame

    def _frame_loop(self):
        try:
            while not self._killswitch:
                if self._source.isOpened():
                    _, f = self._source.read()
                    if _:
                        self._frame = f
                else:
                    self._frame = self._no_frame
                sleep(0.015)
        except SystemExit:
            self.kill()

    def kill(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._source.isOpened():
            self._source.release()

    def __del__(self):
        self._killswitch = True
        if self._frame_thread.is_alive():
            self._frame_thread.join()
        if self._source.isOpened():
            self._source.release()