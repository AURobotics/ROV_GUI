from math import sqrt
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QInputDialog,
    QLineEdit,
)
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QGuiApplication,
    QFont,
)
from PySide6.QtCore import Qt, QPoint, QRect


class MeasurementWindow(QWidget):
    def __init__(self, parent, picture: QPixmap):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Window)
        width, height = QGuiApplication.primaryScreen().size().toTuple()  # type: ignore
        width //= 2
        height //= 2
        self.original_pic = picture.copy()
        self.canvas = QLabel(self)
        self.resize(width, height)
        self.canvas.setScaledContents(True)
        self.canvas.setPixmap(picture)
        self.setWindowTitle("Length Measurement")
        self.show()
        self._ref_1: tuple[int, int] | None = None
        self._ref_2: tuple[int, int] | None = None
        self._ref_distance = 0
        self._ref_pixel_distance = 0

        self._point_1: tuple[int, int] | None = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.pos()
            self.draw_point(point)
        elif event.button() == Qt.MouseButton.RightButton:
            self.reset_points()

    def draw_point(self, point: QPoint):
        pix = self.canvas.pixmap()
        point_x = (point.x() * pix.width()) // self.canvas.width()
        point_y = (point.y() * pix.height()) // self.canvas.height()
        if self._ref_1 is None:
            self._ref_1 = (point_x, point_y)
        elif self._ref_2 is None:
            self._ref_2 = (point_x, point_y)
        painter = QPainter(pix)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.drawPoint(QPoint(point_x, point_y))
        if self._ref_1 is not None and self._ref_2 is not None:
            if self._ref_distance == 0:
                painter.end()
                self.canvas.setPixmap(pix)
                self.prompt_real_length()
                return
            elif self._point_1 is None:
                self._point_1 = (point_x, point_y)
            else:
                x1, y1 = self._point_1
                x2, y2 = (point_x, point_y)
                self._point_1 = None
                painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
                text_rect = QRect((x1 + x2) // 2 - 50, (y1 + y2) // 2 - 30, 100, 20)
                distance = (
                    sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    * self._ref_distance
                    / self._ref_pixel_distance
                )
                font = QFont()
                font.setPointSize(12)
                painter.setFont(font)
                painter.drawText(
                    text_rect, Qt.AlignmentFlag.AlignCenter, f"{distance:.1f}m"
                )
        painter.end()
        self.canvas.setPixmap(pix)

    def reset_points(self):
        self._ref_1 = None
        self._ref_2 = None
        self._ref_distance = 0
        self._ref_pixel_distance = 0
        self._point_1 = None
        self.canvas.setPixmap(self.original_pic)

    def prompt_real_length(self):
        length, ok = QInputDialog.getText(
            self,
            "Real Life Length",
            "Enter real life length:",
            QLineEdit.EchoMode.Normal,
            "1",
        )
        if not ok or int(length) == 0:
            self.reset_points()
            return
        self._ref_distance = float(length)
        x1, y1 = self._ref_1
        x2, y2 = self._ref_2
        self._ref_pixel_distance = int(sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        pix = self.canvas.pixmap()
        painter = QPainter(pix)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.drawLine(QPoint(*self._ref_1), QPoint(*self._ref_2))

        text_rect = QRect((x1 + y1) // 2 - 50, (x2 + y2) // 2 - 30, 100, 20)

        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(
            text_rect, Qt.AlignmentFlag.AlignCenter, f"{self._ref_distance:.1f}m"
        )

        painter.end()
        self.canvas.setPixmap(pix)

    def resizeEvent(self, event):
        self.canvas.resize(event.size())
