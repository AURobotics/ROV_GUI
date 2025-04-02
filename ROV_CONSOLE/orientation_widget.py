from typing import Optional

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import QWidget, QVBoxLayout


class AltitudeIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.roll = 0
        self.pitch = 0

    def set_orientation(self, roll, pitch):
        self.roll = roll
        self.pitch = pitch
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = size / 2

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(center, radius + 2, radius + 2)

        path = QPainterPath()
        path.addEllipse(center, radius, radius)
        painter.setClipPath(path)

        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(center, radius, radius)

        painter.translate(center)
        painter.rotate(self.roll)
        pitch_offset = (self.pitch / 90) * radius
        painter.translate(0, pitch_offset)

        painter.setBrush(QBrush(QColor(0, 150, 255)))
        painter.drawRect(
            QRectF(-radius * 2, -radius * 2, 4 * radius, 2 * radius))

        painter.setBrush(QBrush(QColor(150, 75, 0)))
        painter.drawRect(QRectF(-radius * 2, 0, 4 * radius, 2 * radius))

        painter.resetTransform()

        painter.translate(center)
        painter.rotate(self.roll)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for angle in range(-170, 181, 10):
            painter.save()
            painter.rotate(angle)
            if angle % 30 == 0:
                painter.drawLine(QPointF(0, -radius), QPointF(0, -radius + 10))
                if angle % 180:
                    painter.drawText(QPointF(-10, -radius + 22.5), f"{-angle}")
            else:
                painter.drawLine(QPointF(0, -radius), QPointF(0, -radius + 5))
            painter.restore()

        painter.resetTransform()

        painter.translate(center)
        painter.rotate(self.roll)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        for offset in range(-80, 81, 10):
            y_offset = offset * (radius / 90)
            if -radius <= y_offset <= radius:
                if offset % 30 == 0:
                    painter.drawLine(QPointF(-20, y_offset),
                                     QPointF(20, y_offset))
                    painter.drawText(QPointF(20, y_offset + 5), f"{offset}")
                else:
                    painter.drawLine(QPointF(-10, y_offset),
                                     QPointF(10, y_offset))

        painter.resetTransform()

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawPolygon([
            QPointF(center.x() - 5, center.y() - radius + 10),
            QPointF(center.x() + 5, center.y() - radius + 10),
            QPointF(center.x(), center.y() - radius)
            ])


class Compass(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.yaw = 0

    def set_yaw(self, yaw):
        self.yaw = yaw
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = size / 2

        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(center, radius, radius)

        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        for angle in range(0, 360, 10):
            painter.save()
            painter.translate(center)
            painter.rotate(-angle)

            if angle % 30 == 0:
                painter.drawLine(QPointF(0, -radius + 2),
                                 QPointF(0, -radius + 12))
            else:
                painter.drawLine(QPointF(0, -radius + 2),
                                 QPointF(0, -radius + 7))

            if angle % 90 == 0:
                label = {0: "N", 90: "W", 180: "S", 270: "E"}[angle]
                painter.drawText(QPointF(-5, -radius + 25), label)
            elif angle % 30 == 0:
                painter.drawText(QPointF(-10, -radius + 25), str(angle))

            painter.restore()

        painter.translate(center)
        painter.rotate(-self.yaw)
        painter.setBrush(QBrush(Qt.GlobalColor.red))
        painter.drawPolygon([
            QPointF(0, -radius / 1.5),
            QPointF(-10, 0),
            QPointF(10, 0)
            ])

        painter.resetTransform()

        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(center, 5, 5)


class OrientationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.attitude = AltitudeIndicator()
        self.compass = Compass()

        layout.addWidget(self.attitude)
        layout.addWidget(self.compass)

        self.setLayout(layout)

    def display(self, readings: Optional[dict]):
        yaw, pitch, roll = (0, 0, 0)
        if readings is not None:
            yaw = readings['yaw']
            pitch = readings['pitch']
            roll = readings['roll']
        pitch = pitch % 360
        if pitch > 180:
            pitch -= 360

        if abs(pitch) > 90:
            pitch = 180 - pitch if pitch > 0 else -180 - pitch
            roll = (roll + 180) % 360

        self.attitude.set_orientation(roll, pitch)
        self.compass.set_yaw(yaw)
