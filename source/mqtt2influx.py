import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from time import sleep
import sys

import datetime as dt
from types import FunctionType
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
import yaml
from message_processor import setRules, processMessage


# source_path = os.path.realpath(os.path.dirname(__file__))
source_path = Path(os.path.dirname(__file__))
config_path = source_path.parent/'config'
log_path = source_path.parent/'log'
Path.mkdir(log_path, exist_ok=True)

globalInflux: InfluxDBClient = None
mqtt_subscribed_topics = []

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(levelname)s - %(message)s")
logging.basicConfig(level=logging.INFO, format="%(asctime)s: %(levelname)s - %(message)s")

logger=logging.getLogger("mqtt2influx")

def prepareLogger():
    global logger
    today = dt.datetime.today()
    # filename = f'{today.year}{today.month:02d}{today.day:02d}.log'
    filename = log_path / 'mqtt2influx.log'
    filehandler = RotatingFileHandler(filename=filename, maxBytes=1000000, backupCount=10)
    filehandler.setFormatter(logging.Formatter("%(asctime)s: %(levelname)s - %(message)s"))
    filehandler.setLevel(logging.INFO)  # debug < info < warning < error < critical
    logger.addHandler(filehandler)

def writeProcessId(filename:str):
    outputFile = open(filename, "w")
    pid = str(os.getpid())
    outputFile.write(pid)
    outputFile.close()

def loadYaml(filename: str) -> dict:
    global logger
    logger.info(f"Loading yaml: {filename}")
    result = {}
    with open(filename, "r") as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return result

def connectToMqqt(config:dict)->mqtt.Client:
    global mqtt_subscribed_topics  
    global logger
    client = mqtt.Client("mqtt2influx")
    
    def on_connect(cl, userdata, flags, rc):
        logger.critical('MQTT SERVER CONNECTED')
        mqtt_subscribed_topics.clear()  # flush cashed subscriptions
        loadConfig(cl)  # making sure subscriptions are refreshed
    
    def on_disconnect(cl, userdata,rc=0):
        logger.critical('MQTT SERVER DISCONNECTED')

    logger.info("connecting to mqtt ...")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(username=config['user'], password=config['password'])
    returnCode = client.connect(config['host'], port=config['port'], keepalive=60, bind_address="")
    logger.info(f"mqtt connection return code: {returnCode}")
    return client

def connectToInflux(influxconfig:dict) -> InfluxDBClient:
    global logger
    logger.info("connecting to influx ...")
    client = InfluxDBClient(host=influxconfig['host'], port=influxconfig['port'])
    client.switch_database(influxconfig['database'])
    influxVersion = client.ping()
    logger.info(f"connected to influx {influxVersion}")
    return client

def doSubscriptions(client: mqtt.Client, subscriptionlist: list, handler: FunctionType):
    global mqtt_subscribed_topics
    logger.info(f"doing mqtt subscriptions ({len(subscriptionlist)}), chached ({len(mqtt_subscribed_topics)})")
    k = len(mqtt_subscribed_topics)
    
    # remove any unnecessary subscriptions
    while k>0:
        k-=1
        if not mqtt_subscribed_topics[k] in subscriptionlist:
            client.unsubscribe(mqtt_subscribed_topics[k])
            logger.debug(f"> unsubscribe from ({mqtt_subscribed_topics[k]})")
            del mqtt_subscribed_topics[k]
    
    # add any new subscriptions
    for subscription in subscriptionlist:
        if subscription not in mqtt_subscribed_topics:
            client.subscribe(subscription)
            logger.debug(f"> subscribe to ({subscription})")
            mqtt_subscribed_topics.append(subscription)

    client.on_message = handler

def loadConfig(client: mqtt.Client)->bool:
    global logger
    success=False
    config = loadYaml(filename=config_path/"mapping.yaml")
    if config == {}:
        logger.critical("CONFIG LOADING ERROR")
        return False

    if not isinstance(config['subscriptions'], list):
        logger.critical("CONFIG ERROR: no subscriptions")
        return False

    if not isinstance(config['rules'], list):
        logger.critical("CONFIG ERROR: no rules found")
        return False

    setRules(config['rules'])
    doSubscriptions(client, config['subscriptions'], handler=handleMqttMessage)
    return True

def handleMqttMessage(client: mqtt.Client, userdata: str, message: mqtt.MQTTMessage):
    global logger
    logger.debug(f"mqtt received topic: {message.topic}, payload: {message.payload}")
    datapoints = processMessage(message.topic, message.payload, logger=logger)
    if len(datapoints)==0:
        logger.debug(f"message received that did not match any regular expression. topic: {message.topic}")
    else:
        logger.info(f"writing({len(datapoints)}) {message.topic}")
        success = False
        try:
            success = globalInflux.write_points(datapoints)
        except InfluxDBClientError as e:
            
            logger.error(f"Influx Error {e}")
        if success:
            logger.debug('write to influx Success')
        else:
            logger.error(f'write to influx Failed datapoints: {datapoints}')


if __name__ == "__main__":
    prepareLogger()
    logger.critical("DEAMON START")
    writeProcessId('mqtt2influx.pid')

    if sys.version_info[0]<3:
        logger.critical("Python version 3 required")
        exit()

    serverconfig = loadYaml(filename=config_path/"serverconfig.yaml")
    client = connectToMqqt(config=serverconfig["mqtt"])

    globalInflux = connectToInflux(influxconfig=serverconfig["influx"])

    configFileTime = os.path.getmtime(config_path/"mapping.yaml")
    success = loadConfig(client)
    if not success:
        exit()

    logger.info("STARTING DEAMON LOOP")
    client.loop_start()  # starts the loop in seperate thread and takes care of reconnects if necessary
    while True:
        # client.loop() # replaced by loop_start in seperate thread, also dealing with reconnects.
        sleep(3)
        logger.debug('checking if mapping.yaml was updated')
        if configFileTime < os.path.getmtime(config_path/"mapping.yaml"):
            success = loadConfig(client)
            configFileTime = os.path.getmtime(config_path/"mapping.yaml")
            if success:
                logger.info('successfully reloaded the updated mapping.yaml file')
            else:
                logger.error('failed reloading the mapping.yaml file, sticking to the previous version.')
