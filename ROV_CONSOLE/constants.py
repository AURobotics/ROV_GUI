from pathlib import Path

# ASSETS
ASSETS_PATH = Path(__file__).resolve().parent / 'assets'
APP_ROOT_PATH = Path(__file__).resolve().parent.parent

CAMERA_ICONS = ASSETS_PATH / 'camera_widget'
APP_ICON = ASSETS_PATH / 'app' / 'appicon.ico'
TASKS_ICONS_PATH = ASSETS_PATH / 'tasks_widget'
CONFIG_FILE = APP_ROOT_PATH / 'config.json'
