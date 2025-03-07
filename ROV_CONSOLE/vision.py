import cv2
from threading import Thread

class Camera:
    def __init__(self, camera_fd):
        self.cam = cv2.VideoCapture(camera_fd)

    @property
    def frame(self):
        if self.cam.isOpened():
            _, frame = self.cam.read()
            return frame
        return None

    def __del__(self):
        ...