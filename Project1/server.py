import socket
import pickle
from multiprocessing import Process
import os
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

print(f"Server PID: {os.getpid()}\nStarting to listen on {HOST}:{PORT}\n")
s.listen(5) # start listining and accepting the connections

# Function to serve clients -- it uses threads so it can effectively spin
# a new thread that handles client requests
def new_client(conn, addr):
    with conn:
        print(f"Connection by {addr}\n----------------------\n\n")
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
                    transaction = (pickle.loads(data[HEADERSIZE:]))
                    print(f"Sending ${transaction.amount} from {transaction.sender} to {transaction.reciever}.\n")
                elif msg == 2:
                    client_id = int(pickle.loads(data[HEADERSIZE:]))
                    print(f"Checking the balance for client {client_id}.\n")
                    current_bal = bchain.calculateBalance(INIT_BAL, client_id)
                    print(f"The current balance for {client_id} is {current_bal}.\n")
                    conn.sendall(bytes(f"{current_bal}", "utf-8"))
    conn.close()

# Start accepting connections from the server
# Each time a new request comes it will spin a new thread
# and keep listening for more connection requests
while True:
    conn_sock, addr = s.accept()
    p = Process(target=new_client, args=(conn_sock, addr))
    p.start()
s.close()