import socket
import pickle
from linkedlist import LinkedList, Node

# hostname and port config
HOST = socket.gethostname() # could just be 127.0.0.1
PORT = 1234
HEADERSIZE = 2

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
            else:
                msg = (data[:HEADERSIZE])
                msg = int(msg.decode())
                print(f"The transaction type is {msg}.\n")
                if msg == 1:
                    print(f"Sending $x from a to b")
                elif msg == 2:
                    client_id = int(pickle.loads(data[HEADERSIZE:]))
                    print(f"Checking the balance for client {client_id}")
                    current_bal = bchain.calculateBalance(INIT_BAL, client_id)
                    print(f"The current balance for {client_id} is {current_bal}\n")
                    conn_sock.sendall(bytes(f"{current_bal}", "utf-8"))

