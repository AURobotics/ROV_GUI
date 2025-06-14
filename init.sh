#!/bin/sh
# Startup script for the Raspberry PI

ip addr add 192.168.1.2/24 dev eth0
ip route add default via 192.168.1.1
killall ./ustreamer/ustreamer
sleep 1
./ustreamer/ustreamer --device=/dev/video0 --host=0.0.0.0 --port=8080 -m MJPEG &
./ustreamer/ustreamer --device=/dev/video2 --host=0.0.0.0 --port=8082 -m MJPEG &
./ustreamer/ustreamer --device=/dev/video4 --host=0.0.0.0 --port=8084 -m MJPEG &
sudo ./vhusbdarm -b