
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

def initialize():
    """
    Initialize the configuration. Reads from local file, then from server if available.
    """
    logger.debug("Initializing..")
    readConfigFile()
    readServerConfig()

def registerListener(listener):
    """
    Register a configuration listener

    :param listener: Object with a configUpdate() function that can take zero arguments
    :return: returns nothing
    """
    listeners.append(listener)

def readConfigFile(filename = configFilename):
    """
    Reads the configuration file and loads it into memory.

    :param filename: Configuration filename (probably just /etc/garden.conf)
    :return: returns nothing
    """
    global config
    logger.debug('readConfigFile: Opening configuration file %(file)s' % {'file': configFilename})
    with open(filename) as configFile:
        config = json.load(configFile)

def writeConfigFile(filename = configFilename): 
    """
    Writes the configuration to file

    :param filename: Configuration filename (probably just /etc/garden.conf)
    :return: returns nothing
    """
    global config
    lastVersion = config["version"]
    logger.debug('writeConfigFile: Opening configuration file %(file)s' % {'file': configFilename})
    if not filename:
        filename = configFilename
    with open(filename, 'w') as configFile:
        json.dump(config, configFile, indent=4)


def readServerConfig():
    """
    Read the configuration from the server. If it is new and marked override, save it to file.
    """
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
    """
    Get the configuration data
    :return: returns the global configuration variable
    """
    global configs
    return config

if __name__ == "__main__":
    #TODO: test code
    pass
