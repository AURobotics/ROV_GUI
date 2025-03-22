# ROV-GUI

## Steps to connect to Pi:

1. Connect to the Pi via SSH `ssh -o ServerAliveInterval=600 ubuntu@ubiquityrobot.local`
2. Enter password `ubuntu`
3. Start the cameras using `./ustreamer/ustreamer --device=/dev/video0 --host=0.0.0.0 --port=808x` (change the port for each camera)
4. Connect to camera feed from `192.168.1.2:808x`
5. Start the virtual USB in a new terminal using `sudo ./vhusbdarm -b`
6. Connect to the virtual USB from the client

Extra Steps:

- To kill the cameras, use `killall ./ustreamer/ustreamer`
- Make sure to initialize the python venv using `python -m venv .venv` and activate it using `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux)
- To install the required packages, use `pip install -r requirements.txt`
