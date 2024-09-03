from client import Client
from server import Server
from time import sleep
from settings import *


def main():
    _client = Client()
    _server = Server()

    print('Starting server...')
    _server.start()
    sleep(1)
    print('Opening client...')
    _client.open(HOST, PORT)

    sleep(1)
    print('Writing from client...')
    _client.write(b'test')
    sleep(1)

    if True:
        # Stop the client first
        print('Stopping client...')
        _client.stop()
    
    sleep(1)
    print('Stopping server...')
    _server.stop()
    # Stop the server first
    
    sleep(1)
    print('Finished')
    sleep(1)
    




if __name__ == '__main__':
    main()