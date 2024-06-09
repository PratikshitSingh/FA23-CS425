#!/usr/bin/python3
import json
import socket
import threading
import time
import random
import logging

HOST_NAME_LIST = [
    "fa23-cs425-8001.cs.illinois.edu",
    "fa23-cs425-8002.cs.illinois.edu",
    "fa23-cs425-8003.cs.illinois.edu",
    "fa23-cs425-8004.cs.illinois.edu",
    "fa23-cs425-8005.cs.illinois.edu",
    "fa23-cs425-8006.cs.illinois.edu",
    "fa23-cs425-8007.cs.illinois.edu",
    "fa23-cs425-8008.cs.illinois.edu",
    "fa23-cs425-8009.cs.illinois.edu",
    "fa23-cs425-8010.cs.illinois.edu",
]
# 'Introducor' specifies the introducer node's hostname, which plays a crucial role in system coordination.
Introducor = "fa23-cs425-8002.cs.illinois.edu"

# 'DEFAULT_PORT_NUM' defines the default port number used for communication within the system.
DEFAULT_PORT_NUM = 12360

lock = threading.RLock


# Configure logging for the script. This sets up a logging system that records debug information
# to the 'output.log' file, including timestamps and log levels.
logging.basicConfig(
    level=logging.DEBUG,
    filename="output.log",
    datefmt="%Y/%m/%d %H:%M:%S",
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# The `Server` class represents a node in a distributed system.
class Server:
    def __init__(self, *args):
        self.ip = socket.gethostname()
        self.port = DEFAULT_PORT_NUM
        self.heartbeat = 0
        self.timejoin = int(time.time())
        self.id = f"{self.ip}:{self.port}:{self.timejoin}"
        self.addr = (self.ip, self.port)

        self.fail_threshold = 5
        self.clean_threshold = 5

        self.membership_list = {
            self.id: {
                "id": self.id,
                "address": (self.ip, self.port),
                "heartbeat": self.heartbeat,
                "incarnation": 0,
                "status": "alive",
                "time": time.time(),
            }
        }

    def start(self):
        # use UDP connection as it is cheaper than TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.address, self.port))
        threading.Thread(target=self.receive_hearbeat()).start()
        threading.Thread(target=self.send_heartbeat()).start()

    def receive_hearbeat(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            message = json.loads(data.decode())
            self.process_message(message, addr)

    def process_message(self, message, addr):
        node_id = message["id"]

        if message["type"] == "heartbeat":
            self.update_membership_list(node_id, addr)
        elif message["type"] == "join":
            self.join_group(node_id, message)
        elif message["type"] == "leave":
            self.leave_group(node_id, message)
        else:
            print(f"Unknown message type: {message['type']}")

    def update_membership_list(self, node_id, addr):
        if not self.membership_list.get(node_id):
            self.membership_list[node_id] = {
                "address": addr[0],
                "port": addr[1],
            }
            print(f"Updated membership list: {self.membership_list}")

    def join_group(self, introducer_address, introducer_port):
        self.membership_list[self.id] = {"address": self.address, "port": self.port}
        self.socket.sendto(
            json.dumps({"type": "join", "id": self.id}).encode(),
            (introducer_address, introducer_port),
        )

    def leave_group(self):
        message = json.dumps({"type": "leave", "id": self.id}).encode()
        for node in self.membership_list:
            self.socket.sendto(message, (node["address"], node["port"]))
        self.membership_list.clear()

    def send_heartbeat(self):
        # Send membership table to a random peer every 5 seconds as Gossip
        while True:
            if self.membership_list:
                while True:
                    peer = random.choice(self.membership_list)
                    # send heartbeat to a random peer, but not to self
                    if peer["id"] != self.id:
                        message = {"id": self.id, "type": "heartbeat"}
                        self.socket.sendto(
                            json.dumps(message).encode(),
                            (peer["address"], peer["port"]),
                        )
                        break

            time.sleep(5)  # Adjust as necessary for heartbeat frequency

    def run():
        PORT = int(input("Enter the server port number: ").strip())
        SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = (SERVER, PORT)

        print(f"[STARTING] Server is starting at {ADDR}...")


if __name__ == "__main__":
    server = Server()
    server.run()
