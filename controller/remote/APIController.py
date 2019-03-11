####### Logging #######
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')


def writeChange(state):
    pass