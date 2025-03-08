import time
from collections.abc import Callable
from typing import Any

from threading import Thread
import serial
import struct
import pygame

class Controller:
    """Manages gamepad selection, gamepad bindings and communication over a chosen serial port"""

    _gamepads:               list[pygame.joystick.JoystickType]
    _gamepad:                pygame.joystick.JoystickType | None
    _gamepad_guid:           str | None
    _send_payload:           Callable[[Any], None] | None
    _emit_connection_change: Callable[[], None]

    @staticmethod
    def _no_op():
        pass

    def __init__(self, payload_callback = None, connection_callback = None) -> None:
        pygame.init()
        self._emit_connection_change = connection_callback if connection_callback is not None else self._no_op
        self._gamepad = None
        self._gamepad_guid = None
        self._refresh_gamepads()
        self._send_payload = payload_callback
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
    def payload_callback(self) -> Callable[[Any], None] | None:
        return self._send_payload
    @payload_callback.setter
    def payload_callback(self, payload_callback) -> None:
        self._send_payload = payload_callback
    @property
    def gamepads(self) -> list[str]:
        self._refresh_gamepads()
        return [gamepad.get_name() for gamepad in self._gamepads]

    @property
    def gamepad(self) -> str | None:
        if self._gamepad is not None:
            return f'{self._gamepad.get_id()}: {self._gamepad.get_name()}'
        return None

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

        def sgn(n: int) -> int:
            """Returns 1 for even numbers, -1 for odd numbers"""
            if n % 2:
                return -1
            return 1

        led_and_valves = 0
        order_of_axes = [1, 0, 3, 2]
        leds_buttons = [15, 10, 9]
        while True:

            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    self._refresh_gamepads()
                    self._emit_connection_change()
                if event.type == pygame.JOYDEVICEREMOVED:
                    self._refresh_gamepads()
                    self._emit_connection_change()
            if self._gamepad is None or self._send_payload is None:
                continue

            # Keybindings:
            # LStick - Axis 0 (Horizontal): Shift the ROV sideways
            # LStick - Axis 1 (Vertical): Move forward/ backward
            # RStick - Axis 2 (Horizontal): Rotate sideways about vertical axis
            # RStick - Axis 3 (Vertical): Tilt up or down
            # L2 - Axis 4 (+1 then /2): descend
            # R2 - Axis 5 (+1 then / 2): climb
            # Climb total value: (R2 + 1) / 2 - (L2 + 1) / 2
            signed_payload = [int(254 * sgn(x) * self._gamepad.get_axis(x)) for x in order_of_axes] # all except L2 and R2
            signed_payload = [byte if byte > 30 else 0 for byte in signed_payload]
            # signed_payload = [23, -190, 0, 230]
            climb = int(254 * (((self._gamepad.get_axis(4) + 1) / 2) - ((self._gamepad.get_axis(5) + 1) / 2)))
            signed_payload.append(climb)
            #signed_payload = [0, 0, 150, 0, 0]
            thruster_payload = [abs(b) for b in signed_payload]
            sign_byte = 0
            for i, byte in enumerate(signed_payload):
                if byte < 0:
                    sign_byte |= 1 << i
            payload = thruster_payload
            payload.append(sign_byte)
            # Touchpad Click - LED: 0000 0 LED 0      0
            # L1, R1 - Valves:      0000 0 0   VALVE1 VALVE2
            for i, button in enumerate(leds_buttons):
                led_and_valves ^= (self._gamepad.get_button(button) << i)
            payload.append(led_and_valves)
            payload.append(xor(payload[:7]))
            payload.append(255) # Terminator byte
            print(payload)
            payload = struct.pack("9B", *payload)
            self._send_payload(payload)
            time.sleep(0.015) # attempt at synchronization with main thread which may print output


    def __del__(self) -> None:
        self._handler_thread.join()
        pygame.quit()