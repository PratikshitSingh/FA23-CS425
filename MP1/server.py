import json
import socket
import subprocess
import threading

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from time import gmtime, strftime
from utils import time_now

FORMAT = "utf-8"

def handle_client(conn, addr):
    try:
        print(f"{time_now()} [NEW CLIENT] {addr} connected.")
        
        msg = conn.recv(1024).decode(FORMAT)
        if msg:
            query = json.loads(msg)
            filename = query.get("filename")
            command = query.get("command")
            grep_command = f"{command} {filename}"
            
            with open(filename, "rb") as file:
                try:
                    grep_list = grep_command.split()
                    response = subprocess.run(grep_list, capture_output=True)
                    print(response)
                    if response.returncode == 0:
                        conn.send(response.stdout)
                    else:
                        print(f"{time_now()} [ERROR] {response.stderr.decode(FORMAT)}")
                        error_message = "Error: not able to find suitable value"
                        conn.send(error_message.encode(FORMAT))
                except Exception as e:
                    print(f"{time_now()} [ERROR] {e}")
                    error_message = "Grepping error"
                    conn.send(error_message.encode(FORMAT))
    finally:
        conn.close()
        

def start_server():
    print(f"{time_now()} [STARTING] Server is starting...")
    # This server will listen to IPv4 clients over TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(5)
    
    print(f"{time_now()} [LISTENING] Server is listening on {SERVER}:{PORT}...")
    
    while True:
        conn, addr = server.accept()
        handle_client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        handle_client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        
        handle_client_thread.join()

if __name__ == "__main__":
    PORT = int(input("Enter the server port number: ").strip())
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    start_server()