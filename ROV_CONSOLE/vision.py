import cv2
from threading import Thread

class Camera:
    def __init__(self, camera_fd):
        self._cam = cv2.VideoCapture(camera_fd)

    @property
    def frame(self):
        if self._cam.isOpened():
            _, frame = self._cam.read()
            return frame
        return None

    def __del__(self):
        self._cam.release()