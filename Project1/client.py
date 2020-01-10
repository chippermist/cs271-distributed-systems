import socket
import os
import json
import argparse
from linkedlist import Node, LinkedList

# check for valid command line arguments
parser = argparse.ArgumentParser(description='Blockchain Client')
parser.add_argument('--port' ,nargs=1, type=int, required=True, help="Port number for the client")
args = parser.parse_args()

# the pid will serve as the client ID/PID
PID = os.getpid()
HOSTNAME = socket.gethostname()
PORT = args.port

# local queue for Lamport's Distributed Solution
local_queue = LinkedList()

# client debug information
print(f"The client ID is {PID}\n")
print(f"Socket connection is running on port {PORT}")


c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lamport_clock = 0 # init clock

while True:
    print("What type of transaction do you want to issue?\n1. Transfer\n2. Balance")
    if 1:
        print("Enter the Reciever ID: ")
        reciever = input()
        print("Enter the amount you wish to send: ")
        amount = int(input())
        print(f"You {PID} are sending {amount} to {reciever}")
        # TODO: finish the logic
    else:
        print(f"Checking balance for {PID}...")
        # TODO: finish the balance logic