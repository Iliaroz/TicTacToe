# -*- coding: utf-8 -*-
"""
@author: ilia
"""

from serial.tools import list_ports
import sys
import logging
from pydobot import Dobot

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger() # root logger
logger.setLevel(level=logging.DEBUG)
fh = logging.StreamHandler(sys.stdout)
fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
fh.setFormatter(fh_formatter)
logger.addHandler(fh)
logger2 = logging.getLogger("pydobot")
logger2.disabled = False
logger.debug('test debug message')


ports = list_ports.comports()
port = ports[0].device
print("Port:", port)
logger.debug(f'test debug message 2 : used port is {port}')
device = Dobot()

#device.home()
pose = device.get_pose()
print(pose)
position = pose.position

device.move_to(position.x + 20, position.y, position.z, position.r)
device.move_to(position.x, position.y, position.z, position.r)  # we wait until this movement is done before continuing

device.close()
