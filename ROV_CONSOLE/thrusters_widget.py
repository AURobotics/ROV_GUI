from typing import Optional

from PySide6.QtCore import QRect, QPoint
from PySide6.QtGui import QPainter, QPen, Qt, QPixmap, QColor, QBrush
from PySide6.QtWidgets import QWidget, QLabel


class ThrustersWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._view = QLabel(self)
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self._hplacements = {
            'h1': {
                'origin':    (750, 250),
                'angle':     -45,
                'rectangle': (0, -100)
                },
            'h2': {
                'origin':    (750, 750),
                'angle':     -135,
                'rectangle': (-200, -100)
                },
            'h3': {
                'origin':    (250, 250),
                'angle':     45,
                'rectangle': (-200, -100)
                },
            'h4': {
                'origin':    (250, 750),
                'angle':     135,
                'rectangle': (0, -100)
                }
            }
        self.reset_flag = False

    def resizeEvent(self, event):
        self._view.resize(event.size())

    def display(self, values: Optional[dict]):
        if values is None:
            if not self.reset_flag:
                self.reset_flag = True
                self._view.setText('ESP DISCONNECTED')
            return
        self.reset_flag = False

        canvas = QPixmap(1000, 1000)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.fillRect(250, 250, 500, 500, Qt.GlobalColor.white)
        for thr, data in self._hplacements.items():
            painter.save()
            painter.translate(data['origin'][0], data['origin'][1])
            painter.rotate(data['angle'])
            rect = QRect(data['rectangle'][0], data['rectangle'][1], 200, 200)
            painter.drawRect(rect)
            dy = data['rectangle'][1]
            if values[thr] > 0:
                col = Qt.GlobalColor.green
            else:
                col = Qt.GlobalColor.red
                dy = -dy - (abs(values[thr]) / 255) * 200
            painter.fillRect(data['rectangle'][0], dy, 200, (abs(values[thr]) / 255) * 200, col)
            painter.restore()
        painter.drawEllipse(QPoint(500, 100), 90, 90)
        fill_brush = QBrush(Qt.BrushStyle.SolidPattern)
        normal_brush = QBrush(Qt.BrushStyle.NoBrush)
        col = Qt.GlobalColor.green if values['v1'] > 0 else Qt.GlobalColor.red
        fill_brush.setColor(col)
        painter.setBrush(fill_brush)
        painter.drawEllipse(QPoint(500, 100), abs(values['v1'] / 255) * 90, abs(values['v1'] / 255) * 90)
        painter.setBrush(normal_brush)
        painter.drawEllipse(QPoint(500, 900), 90, 90)
        col = Qt.GlobalColor.green if values['v2'] > 0 else Qt.GlobalColor.red
        fill_brush.setColor(col)
        painter.setBrush(fill_brush)
        painter.drawEllipse(QPoint(500, 900), abs(values['v2'] / 255) * 90, abs(values['v2'] / 255) * 90)
        painter.setBrush(normal_brush)

        painter.end()
        canvas = canvas.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self._view.setPixmap(canvas)
