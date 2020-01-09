import socket
import pickle
from linkedlist import LinkedList, Node

# hostname and port config
HOST = socket.gethostname() # could just be 127.0.0.1
PORT = 1234

# other configurations for clients
INIT_BAL = 10
bchain = LinkedList()

# set up the socket with IPV4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

print(f"Starting to listen on {HOST}:{PORT}\n")
s.listen()
# start listining and accepting the connections
while True:
    conn_sock, addr = s.accept()
    with conn_sock:
        print(f"Connection by {addr}")
        # look for data from the clients
        while True:
            data = conn_sock.recv(1024)
            # if there is no more data then break
            if not data:
                break

