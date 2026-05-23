import time

class Metrics:
    def __init__(self):
        self.total_processed_logs = 0
        self.rate_start_time = time.time()
    
    def add_logs(self, numlogs):
        self.total_processed_logs += numlogs

