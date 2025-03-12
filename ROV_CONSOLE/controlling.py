import time
from collections.abc import Callable
from functools import reduce
from typing import Any
from enum import Enum, StrEnum
from threading import Thread
import struct
import pygame

class BindingNames(dict[str:list[str]], Enum):
    DS4 = {'buttons': ['CROSS', 'CIRCLE', 'SQUARE', 'TRIANGLE', 'SHARE', 'PS', 'OPTIONS', 'L3', 'R3', 'L1', 'R1', 'D-UP', 'D-DOWN',
           'D-LEFT', 'D-RIGHT', 'TOUCHPAD'], 'axes': ['LS-H', 'LS-V', 'RS-H', 'RS-V', 'L2', 'R2']}

class GamepadTypes(StrEnum):
    DS4 = 'PS4 Controller'

class Controller:
    """Manages gamepad selection, gamepad bindings and communication over a chosen serial port"""

    _gamepads:               list[pygame.joystick.JoystickType]
    _gamepad:                pygame.joystick.JoystickType | None
    _gamepad_guid:           str | None
    _send_payload:           Callable[[Any], None] | None
    _emit_connection_change: Callable[[], None]
    _STICK_DEADZONE = 30

    def __init__(self, payload_callback = None) -> None:
        pygame.init()
        self._gamepad = None
        self._gamepad_guid = None
        self._type = None
        self._refresh_gamepads()
        self._send_payload = payload_callback
        self._killswitch = False
        self._bindings_state = {}
        self._handler_thread = Thread(target=self._handler_loop)
        self._handler_thread.start()

    def _disconnect(self) -> None:
        self._gamepad = None
        self._gamepad_guid = None
        self._type = None
        self._gamepads = []
        self._bindings_state = {}
        return

    def _connect(self, i: int) -> None:
        self._gamepad = self._gamepads[i]
        self._gamepad_guid = self._gamepad.get_guid()
        for t in GamepadTypes:
            if t.value == self._gamepad.get_name():
                self._type = t.name

    def _refresh_gamepads(self) -> None:
        gamepad_count = pygame.joystick.get_count()
        if gamepad_count == 0:
            self._disconnect()
            return
        self._gamepads = [pygame.joystick.Joystick(i) for i in range(gamepad_count)]
        for gamepad in self._gamepads:
            if gamepad.get_guid() == self._gamepad_guid:
                self._gamepad = gamepad
                return
        if self._gamepads[0].get_name() not in GamepadTypes:
            self._disconnect()
        self._connect(0)

    @property
    def bindings_state(self):
        return self._bindings_state

    @property
    def payload_callback(self) -> Callable[[Any], None] | None:
        return self._send_payload

    @payload_callback.setter
    def payload_callback(self, payload_callback) -> None:
        self._send_payload = payload_callback

    @property
    def gamepads(self) -> list[str]:
        self._refresh_gamepads()
        return [f'{gamepad.get_id()}: {gamepad.get_name()}' for gamepad in self._gamepads]

    @property
    def connected(self):
        return self._gamepad is not None

    @property
    def gamepad(self) -> str | None:
        if self._gamepad is not None:
            return f'{self._gamepad.get_id()}: {self._gamepad.get_name()}'
        return None

    @gamepad.setter
    def gamepad(self, index: int|None) -> None:
        if index is None or index > len(self._gamepads):
            self._disconnect()
        self._refresh_gamepads()
        n = self._gamepads[index].get_name()
        for i in GamepadTypes:
            if i.value == n:
                self._connect(index)

    def _handler_loop(self):
        toggles_cooldown = [0, 0, 0] # Debounce for toggleable options
        while not self._killswitch:
            time.sleep(0.015)  # attempt at synchronization with main thread which may print output
            for event in pygame.event.get():
                if event.type == pygame.JOYDEVICEADDED:
                    self._refresh_gamepads()
                if event.type == pygame.JOYDEVICEREMOVED:
                    self._refresh_gamepads()
            if self._gamepad is None:
                continue

            buttons = { k:self._gamepad.get_button(i) for i,k in enumerate(BindingNames[self._type]['buttons']) }
            axes = { a:self._gamepad.get_axis(i) for i, a in enumerate(BindingNames[self._type]['axes']) }
            self._bindings_state = {**buttons, **axes}

            if self._send_payload is None:
                continue
            # Keybindings:
            # LStick - Axis 0 (Horizontal): Shift the ROV sideways
            # LStick - Axis 1 (Vertical): Move forward/ backward
            # RStick - Axis 2 (Horizontal): Rotate sideways about vertical axis
            # RStick - Axis 3 (Vertical): Tilt up or down
            # L2 - Axis 4 (+1 then /2): descend
            # R2 - Axis 5 (+1 then / 2): climb
            # Climb total value: (R2 + 1) / 2 - (L2 + 1) / 2
            signed_payload = [int(-254 * self._bindings_state['LS-V']), int(254 * self._bindings_state['LS-H']),
                              int(-254 * self._bindings_state['RS-V']), int(254 * self._bindings_state['RS-H'])]

            # Apply Deadzone
            signed_payload = [direction if abs(direction) > self._STICK_DEADZONE else 0 for direction in signed_payload]

            signed_payload.append(int(254 * ( ((self._bindings_state['R2'] + 1)/2) - ((self._bindings_state['L2'] + 1)/2) )))
            thruster_payload = [abs(byte) for byte in signed_payload]
            sign_byte = 0
            for i, byte in enumerate(signed_payload):
                if byte < 0:
                    sign_byte |= 1 << i
            payload = thruster_payload
            payload.append(sign_byte)

            # Touchpad Click - LED: 0000 0 LED 0      0
            # L1, R1 - Valves:      0000 0 0   VALVE1 VALVE2
            led_and_valves = 0
            if toggles_cooldown[0] == 0 and self._bindings_state['L1']:
                toggles_cooldown[0] = 15
                led_and_valves ^= self._bindings_state['L1']
            if toggles_cooldown[1] == 0 and self._bindings_state['TOUCHPAD']:
                toggles_cooldown[1] = 15
                led_and_valves ^= self._bindings_state['TOUCHPAD'] << 2
            if toggles_cooldown[2] == 0 and self._bindings_state['R1']:
                toggles_cooldown[2] = 15
                led_and_valves ^= self._bindings_state['R1'] << 1
            toggles_cooldown = [i-1 if i>0 else 0 for i in toggles_cooldown]
            payload.append(led_and_valves)

            # Checksum: XOR first 7 bytes
            payload.append(reduce(lambda x, y: x ^ y, payload[:7]))

            # Terminator byte
            payload.append(255)
            payload = struct.pack("9B", *payload)

            self._send_payload(payload)

    def discard(self):
        self._killswitch = True
        if self._handler_thread.is_alive():
            self._handler_thread.join()
        self._disconnect()
        pygame.quit()

    def __del__(self) -> None:
        self._killswitch = True
        if self._handler_thread.is_alive():
            self._handler_thread.join()
        self._disconnect()
        pygame.quit()