
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.ERROR,format='%(asctime)s %(message)s')

from pi_sht1x import SHT1x
from RPi import GPIO

import time

global _data
global _sck
_data = 17
_sck = 27

def getTemperature():
    global _data
    global _sck
    with SHT1x(_data, _sck, gpio_mode=GPIO.BCM) as sensor:
        return ((sensor.read_temperature() * (9.0) / (5.0)) + 32.0)
    return None

def getHumidity():
    global _data
    global _sck
    with SHT1x(_data, _sck, gpio_mode=GPIO.BCM) as sensor:
        return sensor.read_humidity(sensor.read_temperature())
    return None

if __name__ == "__main__":
    print(getTemperature())
    print(" ")
    print(getHumidity())