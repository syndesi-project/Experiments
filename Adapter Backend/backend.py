# yourlib/backend.py
import sys
import threading
from multiprocessing.connection import Listener

HOST = '127.0.0.1'
PORT = 59677
AUTHKEY = b'secret'


class Backend:
    def __init__(self) -> None:
        self.listener = Listener((HOST, PORT), authkey=AUTHKEY)
        print(f"[backend] Listening on {HOST}:{PORT}")
        self._threads = []

    def start(self):
        while True:
            conn = self.listener.accept()
            print("[backend] Client connected.")
            t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
            t.start()

def handle_client(conn):
    print("[backend] Handling new client.")
    try:
        while True:
            try:
                msg = conn.recv()
            except EOFError:
                print("[backend] Client disconnected.")
                break

            print("[backend] Received:", msg)
            if msg == ("ping", None):
                conn.send("pong")
            else:
                conn.send("unknown command")
    finally:
        conn.close()





def main():
    backend = Backend()
    backend.start()    

if __name__ == "__main__":
    main()
