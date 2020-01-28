# Timetable updates
class SyncMsg:
    def __init__(self, client_id, clock_val, bchain_transactions=[]):
        self.client_id = client_id
        self.clock = clock_val
        self.transactions = bchain_transactions

# Node class to handle transactions
class Node: 

    # Function to initialise the node object 
    def __init__(self, sender, reciever, amount, clock): 
        self.sender = sender
        self.reciever = reciever
        self.amount = amount
        self.clock = clock
        # self.next = None # Initialize next as null 

# function to calculate balance given a PID
def calculateBalance(arr, INIT_BAL, PID):
    final_bal = INIT_BAL
    for item in arr:
        if PID == item.sender:
            final_bal -= item.amount
        elif PID == item.reciever:
            final_bal += item.amount
    return final_bal