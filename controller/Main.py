"""
Main controller. Initializes relay, config check daemons.
"""


####### Logging #######
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

####### Import #######

from configuration import Configuration
from control import Relay
import asyncio

global relayDelay
relayDelay = 0.1 # check relay status every second
global configDelay
configDelay = 60 # check configuration updates every minute

####### Daemon Methods #######
async def configurationLoop():
    """
    Configuration loop function
    """
    global configDelay
    while True:
        print("config loop")
        await asyncio.sleep(configDelay)

async def relayLoop():
    """
    Relay state check loop function
    """
    global relayDelay
    while True:
        try:
            Relay.checkRelays()
        except:
            logger.error("Main: uncaught exception", exc_info=True)
        await asyncio.sleep(relayDelay)

def initializeLoops():
    """
    Initialize the daemon loops.
    """
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(configurationLoop())
        asyncio.ensure_future(relayLoop())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error("initializeLoops: Error starting configuration loop.", exc_info=True)
    finally:
        print("Closing Loop")
        loop.close()  

if __name__ == "__main__":
    Configuration.initialize()    
    Relay.initialize()                                  
    initializeLoops()