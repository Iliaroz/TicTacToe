# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 17:21:56 2022

@author: ilia
"""
import logging, sys, time

import serial
from serial.tools import list_ports


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger() # root logger
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler(sys.stdout)
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)
logger.debug('test debug message')


port = 'COM4'

ser = serial.Serial()
ser.port =     port
ser.baudrate=115200
ser.parity=serial.PARITY_NONE
ser.stopbits=serial.STOPBITS_ONE
ser.bytesize=serial.EIGHTBITS
ser.timeout=5

ser.open()
print( ser.isOpen() )
msg = bytearray.fromhex('AA AA 02 f0 01 0f')
#msg = bytearray.fromhex('aa aa 06 1f 01 00 00 00 00 e0')
print(msg)
ser.write(msg)
time.sleep(0.2)
rd = ser.read(6)
print(rd)
c = 0
while (c < 999):
    c += 1
    if ser.isOpen():
        input_data=ser.read(1).decode("utf-8")
        print(input_data, end='')
ser.close()