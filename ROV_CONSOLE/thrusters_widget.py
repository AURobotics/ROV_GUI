from PySide6.QtGui import QColor, QPainter, QPen, QBrush, Qt
from PySide6.QtWidgets import QWidget, QLabel


class ThrustersWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.frontLabel = QLabel(self)
        self.backLabel = QLabel(self)
        self.leftfrontLabel = QLabel(self)
        self.rightfrontLabel = QLabel(self)
        self.leftbackLabel = QLabel(self)
        self.rightbackLabel = QLabel(self)

        # Default colors
        self.square_color = QColor(0, 0, 0)  # Black for center square

        self.circle_colors = [
            QColor(0, 255, 0),  # Top
            QColor(0, 255, 0),
            # ,  # Bottom
            # # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
            ]

        self.rotated_square_colors = [
            QColor(0, 255, 0),  # Front-left
            QColor(0, 255, 0),  # Front-right
            QColor(0, 255, 0),  # Back-left
            QColor(0, 255, 0),  # Back-right
            ]

    def set_colors(self):
        '''Allows changing colors dynamically'''

        frontRightSpeed = 0
        backRightSpeed = 255
        frontLeftSpeed = 100
        backLeftSpeed = 200
        upFrontSpeed = 50
        upBackSpeed = 150

        self.frontLabel.setText(str(upFrontSpeed))
        self.backLabel.setText(str(upBackSpeed))
        self.leftfrontLabel.setText(str(frontLeftSpeed))
        self.rightfrontLabel.setText(str(frontRightSpeed))
        self.leftbackLabel.setText(str(backLeftSpeed))
        self.rightbackLabel.setText(str(backRightSpeed))

        self.square_color = QColor(0, 0, 0)
        self.circle_colors = [
            QColor(upFrontSpeed, 255 - upFrontSpeed, 0),  # Top
            QColor(upBackSpeed, 255 - upBackSpeed, 0),
            # ,  # Bottom
            # QColor(0, 255, 0),  # Left
            # QColor(0, 255, 0)   # Right
            ]
        self.rotated_square_colors = [
            QColor(frontLeftSpeed, 255 - frontLeftSpeed, 0),  # Front-left
            QColor(frontRightSpeed, 255 - frontRightSpeed, 0),  # Front-right
            QColor(backLeftSpeed, 255 - backLeftSpeed, 0),  # Back-left
            QColor(backRightSpeed, 255 - backRightSpeed, 0),  # Back-right
            ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get parent size constraints
        max_width = self.parent.width() // 3
        max_height = self.parent.height() // 4
        size = min(max_width, max_height)

        # Central square (70% of size)
        square_size = int(
            size * 0.7
            )  ###changing the ratio changes the thrusters size###
        square_x = (self.width() - square_size) // 2
        square_y = (self.height() - square_size) // 2

        # Draw the black center square
        painter.setPen(QPen(self.square_color, 3))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawRect(square_x, square_y, square_size, square_size)

        # Circles' and Rotated Squares' Positions
        offsets = [
            (square_x + square_size // 2, square_y - square_size // 3),  # Top
            (square_x + square_size // 2, square_y + square_size + square_size // 3),
            # ,  # Bottom
            # (square_x - square_size // 3, square_y + square_size // 2),  # Left
            # (square_x + square_size + square_size // 3, square_y + square_size // 2)  # Right
            ]

        rotated_offsets = [
            (square_x - square_size // 3, square_y - square_size // 3),  # Top-left
            (
                square_x + square_size + square_size // 3,
                square_y - square_size // 3,
                ),  # Top-right
            (
                square_x - square_size // 3,
                square_y + square_size + square_size // 3,
                ),  # Bottom-left
            (
                square_x + square_size + square_size // 3,
                square_y + square_size + square_size // 3,
                ),  # Bottom-right
            ]

        self.frontLabel.setGeometry(
            offsets[0][0] - 10, offsets[0][1] - 15, 100, 30
            )  # (x, y, width, height)
        self.backLabel.setGeometry(offsets[1][0] - 10, offsets[1][1] - 15, 100, 30)
        self.leftfrontLabel.setGeometry(
            rotated_offsets[0][0] - 10, rotated_offsets[0][1] - 15, 100, 30
            )
        self.rightfrontLabel.setGeometry(
            rotated_offsets[1][0] - 10, rotated_offsets[1][1] - 15, 100, 30
            )
        self.leftbackLabel.setGeometry(
            rotated_offsets[2][0] - 10, rotated_offsets[2][1] - 15, 100, 30
            )
        self.rightbackLabel.setGeometry(
            rotated_offsets[3][0] - 10, rotated_offsets[3][1] - 15, 100, 30
            )

        circle_radius = int(square_size * 0.2)

        # Draw Circles with individual colors
        for i, (x, y) in enumerate(offsets):
            painter.setBrush(QBrush(self.circle_colors[i]))
            painter.drawEllipse(
                x - circle_radius,
                y - circle_radius,
                circle_radius * 2,
                circle_radius * 2,
                )

        # Draw Rotated Squares with individual colors
        for i, (x, y) in enumerate(rotated_offsets):
            painter.setBrush(QBrush(self.rotated_square_colors[i]))
            painter.save()
            painter.translate(x, y)
            painter.rotate(45)  # Rotate by 45 degrees
            painter.drawRect(
                -circle_radius, -circle_radius, circle_radius * 2, circle_radius * 2
                )
            painter.restore()

    def updateThrusters(self):
        self.set_colors()
        self.update()
