from typing import TypedDict, Any
from hashlib import sha256
from threading import Thread
from queue import Queue

import json

# RPC port.
RPC_PORT = 4090

# Same type of outlier-detector.
SAMPLES_T = list[list[float]]

# Cloud block.
class CLOUDBLOCK_T(TypedDict):
	VA:		list[float]
	W:		list[float]
	hash:	str

# App log.
from os import environ
from sys import stdout, stderr
from typing import TextIO

def log(message: Any, tag: str = "Info", file: TextIO = stdout, newline: bool = False) -> None:
	print("%s[%s] %s" % ("\n" if newline else "", tag, message), file=file)

# IPC
q: Queue[SAMPLES_T] = Queue()

# zerorpc server.
import zerorpc

class RPC_callbacks(object):
	def send_samples(self, samples: SAMPLES_T) -> bool:
		log("Samples received.")

		log("Sending samples through the queue.", "Trigger")
		q.put(samples)

		return True

# Threads.
def thread_RPC() -> None:
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

	# Retrive RPC_ADDRESS envroiment variable..
	if "RPC_ADDRESS" in environ:
		RPC_ADDRESS = environ["RPC_ADDRESS"]
		RPC_ENDPOINT = "tcp://%s:%d" % (RPC_ADDRESS, RPC_PORT)

	else:
		log("RPC_ADDRESS envroiment variable not set, exiting...", "Error", stderr)
		exit(1)

	# Run the RPC server (a daemon thread is killed when the main has been executed entirely).
	rpc_thread = Thread(target=thread_RPC, daemon=True)
	rpc_thread.start()

	# Await for samples from rpc_thread.
	while True:
		samples = q.get()

		log("Samples received through the queue.", "Trigger")
		log(samples)
