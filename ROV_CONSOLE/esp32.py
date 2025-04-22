import threading
from sys import stderr
from typing import Optional

import serial
import serial.tools.list_ports
from esptool import main as run_esptool


class ESP32:
    _serial: serial.Serial
    _port_over_rfc: bool

    def __init__(self, baudrate: int = 115200):
        self._connection_in_progress = False
        self._baudrate = baudrate
        self._serial = serial.Serial(port=None, baudrate=baudrate)
        self._resetting = False
        self._port_over_rfc = False

    @property
    def available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    @property
    def port(self) -> Optional[str]:
        return self._serial.port

    @port.setter
    def port(self, port: Optional[str]):
        if port is None:
            self.disconnect()
        else:
            self.connect(port)

    @property
    def is_resetting(self):
        return self._resetting

    @property
    def connected(self) -> bool:
        # TODO: maybe check if it's resetting?
        if self._serial.port is None:
            return False
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

        if not self.connected:
            return
        self._resetting = True
        reset_thread = threading.Thread(target=actual_reset)
        reset_thread.start()

    def disconnect(self):
        self._serial.close()
        self._serial.port = None

    def connect(self, port: str) -> None:
        self._serial.close()
        if self._connection_in_progress:
            return
        self._connection_in_progress = True

        def _actual_connect() -> None:
            try:
                if "rfc2217://" in port and not self._port_over_rfc:
                    print("Ports over RFC is not fully supported, disconnects will not be detected!", file=stderr)
                    self._serial = serial.serial_for_url(port, baudrate=self._baudrate)
                    self._port_over_rfc = True
                    return
                if "rfc2217://" not in port and self._port_over_rfc:
                    self._serial = serial.Serial(port=port, baudrate=self._baudrate)
                    self._port_over_rfc = False
                    return
                self._serial.port = port
                self._serial.open()
            except Exception as e:
                print(e)
                self._serial.port = None
            finally:
                self._connection_in_progress = False

        connection_thread = threading.Thread(target=_actual_connect)
        connection_thread.start()

    def send(self, buffer: bytes) -> None:
        try:
            if self.connected:
                self._serial.write(buffer)
        except (serial.SerialException, serial.serialutil.SerialException):
            self.disconnect()
            return

    @property
    def incoming(self):
        try:
            return self._serial.in_waiting
        except (serial.SerialException, serial.serialutil.PortNotOpenError):
            self.disconnect()
            return None

    @property
    def next_line(self):
        try:
            return self._serial.readline().decode().rstrip()
        except serial.SerialException:
            self.disconnect()
            return None

    def __del__(self):
        self._serial.close()
