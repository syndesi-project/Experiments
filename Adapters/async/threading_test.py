from threading import Thread
from time import sleep, time
import socket
from enum import Enum
import pickle

HOST = 'localhost'
PORT = 8888


class State(Enum):
    IDLE = 0
    WAIT_FOR_RESPONSE = 1
    CONTINUATION = 2

TIMEOUT = 2
CONTINUATION_TIMEOUT = 0.5

class Adapter:
    def __init__(self) -> None:
        self.read_thread = Thread(daemon=True, target=self._read_loop)
        self.write_thread = Thread(daemon=True, target=self._write_loop)
        self._write_buffer = b''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._read_buffer = b''
        self._state = State.IDLE

        self._read_history = []
        
    def _read_loop(self):
        # Set the timeout
        self._socket.settimeout(TIMEOUT)
        self._state = State.WAIT_FOR_RESPONSE
        while True:
            try:
                new_byte = self._socket.recv(1)
            except TimeoutError:
                print("timeout")
                break
            else:
                print(f"Read {new_byte}")
                self._read_history.append((time(), new_byte))
                self._read_buffer += new_byte
                match self._state:
                    case State.WAIT_FOR_RESPONSE:
                        self._state = State.CONTINUATION
                        self._socket.settimeout(CONTINUATION_TIMEOUT)
                    case State.CONTINUATION:
                        self._state = State.IDLE
                        

    def _write_loop(self):
        self._start_write_timestamp = time()
        self._socket.send(self._write_buffer)
        self._end_write_timestamp = time()
        print(f"Write {self._write_buffer}")
        self._write_buffer = b''
        

    def write(self, data):
        self._write_buffer += data
        print("Starting write thread...")
        self.write_thread.start()
        self.write_thread.join()
        print("Finished write thread")

    def read(self) -> bytes:
        print("Starting read thread")
        self.read_thread.start()
        self.read_thread.join()
        print("Finished read thread")



    def connect(self):
        self._socket.connect((HOST, PORT))
        


def main():
    adapter = Adapter()

    adapter.connect()
    adapter.write(b'Hello world !')
    adapter.read()

    # TODO : Try with server

    sleep(5)
    with open('read_history.pkl', 'wb') as f:
        pickle.dump(adapter._read_history, f)

if __name__ == '__main__':
    main()