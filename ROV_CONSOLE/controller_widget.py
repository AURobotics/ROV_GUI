import pygame
import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QIcon

class PS4ControllerSimulation(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PS4 Controller Simulation")
        self.setGeometry(100, 100, 400, 300)

        self.circle = QPushButton(self)
        self.circle.setObjectName("circle")
        self.circle.setIcon(QIcon('Button - PS Circle White 1.png')) 
        self.circle.setIconSize(QSize(60, 60))  # Set the icon size
        self.circle.setStyleSheet("border: none;")  # Remove the button border
        self.circle.move(450, 175)

        self.cross = QPushButton(self)
        self.cross.setObjectName("cross")
        self.cross.setIcon(QIcon('Button - PS Cross White 1.png')) 
        self.cross.setIconSize(QSize(60, 60))  # Set the icon size
        self.cross.setStyleSheet("border: none;")  # Remove the button border
        self.cross.move(400, 125)

        self.square = QPushButton(self)
        self.square.setObjectName("square")
        self.square.setIcon(QIcon('Button - PS Square White 1.png')) 
        self.square.setIconSize(QSize(60, 60))  # Set the icon size
        self.square.setStyleSheet("border: none;")  # Remove the button border
        self.square.move(400, 225)

        self.triangle = QPushButton(self)
        self.triangle.setObjectName("triangle")
        self.triangle.setIcon(QIcon('Button - PS Triangle White 1.png')) 
        self.triangle.setIconSize(QSize(60, 60))  # Set the icon size
        self.triangle.setStyleSheet("border: none;")  # Remove the button border
        self.triangle.move(350, 175)
        
        self.arrow = QPushButton(self)
        self.arrow.setObjectName("arrow")
        self.arrow.setIcon(QIcon('Button - PS Directional Arrows.png')) 
        self.arrow.setIconSize(QSize(125, 125))  # Set the icon size
        self.arrow.setStyleSheet("border: none;")  # Remove the button border
        self.arrow.move(50, 160)

        self.L1 = QPushButton(self)
        self.L1.setObjectName("L1")
        self.L1.setIcon(QIcon('Button - PS L1.png')) 
        self.L1.setIconSize(QSize(70, 70))  # Set the icon size
        self.L1.setStyleSheet("border: none;")  # Remove the button border
        self.L1.move(80, 20)

        self.L2 = QPushButton(self)
        self.L2.setObjectName("L2")
        self.L2.setIcon(QIcon('Button - PS L2.png')) 
        self.L2.setIconSize(QSize(70, 70))  # Set the icon size
        self.L2.setStyleSheet("border: none;")  # Remove the button border
        self.L2.move(80, 60)

        self.R1 = QPushButton(self)
        self.R1.setObjectName("R1")
        self.R1.setIcon(QIcon('Button - PS R1.png')) 
        self.R1.setIconSize(QSize(70, 70))  # Set the icon size
        self.R1.setStyleSheet("border: none;")  # Remove the button border
        self.R1.move(400, 20)

        self.R2 = QPushButton(self)
        self.R2.setObjectName("R2")
        self.R2.setIcon(QIcon('Button - PS R2.png')) 
        self.R2.setIconSize(QSize(70, 70))  # Set the icon size
        self.R2.setStyleSheet("border: none;")  # Remove the button border
        self.R2.move(400, 60)

        self.js_left = QPushButton(self)
        self.js_left.setObjectName("js_left")
        self.js_left.setIcon(QIcon('Button - PS Analogue Blank.png')) 
        self.js_left.setIconSize(QSize(70, 70))  # Set the icon size
        self.js_left.setStyleSheet("border: none;")  # Remove the button border
        self.js_left.move(200, 250)

        self.js_right = QPushButton(self)
        self.js_right.setObjectName("js_right")
        self.js_right.setIcon(QIcon('Button - PS Analogue Blank.png')) 
        self.js_right.setIconSize(QSize(70, 70))  # Set the icon size
        self.js_right.setStyleSheet("border: none;")  # Remove the button border
        self.js_right.move(300, 250)

        self.status_label = QLabel("Controller Status", self)
        self.status_label.move(10, 10)
        # Initialize pygame and joystick
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.status_label.setText("No joystick connected")
        else:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.status_label.setText(f"Joystick connected: {self.joystick.get_name()}")

        # Update joystick status every 100 ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_joystick_status)
        self.timer.start(100)

    def update_joystick_status(self):
        pygame.event.pump()  # Process events
        
        if pygame.joystick.get_count() == 0:
            self.status_label.setText("No joystick connected")
            
        else:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.status_label.setText(f"Joystick connected: {self.joystick.get_name()}")

            # Update button states
            x_button = self.joystick.get_button(0)
            circle_button = self.joystick.get_button(1)
            square_button = self.joystick.get_button(2)
            triangle_button = self.joystick.get_button(3)
            up_button = self.joystick.get_button(11)
            # right_button = self.joystick.get_button(14)
            # down_button = self.joystick.get_button(12)
            # left_button = self.joystick.get_button(13)
            L1_button = self.joystick.get_button(9)
            R1_button = self.joystick.get_button(10)
            # L2_button = self.joystick.get_axis(4)
            # R2_button = self.joystick.get_axis(5)
            js_left_x = self.joystick.get_axis(0)
            js_left_y = self.joystick.get_axis(1)
            # js_right_x = self.joystick.get_axis(2)
            # js_right_y = self.joystick.get_axis(3)

            if circle_button:
                self.circle.setIcon(QIcon('Button - PS Circle 2.svg')) 
            else:
                self.circle.setIcon(QIcon('Button - PS Circle White 1.png'))
            if x_button:
                self.cross.setIcon(QIcon('Button - PS Cross 2.svg')) 
            else:
                self.cross.setIcon(QIcon('Button - PS Cross White 1.png'))
            if square_button:
                self.square.setIcon(QIcon('Button - PS Square 2.svg')) 
            else:
                self.square.setIcon(QIcon('Button - PS Square White 1.png'))
            if triangle_button:
                self.triangle.setIcon(QIcon('Button - PS Triangle 2.svg')) 
            else:
                self.triangle.setIcon(QIcon('Button - PS Triangle White 1.png'))
            if up_button:
                self.arrow.setIcon(QIcon('Button - PS Directional Arrows Up.png'))
            # elif right_button:
            #     self.arrow.setIcon(QIcon('Button - PS Directional Arrows Right.png'))
            # elif down_button:
            #     self.arrow.setIcon(QIcon('Button - PS Directional Arrows Down.png'))
            # elif left_button:       
            #     self.arrow.setIcon(QIcon('Button - PS Directional Arrows Left.png'))
            else:
                self.arrow.setIcon(QIcon('Button - PS Directional Arrows.png'))
            if L1_button:
                self.L1.setIcon(QIcon('Button - PS L1 – 2.png'))
            else:
                self.L1.setIcon(QIcon('Button - PS L1.png'))
            if R1_button:
                self.R1.setIcon(QIcon('Button - PS R1 – 2.png'))
            else:
                self.R1.setIcon(QIcon('Button - PS R1.png'))  

            if js_left_x > 0.5:
                self.js_left.setIcon(QIcon('Button - PS Analogue Blank Right.png'))
            elif js_left_x < -0.5:
                self.js_left.setIcon(QIcon('Button - PS Analogue Blank Left.png'))
            elif js_left_y > 0.5:
                self.js_left.setIcon(QIcon('Button - PS Analogue Blank Down.png'))
            elif js_left_y < -0.5:
                self.js_left.setIcon(QIcon('Button - PS Analogue Blank Up.png'))
            else:
                self.js_left.setIcon(QIcon('Button - PS Analogue Blank.png'))
            
            # if js_right_x > 0.5:
            #     self.js_right.setIcon(QIcon('Button - PS Analogue Blank Down.png'))
            # elif js_right_x < -0.5:
            #     self.js_right.setIcon(QIcon('Button - PS Analogue Blank Up.png'))
            # elif js_right_y > 0.5:
            #     self.js_right.setIcon(QIcon('Button - PS Analogue Blank Up.png'))
            # elif js_right_y < -0.5:
            #     self.js_right.setIcon(QIcon('Button - PS Analogue Blank Down.png'))
            # else:
            #     self.js_right.setIcon(QIcon('Button - PS Analogue Blank.png'))
            # if L2_button:
            #     self.js_left.setIcon(QIcon('Button - PS L2.png'))
            # else:
            #     self.js_left.setIcon(QIcon('Button - PS L2 – 2.png'))
            # if R2_button:
            #     self.js_left.setIcon(QIcon('Button - PS R2.png'))
            # else:
            #     self.js_left.setIcon(QIcon('Button - PS R2 – 2.png'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller_sim = PS4ControllerSimulation()
    controller_sim.show()
    sys.exit(app.exec())