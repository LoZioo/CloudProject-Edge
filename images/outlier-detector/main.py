from typing import Any
from copy import deepcopy

import paho.mqtt.client as mqtt
import json

# Containers names (addresses).
CONTAINER_OUTLIER_DETECTOR = "outlier-detector"
CONTAINER_HASHER = "hasher"

# Command topic.
MQTT_REQUEST_TOPIC = "/PowerMonitor"

# Telemetry topic.
MQTT_DATA_TOPIC = "/PowerMonitor/data"

# VA and W array.
SAMPLES_T = list[list[float]]
samples: SAMPLES_T = [[], []]

# App log.
from os import environ
from sys import stdout, stderr
from typing import TextIO

def log(message: Any, tag: str = "Info", file: TextIO = stdout, newline: bool = False) -> None:
	print("%s[%s] %s" % ("\n" if newline else "", tag, message), file=file)

# Functions
def samples_remove_peaks(samples: SAMPLES_T) -> SAMPLES_T:
	for i in range(len(samples)):
		samples[i].sort()
		samples[i] = samples[i][OUTLYING_SAMPLES_N:-OUTLYING_SAMPLES_N]

	log("Peaks removed.")
	return samples

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

def on_disconnect(client: Any, userdata: Any, rc: Any) -> None:
	log("Disconnected from %s." % MQTT_BROKER)

def on_subscribe(client: Any, userdata: Any, mid: Any, granted_qos: Any) -> None:
	log("Subscribed to the %s MQTT topic." % MQTT_DATA_TOPIC)

def on_message(client: Any, userdata: Any, message: mqtt.MQTTMessage) -> None:
	TOPIC = message.topic
	MESSAGE = message.payload.decode("utf-8")

	if TOPIC == MQTT_DATA_TOPIC:
		samples[0].append(json.loads(MESSAGE)["p"]["VA"])
		samples[1].append(json.loads(MESSAGE)["p"]["W"])

		if len(samples[0]) == SAMPLES_LEN_TOT:
			log("Reached pefixed len of %d samples." % SAMPLES_LEN, "Trigger")

			samples_copy = deepcopy(samples)
			for row in samples:
				row.clear()

			refined_samples = samples_remove_peaks(samples_copy)
			log(refined_samples)

# Graceful shutdown.
from signal import signal, SIGINT

def graceful_shutdown(signal: int, frame: Any) -> None:
	log("SIGINT detected, exiting...", newline=True)

	client.loop_stop()
	client.disconnect()

if __name__ == "__main__":
	log("I'm the outlier-detector!")

	# Attach callbacks.
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.on_subscribe = on_subscribe
	client.on_message = on_message

	signal(SIGINT, graceful_shutdown)

	# Retrive MQTT_BROKER envroiment variable.
	if "MQTT_BROKER" in environ:
		MQTT_BROKER = environ["MQTT_BROKER"]

	else:
		log("MQTT_BROKER envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Retrive OUTLYING_SAMPLES_N envroiment variable.
	if "OUTLYING_SAMPLES_N" in environ:
		OUTLYING_SAMPLES_N = int(environ["OUTLYING_SAMPLES_N"])

	else:
		log("OUTLYING_SAMPLES_N envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Retrive SAMPLES_LEN envroiment variable and set SAMPLES_LEN_TOT.
	if "SAMPLES_LEN" in environ:
		SAMPLES_LEN = int(environ["SAMPLES_LEN"])
		SAMPLES_LEN_TOT = SAMPLES_LEN + 2 * OUTLYING_SAMPLES_N

	else:
		log("SAMPLES_LEN envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Connect to the broker.
	log("Connecting to %s..." % MQTT_BROKER)
	try:
		client.connect(MQTT_BROKER)

	except Exception as e:
		log("Connection to %s failed: %s." % (MQTT_BROKER, e), "Error", stderr)
		log("Exiting...")
		exit(1)

	# Topic subscriprions.
	client.subscribe(MQTT_DATA_TOPIC)

	# Begin MQTT event loop.
	client.loop_forever()
