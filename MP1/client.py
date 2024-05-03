import json
import socket
from concurrent.futures import ProcessPoolExecutor

from utils import time_now, get_vm_dns

FORMAT = "utf-8"
# server_details = [
#     (socket.gethostbyname(dns), port, "machine.i.log") for dns, port in get_vm_dns()
# ]
server_details = [
    ("192.168.64.2", 5000, "machine.i.log"),
    ("192.168.64.3", 5000, "machine.i.log")
]

def get_logs(server, pattern, index):
    ip, port, filename = server
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        print(2, client, ip, port, filename)
    except Exception as e:
        print(f"{time_now()} [ERROR] Error connecting to VM {index + 1} at {ip}:{port}")
        return
    
    query = {}
    # query["command"] = r"grep -c \([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"
    query["command"] = f"grep -c {pattern}"
    query["filename"] = filename
    print()
    
    try:
        client.send(json.dumps(query).encode(FORMAT))
        response = client.recv(1024).decode(FORMAT)
        print(f"{time_now()} VM {index+1} : {response}")
        
        client.close()
    except Exception as e:
        print(f"{time_now()} [ERROR] Error in getting logs from VM {index + 1} at {ip}:{port}")
        client.close()
    

if __name__ == "__main__":
    pattern = input("Enter the pattern to search in logs: ")
    with ProcessPoolExecutor() as executor:
        for index, server in enumerate(server_details):
            executor.submit(get_logs, server, pattern, index)