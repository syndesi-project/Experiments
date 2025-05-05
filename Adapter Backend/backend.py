import threading
import time
import uuid
from multiprocessing.connection import Listener
import tempfile
from colorama import Fore

class Backend:
    SHUTDOWN_DELAY = 2

    def __init__(self, address=('localhost', 59677), authkey=b'secret'):
        print('starting listener')
        self.listener = Listener(address, authkey=authkey)
        self.active_clients = set()
        self.running = True
        self.lock = threading.RLock()
        self.shutdown_timer = None

    def start(self):
        print("[backend] Server started.")
        while self.running:
            print('[backend] listening for client...')
            try:
                conn = self.listener.accept()
            except (OSError, EOFError):
                if not self.running:
                    # Retry
                    break
            print('[backend] accepted client...')
            client_id = uuid.uuid4()
            if self.listener.last_accepted is not None:
                # Check if the client didn't disconnect in the meantime
                print(f"[backend] Accepted connection from {self.listener.last_accepted}, client ID: {client_id}")
            
                self._register_client(client_id)

                t = threading.Thread(
                    target=self.handle_client,
                    args=(conn, client_id),
                    daemon=True
                )
                t.start()

            # if self.running:
            #     print(f"{Fore.RED}[backend] Exception in accept loop: {e}{Fore.RESET}")
                #break

        print("[backend] Server stopped.")

    def handle_client(self, conn, client_id):
        try:
            while True:
                msg = conn.recv()
                print(f"[backend] Received from {client_id}: {msg}")
                if msg == "ping":
                    conn.send("pong")
                else:
                    conn.send(f"echo: {msg}")
        except EOFError:
            print(f"[backend] Client {client_id} disconnected.")
        finally:
            conn.close()
            self._unregister_client(client_id)

    def _register_client(self, client_id):
        with self.lock:
            self.active_clients.add(client_id)
            print(f"[backend] Active clients: {len(self.active_clients)}")
            print(self.active_clients)
            # If a shutdown timer is running, cancel it
            if self.shutdown_timer:
                print("[backend] New client connected: canceling pending shutdown.")
                self.shutdown_timer.cancel()
                self.shutdown_timer = None

    def _unregister_client(self, client_id):
        with self.lock:
            self.active_clients.discard(client_id)
            print(f"[backend] Active clients: {len(self.active_clients)}")
            print(self.active_clients)

            # Start a shutdown timer if no clients left
            if not self.active_clients:
                print(f"[backend] No more clients. Starting shutdown countdown ({self.SHUTDOWN_DELAY}s).")
                self.shutdown_timer = threading.Timer(self.SHUTDOWN_DELAY, self._delayed_stop)
                self.shutdown_timer.start()

    def _delayed_stop(self):
        print('[backend] delayed stop')
        with self.lock:
            if not self.active_clients:
                print("[backend] No clients reconnected during countdown. Stopping server.")
                self.stop()
            else:
                print("[backend] New client connected during countdown. Abort shutdown.")

    def stop(self):
        print(f'[backend] stop')
        with self.lock:
            if self.running:
                self.running = False
                self.listener.close()
                print("[backend] Listener closed.")

def main():
    backend = Backend()
    backend.start()

if __name__ == "__main__":
    main()