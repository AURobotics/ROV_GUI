# ROV-GUI

## Description

This is the GUI for 2025's ROV, Giulietta. It allows the user to control the ROV and view the camera feeds and telemetry data. It also facilitates the execution of underwater missions.

## User Guide

### Controls

[placeholder]

### Steps to connect to Pi:

1. Connect to the Pi via SSH `ssh -o ServerAliveInterval=600 ubuntu@ubiquityrobot.local`
2. Enter password `ubuntu`
3. Start the cameras using `./ustreamer/ustreamer --device=/dev/videox --host=0.0.0.0 --port=808x` (change the port for
   each camera)
4. Connect to camera feeds from `http://192.168.1.2:808x/stream`
5. Start the virtual USB in a new terminal using `sudo ./vhusbdarm -b`
6. Connect to the virtual USB from the client

#### Extra Steps:

- To kill the cameras, use `killall ./ustreamer/ustreamer`

## Contributing

### Style Guidelines

[placeholder]

### Development Environment

This program is made to run on Python 3.11.x - 3.13.x

- Make sure to initialize the python venv using `python -m venv .venv` and activate it using `.venv\Scripts\activate` (
  Windows) or `source .venv/bin/activate` (Linux)
- To install the required packages, use `pip install -r requirements.txt`
- To run the program, use `python -m ROV_CONSOLE`

### Deployment

To deploy this project using `nuitka`, you should set up your project interpreter to be Python 3.12.x as `nuitka`
doesn't
support Python 3.13.x yet.

The compilation command is:

**Windows**

```shell
python -m nuitka .\ROV_CONSOLE\__main__.py --follow-imports --enable-plugin=pyside6 --output-dir=deployment --quiet --noinclude-qt-translations --onefile --noinclude-dlls=*.cpp.o --noinclude-dlls=*.qsb --windows-icon-from-ico=.\ROV_CONSOLE\assets\app\appicon.ico --include-qt-plugins=platforminputcontexts --include-data-dir=ROV_CONSOLE/assets=ROV_CONSOLE/assets --windows-console-mode=attach
```

Be sure to add `--msvc=latest` as an option if the MSVC compiler is present on your machine.
