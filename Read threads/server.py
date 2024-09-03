import socket
import threading
from time import sleep
from settings import *
import select


class Server:
    def __init__(self) -> None:
        stop_socket_read, self._stop_socket_write = socket.socketpair()
        self._thread = threading.Thread(target=self.server_thread, args=(HOST, PORT, stop_socket_read))

    def server_thread(self, host, port, stop):
        print('[Server] Starting server thread')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)

        threads = []

        while True:
            # Accept incoming connections
            ready, _, _ = select.select([s, stop], [], [])
            if stop in ready:
                # Stop all the client handles
                print(f'[Server] Closing all threads...')
                thread : threading.Thread
                for i, (stop_write, thread) in enumerate(threads):
                    #thread: threading.Thread
                    if thread.is_alive():
                        print(f'[Server] Closing thread number {i}')
                        stop_write.send(b'1')
                        thread.join()
                break
            else:
                conn, address = s.accept()
                print(f'[Server] Creating thread with {address}')
                client_stop_read, client_stop_write = socket.socketpair()
                threads.append((client_stop_write, threading.Thread(target=self.client_handle_thread, args=(conn, client_stop_read))))
                threads[-1][1].start()
        print('[Server] Server thread stopped')

                

    def client_handle_thread(self, conn : socket.socket, stop : socket.socket):
        print('[Server] Starting client handle thread')
        while True:
            ready, _, _ = select.select([conn, stop], [], [])
            if stop in ready:
                # Stop the thread
                stop.recv(1)
                print('[Server] Closing thread...')
                conn.close()
                break
            else:
                buf = conn.recv(BUF_SIZE)
                print(f'[Server] Received {buf}')
                if len(buf) > 0:
                    print(f'[Server] Sending {buf}')
                    conn.send(buf)
                else:
                    break
        print('[Server] Client handle thread stopped')


    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_socket_write.send(b'1')


def main():


    server = Server()
    server.start()

    sleep(10)
    print('Stopping server after 10 seconds...')
    server.stop()



if __name__ == '__main__':
    main()
