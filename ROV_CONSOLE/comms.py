import json
import struct
from functools import reduce
from threading import Thread
from time import sleep
from typing import Optional

from plyer import notification
from schema import Schema, Optional, SchemaError

from ROV_CONSOLE.esp32 import ESP32
from ROV_CONSOLE.gamepad import Controller

readings_schema = Schema(
    {
        'thrusters':    {'h1': float, 'h2': float, 'h3': float, 'h4': float, 'v1': float, 'v2': float},
        'orientation':  {'roll': float, 'pitch': float, 'yaw': float},
        'acceleration': {'x': float, 'y': float, 'z': float},
        'status':       {'led': bool, 'dcv1': bool, 'dcv2': bool},
        }
    )


class CommunicationManager:
    """Competition-specific handler for the ESP Comms"""
    _PAYLOAD_MS = 0.033

    def __init__(self, esp: ESP32, controller: Controller):
        self._esp = esp
        self._controller = controller
        self._cache = {
            'controller':  {'led_and_valves': 0, 'L1': 0, 'R1': 0, 'TOUCHPAD': 0},
            'thrusters':   None,
            'orientation': None,
            }
        self._killswitch = False
        self._serial_incoming_thread = Thread(target=self._serial_incoming_loop, daemon=True)
        self._serial_incoming_thread.start()
        self._serial_outgoing_thread = Thread(target=self._serial_outgoing_loop, daemon=True)
        self._serial_outgoing_thread.start()
        self._controller.register_listener(self._controller_toggles, ['L1', 'R1', 'TOUCHPAD'], send_buttons=True)

    def _controller_toggles(self, button):
        if self._esp.serial_ready:
            self._cache['controller'][button] = not self._cache['controller'][button]

    @property
    def thrusters_readings(self):
        return self._cache['thrusters']

    @property
    def orientations_readings(self):
        return self._cache['orientation']

    def _serial_outgoing_loop(self):
        while not self._killswitch:
            sleep(self._PAYLOAD_MS)
            if self._esp.serial_ready:
                if self._controller.connected:
                    self._esp.send(self._serial_controller_payload())

    def _serial_incoming_loop(self):
        """Updates internal values, runs on separate internal thread"""
        while not self._killswitch:
            sleep(0.015)
            if not self._esp.serial_ready:
                # Reset the transient part of the cache
                # Non-transient keys include: controller['leds_and_valves']

                self._cache['thrusters'] = None
                self._cache['orientation'] = None
            else:
                consumed: Optional[str] = None

                while self._esp.incoming:
                    readings = None
                    # TODO: Tolerate sudden disconnect
                    consumed = self._esp.next_line
                    try:
                        readings = json.loads(consumed, parse_int=float)
                        readings = readings_schema.validate(readings)
                    except json.JSONDecodeError:
                        # Consumed message was an error or debug message
                        readings = None
                        # temporarily removed because of spam
                        # notification.notify(
                        #     title='ROV MESSAGE',
                        #     message=consumed,
                        #     timeout=2,
                        #     app_name='AU Robotics ROV GUI'
                        #     )
                        print(consumed);
                    except SchemaError:
                        # Consumed message was a malformed readings message
                        readings = None

                    if readings is not None:
                        self._cache['thrusters'] = readings['thrusters'].copy()
                        self._cache['orientation'] = readings['orientation'].copy()

    def _serial_controller_payload(self):
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

        toggles = self._cache['controller']
        # Touchpad Click - LED: 0000 0 LED 0      0
        # L1, R1 - Valves:      0000 0 0   VALVE1 VALVE2
        toggles['led_and_valves'] ^= toggles['TOUCHPAD'] << 2
        toggles['led_and_valves'] ^= toggles['L1'] << 1
        toggles['led_and_valves'] ^= toggles['R1']

        payload.append(toggles['led_and_valves'])

        # Checksum: XOR first 7 bytes
        payload.append(reduce(lambda x, y: x ^ y, payload[:7]))

        # Terminator byte
        payload.append(255)
        payload = struct.pack("9B", *payload)
        return payload

    def __del__(self):
        self._killswitch = True
        if self._serial_incoming_thread.is_alive():
            self._serial_incoming_thread.join()
        if self._serial_outgoing_thread.is_alive():
            self._serial_outgoing_thread.join()
