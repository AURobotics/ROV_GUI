from typing import Optional

from PySide6.QtCore import QSize, Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QBrush
from PySide6.QtWidgets import QLabel

from .constants import ASSETS_PATH

paths = [fp for fp in (ASSETS_PATH / 'controller_widget').iterdir()]
DS4_ICONS = {f.stem: f for f in paths}


class ControllerDisplay(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self._buttons = {
            'CIRCLE': {
                'size':     QSize(250, 250),
                'icons':    (DS4_ICONS['CIRCLE'], DS4_ICONS['CIRCLE-1']),
                'position': (2050, 725)
                },
            'CROSS':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['CROSS'], DS4_ICONS['CROSS-1']),
                          'position': (1850, 925)
                          },
            'SQUARE':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['SQUARE'], DS4_ICONS['SQUARE-1']),
                          'position': (1650, 725)
                          },
            'TRIANGLE':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['TRIANGLE'], DS4_ICONS['TRIANGLE-1']),
                          'position': (1850, 525)
                          },
            'D-UP':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['D-UP'], DS4_ICONS['D-UP-1']),
                          'position': (200, 525)
                          },
            'D-DOWN':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['D-DOWN'], DS4_ICONS['D-DOWN-1']),
                          'position': (200, 925)
                          },
            'D-LEFT':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['D-LEFT'], DS4_ICONS['D-LEFT-1']),
                          'position': (0, 725)
                          },
            'D-RIGHT':
                      {
                          'size':     QSize(250, 250),
                          'icons':    (DS4_ICONS['D-RIGHT'], DS4_ICONS['D-RIGHT-1']),
                          'position': (400, 725)
                          },
            'L1':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['L1'], DS4_ICONS['L1-1']),
                          'position': (0, 200)
                          },
            'L2':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['L2'], DS4_ICONS['L2-1']),
                          'position': (0, 0)
                          },
            'R1':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['R1'], DS4_ICONS['R1-1']),
                          'position': (1950, 200)
                          },
            'R2':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['R2'], DS4_ICONS['R2-1']),
                          'position': (1950, 0)
                          },
            'LS':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['STICK-BASE'], DS4_ICONS['STICK-BASE']),
                          'position': (650, 950)
                          },
            'RS':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['STICK-BASE'], DS4_ICONS['STICK-BASE']),
                          'position': (1325, 950)
                          },
            'L3':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['LS'], DS4_ICONS['L3']),
                          'position': (650, 950)
                          },
            'R3':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['RS'], DS4_ICONS['R3']),
                          'position': (1325, 950)
                          },
            'PS':
                      {
                          'size':     QSize(150, 150),
                          'icons':    (DS4_ICONS['PS'], DS4_ICONS['PS-1']),
                          'position': (1100, 1050)
                          },
            'TOUCHPAD':
                      {
                          'size':     QSize(1450, 700),
                          'icons':    (DS4_ICONS['TOUCHPAD'], DS4_ICONS['TOUCHPAD-1']),
                          'position': (425, 0)
                          },
            'SHARE':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['SHARE'], DS4_ICONS['SHARE-1']),
                          'position': (275, 0)
                          },
            'OPTIONS':
                      {
                          'size':     QSize(350, 350),
                          'icons':    (DS4_ICONS['OPTIONS'], DS4_ICONS['OPTIONS-1']),
                          'position': (1685, 0)
                          }
            }

        for b in self._buttons.values():
            pix1 = QPixmap(b['icons'][0])
            spix1 = pix1.scaled(b['size'], Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            pix2 = QPixmap(b['icons'][1])
            spix2 = pix2.scaled(b['size'], Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            b['pixes'] = (spix1, spix2)

        self._reset_flag = False

        canvas = QPixmap(2300, 1300)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        painter.setOpacity(0.3)
        for b, meta in self._buttons.items():
            painter.drawPixmap(meta['position'][0], meta['position'][1], meta['pixes'][0])
        font = QFont('Arial', 100)
        painter.setFont(font)
        text = 'Connect a controller'
        text_rect = QFontMetrics(font).tightBoundingRect(text)
        painter.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
        back_rect = QRect((2300 - text_rect.width() - 100) // 2, (1300 - text_rect.height() - 100) // 2,
                          text_rect.width() + 100, text_rect.height() + 100)
        painter.setOpacity(0.8)
        painter.drawRoundedRect(back_rect, 40, 40)
        painter.setOpacity(1)
        painter.drawText(0, 0, 2300, 1300, Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        self._no_controller_frame = canvas
        self._canvas = self._no_controller_frame

    def resizeEvent(self, event):
        self.resize(event.size())
        self.setPixmap(self._canvas.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                           Qt.TransformationMode.SmoothTransformation))

    def display(self, states=Optional[dict]):
        if states is None:
            if not self._reset_flag:
                self._reset_flag = True
                self.setPixmap(self._no_controller_frame.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation))
            return

        self._reset_flag = False

        canvas = QPixmap(2300, 1300)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        for b, meta in self._buttons.items():
            if b == 'R3':
                painter.drawPixmap(meta['position'][0] + states['RS-H'] * 50,
                                   meta['position'][1] + states['RS-V'] * 50,
                                   meta['pixes'][states[b] > 0])
                continue
            if b == 'L3':
                painter.drawPixmap(meta['position'][0] + states['LS-H'] * 50,
                                   meta['position'][1] + states['LS-V'] * 50,
                                   meta['pixes'][states[b] > 0])
                continue
            if b in ['RS', 'LS']:
                painter.drawPixmap(meta['position'][0], meta['position'][1], meta['pixes'][0])
                continue
            painter.drawPixmap(meta['position'][0], meta['position'][1], meta['pixes'][states[b] > 0])

        painter.end()
        canvas = canvas.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self._canvas = canvas
        self.setPixmap(canvas)
