# yourlib/wrapper.py
import subprocess
import sys
import time
import socket
from multiprocessing.connection import Client

HOST = '127.0.0.1'
PORT = 59677
AUTHKEY = b'secret'

def is_backend_running():
    try:
        # test = Client((HOST, PORT), authkey=AUTHKEY)
        # test.close()
        with socket.create_connection((HOST, PORT), timeout=0.2) as s:
           return True
    except OSError:
        return False

def start_backend():
    print("[wrapper] Starting backend...")
    subprocess.Popen([sys.executable, '-m', 'backend'])

class Wrapper:
    def __init__(self, name):
        self.name = name
        print(f'[wrapper {self.name}] init...')
        if not is_backend_running():
            print(f'[wrapper] backend is not running, starting it...')
            start_backend()
            time.sleep(0.5)  # Give the backend time to start
        else:
            print(f'[wrapper] backend is already running')


        print(f'[wrapper] connecting to backend')
        self.conn = Client((HOST, PORT), authkey=AUTHKEY)
        print(f"[wrapper {self.name}] Connected to backend.")

    def ping(self):
        self.conn.send(("ping", None))
        return self.conn.recv()
