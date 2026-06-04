import time

class Metrics:

    def __init__(self):
        self.total_processed_logs = 0
        self.recent_logs = 0
        self.last_reset_time = time.time()

    def add_logs(self, numlogs):
        self.total_processed_logs += numlogs
        self.recent_logs += numlogs