from typing import Optional

from PySide6.QtCore import QRect, QPoint
from PySide6.QtGui import QPainter, QPen, Qt, QPixmap, QColor, QBrush, QFont, QFontMetrics
from PySide6.QtWidgets import QLabel

from ROV_CONSOLE.paths import ROV_ASSETS


class ROVDisplayWidget(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
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
        self._pixmaps = {f.stem: QPixmap(str(f)) for f in ROV_ASSETS}
        self._reset_flag = False
        self._canvas = None

    def resizeEvent(self, event):
        self.resize(event.size())
        if self._canvas is not None:
            self.setPixmap(self._canvas.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))

    def display(self, values: Optional[dict]):
        if len(values) == 0:
            if self._reset_flag:
                return
            self._reset_flag = True
            values = {'h1':  255, 'h2': 255, 'h3': 255, 'h4': 255, 'v1': 255, 'v2': 255, 'dcv1': False, 'dcv2': False,
                      'led': True}
        else:
            self._reset_flag = False
            values['h3'] = -values['h3']
            values['h4'] = -values['h4']

        canvas = QPixmap(1000, 1000)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        if self._reset_flag:
            painter.setOpacity(0.2)
        painter.fillRect(250, 250, 500, 500, Qt.GlobalColor.white)
        if values['led']:
            painter.drawPixmap(450, 450, self._pixmaps['led-on'])
        else:
            painter.drawPixmap(450, 450, self._pixmaps['led-off'])

        if values['dcv1']:
            painter.drawPixmap(850, 300, self._pixmaps['dcv-open'])
        else:
            painter.drawPixmap(850, 300, self._pixmaps['dcv-closed'])

        if values['dcv2']:
            painter.drawPixmap(0, 300, self._pixmaps['dcv-open'])
        else:
            painter.drawPixmap(0, 300, self._pixmaps['dcv-closed'])
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
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
        col = Qt.GlobalColor.green if values['v2'] > 0 else Qt.GlobalColor.red
        fill_brush.setColor(col)
        painter.setBrush(fill_brush)
        painter.drawEllipse(QPoint(500, 100), abs(values['v2'] / 255) * 90, abs(values['v2'] / 255) * 90)
        painter.setBrush(normal_brush)
        painter.drawEllipse(QPoint(500, 900), 90, 90)
        col = Qt.GlobalColor.green if values['v1'] > 0 else Qt.GlobalColor.red
        fill_brush.setColor(col)
        painter.setBrush(fill_brush)
        painter.drawEllipse(QPoint(500, 900), abs(values['v1'] / 255) * 90, abs(values['v1'] / 255) * 90)
        painter.setBrush(normal_brush)

        if self._reset_flag:
            painter.setOpacity(0.8)
            text = 'Connect to the ROV'
            font = QFont('Arial', 60)
            painter.setFont(font)
            text_rect = QFontMetrics(font).tightBoundingRect(text)
            painter.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
            back_rect = QRect((1000 - text_rect.width() - 100) // 2, (1000 - text_rect.height() - 100) // 2,
                              text_rect.width() + 100, text_rect.height() + 100)
            painter.setOpacity(0.8)
            painter.drawRoundedRect(back_rect, 40, 40)
            painter.setOpacity(1)
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.drawText(0, 0, 1000, 1000, Qt.AlignmentFlag.AlignCenter, text)

        painter.end()
        canvas = canvas.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self._canvas = canvas
        self.setPixmap(canvas)
