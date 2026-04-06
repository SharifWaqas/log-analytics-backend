import sqlite3
class SQLiteDB:

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
    
    def create_valid_logs_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS valid_logs(
        id INTEGER PRIMARY KEY, 
        timestamp TEXT, 
        level TEXT, 
        service TEXT, 
        user_id TEXT, 
        action TEXT, 
        status TEXT, 
        ip TEXT)
        """
        self.cursor.execute(query)
        self.connection.commit()
    
    def create_failed_logs_table(self):
        query = """ 
        CREATE TABLE IF NOT EXISTS failed_logs(
        id INTEGER PRIMARY KEY,
        raw_log TEXT,
        error_details TEXT)
        """
        self.cursor.execute(query)
        self.connection.commit()

    def insert_valid_logs(self,batch):
        data = []
        for log in batch:
            row = (log.timestamp, log.level, log.service, log.user_id, log.action, log.status, log.ip)
            data.append(row)
        
        query = "INSERT INTO valid_logs (timestamp, level, service, user_id, action, status, ip) VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.cursor.executemany(query, data)
        self.connection.commit()
    

    def insert_failed_logs(self, batch):
        data = []
        for log in batch:
            row = (log.raw_log, str(log.error_details))
            data.append(row)

        query = "INSERT INTO failed_logs (raw_log, error_details) VALUES (?, ?)"
        self.cursor.executemany(query, data)
        self.connection.commit()
    
    def fetch_logs(self, startTime, endTime, level):
        query = "SELECT * FROM valid_logs WHERE timestamp >= ? AND timestamp <= ? and level = ?"
        temp = (startTime,endTime,level)
        self.cursor.execute(query, temp)
        rows = self.cursor.fetchall()  
        return rows
    
    def get_counts_grouped_by_user(self, action):
        query = """
                SELECT user_id, COUNT(*)
                FROM valid_logs
                WHERE action = ?
                GROUP BY user_id
                """
        self.cursor.execute(query, (action,))
        returnval = self.cursor.fetchall()
        return (returnval)
