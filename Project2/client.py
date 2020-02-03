import socket
import pickle
import argparse
import threading
from termcolor import colored
from linkedlist import Node, SyncMsg, calculateBalance

# check for valid command line arguments
parser = argparse.ArgumentParser(description='Blockchain Client')
parser.add_argument('--port' ,nargs=1, type=int, required=True, help="Port number for the client")
args = parser.parse_args()

# the pid will serve as the client ID/PID
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
    global time_table
    while True:
        print(bchain)
        print(colored(f"\n\n(alert) This client ID is {PORT}.", 'cyan'))
        print("What type of transaction do you want to issue?\n\t1. Transfer\n\t2. Balance\n\t3. Send Sync")
        option = int(input())
        if option == 1:
            # update the clock for each transaction
            local_clock[CLIENT_ID] += 1
            print("Enter the Reciever ID: ")
            reciever = int(input())
            print("Enter the amount you wish to send: ")
            amount = float(input())
            print(colored(f"(message) You {PORT} are sending {amount} to {reciever}", 'yellow'))
            if calculateBalance(bchain, INIT_BAL, PORT) >= amount:
                transaction = Node(PORT, reciever, amount, local_clock[CLIENT_ID])
                bchain.append(transaction)
                print(colored("(response) SUCCESS", 'green'))
            else:
                print(colored("(response) INCORRECT", 'red'))
                local_clock[CLIENT_ID] -= 1
            # TODO: need to figure out the logic of what needs to happen.
            # maybe send updates to all the other clients-timetables 
        elif option == 2:
            # this should be simple since there is no need to check or make any request to other clients
            print(colored(f"(message) Checking balance for {PORT}.", 'yellow'))
            balance = calculateBalance(bchain, INIT_BAL, PORT)
            print(colored(f"(response) The balance is: ${balance}.", 'green'))
        elif option == 3:
            # TODO: maybe logic for sync to a specific client
            print("Enter the Reciever ID: ")
            reciever = int(input())
            msg = build_msg(reciever)
            send_sync = threading.Thread(name="Send sync message thread", target=send_to_clients, args=(msg, reciever))
            send_sync.start()
            send_sync.join()
        time_table[CLIENT_ID] = local_clock
        print(colored(f"(message) Clock: {local_clock}", 'yellow'))
        print(colored(f"(message) Updated TT for {CLIENT_ID}", 'yellow'))
        print(colored(f"(message) TT: {time_table}", 'yellow'))

def build_msg(client_id):
    global bchain
    global time_table
    global local_clock
    client_id = client_id - 9000 - 1
    msg = SyncMsg(CLIENT_ID, local_clock)
    client_clock = time_table[client_id]

    for i in range(len(client_clock)):
        curr_client = i + 9000 + 1
        # TODO: filter the transactions based on clock value and client
        for transaction in bchain:
            if transaction.sender == curr_client and transaction.clock >= client_clock[i] and transaction.sender != client_id+9000+1:
                # print(colored(f"(message) Found a non sync transcation.", 'yellow'))
                if transaction not in msg.transactions:
                    msg.transactions.append(transaction)

    print(colored(f"(message) The sync message is built: {msg}.", 'yellow'))
    msg = pickle.dumps(msg)
    return msg


def send_to_clients(msg, client_id):
    global local_clock
    global CLIENTS
    
    print(colored(f"(message) Sync timetable and transactions.", 'yellow'))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # sending the sync message to client_id
        s.connect((HOSTNAME, client_id))
        s.send(msg)
        s.close()
    except:
        print(colored(f"(message) Client on port {client_id} is offline.", 'yellow'))
    
def process_clients_sync(conn, addr):
    data = conn.recv(1024)
    msg = pickle.loads(data)
    update_bchain(msg.transactions, msg.client_id)
    update_clock(msg.clock,msg.client_id)


def listen_to_clients():
    client_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_listen.bind((HOSTNAME, PORT))
    client_listen.listen()
    while True:
        print(colored("(alert) Waiting for connections.", 'cyan'))
        conn, addr = client_listen.accept()
        print(colored(f"(message) Sync message recieved.", 'yellow'))
        update_thread = threading.Thread(name="Sync Message Thread", target=process_clients_sync, args=(conn, addr))
        update_thread.start()
        update_thread.join()
    client_listen.close()

def update_bchain(transactions, client_id):
    global local_clock
    global bchain
    lock2.acquire()
    for transaction in transactions:
        if transaction.clock <= local_clock[client_id] and (transaction.sender is (9001+client_id)):
            # print(colored(f'Clock is low. Clock value in transaction is {transaction.clock}', 'red'))
            continue
        elif (transaction.clock > local_clock[client_id]) and (transaction not in bchain):
            bchain.append(transaction)
            print(colored(f"(message) Adding transaction: {transaction.sender} to {transaction.reciever} for {transaction.amount}.", 'yellow'))
    lock2.release()


# update the local clock
def update_clock(recieved_clock, client_id):
    global local_clock
    global time_table
    lock1.acquire()
    for client in range(len(recieved_clock)):
        local_clock[client] = max(recieved_clock[client], local_clock[client])
    # updating the 2D-time table here as well 
    time_table[client_id] = recieved_clock
    time_table[CLIENT_ID] = local_clock
    print(time_table)
    lock1.release()



if __name__ == '__main__':
    print(colored(f"(alert) Starting client with ID: {PORT}.", 'blue'))
    p = threading.Thread(name='Listen to Clients', target=listen_to_clients, args=())
    p.daemon = True
    p.start()
    create_transactions()

    # cleanup
    p.join()
