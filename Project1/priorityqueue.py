class QueueNode:
    # Function to initialise the node object 
    def __init__(self, clock, pid, transaction): 
        self.clock = clock
        self.pid = pid
        self.transaction = transaction


class PriorityQueue(object): 
    def __init__(self): 
        self.queue = []
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # for checking if the queue is empty 
    def isEmpty(self): 
        return len(self.queue) == [] 
  
    # for inserting an element in the queue 
    def insert(self, data): 
        self.queue.append(data)
  
    # for popping an element based on Priority 
    def delete(self): 
        try: 
            min = 0
            for i in range(len(self.queue)): 
                if self.queue[i] < self.queue[min]: 
                    min = i 
            item = self.queue[min] 
            del self.queue[min] 
            return item 
        except IndexError: 
            print() 
            exit()

    # for finding the first element in queue
    def find_first(self):
        try:
            min = 0
            for i in range(len(self.queue)):
                if self.queue[i].clock < self.queue[min].clock:
                    min = i
                item = self.queue[min]
                return item
        except IndexError:
            print()
            exit()