import socket
from settings import *
import threading
import select
from time import sleep




class Client:
    def __init__(self) -> None:
        self._thread = None


    def open(self, address, port):
        print(f'[Client] opening')
        stop_read, self._stop_write = socket.socketpair()
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn.connect((address, port))

        self._thread = threading.Thread(target=self.read_thread, args=(self._conn, stop_read))
        self._thread.start()

    def write(self, data):
        print(f'[Client] Sending {data}')
        self._conn.send(data)

    def read_thread(self, conn, stop):
        while True:
            ready, _, _ = select.select([conn, stop], [], [])
            if stop in ready:
                # Stop the thread
                print('[Client] Closing thread...')
                conn.close()
                break
            else:
                buf = conn.recv(BUF_SIZE)
                print(f'[Client] Received {buf}')
                if len(buf) == 0:
                    break
        print('[Client] thread closing due to adapter disconnect')


    def start(self):
        self._thread.start()

    def stop(self):
        if self._thread.is_alive():
            print(f'[Client] stopping...')
            try:
                self._stop_write.send(b'1')
            except BrokenPipeError:
                pass
            else:
                self._thread.join()

    def __del__(self):
        print('[Client] __del__')
        self.stop()
        self._stop_write.close()

def main():
    client = Client()

    client.open(HOST, PORT)

    client.write(b'123')


    sleep(5)


if __name__ == '__main__':
    main()