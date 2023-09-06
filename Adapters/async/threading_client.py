import socket
import threading
import time



# Threads seem to be the right tool for the job
# asyncio is made for sockets and in this case we would like for
# the adapter to be universal
#
#

class TCPClientAdapter:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.data_to_send = []
        self.reader = None
        self.writer = None

    def connect(self):
        self.reader, self.writer = socket.socket(socket.AF_INET, socket.SOCK_STREAM), None
        self.reader.connect((self.host, self.port))

    def receive_and_record(self):
        while True:
            try:
                data = self.reader.recv(1)  # Read one byte synchronously
                if not data:
                    break  # Connection closed

                received_time = time.time()
                print(f"Received: {data} at {received_time}")
                # You can process the received data here as needed

            except socket.timeout:
                print("Timeout occurred")

    def send(self, data):
        if self.writer:
            self.writer.send(data.encode())

    def close(self):
        if self.writer:
            self.writer.close()

    def run(self):
        self.connect()

        # Start the receive thread
        receive_thread = threading.Thread(target=self.receive_and_record)
        receive_thread.daemon = True
        receive_thread.start()

        # Start the send thread
        send_thread = threading.Thread(target=self.send_data_periodically)
        send_thread.daemon = True
        send_thread.start()

        # Wait for threads to finish (in this case, never)
        receive_thread.join()
        send_thread.join()

    def send_data_periodically(self):
        # Modify this method to send data as needed
        while True:
            data = "Hello, Server!"  # Replace with your data to send
            self.send(data)
            time.sleep(1)  # Adjust the sending interval as needed

    def send_data_from_main(self, data):
        self.data_to_send.append(data)  # Add data to the send queue

def main():
    host = '127.0.0.1'  # Replace with the host you want to connect to
    port = 8888         # Replace with the port you want to connect to

    client = TCPClientAdapter(host, port)
    client.run()

    # Example of sending data from the main program execution
    client.send_data_from_main("Data from main program")

if __name__ == '__main__':
    main()