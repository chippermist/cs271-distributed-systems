import socket
import os
import pickle
import time
import argparse
import threading
from multiprocessing import Process, Lock, Value
from termcolor import colored
from linkedlist import Node, SyncMsg, calculateBalance

# check for valid command line arguments
parser = argparse.ArgumentParser(description='Blockchain Client')
parser.add_argument('--port' ,nargs=1, type=int, required=True, help="Port number for the client")
args = parser.parse_args()

# the pid will serve as the client ID/PID
PID         = os.getpid()
HOSTNAME    = socket.gethostname()
PORT        = (args.port)[0]
HEADERSIZE  = 2
CLIENTS     = [9001,9002,9003]
CLIENT_ID   = PORT - 9000 - 1
INIT_BAL    = 10
CLIENTS.remove(PORT) #removing the current clients port

# globals
local_clock = [0,0,0]
lock1       = threading.Lock()
lock2       = threading.Lock()
bchain      = []
time_table  = [[0,0,0], [0,0,0], [0,0,0]]

def create_transactions():
    global local_clock
    global bchain
    while True:
        print(colored(f"\n\nThis client ID is {PID}.", 'cyan'))
        print("What type of transaction do you want to issue?\n\t1. Transfer\n\t2. Balance\n\t3. Send Sync")
        option = int(input())
        if option == 1:
            print("Enter the Reciever ID: ")
            reciever = int(input())
            print("Enter the amount you wish to send: ")
            amount = float(input())
            print(colored(f"You {PID} are sending {amount} to {reciever}", 'yellow'))
            if calculateBalance(bchain, INIT_BAL, PID) >= amount:
                transaction = Node(PID, reciever, amount, local_clock[CLIENT_ID-1])
                print(colored("SUCCESS", 'green'))
            else:
                print(colored("INCORRECT", 'red'))
            bchain.append(transaction)
            # update the clock for each transaction
            local_clock[CLIENT_ID] += 1
            # TODO: need to figure out the logic of what needs to happen.
            # maybe send updates to all the other clients-timetables 
        elif option == 2:
            # this should be simple since there is no need to check or make any request to other clients
            print(colored(f"Checking balance for {PID}.", 'yellow'))
            balance = calculateBalance(bchain, INIT_BAL, PID)
            print(colored(f"The balance is: ${balance}.", 'green'))
        elif option == 3:
            # TODO: maybe logic for sync to a specific client
            print("Enter the Reciever ID: ")
            reciever = int(input())
            msg = build_msg(reciever)
            send_sync = threading.Thread(name="Send sync message thread", target=send_to_clients, args=(msg, reciever))
            send_sync.start()
            send_sync.join()
    
        print(colored(f"Clock: {local_clock}", 'yellow'))

def build_msg(client_id):
    global bchain
    global time_table
    global local_clock
    client_id = client_id - 9000 - 1
    msg = SyncMsg(CLIENT_ID, local_clock)
    client_clock = time_table[client_id]

    for i in range(len(client_clock)):
        curr_sender = i + 9000 + 1
        # TODO: filter the transactions based on clock value and client
        for transaction in bchain:
            if transaction.sender == curr_sender and transaction.clock > client_clock[i]:
                msg.transactions.append(transaction)

    print(colored(f"The sync message is built: {msg} with {len(msg.transactions)} transactions.", 'yellow'))
    msg = pickle.dumps(msg)
    return msg


def send_to_clients(msg, client_id):
    global local_clock
    global CLIENTS
    
    print(colored(f"Sync timetable and transactions.", 'yellow'))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # sending the sync message to client_id
        s.connect((HOSTNAME, client_id))
        s.send(msg)
        s.close()
    except:
        print(colored(f"Client on port {client_id} is offline.", 'yellow'))

    # for client_port in CLIENTS:
    #     print(colored("Sending sync message to {client}.", 'yellow'))
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     try:
    #         # sending the sync message to all clients
    #         s.connect((HOSTNAME, client_port))
    #         s.send(msg)
    #         # TODO: check if something else needs to be done here
    #         s.close()
    #     except:
    #         print(colored(f"Client on port {client_port} is offline.", 'yellow'))
    #         CLIENTS.remove(client_port)
    
def process_clients_sync(conn, addr):
    data = conn.recv(1024)
    msg = pickle.loads(data)

    # thread to update the time table and local clock
    clock_update = threading.Thread(name="Update clock and time table thread", target=update_clock, args=(msg.clock,))
    clock_update.start()
    
    # thread to update blockchain
    bchain_update = threading.Thread(name="Update blockchain thread", target=update_bchain, args=(msg.transactions, msg.client_id))
    bchain_update.start()

    # cleanup
    clock_update.join()
    bchain_update.join()


def listen_to_clients():
    client_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_listen.bind((HOSTNAME, PORT))
    client_listen.listen()
    while True:
        print("Waiting for connections.")
        conn, addr = client_listen.accept()
        update_thread = threading.Thread(name="Sync Message Thread", target=process_clients_sync, args=(conn, addr))
        update_thread.start()
        update_thread.join()
    client_listen.close()

def update_bchain(transactions, client_id):
    global local_clock
    global bchain
    lock2.acquire()
    for transaction in transactions:
        if transaction.clock <= local_clock[client_id]:
            continue
        bchain.append(transaction)
        print(colored(f"Adding transaction.", 'yellow'))
    lock2.release()


# update the local clock
def update_clock(recieved_clock):
    global local_clock
    global time_table
    lock1.acquire()
    for client_id in range(len(recieved_clock)):
        local_clock[client_id] = max(recieved_clock[client_id], local_clock[client_id])
    # updating the 2D-time table here as well 
    time_table[CLIENT_ID] = recieved_clock
    lock1.release()



if __name__ == '__main__':
    print(colored(f"Starting client with PID: {PID}.", 'blue'))
    p = threading.Thread(name='Listen to Clients', target=listen_to_clients, args=())
    p.daemon = True
    p.start()
    create_transactions()

    # cleanup
    p.join()
