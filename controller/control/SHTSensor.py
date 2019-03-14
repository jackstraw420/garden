
"""
Interface for SHT1x sensor.
"""

import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
global logger
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.ERROR,format='%(asctime)s %(message)s')

#from pi_sht1x import SHT1x
#from RPi import GPIO

def getReading(_data=17, _sck=27):
    """
    Gets the data reading from a SHT1x sensor.

    :param _data: Optional parameter defining GPIO pin for the data wire from the sensor. Default: 17
    :param _skc: Optional parameter defining GPIO pin for sck wire from the sensor. Default: 27
    :return: Object with the following keys/datapoints: humidity, temperature
    """
    global logger
    if True:
        return None
    with SHT1x(_data, _sck, gpio_mode=GPIO.BCM, logger=logger) as sensor:
        return {
            'humidity': sensor.read_humidity(sensor.read_temperature()),
            'temperature': ((sensor.read_temperature() * (9.0) / (5.0)) + 32.0)
        }
    return None


if __name__ == "__main__":
    print(getReading())
    pass
