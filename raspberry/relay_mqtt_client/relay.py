import gpiozero
from paho.mqtt import client as mqtt_client
import logging
import sys
import tomllib
import json
from systemd.journal import JournalHandler

# https://github.com/systemd/python-systemd?tab=readme-ov-file  Install using apt install python3-systemd
# It works on ArchLinux

# Run with GPIOZERO_PIN_FACTORY=mock for development

# https://webscrapingsite.com/resources/python-script-service-guide/

# Logging to systemd journal
log = logging.getLogger()
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

# Load configuration
try:
    file = open("config.toml", "rb")
except Exception:
    logging.error("Can't open config file", exc_info=True)
    exit(1)
else:
    with file:
        config = tomllib.load(file)

logging.info("Configuration loaded!")

# Check the GPIO pinout guide here https://pinout.xyz
RELAY_PIN = config["gpio"]["pin"]

# Load mqtt broker config
broker = config["mqtt"]["broker"]
mqtt_port = config["mqtt"]["port"]
client_id = config["mqtt"]["client"]
to_scooter_topic = config["mqtt"]["to_scooter_topic"]
to_server_topic = config["mqtt"]["to_server_topic"]

# Relays have different modes https://engineerfix.com/electrical/circuits/normally-open-vs-normally-closed-what-do-they-mean/
# Normally Closed => Closed by default
# Normally Open => Open by default

# For development use Normally Closed: As it allows the scooter to turn on even when the RPI is down

# Triggered by the output pin going high: active_high=True
# Initially off: initial_value=False
# Initilize the relay
relay = gpiozero.OutputDevice(RELAY_PIN, active_high=False, initial_value=False)

# Setup and connect to the MQTT broker


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logging.info("Connected to MQTT Broker!")
        client.subscribe(to_scooter_topic, 1)
    else:
        logging.exception("Failed to connect, return code %d\n", reason_code)


def on_control_message(client, userdata, msg):

    logging.info("Control message received")

    """
        Example payload

        {
            "status": "open"
        }
    """
    # Prepare the response
    response = {
        "response": {
            "result": False,
            "status": "unknown",
            "reason": "",
        }
    }

    message = msg.payload.decode()
    data = json.loads(message)

    logging.info(f"Received {data}")

    logging.info(data["status"])

    try:
        if data["status"] == "query":
            response["response"]["result"] = True
            response["response"]["status"] = "open" if relay.value else "close"

        elif data["status"] == "open":
            relay.on()
            if relay.value == 1:
                response["response"]["result"] = True
                response["response"]["status"] = "open"
        else:
            relay.off()
            if relay.value == 0:
                response["response"]["result"] = True
                response["response"]["status"] = "close"

    except Exception as e:
        logging.error("Error occurred while handling the relay: %s", str(e))
        response["response"]["reason"] = str(e)

    logging.info(f"Sending response {response}")
    client.publish(to_server_topic, json.dumps(response), 1)


#  Create the MQTT client
client = mqtt_client.Client(
    mqtt_client.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt_client.MQTTv5
)
client.on_connect = on_connect

# This filters the message action only to the desired topic
client.message_callback_add(to_scooter_topic, on_control_message)

# Connect to the broker
client.connect(broker, mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.

# In this case I use a blocking loop because listening to messages is the only purpose of this Python script

client.loop_forever()
