class Queue:

    def __init__(self):
        self.__Queue = [None] * 10000
        self.__headpointer = 0
        self.__tailpointer = 0
        self.__MAX_SIZE = 10000
        self.__numberoflogs = 0

    def enqueue(self, data):
        if self.__numberoflogs >= self.__MAX_SIZE:
            return False

        self.__Queue[self.__tailpointer] = data
        self.__tailpointer += 1
        if self.__tailpointer == self.__MAX_SIZE:
            self.__tailpointer = 0

        self.__numberoflogs += 1
        return True

    def dequeue(self):
        if self.__numberoflogs == 0:
            return None

        value = self.__Queue[self.__headpointer]
        self.__Queue[self.__headpointer] = None
        self.__headpointer += 1

        if self.__headpointer == self.__MAX_SIZE:
            self.__headpointer = 0

        self.__numberoflogs -= 1
        return value
    
    def get_number_of_logs(self):
        return self.__numberoflogs

    def peek(self):
        if self.__numberoflogs == 0:
            return None

        return self.__Queue[self.__headpointer]


