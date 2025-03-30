import json

from schema import Schema, Optional, Or

from ROV_CONSOLE.constants import CONFIG_FILE

CONFIG_SCHEMA = Schema(
    {
        Optional('tasks'):        list[str],
        Optional('main_camera'):  Or(None, str, int),
        Optional('left_camera'):  Or(None, str, int),
        Optional('right_camera'): Or(None, str, int),
        Optional('com_port'):     Or(None, str),
        }
    )


class Config:
    _DEFAULTS = {
        'tasks':        ['Task 1'],
        'main_camera':  0,
        'left_camera':  0,
        'right_camera': 0,
        'com_port':     None,
        }

    def __init__(self):
        self._json = Config._DEFAULTS
        try:
            with open(CONFIG_FILE) as f:
                buffer = json.load(f)
                if CONFIG_SCHEMA.is_valid(buffer):
                    self._json = CONFIG_SCHEMA.validate(buffer)
        except Exception:
            pass

    @property
    def tasks(self) -> list[str]:
        return self._json['tasks']

    @property
    def main_camera(self) -> int | str:
        return self._json['main_camera']

    @property
    def left_camera(self) -> int | str:
        return self._json['left_camera']

    @property
    def right_camera(self) -> int | str:
        return self._json['right_camera']

    @property
    def com_port(self) -> str | None:
        return self._json['com_port']

    def __del__(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self._json, f)
        except Exception as e:
            print(e)
