"""
Wrapper for PyGame with an RAII-conforming class 'Controller'.
Manages the following:
   - Choosing one or none of the currently connected gamepads
   - Regularly presenting the state of the keybindings
   - Regularly checking for, presenting and managing connection changes
   - Publishing a human-readable interface for reading the state of keybindings
   - TODO: support different types/ brands of gamepads - currently supports PS4/DS4 only
"""

import struct
import time
from collections.abc import Callable
from enum import Enum, StrEnum
from functools import reduce
from threading import Thread
from typing import Any

import pygame


class BindingNames(dict[str, list[str]], Enum):
    DS4 = {
        "buttons": [
            "CROSS",
            "CIRCLE",
            "SQUARE",
            "TRIANGLE",
            "SHARE",
            "PS",
            "OPTIONS",
            "L3",
            "R3",
            "L1",
            "R1",
            "D-UP",
            "D-DOWN",
            "D-LEFT",
            "D-RIGHT",
            "TOUCHPAD",
        ],
        "axes": ["LS-H", "LS-V", "RS-H", "RS-V"],
        "triggers": ["L2", "R2"],
    }


class GamepadTypes(StrEnum):
    DS4 = "PS4 Controller"


class Controller:
    """Manages gamepad connection, gamepad selection, and gamepad bindings"""

    _gamepads: list[pygame.joystick.JoystickType]
    _gamepad: pygame.joystick.JoystickType | None
    _type: str | None
    _gamepad_guid: str | None
    _bindings_state: dict[str, int | float]
    _killswitch: bool
    _handler_thread: Thread
    _send_payload: Callable[[Any], None] | None
    _STICK_DEADZONE = 0.12

    def __init__(self, payload_callback=None) -> None:
        pygame.init()
        self._gamepad = None
        self._gamepad_guid = None
        self._type = None
        pygame.event.pump()
        self._refresh_gamepads(connect_if_only_device=True)
        self._send_payload = payload_callback
        self._killswitch = False
        self._bindings_state = {}
        self._handler_thread = Thread(target=self._handler_loop, daemon=True)
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

    def _refresh_gamepads(self, connect_if_only_device=False) -> None:
        gamepad_count = pygame.joystick.get_count()
        if gamepad_count == 0:
            self._disconnect()
            return
        self._gamepads = [pygame.joystick.Joystick(i) for i in range(gamepad_count)]
        for gamepad in self._gamepads:
            if gamepad.get_guid() == self._gamepad_guid:
                self._gamepad = gamepad
                return
        if connect_if_only_device:
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
        return [
            f"{gamepad.get_id()}: {gamepad.get_name()}" for gamepad in self._gamepads
        ]

    @property
    def connected(self):
        return self._gamepad is not None

    @property
    def gamepad(self) -> str | None:
        if self._gamepad is not None:
            return f"{self._gamepad.get_id()}: {self._gamepad.get_name()}"
        return None

    @gamepad.setter
    def gamepad(self, index: int | None) -> None:
        if index is None or index > len(self._gamepads):
            self._disconnect()
            return
        self._refresh_gamepads()
        n = self._gamepads[index].get_name()
        for i in GamepadTypes:
            if i.value == n:
                self._connect(index)

    def _handler_loop(self):
        toggles_cooldown = [0, 0, 0]  # Debounce for toggleable options
        led_and_valves: int = 0
        try:
            while not self._killswitch:
                time.sleep(0.015)
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.JOYDEVICEADDED:
                            self._refresh_gamepads(connect_if_only_device=True)
                        if event.type == pygame.JOYDEVICEREMOVED:
                            self._refresh_gamepads()
                except Exception:
                    if self._killswitch:
                        break
                if self._gamepad is None:
                    continue

                buttons = {
                    k: self._gamepad.get_button(i)
                    for i, k in enumerate(BindingNames[self._type]["buttons"])
                }
                axes = {
                    a: (
                        self._gamepad.get_axis(i)
                        if abs(self._gamepad.get_axis(i)) > self._STICK_DEADZONE
                        else 0
                    )
                    for i, a in enumerate(BindingNames[self._type]["axes"])
                }
                triggers = {
                    t: (
                        self._gamepad.get_axis(
                            i + len(BindingNames[self._type]["axes"])
                        )
                        + 1
                    )
                    / 2
                    for i, t in enumerate(BindingNames[self._type]["triggers"])
                }
                self._bindings_state = {**buttons, **axes, **triggers}

                if self._send_payload is None:
                    continue
                # Keybindings:
                # LStick - Axis 0 (Horizontal): Shift the ROV sideways
                # LStick - Axis 1 (Vertical): Move forward/ backward
                # RStick - Axis 2 (Horizontal): Rotate sideways about vertical axis
                # RStick - Axis 3 (Vertical): Tilt up or down
                # L2 - Axis 4 (+1 then /2): descend
                # R2 - Axis 5 (+1 then / 2): climb
                # Climb total value: R2 - L2
                signed_payload = [
                    int(-254 * self._bindings_state["LS-V"]),
                    int(254 * self._bindings_state["LS-H"]),
                    int(-254 * self._bindings_state["RS-V"]),
                    int(254 * self._bindings_state["RS-H"]),
                    int(
                        254 * (self._bindings_state["R2"] - self._bindings_state["L2"])
                    ),
                ]

                thruster_payload = [abs(byte) for byte in signed_payload]
                sign_byte = 0
                for i, byte in enumerate(signed_payload):
                    if byte < 0:
                        sign_byte |= 1 << i
                payload = thruster_payload
                payload.append(sign_byte)

                # Touchpad Click - LED: 0000 0 LED 0      0
                # L1, R1 - Valves:      0000 0 0   VALVE1 VALVE2
                if toggles_cooldown[0] == 0 and self._bindings_state["L1"]:
                    toggles_cooldown[0] = 15
                    led_and_valves ^= 1
                if toggles_cooldown[1] == 0 and self._bindings_state["TOUCHPAD"]:
                    toggles_cooldown[1] = 15
                    led_and_valves ^= 4
                if toggles_cooldown[2] == 0 and self._bindings_state["R1"]:
                    toggles_cooldown[2] = 15
                    led_and_valves ^= 4
                toggles_cooldown = [i - 1 if i > 0 else 0 for i in toggles_cooldown]
                payload.append(led_and_valves)

                # Checksum: XOR first 7 bytes
                payload.append(reduce(lambda x, y: x ^ y, payload[:7]))

                # Terminator byte
                payload.append(255)
                payload = struct.pack("9B", *payload)

                self._send_payload(payload)
        except SystemExit:
            self.kill()

    def kill(self):
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
