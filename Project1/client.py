import socket
import os
import pickle
import time
import argparse
from multiprocessing import Process, Lock
from linkedlist import Node, LinkedList
# from queue import PriorityQueue
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
# TODO: maybe this needs to be a priority queue
local_queue = PriorityQueue()

# client debug information
print(f"The client ID is {PID}\n")
print(f"Socket connection is running on port {PORT}")

# set up the socket with IPV4 and TCP
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((HOSTNAME, 1234))
local_clock = 0 # init clock


# Possible thread1 -- parent thread
# could handle user input
def transactions():
    while True:
        print("What type of transaction do you want to issue?\n1. Transfer\n2. Balance")
        option = int(input())
        if option == 1:
            print("Enter the Reciever ID: ")
            reciever = int(input())
            print("Enter the amount you wish to send: ")
            amount = int(input())
            print(f"You {PID} are sending {amount} to {reciever}")
            transaction = Node(PID, reciever, amount)
            # TODO: finish the transaction logic
            msg = pickle.dumps(transaction)
            msg = bytes(f"{1:<{HEADERSIZE}}", "utf-8")+msg
            # c.send(msg)
            # response = (c.recv(1024))
            # print(f"Response from server: {response.decode()}")
            local_queue.insert(QueueNode(local_clock, PID, msg))
            msg = bytes(f"T:<{HEADERSIZE}", "utf-8")
            p = Process(name="Send Request Thread Transaction", target=send_request, args=(local_clock, msg))
            p.start()
            p.join()
        else:
            print(f"Checking balance for {PID}...")
            # TODO: finish the balance logic
            msg = pickle.dumps(PID)
            # print(pickle.loads(msg))
            msg = bytes(f"{2:<{HEADERSIZE}}", "utf-8")+msg
            # print(msg)
            # c.send(msg)
            # current_balance = (c.recv(1024))
            # print(f"The client {PID} has the current balance of ${current_balance.decode()}.\n")
            local_queue.insert(QueueNode(local_clock, PID, msg))
            msg = bytes(f"B:<{HEADERSIZE}", "utf-8")
            p = Process(name="Send Request Thread Balance", target=send_request, args=(local_clock, msg))
            p.start()
            p.join()
    c.close()

# function to reply to client and send to server
def send_reply(conn, addr):
    # recieve message from conn
    # update the clock from within the message
    # check what kind of message it is and reply accordingly
    while True:
        data = conn.recv(1024)
        if not data:
            break
        msg = (data[:HEADERSIZE])
        msg = msg.decode()
        recv_clock = (data[HEADERSIZE:])
        print(f"The clock in message is {recv_clock}")
        recv_clock = int(recv_clock.decode())
        update_clock(recv_clock, local_clock)
        print(f"The message is {msg}.\nThe clock recieved is {recv_clock}.")
        if msg is "G":
            # TODO: finish logic here
            # if it's the first then send to server
            item = local_queue.find_first()
            if item.pid == PID and item.clock <= local_clock:
                msg = item.transaction
                local_queue.delete()
                c.send(msg)
                response = (c.recv(1024))
                print(f"{response.decode()}\n")
        else:
            conn.sendall(bytes(f"G:<{HEADERSIZE}", "utf-8"))
    conn.close()

def send_request(local_clock, msg):
    # read a list of ports of other clients, 
    # if they are alive then send the request for whatever is the message, 
    # if they are not alive then ignore
    time.sleep(5)
    send_msg = msg + bytes(f"{local_clock}", "utf-8")
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Sending request to clients on ports {CLIENTS}.")
    for client_port in CLIENTS:
        s1.connect((HOSTNAME, client_port))
        try:
            s1.send(send_msg)
        except:
            print(f"Client on port {client_port} is not alive.")
        s1.close()

# Possible thread2 -- could handle updating queue and sending replies
def client_processing():
    client_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_listen.bind((HOSTNAME, PORT))
    client_listen.listen()
    while True:
        # TODO: finish logic for recieving the requests as well as updating queue & clock
        conn, addr = client_listen.accept()
        response_thread = Process(name="Response thread", target=send_reply, args=(conn, addr))
        response_thread.start()
        response_thread.join()
    client_listen.close()

# update the local clock
def update_clock(recieved_clock, local_clock):
    return max(recieved_clock, local_clock) + 1

if __name__ == "__main__":
    # create a background thread for the client processing
    p1 = Process(name="Client Processing -- Background", target=client_processing, args=())
    p1.daemon = False
    p1.start()

    # continue with the parent thread for user input
    transactions()
    p1.join()