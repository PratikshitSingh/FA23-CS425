import time

def time_now():
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

def get_vm_dns():
    # DNS and port of 5 VMs
    servers = [
        ("localhost", 5000),
        ("localhost", 5001),
        ("localhost", 5002),
        ("localhost", 5003),
        ("localhost", 5004),
    ]
    return servers