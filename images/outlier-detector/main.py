from typing import Any
from copy import deepcopy
import json

# RPC port.
RPC_PORT = 4090

# Command topic.
MQTT_REQUEST_TOPIC = "/PowerMonitor"

# Telemetry topic.
MQTT_DATA_TOPIC = "/PowerMonitor/data"

# VA and W array.
SAMPLES_T = list[list[float]]
samples: SAMPLES_T = [[], []]

# Functions
def samples_remove_peaks(samples: SAMPLES_T) -> SAMPLES_T:
	for i in range(len(samples)):
		samples[i].sort()
		samples[i] = samples[i][OUTLYING_SAMPLES_N:-OUTLYING_SAMPLES_N]

	return samples

# App log.
from os import environ
from sys import stdout, stderr
from typing import TextIO

def log(message: Any, tag: str = "Info", file: TextIO = stdout, newline: bool = False) -> None:
	print("%s[%s] %s" % ("\n" if newline else "", tag, message), file=file)

# zerorpc client.
import zerorpc
rpc = zerorpc.Client()

# MQTT configurations (protocol can be also "websocket").
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client(
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
			log("Peaks removed; sending samples to hasher...")

			rpc.send_samples(refined_samples)
			log("Samples sent.")

# Graceful shutdown.
from signal import signal, SIGINT

def graceful_shutdown(signal: int, frame: Any) -> None:
	log("SIGINT detected, exiting...", newline=True)

	mqtt_client.loop_stop()
	mqtt_client.disconnect()

	rpc.close()

if __name__ == "__main__":
	log("I'm the outlier-detector!")

	# Attach callbacks.
	mqtt_client.on_connect = on_connect
	mqtt_client.on_disconnect = on_disconnect
	mqtt_client.on_subscribe = on_subscribe
	mqtt_client.on_message = on_message

	signal(SIGINT, graceful_shutdown)

	# Retrive MQTT_BROKER envroiment variable.
	if "MQTT_BROKER" in environ:
		MQTT_BROKER = environ["MQTT_BROKER"]

	else:
		log("MQTT_BROKER envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Retrive RPC_ADDRESS envroiment variable.
	if "RPC_ADDRESS" in environ:
		RPC_ADDRESS = environ["RPC_ADDRESS"]
		RPC_ENDPOINT = "tcp://%s:%d" % (RPC_ADDRESS, RPC_PORT)

	else:
		log("RPC_ADDRESS envroiment variable not set, exiting...", "Error", stderr)
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

	# Connect to the RPC server.
	log("RPC endpoint set to \"%s\"." % RPC_ENDPOINT)
	rpc.connect(RPC_ENDPOINT)

	# Connect to the broker.
	log("Connecting to %s..." % MQTT_BROKER)
	try:
		mqtt_client.connect(MQTT_BROKER)

	except Exception as e:
		log("Connection to %s failed: %s." % (MQTT_BROKER, e), "Error", stderr)
		log("Exiting...")
		exit(1)

	# Topic subscriprions.
	mqtt_client.subscribe(MQTT_DATA_TOPIC)

	# Begin MQTT event loop.
	mqtt_client.loop_forever()
