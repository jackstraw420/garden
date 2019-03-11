
"""
Configuration module. Loads configuration settings from local file, server, updates listeners.
"""
####### Logging #######
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

####### Imports #######
import json

####### Members #######
configFilename = '/etc/garden.conf'
listeners = []
global config
config = {}
global lastVersion
lastVersion = "--"

####### Member Functions #######
"""
Initialize the configuration. Reads from local file, then from server if available.
"""
def initialize():
    logger.debug("Initializing..")
    readConfigFile()
    readServerConfig()

def registerListener(listener):
    listeners.append(listener)

def readConfigFile(filename = configFilename):
    global config
    logger.debug('readConfigFile: Opening configuration file %(file)s' % {'file': configFilename})
    with open(filename) as configFile:
        config = json.load(configFile)

def writeConfigFile(filename = configFilename): 
    global config
    lastVersion = config["version"]
    logger.debug('writeConfigFile: Opening configuration file %(file)s' % {'file': configFilename})
    if not filename:
        filename = configFilename
    with open(filename, 'w') as configFile:
        json.dump(config, configFile, indent=4)

"""
Read the configuration from the server. If it is new and marked override, save it to file.
"""
def readServerConfig():
    global config
    if config is not None:
        if "server" in config.keys():
            logger.debug('readServerConfig: Reading Server Configuration From Server %(name)s:%(port)s' % config["server"])
            try:
                newConfig = config
                if newConfig["version"] != config["version"]: #TODO: check latest
                    config = newConfig
                    writeConfigFile()

                for listener in listeners:
                    listener.configUpdate()
                return
            except Exception:
                logger.error("readServerConfig: Error reading config from server.", exc_info=True)
    logger.debug('readServerConfig: No server config available.')

def getConfig():
    global configs
    return config

if __name__ == "__main__":
    pass
