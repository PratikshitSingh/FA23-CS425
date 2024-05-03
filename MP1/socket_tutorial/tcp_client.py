"""
 Client should ping server in every 10 sec to pull latest messages, when not sending any message
"""
import time
import socket
import sys

import threading

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send_message(msg):
    message = msg.encode(FORMAT)
    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b' '* (HEADER - len(send_len))
    client.send(send_len)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

def ping_server():
    while True:
        time.sleep(5)
        send_message("PING")

def message_server():
    while True:
        message = input().strip()
        if message:
            send_message(message)
            if message == DISCONNECT_MESSAGE:
                # Sleep for 2 seconds to allow the server to send the last message
                time.sleep(2)
                # exiting the client
                client.close()
                break


if __name__ == "__main__":
    ping_thread = threading.Thread(target=ping_server)
    ping_thread.daemon = True
    ping_thread.start()
    
    message_thread = threading.Thread(target=message_server)
    message_thread.start()
    
    try:
        message_thread.join()
        print("Client is exiting because of DISCONNECT MESSAGE.")
    except KeyboardInterrupt:
        print("KeyboardInterrupt, exiting the main thread.")
        client.close()
        sys.exit()