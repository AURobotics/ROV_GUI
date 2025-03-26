import json
import struct
from functools import reduce
from threading import Thread
from time import sleep
from typing import Optional

from plyer import notification

from ROV_CONSOLE.esp32 import ESP32
from ROV_CONSOLE.gamepad import Controller


class CommunicationManager:
    """Competition-specific handler for the ESP Comms"""
    _VALID_LINES = [
        'Checksum error! Ignoring packet',  # notify
        'DC Valve 1: %boolN',  # Valve 1
        'DC Valve 2: %boolN',  # Valve 2
        'BNO055 not detected',  # notify
        'All systems are working fine from Guileta',  # ignore
        'Thruster Forces:'  # ignore
        ' F1: %.2f F2: %.2f F3: %.2f F4: %.2f F5: %.2f F6: %.2f',  # Thruster forces
        '%d  %d  %d'  # IMU Readings: yaw, pitch, roll
        ]

    def __init__(self, esp: ESP32, controller: Controller, thrusters_callback: None, imu_callback=None):
        self._esp = esp
        self._controller = controller
        self._cache = {
            'controller': {'led_and_valves': 0, 'L1_debounce': 0, 'R1_debounce': 0, 'TOUCHPAD_debounce': 0}
            }
        self._thrusters_callback = thrusters_callback
        self._imu_callback = imu_callback
        self._killswitch = False
        self._comms_thread = Thread(target=self._comms_loop, daemon=True)

    def _comms_loop(self):
        while not self._killswitch:
            sleep(0.015)
            if self._esp.serial_ready:
                consumed: Optional[str] = None
                if self._esp.incoming:
                    consumed = self._esp.next_line

                readings = None
                try:
                    readings = json.loads(consumed)
                except json.JSONDecodeError:
                    readings = None
                    notification.notify(
                        title='ROV ERROR',
                        message=consumed,
                        timeout=2,
                        app_name='AU Robotics ROV GUI'
                        )

                if readings is not None:
                    if self._thrusters_callback is not None:
                        ...

                    if self._imu_callback is not None:
                        ...

                if self._controller is not None:
                    if self._controller.connected:
                        self._esp.send(self._controller_payload())

    def _controller_payload(self):
        # Keybindings:
        # LStick - Axis 0 (Horizontal): Shift the ROV sideways
        # LStick - Axis 1 (Vertical): Move forward/ backward
        # RStick - Axis 2 (Horizontal): Rotate sideways about vertical axis
        # RStick - Axis 3 (Vertical): Tilt up or down
        # L2 - Axis 4 (+1 then /2): descend
        # R2 - Axis 5 (+1 then / 2): climb
        # Climb total value: R2 - L2
        bindings = self._controller.bindings_state
        signed_payload = [
            int(-254 * bindings["LS-V"]),
            int(254 * bindings["LS-H"]),
            int(-254 * bindings["RS-V"]),
            int(254 * bindings["RS-H"]),
            int(
                254 * (bindings["R2"] - bindings["L2"])
                ),
            ]
        thruster_payload = [abs(byte) for byte in signed_payload]
        sign_byte = 0
        for i, byte in enumerate(signed_payload):
            if byte < 0:
                sign_byte |= 1 << i
        payload = thruster_payload
        payload.append(sign_byte)

        toggles_cache = self._cache['controller']
        # Touchpad Click - LED: 0000 0 LED 0      0
        # L1, R1 - Valves:      0000 0 0   VALVE1 VALVE2
        if toggles_cache['L1_debounce'] == 0 and bindings["L1"]:
            toggles_cache['L1_debounce'] = 15
            toggles_cache['led_and_valves'] ^= 1

        if toggles_cache['TOUCHPAD_debounce'] == 0 and bindings["TOUCHPAD"]:
            toggles_cache['TOUCHPAD_debounce'] = 15
            toggles_cache['led_and_valves'] ^= 4

        if toggles_cache['R1_debounce'] == 0 and bindings["R1"]:
            toggles_cache['R1_debounce'] = 15
            toggles_cache['led_and_valves'] ^= 4

        if toggles_cache['L1_debounce'] > 0:
            toggles_cache['L1_debounce'] -= 1
        if toggles_cache['TOUCHPAD_debounce'] > 0:
            toggles_cache['TOUCHPAD_debounce'] -= 1
        if toggles_cache['R1_debounce'] > 0:
            toggles_cache['R1_debounce'] -= 1

        payload.append(toggles_cache['led_and_valves'])

        # Checksum: XOR first 7 bytes
        payload.append(reduce(lambda x, y: x ^ y, payload[:7]))

        # Terminator byte
        payload.append(255)
        payload = struct.pack("9B", *payload)
        return payload

    def __del__(self):
        self._killswitch = True
        self._comms_thread.join()
