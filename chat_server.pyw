# Importing the socket module.
import socket

# Used to pack and unpack data.
import struct

# Pickle is used to serialize and deserialize a Python object structure. Any object in python can be
# pickled so that it can be saved on disk. What pickle does is that it “serialises” the object first
# before writing it to file. Pickling is a way to convert a python object (list, dict, etc.) into a
# character stream. The idea is that this character stream contains all the information necessary to
# reconstruct the object in another python script.
import pickle


# Importing the threading module.
import threading


# This is importing the time, requests, json, and os modules.
import time, requests, json, os

# This is creating a socket object.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# This is the port and host that the server is running on.
PORT = 9999
# HOST = '127.0.0.1'
HOST = socket.gethostbyname(socket.gethostname())
print(f"\n\nUse this HOST to Connect: ' {HOST} '\n")

# This is binding the socket to the host and port.
server_socket.bind((HOST, PORT))
server_socket.listen(4)

clients_connected = {}
clients_data = {}
count = 1



def connection_requests():
    """
    It waits for a connection, then it checks if the number of clients connected is less than 10, if it
    is, it sends the client an 'allowed' message, then it receives the client's name, then it receives
    the image, then it sends the client the data of all the clients connected, then it sends the client
    the id of the client, then it sends a notification to all the clients connected that a new client
    has joined the chat, then it starts a new thread to receive data from the client.
    """
    global count

    while True:
        # print("Waiting for connection...")
        client_socket, address = server_socket.accept()

        # print(f"Connections from {address} has been established")
        # print(len(clients_connected))
        if len(clients_connected) == 10:
            client_socket.send('not_allowed'.encode())

            client_socket.close()
            continue
        else:
            client_socket.send('allowed'.encode())

        # Trying to receive the client's name, if it fails, it prints that the client has
        # disconnected, then it closes the client's socket, then it continues.
        try:
            client_name = client_socket.recv(1024).decode('utf-8')
        except:
            # print(f"{address} disconnected")
            client_socket.close()
            continue

        # print(f"{address} identified itself as {client_name}")

        clients_connected[client_socket] = (client_name, count)

        image_size_bytes = client_socket.recv(1024)
        # image_size_int = int(image_size_bytes,2)
        image_size_int = struct.unpack('i', image_size_bytes)[0]

        client_socket.send('received'.encode())
        image_extension = client_socket.recv(1024).decode()

        b = b''
        # Receiving the image from the client.
        while True:
            image_bytes = client_socket.recv(1024)
            b += image_bytes
            if len(b) == image_size_int:
                break

       # Sending the data of all the clients connected to the client that just connected.
        clients_data[count] = (client_name, b, image_extension)

        clients_data_bytes = pickle.dumps(clients_data)
        clients_data_length = struct.pack('i', len(clients_data_bytes))

        client_socket.send(clients_data_length)

        client_socket.send(clients_data_bytes)

        # Sending the id of the client to the client, then it is sending a notification to all the
        # clients
        # connected that a new client has joined the chat.
        if client_socket.recv(1024).decode() == 'image_received':
            client_socket.send(struct.pack('i', count))

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())
                    data = pickle.dumps(
                        {'message': f"{clients_connected[client_socket][0]} joined the chat", 'extension': image_extension,
                         'image_bytes': b, 'name': clients_connected[client_socket][0], 'n_type': 'joined', 'id': count})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)
        count += 1
        # Creating a new thread to receive data from the client.
        t = threading.Thread(target=receive_data, args=(client_socket,))
        t.start()


def receive_data(client_socket):
    """
    It receives data from the client, and sends it to all the other clients.
    
    :param client_socket: The socket object of the client that sent the data
    """
    # Receiving data from the client, and sending it to all the other clients.
    while True:
        # Trying to receive data from the client, if it fails, it prints that the client has
        # disconnected, then it sends a notification to all the clients connected that the client has
        # left the
        # chat, then it deletes the client's data from the clients_data dictionary, then it deletes
        # the client
        # from the clients_connected dictionary, then it closes the client's socket, then it breaks
        # out of the
        # loop.
        try:
            data_bytes = client_socket.recv(1024)
        except ConnectionResetError:
            # print(f"{clients_connected[client_socket][0]} disconnected")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())

                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
                                         'id': clients_connected[client_socket][1], 'n_type': 'left'})

                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)

                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break
        except ConnectionAbortedError:
            # print(f"{clients_connected[client_socket][0]} disconnected unexpectedly.")

            for client in clients_connected:
                if client != client_socket:
                    client.send('notification'.encode())
                    data = pickle.dumps({'message': f"{clients_connected[client_socket][0]} left the chat",
                                         'id': clients_connected[client_socket][1], 'n_type': 'left'})
                    data_length_bytes = struct.pack('i', len(data))
                    client.send(data_length_bytes)
                    client.send(data)

            del clients_data[clients_connected[client_socket][1]]
            del clients_connected[client_socket]
            client_socket.close()
            break

        for client in clients_connected:
            # print(len(clients_connected),clients_connected)
            if client != client_socket:
                client.send('message'.encode())
                client.send(data_bytes)


# It waits for a connection, then it checks if the number of clients connected is less than 10, if it
# is, it sends the client an 'allowed' message, then it receives the client's name, then it receives
# the image, then it sends the client the data of all the clients connected, then it sends the client
# the id of the client, then it sends a notification to all the clients connected that a new client
# has joined the chat, then it starts a new thread to receive data from the client.
connection_requests()
