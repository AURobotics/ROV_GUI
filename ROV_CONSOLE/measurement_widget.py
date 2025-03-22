from math import sqrt, atan, degrees

from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QGuiApplication,
    QFont, QFontMetrics,
    )
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QInputDialog,
    QLineEdit,
    )


class MeasurementWindow(QWidget):
    _ref_p1: tuple[int, int] | None  # Reference point 1: (x,y) pixels on pixmap
    _ref_p2: tuple[int, int] | None  # Reference point 1: (x,y) pixels on pixmap
    _ref_length: float  # Real life distance between 2 reference points
    _ref_pixel_length: int  # Distance between the 2 reference points in pixels on the pixmap
    _temp_query_point: tuple[int, int] | None  # Holder for the first point when inputting 2 non-reference points

    _canvas: QLabel

    def __init__(self, parent, picture: QPixmap):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        width, height = QGuiApplication.primaryScreen().size().toTuple()  # type: ignore
        width //= 2
        height //= 2
        self.original_pic = picture.copy()
        self._canvas = QLabel(self)
        self.resize(width, height)
        self._canvas.setScaledContents(True)
        self._canvas.setPixmap(picture)
        self.setWindowTitle("Length Measurement")
        self.show()

        self._ref_p1 = None
        self._ref_p2 = None
        self._ref_length = 0
        self._ref_pixel_length = 0

        self._temp_query_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.pos()
            self._draw_point(point)
        elif event.button() == Qt.MouseButton.RightButton:
            self._reset_points()

    def _draw_point(self, point: QPoint):
        pix = self._canvas.pixmap()
        point_x = (point.x() * pix.width()) // self._canvas.width()
        point_y = (point.y() * pix.height()) // self._canvas.height()
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.black, 2)
        painter.setPen(pen)
        font = QFont()
        font.setPixelSize(12)
        painter.setFont(font)
        if self._ref_p1 is None:
            self._ref_p1 = (point_x, point_y)
            painter.drawText(QPoint(point_x, point_y), 'R1')
        elif self._ref_p2 is None:
            self._ref_p2 = (point_x, point_y)
            self._ref_length = 0
            pix_copy = pix.copy()
            painter.drawText(QPoint(point_x, point_y), 'R2')

        painter.drawPoint(QPoint(point_x, point_y))
        painter.end()
        self._canvas.setPixmap(pix)
        if self._ref_p1 is not None and self._ref_p2 is not None:
            if self._ref_length == 0:
                self._prompt_real_length()
                if self._ref_p2 is None:
                    self._canvas.setPixmap(pix_copy)
                return
            elif self._temp_query_point is None:
                self._temp_query_point = (point_x, point_y)
            else:
                self._draw_labeled_line(self._temp_query_point, (point_x, point_y), 12)
                self._temp_query_point = None

    def _draw_labeled_line(self, point1: tuple[int, int], point2: tuple[int, int], font_pixel_size: int = None):
        x1, y1 = point1
        x2, y2 = point2
        # Ensure (x1,y1) is the leftmost point -> for easily calculating the slope
        if x1 != min(x1, x2):
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        theta = 0
        if x2 - x1 != 0:
            alpha = degrees(atan((y2 - y1) / (x2 - x1)))
            theta = 360 + alpha if alpha < 0 else alpha
        else:
            theta = 90
        if font_pixel_size is None:
            font_pixel_size = 12
        pix = self._canvas.pixmap()
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
        font = QFont()
        font.setPixelSize(font_pixel_size)
        painter.setFont(font)
        distance = (sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * self._ref_length / self._ref_pixel_length)
        distance_text = f'{distance:.1f}m'
        text_width = QFontMetrics(font).tightBoundingRect(distance_text).width()
        painter.save()
        painter.translate((x1 + x2) // 2, (y1 + y2) // 2)
        painter.rotate(theta)
        text_rect = QRect(-text_width // 2, 0, text_width, font_pixel_size)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, distance_text)
        painter.restore()
        painter.end()
        self._canvas.setPixmap(pix)

    def _reset_points(self):
        self._ref_p1 = None
        self._ref_p2 = None
        self._ref_length = 0
        self._ref_pixel_length = 0
        self._temp_query_point = None
        self._canvas.setPixmap(self.original_pic)

    def _prompt_real_length(self):
        length, ok = QInputDialog.getText(
            self,
            "Real Life Length",
            "Enter real life length:",
            QLineEdit.EchoMode.Normal,
            "1",
            )
        if not ok or float(length) == 0:
            self._ref_p2 = None
            return
        self._ref_length = float(length)
        x1, y1 = self._ref_p1
        x2, y2 = self._ref_p2
        self._ref_pixel_length = int(sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        self._draw_labeled_line(self._ref_p1, self._ref_p2, 12)

    def resizeEvent(self, event):
        self._canvas.resize(event.size())
