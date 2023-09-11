import threading
import socket
import select

def receive_data(sock, timeout):
    while True:
        ready_to_read, _, _ = select.select([sock], [], [], timeout)
        
        if ready_to_read:
            try:
                data = sock.recv(1)  # Try to receive one byte
                if data:
                    print(f"Received: {data.decode('utf-8')}")
                else:
                    print("No more data received. Exiting receive loop.")
                    break  # Exit the loop when no more data is received
            except Exception as e:
                print(f"Error: {str(e)}")
                break  # Exit the loop on error
        else:
            print("Timeout occurred. Exiting receive loop.")
            break  # Exit the loop on timeout

def main():
    host = "localhost"
    port = 12345

    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Listen for incoming connections
    server_socket.listen(1)
    print(f"Listening on {host}:{port}")

    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")

    # Set the timeout for the receive operation (e.g., 10 seconds)
    timeout = 10

    # Create a thread to receive data
    receive_thread = threading.Thread(target=receive_data, args=(client_socket, timeout))

    # Start the thread
    receive_thread.start()

    # You can perform other tasks in the main thread while the receive thread runs

    # Wait for the receive thread to finish (not necessary in this case, as it's running in a loop)
    # receive_thread.join()

    # Close the sockets when done
    # client_socket.close()
    # server_socket.close()

if __name__ == "__main__":
    main()