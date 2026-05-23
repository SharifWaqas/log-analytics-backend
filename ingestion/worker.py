import time

class Worker:

    def __init__(self, database, logqueue, metricobj):
        self.__metric_object = metricobj
        self.__batch = []
        self.__database = database
        self.__queue = logqueue
        self.__batch_start_time = None

    def start_worker(self):
        while True:
                
            log = self.__queue.peek()        
            if log is not None:
                if len(self.__batch) == 0:
                    self.__batch_start_time = time.time()
                self.__queue.dequeue()    
                self.__batch.append(log)
                end_time = time.time()
                elapsed_time = end_time - self.__batch_start_time
                if len(self.__batch) >= 1000 or elapsed_time > 0.1:        
                    flag = True
                    index = 0
                    while flag == True and index < 3:
                        try:
                            self.__database.insert_valid_logs(self.__batch)        
                            self.__metric_object.add_logs(len(self.__batch))
                            self.__batch = []
                            self.__batch_start_time = None
                            flag = False
                        except:
                            index +=1
                    if index == 3:
                        self.__database.insert_failed_logs(self.__batch)
                        self.__batch = []
                        self.__batch_start_time = None
                        index = 0
                        flag = False            
            else:
                time.sleep(0.1)