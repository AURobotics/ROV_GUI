import random

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class OrientationWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()

        self.setLayout(layout)

        self.depthLabel = QLabel(self)
        self.yawLabel = QLabel(self)
        self.pitchLabel = QLabel(self)
        self.rollLabel = QLabel(self)

        layout.addWidget(self.depthLabel)
        layout.addWidget(self.yawLabel)
        layout.addWidget(self.pitchLabel)
        layout.addWidget(self.rollLabel)

        self.update()

    def update(self):
        depthReading = random.randint(0, 10)
        yawReading = random.randint(0, 10)
        pitchReading = random.randint(0, 10)
        rollReading = random.randint(0, 10)

        self.depthLabel.setText('Depth: ' + str(depthReading))
        self.yawLabel.setText('Yaw: ' + str(yawReading))
        self.pitchLabel.setText('Pitch: ' + str(pitchReading))
        self.rollLabel.setText('Roll: ' + str(rollReading))
