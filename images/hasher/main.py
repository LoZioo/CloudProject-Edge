from typing import TypedDict, Any
from datetime import datetime, timezone
from hashlib import sha256

import json

# RPC port.
RPC_PORT = 4090

# Same type of outlier-detector.
samples_t = list[list[float]]

# Cloud block.
class cloudblock_t(TypedDict):
	VA:					list[float]
	W:					list[float]

	timestamp:	str
	hash:				str

# App log.
from os import environ
from sys import stdout, stderr
from typing import TextIO

def log(message: Any, tag: str = "Info", file: TextIO = stdout, newline: bool = False) -> None:
	print("%s[%s] %s" % ("\n" if newline else "", tag, message), file=file)

# IPC
from queue import Queue

q: Queue[samples_t] = Queue()

# zerorpc server.
import zerorpc

class RPC_callbacks(object):
	def send_samples(self, samples: samples_t) -> bool:
		log("Samples received.")

		log("Sending samples through the queue.", "Trigger")
		q.put(samples)

		return True

# Threads.
from threading import Thread

def thread_RPC_receiver() -> None:
	log("RPC server listening on %s." % RPC_ENDPOINT)

	rpc = zerorpc.Server(RPC_callbacks())
	rpc.bind(RPC_ENDPOINT)
	rpc.run()

# Graceful shutdown.
from signal import signal, SIGINT

def graceful_shutdown(signal: int, frame: Any) -> None:
	log("SIGINT detected, exiting...", newline=True)
	exit(0)

if __name__ == "__main__":
	log("I'm the hasher!")

	# Attach the graceful shutdown callback.
	signal(SIGINT, graceful_shutdown)

	# Retrive RPC_ADDRESS envroiment variable.
	if "RPC_ADDRESS" in environ:
		RPC_ADDRESS = environ["RPC_ADDRESS"]
		RPC_ENDPOINT = "tcp://%s:%d" % (RPC_ADDRESS, RPC_PORT)

	else:
		log("RPC_ADDRESS envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Retrive DB_FILE envroiment variable.
	if "DB_FILE" in environ:
		DB_FILE = environ["DB_FILE"]

	else:
		log("DB_FILE envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Run the RPC server (a daemon thread is killed when the main has been executed entirely).
	rpc_thread = Thread(target=thread_RPC_receiver, daemon=True)
	rpc_thread.start()

	# Await for samples from rpc_thread.
	while True:
		samples = q.get()
		log("Samples received through the queue.", "Trigger")

		block: cloudblock_t = {
			"VA":	samples[0],
			"W":	samples[1],

			# Timestamp in UTC (Zulu) ISO 8601.
			"timestamp":	datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),

			# Hash is computed by initially evaluating the empty string.
			"hash":	""
		}

		block["hash"] = sha256(json.dumps(block).encode("utf-8")).hexdigest()
		hashed_block = json.dumps(block)

		log("Saving the resulted block.")
		with open(DB_FILE, "a") as db:
			db.write("%s\n" % block["hash"])
