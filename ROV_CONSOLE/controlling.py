import time
from collections.abc import Callable

from threading import Thread
import serial
import struct
import pygame

class Controller:
    """Manages gamepad selection, gamepad bindings and communication over a chosen serial port"""

    _gamepads:               list[pygame.joystick.JoystickType]
    _gamepad:                pygame.joystick.JoystickType | None
    _gamepad_guid:           str | None
    _serial:                 serial.Serial | None
    _emit_connection_change: Callable[[], None]

    @staticmethod
    def _no_op():
        pass

    def __init__(self, _serial = None, _connection_callback = None) -> None:
        pygame.init()
        self._emit_connection_change = _connection_callback if _connection_callback is not None else self._no_op
        self._gamepad = None
        self._gamepad_guid = None
        self._refresh_gamepads()
        self._serial = _serial
        self._handler_thread = Thread(target=self._handler_loop, daemon=True)
        self._handler_thread.start()

    def _refresh_gamepads(self) -> None:
        gamepad_count = pygame.joystick.get_count()
        if gamepad_count == 0:
            self._gamepad = None
            self._gamepad_guid = None
            self._gamepads = []
            return
        self._gamepads = [pygame.joystick.Joystick(i) for i in range(gamepad_count)]
        for gamepad in self._gamepads:
            if gamepad.get_guid() == self._gamepad_guid:
                self._gamepad = gamepad
                return
        self._gamepad = self._gamepads[0]
        self._gamepad_guid = self._gamepad.get_guid()

    @property
    def gamepads(self) -> list[str]:
        self._refresh_gamepads()
        return [gamepad.get_name() for gamepad in self._gamepads]

    @property
    def gamepad(self) -> str:
        if self._gamepad is not None:
            return f'{self._gamepad.get_id()}: {self._gamepad.get_name()}'

    @gamepad.setter
    def gamepad(self, index: int) -> None:
        self._refresh_gamepads()
        if index < len(self._gamepads):
            self._gamepad = self._gamepads[index]

    def _handler_loop(self):
        def xor(byte_list: list[int]) -> int:
            result = byte_list.pop(0)
            for byte in byte_list:
                result ^= byte
            return result

        while True:

            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    self._refresh_gamepads()
                    self._emit_connection_change()
                if event.type == pygame.JOYDEVICEREMOVED:
                    self._refresh_gamepads()
                    self._emit_connection_change()
            if self._gamepad is None or self._serial is None:
                continue
            if self._serial.in_waiting:
                print(self._serial.readline())
            time.sleep(1)
            payload = [int(254 * self._gamepad.get_button(x)) for x in range(8)]
            payload.insert(0, 255)
            payload.append(0b10101010)  # directions
            payload.append(0b10101010)  # leds
            payload.append(xor(payload[1:8]))
            payload = struct.pack("12B", *payload)
            self._serial.write(payload)


    def __del__(self) -> None:
        self._handler_thread.join()
        pygame.quit()