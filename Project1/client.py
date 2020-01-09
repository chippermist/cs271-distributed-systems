import socket
import os

# the pid will serve as the client ID/PID
PID = os.getpid()
HOSTNAME = socket.gethostname()
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

