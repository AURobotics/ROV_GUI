import serial
import struct
import time
import random
import pygame

def xor(byte_list: list[int]) -> int:
    result = byte_list.pop(0)
    for byte in byte_list:
        result ^= byte
    return result

pygame.init()
gp = pygame.joystick.Joystick(0)

ser = serial.Serial('COM10')
while True:
    time.sleep(1)
    if ser.in_waiting:
        print(ser.readline())
    l = [int(254 * gp.get_button(x)) for x in range(8)]
    l.insert(0, 255)
    l.append(0b10101010) # directions
    l.append(0b10101010) # leds
    l.append(xor(l[1:8]))
    print(l)
    ser.write(struct.pack("12B", *l))
    for event in pygame.event.get():
        """Must consume events"""
        pass