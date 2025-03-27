from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QWidget, QLabel

from .constants import DS4_ICONS_PATHS

DS4_ICONS = {f.stem: f for f in DS4_ICONS_PATHS}


class ControllerDisplay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._view = QLabel(self)
        self._view.setText('Please connect a controller')
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self._view.setScaledContents(True)

        self.buttons = {
            'CIRCLE': {
                'size':     QSize(50, 50),
                'icons':    (DS4_ICONS['CIRCLE'], DS4_ICONS['CIRCLE-1']),
                'position': (410, 145)
                },
            'CROSS':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['CROSS'], DS4_ICONS['CROSS-1']),
                          'position': (370, 185)
                          },
            'SQUARE':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['SQUARE'], DS4_ICONS['SQUARE-1']),
                          'position': (330, 145)
                          },
            'TRIANGLE':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['TRIANGLE'], DS4_ICONS['TRIANGLE-1']),
                          'position': (370, 105)
                          },
            'D-UP':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['D-UP'], DS4_ICONS['D-UP-1']),
                          'position': (40, 105)
                          },
            'D-DOWN':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['D-DOWN'], DS4_ICONS['D-DOWN-1']),
                          'position': (40, 185)
                          },
            'D-LEFT':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['D-LEFT'], DS4_ICONS['D-LEFT-1']),
                          'position': (0, 145)
                          },
            'D-RIGHT':
                      {
                          'size':     QSize(50, 50),
                          'icons':    (DS4_ICONS['D-RIGHT'], DS4_ICONS['D-RIGHT-1']),
                          'position': (80, 145)
                          },
            'L1':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['L1'], DS4_ICONS['L1-1']),
                          'position': (0, 40)
                          },
            'L2':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['L2'], DS4_ICONS['L2-1']),
                          'position': (0, 0)
                          },
            'R1':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['R1'], DS4_ICONS['R1-1']),
                          'position': (410, 40)
                          },
            'R2':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['R2'], DS4_ICONS['R2-1']),
                          'position': (410, 0)
                          },
            'LS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['STICK-BASE'], DS4_ICONS['STICK-BASE']),
                          'position': (145, 190)
                          },
            'RS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['STICK-BASE'], DS4_ICONS['STICK-BASE']),
                          'position': (265, 190)
                          },
            'L3':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['LS'], DS4_ICONS['L3']),
                          'position': (145, 190)
                          },
            'R3':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['RS'], DS4_ICONS['R3']),
                          'position': (265, 190)
                          },
            'PS':
                      {
                          'size':     QSize(30, 30),
                          'icons':    (DS4_ICONS['PS'], DS4_ICONS['PS-1']),
                          'position': (225, 230)
                          },
            'TOUCHPAD':
                      {
                          'size':     QSize(290, 140),
                          'icons':    (DS4_ICONS['TOUCHPAD'], DS4_ICONS['TOUCHPAD-1']),
                          'position': (85, 0)
                          },
            'SHARE':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['SHARE'], DS4_ICONS['SHARE-1']),
                          'position': (100, 0)
                          },
            'OPTIONS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    (DS4_ICONS['OPTIONS'], DS4_ICONS['OPTIONS-1']),
                          'position': (300, 0)
                          }
            }

        for b in self.buttons.values():
            pix1 = QPixmap(b['icons'][0])
            spix1 = pix1.scaled(b['size'], Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            pix2 = QPixmap(b['icons'][1])
            spix2 = pix2.scaled(b['size'], Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
            b['pixes'] = (spix1, spix2)

        self.reset_flag = False

    def resizeEvent(self, event):
        self._view.resize(event.size())

    def display(self, states=Optional[dict]):
        if states is None:
            if not self.reset_flag:
                self.reset_flag = True
                self._view.setText('Please connect a controller')
            return

        self.reset_flag = False

        canvas = QPixmap(460, 260)
        canvas.fill(QColor(0, 0, 0, 0))
        painter = QPainter(canvas)
        for b, meta in self.buttons.items():
            if b == 'R3':
                painter.drawPixmap(meta['position'][0] + states['RS-H'] * 10, meta['position'][1] + states['RS-V'] * 10,
                                   meta['pixes'][0])
                continue
            if b == 'L3':
                painter.drawPixmap(meta['position'][0] + states['LS-H'] * 10, meta['position'][1] + states['LS-V'] * 10,
                                   meta['pixes'][0])
                continue
            if b in ['RS', 'LS']:
                painter.drawPixmap(meta['position'][0], meta['position'][1], meta['pixes'][0])
                continue
            painter.drawPixmap(meta['position'][0], meta['position'][1], meta['pixes'][states[b] > 0])

        painter.end()
        self._view.setPixmap(canvas)

        # ls_x = states['LS-H'] * 10 + int(self.button_scheme['L3']['position'][0])
        # ls_y = states['LS-V'] * 10 + int(self.button_scheme['L3']['position'][1])
        # rs_x = states['RS-H'] * 10 + int(self.button_scheme['R3']['position'][0])
        # rs_y = states['RS-V'] * 10 + int(self.button_scheme['R3']['position'][1])
        # self.buttons['L3'].move(ls_x, ls_y)
        # self.buttons['R3'].move(rs_x, rs_y)
