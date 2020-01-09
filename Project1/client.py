import socket
import os
import pickle
from linkedlist import Node

# the pid will serve as the client ID/PID
PID = os.getpid()
HOSTNAME = socket.gethostname()
PORT = 1234

print(f"The client ID is {PID}\n")

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lamport_clock = 1 #init

while True:
    print("What type of transaction do you want to issue?\n1. Transfer\n2. Balance")
    if 1:
        print("Enter the Reciever ID: ")
        reciever = input()
        print("Enter the amount you wish to send: ")
        amount = input()
        print(f"You {PID} are sending {amount} to {reciever}")
        # TODO: finish the logic
    else:
        print(f"Checking balance for {PID}...")
        # TODO: finish the balance logic