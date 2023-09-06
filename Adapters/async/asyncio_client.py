import asyncio
import time

class TCPClientAdapter:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.data_to_send = []

    async def _connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def _receive_and_record(self):
        while True:
            # Create a list of tasks to await multiple events, including a timer
            tasks = [self._read_data(), self._timeout(5)]  # 5-second timeout
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            if not pending:
                # All tasks are done
                break

            for task in done:
                if task == tasks[0]:  # Data received from the server
                    data, received_time = task.result()
                    print(f"Received: {data} at {received_time}")
                    # You can process the received data here as needed

                elif task == tasks[1]:  # Data sent to the server
                    pass  # Handle sent data completion if needed

                elif task == tasks[2]:  # Timeout event
                    print("Timeout occurred")

    async def _read_data(self):
        data = await self.reader.read(1)  # Read one byte asynchronously
        received_time = time.time()
        return data, received_time

    async def _send_pending_data(self):
        # Send pending data in the self.data_to_send list
        while self.data_to_send:
            data = self.data_to_send.pop(0)
            self.writer.write(data.encode())
            await self.writer.drain()

    async def _close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    def run(self):
        async def main():
            await self._connect()
            await asyncio.gather(self._receive_and_record(), self._send_data())
            await self._close()

        asyncio.run(main())

    async def _send_data(self):
        # Modify this method to send data as needed
        while True:
            data = "Hello, Server!"  # Replace with your data to send
            self.data_to_send.append(data)
            await asyncio.sleep(1)  # Adjust the sending interval as needed

    def send_data_from_main(self, data):
        self.
        self.data_to_send.append(data)  # Add data to the send queue

    async def _timeout(self, seconds):
        await asyncio.sleep(seconds)

def main():
    host = '127.0.0.1'  # Replace with the host you want to connect to
    port = 8888         # Replace with the port you want to connect to

    client = TCPClientAdapter(host, port)
    client.run()

    client.write(b'test')

if __name__ == '__main__':
    main()