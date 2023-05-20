from typing import Any
import paho.mqtt.client as mqtt

# App log.
from os import environ
from sys import stdout, stderr
from typing import TextIO

def log(message: str, file: TextIO = stdout, newline: bool = False) -> None:
	HOSTNAME = environ["HOSTNAME"] if "HOSTNAME" in environ else "Log"

	print("%s[%s] %s" % ("\n" if newline else "", HOSTNAME, message), file=file)

# Protocol can be also "websocket".
client = mqtt.Client(
	client_id = "outlier-detector",
	transport = "tcp",
	protocol = mqtt.MQTTv311,
	clean_session = True
)

# MQTT Callbacks.
def on_connect(client: Any, userdata: Any, flags: Any, rc: Any) -> None:
	log("Connected to %s!" % MQTT_BROKER)

def on_disconnect(client: Any, userdata: Any, flags: Any) -> None:
	log("Disconnected from %s." % MQTT_BROKER)

# Graceful shutdown.
from signal import signal, SIGINT

def graceful_shutdown(signal: int, frame: Any) -> None:
	log("SIGINT detected, exiting...", stdout, True)

	client.loop_stop()
	client.disconnect()

if __name__ == "__main__":
	log("I'm the outlier-detector!")

	# Attach callbacks.
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect

	signal(SIGINT, graceful_shutdown)

	# Retrive MQTT_BROKER envroiment variable.
	if "MQTT_BROKER" in environ:
		MQTT_BROKER = environ["MQTT_BROKER"]
	
	else:
		log("MQTT_BROKER envroiment variable not set, aborting.", stderr)
		exit(1)

	# Connect to the broker.
	log("Connecting to %s..." % MQTT_BROKER)
	try:
		client.connect(MQTT_BROKER)

	except Exception as e:
		log("Connection to %s failed: %s." % (MQTT_BROKER, e), stderr)
		exit(1)

	# Begin MQTT event loop.
	client.loop_forever()
