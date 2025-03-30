from typing import Optional

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

        layout.addWidget(self.yawLabel)
        layout.addWidget(self.pitchLabel)
        layout.addWidget(self.rollLabel)

        self.display(None)

    def display(self, readings: Optional[dict]):
        yaw, pitch, roll = (0, 0, 0)
        if readings is not None:
            yaw = readings['yaw']
            pitch = readings['pitch']
            roll = readings['roll']

        self.yawLabel.setText('Yaw: ' + str(yaw))
        self.pitchLabel.setText('Pitch: ' + str(pitch))
        self.rollLabel.setText('Roll: ' + str(roll))
