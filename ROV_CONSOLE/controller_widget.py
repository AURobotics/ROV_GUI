from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QLabel

from .constants import DS4_ICONS_PATHS

DS4_ICONS = {f.stem: QIcon(str(f)) for f in DS4_ICONS_PATHS}


class ControllerDisplay(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.button_scheme = {
            'CIRCLE': {
                'size':     QSize(50, 50),
                'icons':    ('CIRCLE', 'CIRCLE-1'),
                'position': (410, 145)
                },
            'CROSS':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('CROSS', 'CROSS-1'),
                          'position': (370, 185)
                          },
            'SQUARE':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('SQUARE', 'SQUARE-1'),
                          'position': (330, 145)
                          },
            'TRIANGLE':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('TRIANGLE', 'TRIANGLE-1'),
                          'position': (370, 105)
                          },
            'D-UP':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('D-UP', 'D-UP-1'),
                          'position': (40, 105)
                          },
            'D-DOWN':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('D-DOWN', 'D-DOWN-1'),
                          'position': (40, 185)
                          },
            'D-LEFT':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('D-LEFT', 'D-LEFT-1'),
                          'position': (0, 145)
                          },
            'D-RIGHT':
                      {
                          'size':     QSize(50, 50),
                          'icons':    ('D-RIGHT', 'D-RIGHT-1'),
                          'position': (80, 145)
                          },
            'L1':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('L1', 'L1-1'),
                          'position': (0, 40)
                          },
            'L2':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('L2', 'L2-1'),
                          'position': (0, 0)
                          },
            'R1':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('R1', 'R1-1'),
                          'position': (410, 40)
                          },
            'R2':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('R2', 'R2-1'),
                          'position': (410, 0)
                          },
            'LS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('STICK-BASE', 'STICK-BASE'),
                          'position': (145, 190)
                          },
            'RS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('STICK-BASE', 'STICK-BASE'),
                          'position': (265, 190)
                          },
            'L3':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('LS', 'L3'),
                          'position': (145, 190)
                          },
            'R3':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('RS', 'R3'),
                          'position': (265, 190)
                          },
            'PS':
                      {
                          'size':     QSize(30, 30),
                          'icons':    ('PS', 'PS-1'),
                          'position': (225, 230)
                          },
            'TOUCHPAD':
                      {
                          'size':     QSize(300, 150),
                          'icons':    ('TOUCHPAD', 'TOUCHPAD-1'),
                          'position': (85, 0)
                          },
            'SHARE':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('SHARE', 'SHARE-1'),
                          'position': (100, 0)
                          },
            'OPTIONS':
                      {
                          'size':     QSize(70, 70),
                          'icons':    ('OPTIONS', 'OPTIONS-1'),
                          'position': (300, 0)
                          }
            }

        self.buttons = {}
        for b in self.button_scheme:
            button = QPushButton(self)
            button.setObjectName(b)
            button.setIcon(DS4_ICONS[self.button_scheme[b]['icons'][0]])
            pos = self.button_scheme[b]['position']
            button.move(pos[0], pos[1])
            button.setIconSize(self.button_scheme[b]['size'])
            button.setStyleSheet("border: none;")
            self.buttons[b] = button

        self.no_controller_label = QLabel('Please connect a controller.', self)
        self.no_controller_label.move(205, 105)
        self.no_controller_label.setVisible(False)

        self.controller = controller
        self.reset_flag = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        if not self.controller.connected:
            if not self.reset_flag:
                self.reset_flag = True
                for b in self.buttons:
                    self.buttons[b].setIcon(DS4_ICONS[self.button_scheme[b]['icons'][0]])
                    pos = self.button_scheme[b]['position']
                    self.buttons[b].move(pos[0], pos[1])
                    self.buttons[b].setVisible(False)
                    self.no_controller_label.setVisible(True)
            return

        if self.reset_flag:
            for b in self.buttons:
                self.buttons[b].setVisible(True)
                self.no_controller_label.setVisible(False)

        self.reset_flag = False
        states = self.controller.bindings_state
        for b in states:
            v = states[b]
            if b in self.buttons:
                self.buttons[b].setIcon(DS4_ICONS[self.button_scheme[b]['icons'][v != 0]])
        ls_x = states['LS-H'] * 10 + int(self.button_scheme['L3']['position'][0])
        ls_y = states['LS-V'] * 10 + int(self.button_scheme['L3']['position'][1])
        rs_x = states['RS-H'] * 10 + int(self.button_scheme['R3']['position'][0])
        rs_y = states['RS-V'] * 10 + int(self.button_scheme['R3']['position'][1])
        self.buttons['L3'].move(ls_x, ls_y)
        self.buttons['R3'].move(rs_x, rs_y)
