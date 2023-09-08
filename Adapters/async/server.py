import socket
from time import sleep
PORT = 8888
HOST = 'localhost'





def server_program():
    # get the hostname
    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((HOST, PORT))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024)
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data) + ", sending back...")

        conn.send(data[:5]) # send data to the client
        sleep(2e-3)
        conn.send(data[5:])

    conn.close()  # close the connection


if __name__ == '__main__':
    server_program()