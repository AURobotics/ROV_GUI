import threading
import serial
import serial.tools.list_ports
from sys import stderr
from esptool import main as run_esptool


class ESP32:
    _BAUDRATE: int = 115200
    _serial: serial.Serial
    _port_rfc: bool

    def __init__(self):
        self._serial = serial.Serial(port=None, baudrate=self._BAUDRATE)
        self._resetting = False
        self._port_rfc = False

    @property
    def available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    @property
    def port(self) -> str | None:
        return self._serial.port

    @port.setter
    def port(self, port: str | None):
        if port is None:
            self.disconnect()
        else:
            self.connect(port)

    @property
    def is_resetting(self):
        return self._resetting

    @property
    def connected(self) -> bool:
        try:
            # Works with actual serial ports, network ports may need a write/ read operation instead to raise exception
            _ = self._serial.in_waiting
        except serial.SerialException:
            self._serial.close()
            if self._serial.port in self.available_ports:
                # Try to revive connection
                self._serial.open()
            else:
                # Forget connection
                self._serial.port = None
        return self._serial.port is not None

    @property
    def serial_ready(self):
        return self.connected and not self._resetting

    def reset(self):
        def actual_reset():
            run_esptool(["--port", self.port, "reset"])
            self._resetting = False

        self._resetting = True
        reset_thread = threading.Thread(target=actual_reset)
        reset_thread.start()

    def disconnect(self):
        self._serial.close()
        self._serial.port = None

    def connect(self, port: str) -> None:
        self._serial.close()
        if "rfc2217://" in port and not self._port_rfc:
            print(
                "Ports over RFC is not fully supported, disconnects will not be detected!",
                stderr,
            )
            self._serial = serial.serial_for_url(port, baudrate=self._BAUDRATE)
            self._port_rfc = True
            return
        if "rfc2217://" not in port and self._port_rfc:
            self._serial = serial.Serial(port=port, baudrate=self._BAUDRATE)
            self._port_rfc = False
            return
        try:
            self._serial.port = port
            self._serial.open()
        except serial.SerialException:
            self._serial.port = None

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
        self._serial.close()
