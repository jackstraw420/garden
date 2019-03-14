
"""
Interface for FTDI bitbang device.
"""

import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

from pylibftdi import BitBangDevice
import subprocess

def setFTDIDeviceDataForked(value):
    """
    Write the bitbang value to the device.

    :param value: integer representing bitbang value
    :return: Returns nothing.
    """
    with BitBangDevice() as ftdiDevice:
        ftdiDevice.baudrate=921600
        ftdiDevice.write(int(value))

def setFTDIDeviceData(value):
    """
    Write the bitbang value to the device.

    :param value: integer representing bitbang value
    :return: Returns nothing.
    """
    import json
    stdout = None
    try:
        output = subprocess.check_output(["python",__file__,'--value', str(value)])
        data = json.load(output)
        return data
    except subprocess.CalledProcessError:
        logger.error("setFTDIDeviceData: Error changing relay state.", exc_info=True)
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Interact with SHT1x Sensor')
    parser.add_argument('--value', dest='value', required=True)
    args = parser.parse_args()
    setFTDIDeviceDataForked(args.value)