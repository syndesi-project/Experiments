import time
from syndesi import IP, IPServer, AdapterEvent

def callback(client : IP, event : AdapterEvent):
    """..."""
    print(f'Callback {client} {event}')

def main():
    """..."""
    server = IPServer('127.0.0.1', port=4242)
    server.register_client_callback(callback)
    client = IP('127.0.0.1', port=4242, auto_open=False)

    client_opened = client.try_open()
    print(f'Client opened : {client_opened}')
    
    time.sleep(0.5)
    print('Client write')
    client.write(b'123\n')


    client.close()
    server.close()


if __name__ == '__main__':
    main()