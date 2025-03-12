import cv2
from threading import Thread
from time import sleep


NO_VIDEO_INDICATOR = __file__[:__file__.rfind('/')][:__file__.rfind('\\')] + '/assets/novideo.jpeg'

class Camera:
    def __init__(self, camera_fd):
        self._cam = cv2.VideoCapture(camera_fd)
        self._no_frame = cv2.imread(NO_VIDEO_INDICATOR)
        self._frame = self._no_frame
        self._frame_thread = Thread(target=self._frame_loop)
        self._frame_thread.start()

    def _frame_loop(self):
        while True:
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

    def __del__(self):
        self._frame_thread.join()
        self._cam.release()
