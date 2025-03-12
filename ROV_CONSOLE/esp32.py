import serial
import serial.tools.list_ports

ESP_TOOL = ["python", "-m", "esptool"]

class ESP32:
    _BAUDRATE: int = 115200
    def __init__(self):
        self._serial: serial.Serial|None = None
        ...

    @property
    def available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    @property
    def connected(self) -> bool:

        try:
            _ = self._serial.in_waiting
        except serial.SerialException:
            self._serial = None
        return self._serial is not None

    def disconnect(self):
        ...

    def connect(self, port):
        if port.startswith("rfc://"):
            self._serial = serial.serial_for_url(port, baudrate=self._BAUDRATE)
        else:
            self._serial = serial.Serial(port , baudrate=self._BAUDRATE)

    def send(self, buffer: bytes) -> None:
        if self.connected:
            self._serial.write(buffer)

    @property
    def incoming(self):
        return self._serial.in_waiting

    @property
    def next_line(self):
        return self._serial.readline().decode()

    def __del__(self):
        ...