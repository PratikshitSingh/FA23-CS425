import sys

import json
import socket
import threading

from collections import defaultdict
from time import gmtime, strftime

HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

GLOBAL_MESSAGES = defaultdict(list)
lock = threading.Lock()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    global GLOBAL_MESSAGES
    
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            with lock:
                GLOBAL_MESSAGES[str(addr[0]) + ":" + str(addr[1])].append(msg) # json.dumps can't serialize a tuple keys in a dictionary, to avoid raising TypeError
            print(f"[{addr}] : {msg}")
            
            conn.send(f"[MSG FROM SERVER] {strftime('%a, %d %b %Y %H:%M:%S', gmtime())} {json.dumps(GLOBAL_MESSAGES)}".encode(FORMAT))
            
    conn.close()

def start_server():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        
        # thread.join()
    

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("[STOPPING] Server is stopping due to keyboard interuption...")
        sys.exit()