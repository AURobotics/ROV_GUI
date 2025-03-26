from pathlib import Path

# ASSETS
ASSETS_PATH = Path(__file__).resolve().parent / 'assets'
DS4_ICONS_PATHS = [fp for fp in (ASSETS_PATH / 'ds4icons').iterdir()]
NOVIDEO_PICTURE_PATH = ASSETS_PATH / 'novideo.png'
APP_ICON = ASSETS_PATH / 'appicon.png'
