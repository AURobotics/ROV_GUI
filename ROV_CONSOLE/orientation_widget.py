from typing import Optional

from PySide6.QtCore import Qt, QPointF, QRectF, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QPixmap, QPainterPath, QColor, QFontMetrics, QFont
from PySide6.QtWidgets import QLabel


class OrientationWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._base_altitude_pixmap = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
            roll = - roll

        pix = QPixmap(self.width(), self.height())
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        if readings is None:
            painter.setOpacity(0.3)
        painter.drawPixmap(0, 0, self._altitude_pixmap(roll, pitch))
        painter.drawPixmap(0, self.height() // 2, self._compass_pixmap(yaw))
        if readings is None:
            painter.setOpacity(0.8)
            font = QFont('Arial', 16)
            painter.setFont(font)
            text = 'Connect to the ROV'
            text_rect = QFontMetrics(font).tightBoundingRect(text)
            painter.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
            back_rect = QRect((self.width() - text_rect.width() - 20) // 2,
                              (self.height() - text_rect.height() - 20) // 2,
                              text_rect.width() + 20, text_rect.height() + 20)
            painter.setOpacity(0.8)
            painter.drawRoundedRect(back_rect, 8, 8)
            painter.setOpacity(1)
            painter.drawText(0, 0, self.width(), self.height(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        self.setPixmap(pix)

    def _altitude_pixmap(self, roll, pitch):
        w, h = (self.width(), self.height() // 2)
        pix = QPixmap(w, h)
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(w, h)
        center = QPointF(w / 2, h / 2)
        radius = size / 2

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(center, radius + 2, radius + 2)

        path = QPainterPath()
        path.addEllipse(center, radius, radius)
        painter.setClipPath(path)

        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(center, radius, radius)

        painter.translate(center)
        painter.rotate(roll)
        pitch_offset = (pitch / 90) * radius
        painter.translate(0, pitch_offset)

        painter.setBrush(QBrush(QColor(0, 150, 255)))
        painter.drawRect(
            QRectF(-radius * 2, -radius * 2, 4 * radius, 2 * radius))

        painter.setBrush(QBrush(QColor(150, 75, 0)))
        painter.drawRect(QRectF(-radius * 2, 0, 4 * radius, 2 * radius))

        painter.resetTransform()

        painter.translate(center)
        painter.rotate(roll)
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
        painter.rotate(roll)
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
        painter.end()
        return pix

    def _compass_pixmap(self, yaw):
        w, h = (self.width(), self.height() // 2)
        pix = QPixmap(w, h)
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(w, h)
        center = QPointF(w / 2, h / 2)
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
        painter.rotate(-yaw)
        painter.setBrush(QBrush(Qt.GlobalColor.red))
        painter.drawPolygon([
            QPointF(0, -radius / 1.5),
            QPointF(-10, 0),
            QPointF(10, 0)
            ])

        painter.resetTransform()

        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(center, 5, 5)
        painter.end()
        return pix
