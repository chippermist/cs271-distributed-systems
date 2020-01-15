# Node class 
class Node: 

    # Function to initialise the node object 
    def __init__(self, sender, reciever, amount): 
        self.sender = sender
        self.reciever = reciever
        self.amount = amount
        self.next = None # Initialize next as null 


# Linked List class contains a Node object 
class LinkedList():

    # Function to initialize head 
    def __init__(self, head=None): 
        self.head = head
        
    # Function to insert a new Node into linked list
    def insert(self, transaction):
        temp = self.head
        if temp is not None:
            while(temp is not None and temp.next is not None):
                temp = temp.next
                continue
            temp.next = transaction
        else:
            temp = transaction
        self.printList()

    # This function prints contents of linked list 
    # starting from head 
    def printList(self):
        temp = self.head 
        while (temp): 
            print(temp.data) 
            temp = temp.next

    # This function calculates the current balanace
    # of a client using it's PID
    def calculateBalance(self, INIT_BAL, PID):
        temp = self.head
        final_bal = INIT_BAL
        while (temp):
            if PID == temp.sender:
                final_bal -= temp.amount
            elif PID == temp.reciever:
                final_bal += temp.amount
        return final_bal

def calculateBalance(arr, INIT_BAL, PID):
    final_bal = INIT_BAL
    for item in arr:
        if PID == item.sender:
            final_bal -= item.amount
        elif PID == item.reciever:
            final_bal += item.amount
    return final_bal
