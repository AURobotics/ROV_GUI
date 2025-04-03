import sys
from pathlib import Path

# ASSETS
ASSETS_PATH = Path(__file__).resolve().parent / 'assets'

CAMERA_ICONS = ASSETS_PATH / 'camera_widget'
APP_ICON = ASSETS_PATH / 'app' / 'appicon.ico'
TASKS_ICONS_PATH = ASSETS_PATH / 'tasks_widget'
if getattr(sys, "frozen", False):
    CONFIG_FILE = Path('config.json')
    PANO_SAVE = Path('pano/')
else:
    CONFIG_FILE = Path(__file__).resolve().parent.parent / 'config.json'
    PANO_SAVE = Path(__file__).resolve().parent.parent / 'pano/'

PANO_SAVE.mkdir(parents=True, exist_ok=True)
