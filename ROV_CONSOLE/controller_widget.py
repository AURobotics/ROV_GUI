import pygame
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QIcon

icons_path = __file__[:__file__.rfind('/')][:__file__.rfind('\\')] + '/assets/ds4icons'
class ControllerDisplay(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.circle = QPushButton(self)
        self.circle.setObjectName("circle")
        self.circle.setIcon(QIcon(f'{icons_path}/Button - PS Circle White 1.png'))
        self.circle.setIconSize(QSize(60, 60))  # Set the icon size
        self.circle.setStyleSheet("border: none;")  # Remove the button border
        self.circle.move(420, 155)

        self.cross = QPushButton(self)
        self.cross.setObjectName("cross")
        self.cross.setIcon(QIcon(f'{icons_path}/Button - PS Cross White 1.png'))
        self.cross.setIconSize(QSize(60, 60))  # Set the icon size
        self.cross.setStyleSheet("border: none;")  # Remove the button border
        self.cross.move(370, 205)


        self.square = QPushButton(self)
        self.square.setObjectName("square")
        self.square.setIcon(QIcon(f'{icons_path}/Button - PS Square White 1.png'))
        self.square.setIconSize(QSize(60, 60))  # Set the icon size
        self.square.setStyleSheet("border: none;")  # Remove the button border
        self.square.move(320, 155)


        self.triangle = QPushButton(self)
        self.triangle.setObjectName("triangle")
        self.triangle.setIcon(QIcon(f'{icons_path}/Button - PS Triangle White 1.png'))
        self.triangle.setIconSize(QSize(60, 60))  # Set the icon size
        self.triangle.setStyleSheet("border: none;")  # Remove the button border
        self.triangle.move(370, 105)

        self.arrow = QPushButton(self)
        self.arrow.setObjectName("arrow")
        self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows.png'))
        self.arrow.setIconSize(QSize(125, 125))  # Set the icon size
        self.arrow.setStyleSheet("border: none;")  # Remove the button border
        self.arrow.move(20, 140)

        self.L1 = QPushButton(self)
        self.L1.setObjectName("L1")
        self.L1.setIcon(QIcon(f'{icons_path}/Button - PS L1.png'))
        self.L1.setIconSize(QSize(70, 70))  # Set the icon size
        self.L1.setStyleSheet("border: none;")  # Remove the button border
        self.L1.move(50, 0)

        self.L2 = QPushButton(self)
        self.L2.setObjectName("L2")
        self.L2.setIcon(QIcon(f'{icons_path}/Button - PS L2.png'))
        self.L2.setIconSize(QSize(70, 70))  # Set the icon size
        self.L2.setStyleSheet("border: none;")  # Remove the button border
        self.L2.move(50, 40)

        self.R1 = QPushButton(self)
        self.R1.setObjectName("R1")
        self.R1.setIcon(QIcon(f'{icons_path}/Button - PS R1.png'))
        self.R1.setIconSize(QSize(70, 70))  # Set the icon size
        self.R1.setStyleSheet("border: none;")  # Remove the button border
        self.R1.move(370, 0)

        self.R2 = QPushButton(self)
        self.R2.setObjectName("R2")
        self.R2.setIcon(QIcon(f'{icons_path}/Button - PS R2.png'))
        self.R2.setIconSize(QSize(70, 70))  # Set the icon size
        self.R2.setStyleSheet("border: none;")  # Remove the button border
        self.R2.move(370, 40)

        self.js_left = QPushButton(self)
        self.js_left.setObjectName("js_left")
        self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank.png'))
        self.js_left.setIconSize(QSize(70, 70))  # Set the icon size
        self.js_left.setStyleSheet("border: none;")  # Remove the button border
        self.js_left.move(170, 230)

        self.js_right = QPushButton(self)
        self.js_right.setObjectName("js_right")
        self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank.png'))
        self.js_right.setIconSize(QSize(70, 70))  # Set the icon size
        self.js_right.setStyleSheet("border: none;")  # Remove the button border
        self.js_right.move(270, 230)

        self.controller = controller

        # Update joystick status every 100 ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_joystick_status)
        self.timer.start(100)

    def update_joystick_status(self):
        if not self.controller.connected:
            return
        states = self.controller.bindings_state
        # Update button states
        x_button = states['CROSS']
        circle_button = states['CIRCLE']
        square_button = states['SQUARE']
        triangle_button = states['TRIANGLE']
        up_button = states['D-UP']
        right_button = states['D-RIGHT']
        down_button = states['D-DOWN']
        left_button = states['D-LEFT']
        L1_button = states['L1']
        R1_button = states['R1']
        L2_button = states['L2']
        R2_button = states['R2']
        js_left_x = states['LS-H']
        js_left_y = states['LS-V']
        js_right_x = states['RS-H']
        js_right_y = states['RS-V']

        if circle_button:
            self.circle.setIcon(QIcon(f'{icons_path}/Button - PS Circle 2.svg'))
        else:
            self.circle.setIcon(QIcon(f'{icons_path}/Button - PS Circle White 1.png'))
        if x_button:
            self.cross.setIcon(QIcon(f'{icons_path}/Button - PS Cross 2.svg'))
        else:
            self.cross.setIcon(QIcon(f'{icons_path}/Button - PS Cross White 1.png'))
        if square_button:
            self.square.setIcon(QIcon(f'{icons_path}/Button - PS Square 2.svg'))
        else:
            self.square.setIcon(QIcon(f'{icons_path}/Button - PS Square White 1.png'))
        if triangle_button:
            self.triangle.setIcon(QIcon(f'{icons_path}/Button - PS Triangle 2.svg'))
        else:
            self.triangle.setIcon(QIcon(f'{icons_path}/Button - PS Triangle White 1.png'))
        if up_button:
            self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows Up.png'))
        # elif right_button:
        #     self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows Right.png'))
        # elif down_button:
        #     self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows Down.png'))
        # elif left_button:
        #     self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows Left.png'))
        else:
            self.arrow.setIcon(QIcon(f'{icons_path}/Button - PS Directional Arrows.png'))
        if L1_button:
            self.L1.setIcon(QIcon(f'{icons_path}/Button - PS L1 – 2.png'))
        else:
            self.L1.setIcon(QIcon(f'{icons_path}/Button - PS L1.png'))
        if R1_button:
            self.R1.setIcon(QIcon(f'{icons_path}/Button - PS R1 – 2.png'))
        else:
            self.R1.setIcon(QIcon(f'{icons_path}/Button - PS R1.png'))

        if js_left_x > 0.5:
            self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Right.png'))
        elif js_left_x < -0.5:
            self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Left.png'))
        elif js_left_y > 0.5:
            self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Down.png'))
        elif js_left_y < -0.5:
            self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Up.png'))
        else:
            self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank.png'))
        # if js_right_x > 0.5:
        #     self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Down.png'))
        # elif js_right_x < -0.5:
        #     self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Up.png'))
        # elif js_right_y > 0.5:
        #     self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Up.png'))
        # elif js_right_y < -0.5:
        #     self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank Down.png'))
        # else:
        #     self.js_right.setIcon(QIcon(f'{icons_path}/Button - PS Analogue Blank.png'))
        # if L2_button:
        #     self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS L2.png'))
        # else:
        #     self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS L2 – 2.png'))
        # if R2_button:
        #     self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS R2.png'))
        # else:
        #     self.js_left.setIcon(QIcon(f'{icons_path}/Button - PS R2 – 2.png'))