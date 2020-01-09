# Node class 
class Node: 

    # Function to initialise the node object 
    def __init__(self, sender, reciever, amount): 
        self.sender = sender
        self.reciever = reciever
        self.amount = amount
        self.next = None # Initialize next as null 


# Linked List class contains a Node object 
class LinkedList: 

    # Function to initialize head 
    def __init__(self): 
        self.head = None

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
                final_bal -= temp.amount
        return final_bal