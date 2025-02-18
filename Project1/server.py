import socket
import pickle   # TODO: Unsafe -- change to some safe object
import os
from multiprocessing import Process, Array
from termcolor import colored
import threading
from linkedlist import Node, calculateBalance

# hostname and port config
HOST = socket.gethostname() # could just be 127.0.0.1
PORT = 1234
HEADERSIZE = 2

# other configurations for clients
INIT_BAL = 10
bchain = []

# set up the socket with IPV4 and TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

print(colored(f"Server PID: {os.getpid()}\nStarting to listen on {HOST}:{PORT}\n", 'green'))
s.listen(5) # start listening and accepting the connections

# Function to serve clients -- it uses threads so it can effectively spin
# a new thread that handles client requests
def new_client(conn, addr):
    global bchain
    with conn:
        print(colored(f"Connection by {addr}\n----------------------\n\n", 'green'))
        # look for data from the client
        while True:
            data = conn.recv(1024)
            # if there is no more data then release lock and break
            if not data:
                print(colored("There is no more data. Closing connection.", 'yellow'))
                conn.close()
                break
            else:
                msg = (data[:HEADERSIZE])
                msg = int(msg.decode())
                print("----------------------")
                print(colored(f"The transaction type is {msg}.\n", 'blue'))
                # Money Transactions
                if msg == 1:
                    transaction = (pickle.loads(data[HEADERSIZE:]))
                    print(f"Sending ${transaction.amount} from {transaction.sender} to {transaction.reciever}.\n")
                    # check if the balance is enough so that the transaction is valid
                    if calculateBalance(bchain, INIT_BAL, transaction.sender) >= transaction.amount:
                        bchain.append(transaction)
                        conn.sendall(bytes(f"SUCCESS", "utf-8"))
                        print(colored(f"COMPLETED transaction from {transaction.sender}.", 'green'))
                    else:
                        conn.sendall(bytes(f"INCORRECT", "utf-8"))
                        print(colored(f"INCORRECT transaction from {transaction.sender}.", 'red'))
                # Balance Transactions
                elif msg == 2:
                    client_id = int(pickle.loads(data[HEADERSIZE:]))
                    print(f"Checking the balance for client {client_id}.")
                    current_bal = calculateBalance(bchain, INIT_BAL, client_id)
                    print(colored(f"The current balance for {client_id} is ${current_bal}.", 'green'))
                    conn.sendall(bytes(f"The current balance for client {client_id} is ${current_bal}", "utf-8"))
                    print(colored(f"The balance has been sent to {client_id}.\n", 'green'))
                print(bchain)
    conn.close()

# Start accepting connections from the server
# Each time a new request comes it will spin a new thread
# and keep listening for more connection requests
while True:
    client_sock, addr = s.accept()
    p = threading.Thread(target=new_client, args=(client_sock, addr))
    p.start()
p.join()
s.close()