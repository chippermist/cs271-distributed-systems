import socket
import pickle   # TODO: Unsafe -- change to some safe object
import os
from multiprocessing import Process, Lock
from linkedlist import LinkedList, Node

# hostname and port config
HOST = socket.gethostname() # could just be 127.0.0.1
PORT = 1234
HEADERSIZE = 2

# other configurations for clients
INIT_BAL = 10
bchain = LinkedList()
lock = Lock() # lock to make sure there's atomicity in responses

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
        # look for data from the client
        while True:
            # lock.acquire()
            data = conn.recv(1024)
            # if there is no more data then release lock and break
            if not data:
                # TODO: check if this is ok...since this stays open until client quits
                print("There is no more data. Closing connection.")
                conn.close()
                break
            else:
                msg = (data[:HEADERSIZE])
                msg = int(msg.decode())
                print("----------------------")
                print(f"The transaction type is {msg}.\n")
                if msg == 1:
                    transaction = (pickle.loads(data[HEADERSIZE:]))
                    print(f"Sending ${transaction.amount} from {transaction.sender} to {transaction.reciever}.\n")
                    # TODO: finish logic for adding transaction to linked list
                    # is it possible to have a client that does not exist (sender or reciever)? 
                    # this is already checked when clients communicate?
                    # what other checks need to be done?
                    if bchain.calculateBalance(INIT_BAL, transaction.sender) >= transaction.amount:
                        bchain.insert(transaction)
                        conn.sendall(bytes(f"SUCCESS", "utf-8"))
                        print(f"COMPLETED transaction from {transaction.sender}.")
                    else:
                        conn.sendall(bytes(f"INCORRECT", "utf-8"))
                        print(f"INCORRECT transaction from {transaction.sender}.")
                elif msg == 2:
                    client_id = int(pickle.loads(data[HEADERSIZE:]))
                    print(f"Checking the balance for client {client_id}.")
                    current_bal = bchain.calculateBalance(INIT_BAL, client_id)
                    print(f"The current balance for {client_id} is ${current_bal}.")
                    conn.sendall(bytes(f"The current balance foor client {client_id} is ${current_bal}", "utf-8"))
                    print(f"The balance has been sent to {client_id}.\n")
    conn.close()
    # lock.release()

# Start accepting connections from the server
# Each time a new request comes it will spin a new thread
# and keep listening for more connection requests
while True:
    client_sock, addr = s.accept()
    p = Process(target=new_client, args=(client_sock, addr))
    p.start()
p.join()
s.close()