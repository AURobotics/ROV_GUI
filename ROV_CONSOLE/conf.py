import json

from schema import Schema, Optional, Or, And

from ROV_CONSOLE.paths import CONFIG_FILE

_TASK_TREE = Schema({
    'name':            And(str, len),
    Optional('tasks'): [Or(
        And(str, len),
        lambda task: _TASK_TREE.validate(task)
        )],
    })

_CAMERA = Schema({
    'descriptor':       Or(None, And(str, len), int),
    'initial_rotation': Or(None, int)
    })

CONFIG_SCHEMA = Schema(
    {
        Optional('tasks'):        [Or(And(str, len), _TASK_TREE)],
        Optional('main_camera'):  _CAMERA,
        Optional('left_camera'):  _CAMERA,
        Optional('right_camera'): _CAMERA,
        Optional('com_port'):     Or(None, And(str, len)),
        }
    )


class Config:
    _DEFAULTS = {
        'tasks':        ['Task 1'],
        'main_camera':  {'descriptor': 0, 'initial_rotation': 0},
        'left_camera':  {'descriptor': 0, 'initial_rotation': 0},
        'right_camera': {'descriptor': 0, 'initial_rotation': 0},
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

        for key in Config._DEFAULTS:
            if key not in self._json:
                self._json[key] = Config._DEFAULTS[key]

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
