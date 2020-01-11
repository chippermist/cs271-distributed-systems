import socket
import os
import json
import pickle
import argparse
from linkedlist import Node, LinkedList
from queue import PriorityQueue

# check for valid command line arguments
parser = argparse.ArgumentParser(description='Blockchain Client')
parser.add_argument('--port' ,nargs=1, type=int, required=True, help="Port number for the client")
args = parser.parse_args()

# the pid will serve as the client ID/PID
PID = os.getpid()
HOSTNAME = socket.gethostname()
PORT = args.port
HEADERSIZE = 2

# local queue for Lamport's Distributed Solution
# this list needs to be maintained based on the priority
# TODO: maybe this needs to be a priority queue
local_queue = PriorityQueue()

# client debug information
print(f"The client ID is {PID}\n")
print(f"Socket connection is running on port {PORT}")


c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# c.bind((HOSTNAME, PORT))
c.connect((HOSTNAME, 1234))
lamport_clock = 0 # init clock

while True:
    print("What type of transaction do you want to issue?\n1. Transfer\n2. Balance")
    option = int(input())
    if option == 1:
        print("Enter the Reciever ID: ")
        reciever = input()
        print("Enter the amount you wish to send: ")
        amount = int(input())
        print(f"You {PID} are sending {amount} to {reciever}")
        # TODO: finish the logic
    else:
        print(f"Checking balance for {PID}...")
        # TODO: finish the balance logic
        msg = pickle.dumps(PID)
        print(pickle.loads(msg))
        msg = bytes(f"{2:<{HEADERSIZE}}", "utf-8")+msg
        print(msg)
        c.send(msg)
        current_balance = (c.recv(1024))
        print(f"The client {PID} has the current balance of ${current_balance.decode()}.\n")


def recv_msg(sock):
    while True:
        data, addr = c.recv(1024)
        sys.stdout.write(data)

