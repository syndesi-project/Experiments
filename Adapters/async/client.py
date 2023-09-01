from threading import Thread
from time import sleep, time
import socket


HOST = 'localhost'
PORT = 8888


class AdapterReadThread(Thread):
    def __init__(self, socket : socket.socket):
        super().__init__()
        self.daemon = True
        self.socket = socket

        self.buffer = []

    def run(self) -> None:
        while True:
            byte = self.socket.recv(1)
            self.buffer.append((time(), byte))

class Adapter():
    def __init__(self):
        super().__init__()
        self.daemon = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(HOST, PORT)

        self._read_thread = AdapterReadThread()
        self._read_thread.start()

    def write(self, data):
        self.socket.send(data)



def main():
    adapter = Adapter()
    adapter.start()

    sleep(10)



if __name__ == '__main__':
    main()