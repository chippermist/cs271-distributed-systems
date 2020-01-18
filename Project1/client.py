import socket
import os
import pickle
import time
import argparse
import threading
from multiprocessing import Process, Lock, Value
from termcolor import colored
from linkedlist import Node
from priorityqueue import *

# check for valid command line arguments
parser = argparse.ArgumentParser(description='Blockchain Client')
parser.add_argument('--port' ,nargs=1, type=int, required=True, help="Port number for the client")
args = parser.parse_args()

# the pid will serve as the client ID/PID
PID = os.getpid()
HOSTNAME = socket.gethostname()
PORT = (args.port)[0]
HEADERSIZE = 2
CLIENTS = [9001,9002,9003]
CLIENTS.remove(PORT) #removing the current clients port

# local queue for Lamport's Distributed Solution
# this list needs to be maintained based on the priority
local_queue = PriorityQueue()

# client debug information
print(f"The client ID is {PID}\n")
print(f"Socket connection is running on port {PORT}")

# set up the socket with IPV4 and TCP
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((HOSTNAME, 1234))
local_clock = 0 # init clock
l = Lock()


# Possible thread1 -- parent thread
# could handle user input
def transactions():
    global local_clock
    global local_queue
    while True:
        print(f"\n\nThis client ID is {PID}.")
        print("What type of transaction do you want to issue?\n1. Transfer\n2. Balance")
        option = int(input())
        if option == 1:
            print("Enter the Reciever ID: ")
            reciever = int(input())
            print("Enter the amount you wish to send: ")
            amount = float(input())
            print(f"You {PID} are sending {amount} to {reciever}")
            transaction = Node(PID, reciever, amount)
            msg = pickle.dumps(transaction)
            msg = bytes(f"{1:<{HEADERSIZE}}", "utf-8")+msg
            local_queue.insert(QueueNode(local_clock, PID, msg))
            msg = bytes(f"{'T':<{HEADERSIZE}}", "utf-8") + pickle.dumps(QueueNode(local_clock, PID, msg))
            print("Starting thread for transaction.")
            p = threading.Thread(name="Send Request Thread Transaction", target=send_request, args=(msg,))
            p.start()
            p.join()
        else:
            print(f"Checking balance for {PID}...")
            msg = pickle.dumps(PID)
            msg = bytes(f"{2:<{HEADERSIZE}}", "utf-8")+msg
            local_queue.insert(QueueNode(local_clock, PID, msg))
            msg = bytes(f"{'B':<{HEADERSIZE}}", "utf-8") + pickle.dumps(QueueNode(local_clock, PID, msg))
            print("Starting thread for balance.")
            p = threading.Thread(name="Send Request Thread Balance", target=send_request, args=(msg,))
            p.start()
            p.join()
        update_clock(local_clock)


# function to reply to client and send to server
def send_reply(conn, addr):
    # global local_clock
    global local_queue
    # recieve message from conn
    # update the clock from within the message
    # check what kind of message it is and reply accordingly
    data = conn.recv(1024)
    msg = (data[:HEADERSIZE])
    msg = msg.decode().lstrip().rstrip()
    print(f"The message is {msg}.")
    recv_msg = (data[HEADERSIZE:])
    # print(f"Message recieved is {recv_msg}.")
    recv_msg = pickle.loads(recv_msg)
    recv_clock = recv_msg.clock
    update_clock(recv_clock)
    print(f"Clock recieved is {recv_clock}")
    # recv_clock = int(recv_clock.decode())
    print(f"The clock recieved is {recv_clock}. Local clock now is {local_clock}.")
    if msg == 'B' or msg == 'T':
        conn.sendall(bytes(f"{'G':<{HEADERSIZE}}", "utf-8") + bytes(f"{str(local_clock)}", "utf-8"))
        print(colored(f"Adding remote transaction from {recv_msg.pid} with clock {recv_clock}.", 'blue'))
        local_queue.insert(recv_msg)
        print(f"Sending OK to client: {addr}.")
    elif msg == 'D':
        # delete from the queue
        print(colored(f"Removing remote transaction from {recv_msg.pid} with clock {recv_clock}.", 'blue'))
        local_queue.delete_with_pid(recv_clock, recv_msg.pid)
    conn.close()

# Function to send request to the clients and server
def send_request(msg):
    global local_clock
    global CLIENTS
    global local_queue
    # read a list of ports of other clients, 
    # if they are alive then send the request for whatever is the message, 
    # if they are not alive then ignore
    # maybe wait 5 seconds so you can do concurrent requests within clients
    # time.sleep(5)
    print(f"Local clock is {local_clock}.")
    send_msg = msg
    print(f"Sending request to clients on ports {CLIENTS}.")
    count_responses = 0
    for client_port in CLIENTS:
        print(f"Trying to connect to client: {client_port}.")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # send message to client to sync and get their OK
        try:
            s.connect((HOSTNAME, client_port))
            s.send(send_msg)
            update_clock(local_clock)
            print(f"Message sent to client: {client_port}.")
            message_type = (send_msg[:HEADERSIZE])
            message_type = message_type.decode().lstrip().rstrip()
            if message_type == 'D':
                print(f"Message is delete : {message_type}")
                continue
            recv_msg = (s.recv(1024))
            s.close()
            header = (recv_msg[:HEADERSIZE])
            header = header.decode().lstrip().rstrip()
            print(f"Message recieved from other clients: {header}.")
            recv_clock = (recv_msg[HEADERSIZE:])
            recv_clock = int(recv_clock.decode())
            print(f"Clock recieved from client {client_port} is {recv_clock}.")
            update_clock(recv_clock)
            if header == 'G':
                count_responses += 1
        except:
            print(colored(f"Client on port {client_port} is not alive.", 'yellow'))
            CLIENTS.remove(client_port)
        
    # check if you can process the transaction
    if count_responses == len(CLIENTS):
        item = local_queue.find_first()

        # if there is a item remaining 
        # if the transcation in the front of the queue is yours
        if item and item.pid == PID:
            msg = item.transaction
            print("Removing transaction from local queue.")
            local_queue.delete_with_pid(item.clock, item.pid)
            local_queue.printQueue()
            print("Sending transaction to server.")
            c.send(msg)
            response = (c.recv(1024))
            print(colored(f"{response.decode()}\n", 'green'))
            remove_msg = bytes(f"{'D':<{HEADERSIZE}}", "utf-8") + pickle.dumps(item)
            p = threading.Thread(name="Remove processed transaction thread", target=send_request, args=(remove_msg,))
            p.start()
            p.join()

        # s.close()

# Possible thread2 -- could handle updating queue and sending replies
def client_processing():
    client_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_listen.bind((HOSTNAME, PORT))
    client_listen.listen()
    while True:
        print("Waiting for connections.")
        conn, addr = client_listen.accept()
        response_thread = threading.Thread(name="Client Response thread", target=send_reply, args=(conn, addr))
        response_thread.start()
        response_thread.join()
    client_listen.close()

# update the local clock
def update_clock(recieved_clock):
    global local_clock
    l.acquire()
    local_clock = max(recieved_clock, local_clock) + 1
    l.release()

if __name__ == "__main__":
    print(colored('The current balance is $10', 'green'))
    # create a background thread for the client processing
    p1 = threading.Thread(name="Client Processing -- Background", target=client_processing, args=())
    p1.daemon = True   # maybe try running in daemon if they allow spawnning threads
    p1.start()

    # continue with the parent thread for user input
    transactions()
    p1.join()
    c.close()