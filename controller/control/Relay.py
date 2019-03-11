
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/%s.log' % __name__,maxBytes=1000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')

from configuration import Configuration
from control import FTDIRelayController
from remote import APIController
from control import SHTSensor
import sys
import time
import asyncio

global configUpdateLock
configUpdateLock = False

global relayState
relayState = 0

global relays
relays = []

global relayRules
relayRules = {}

def generateRelay(relayConfig, rulesConfig, duration):
    id = relayConfig["id"]
    rules = []
    try:
        for rule in relayConfig["rules"]:
            for ruleConfig in rulesConfig:
                if rule == ruleConfig:
                    rules.append(rule)
    except:
        logger.error('Error parsing relay configuration', exc_info=True)
    logger.debug('generateRelay: Generating Relay %(relayid)s with %(rules)s rules' % {"relayid":id, "rules": len(rules)})
    logger.debug('generateRelay: Generating Relay %s' % id)
    return Relay(id, rules, duration)


def getRuleData(id):
    global relayRules
    return relayRules[id]


class RelayRule:
    def __init__(self, rule):
        self.rule = rule
        self.otherRules = []
        if "and" in self.rule.keys():
            self.otherRules = self.rule["and"]

    def getRuleData(self):
        return getRuleData(self.rule["id"])

    def checkSubRules(self, relay):
        for rule in self.otherRules:
            if getRuleData(rule).checkRule(relay) is not True:
                return False
        return True
        
    def checkRule(self, relay):
        if self.checkSubRules(relay) is not True:
            return False
        rule = self.getRuleData().rule["rule"]
        subject = rule["subject"]
        predicate = rule["predicate"]
        obj = rule["object"]
        if subject == "LAST_OPEN":
            return self.checkLastOpen(relay, predicate, obj)
        if subject == "HUMIDITY":
            retVal = self.checkHumidity(relay, predicate, obj)
            if retVal is True:
                print("humidityTriggered")
            return retVal
        if subject == "TEMPERATURE":
            retVal = self.checkTemperature(relay, predicate, obj)
            if retVal is True:
                print("tempTriggered")
            return retVal

    def checkLastOpen(self, relay, predicate, obj):
        timenow = time.time()*1000.0
        lastOpen = timenow - relay.lastOpen
        if predicate == "GREATER_OR_EQUAL":
            return lastOpen >= obj
        if predicate == "LESS_OR_EQUAL":
            return lastOpen <= obj
        pass

    def checkHumidity(self, relay, predicate, obj):
        humidity = SHTSensor.getHumidity()
        if humidity is None:
            return False
        if predicate == "GREATER_OR_EQUAL":
            return humidity >= obj
        if predicate == "LESS_OR_EQUAL":
            return humidity <= obj
        pass
    
    def checkTemperature(self, relay, predicate, obj):
        temperature = SHTSensor.getTemperature()
        if temperature is None:
            return False
        if predicate == "GREATER_OR_EQUAL":
            return temperature >= obj
        if predicate == "LESS_OR_EQUAL":
            return temperature <= obj
        pass
        
class Relay:
    def __init__(self, id, rules, duration):
        self.id = id
        self.rules = rules
        self.lastOpen = 0
        self.state = 0
        self.duration = duration

    def checkKeepOpen(self):
        timenow = time.time()*1000.0
        timeSinceOpen = timenow - self.lastOpen
        if timeSinceOpen <= self.duration:
            return True
        return False

    def checkTrigger(self):
        if self.state == 1:
            if self.checkKeepOpen() is True:
                return True
            logger.debug('Close open relay %s' % self.id)
            return False

        for rule in self.rules:
            ruleCheck = getRuleData(rule).checkRule(self)
            if ruleCheck is True:
                self.lastOpen = time.time()*1000.0
                return True
        return False

    def openRelay(self):
        logger.debug('Open relay %s' % self.id)
        self.state = 1

    def closeRelay(self):
        self.state = 0

    def getState(self):
        return self.state




def initialize():
    logger.debug('Initializing relay')
    Configuration.registerListener(sys.modules[__name__])
    createRelays(Configuration.getConfig())

def checkRelays():
    try:
        global relays
        global relayState
        newRelayState = 0
        for relay in relays:
            if relay.checkTrigger():
                relay.openRelay()
                newRelayState += 1 << relay.id
            else:
                relay.closeRelay()
        if newRelayState != relayState:
            relayState = newRelayState
            FTDIRelayController.setFTDIDeviceData(relayState)
            APIController.writeChange(relayState)
    finally:
        pass


def createRelays(config):
    global relays
    relays = []
    global relayRules
    relayRules = {}
    if "relays" in config.keys():
        if "rules" in config.keys():
            duration = config["duration"]
            for ruleConfig in config["rules"]:
                relayRule = RelayRule(ruleConfig)
                relayRules[ruleConfig["id"]] = relayRule

            for relayConfig in config["relays"]:
                relay = generateRelay(relayConfig, relayConfig["rules"], duration)
                relays.append(relay)
    pass

def configUpdate():
    createRelays(Configuration.getConfig())
    logger.debug('Config Update')
