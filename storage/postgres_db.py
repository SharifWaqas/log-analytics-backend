import psycopg2

class PostgreSQLDB:

    def __init__(self):
        self.connection = psycopg2.connect(database="log_engine", user="postgres", password="Z7@pL3!xQ9#tV2$k", host="localhost",port=5432)
        self.cursor = self.connection.cursor()


    def get_total_log_count(self):
        query = """
                SELECT COUNT(*) FROM valid_logs
                """
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return int(row[0])

    def get_error_log_count(self):
        query = """
                SELECT COUNT(*) FROM valid_logs WHERE level = 'ERROR' 
                """
        self.cursor.execute(query)
        temp = self.cursor.fetchone()
        return int(temp[0])
    
    def insert_valid_logs(self,batch):
        batch_data = []
        for log in batch:
            row = (log.timestamp, log.level, log.service, log.user_id, log.action, log.status, log.ip)
            batch_data.append(row)
        
        query = "INSERT INTO valid_logs (timestamp, level, service, user_id, action, status, ip) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        self.cursor.executemany(query, batch_data)
        self.connection.commit()
    
    def get_failed_login_counts_per_user(self):
        query = """
                SELECT user_id, COUNT(*) AS failure_count
                FROM valid_logs 
                WHERE action = 'login' AND status IN (401, 500, 503)
                GROUP BY user_id
                ORDER BY failure_count DESC;
                """
        self.cursor.execute(query)
        return(self.cursor.fetchall())


    def insert_failed_logs(self, batch):
        data = []
        for log in batch:
            row = (log.raw_log, str(log.error_details))
            data.append(row)

        query = "INSERT INTO failed_logs (raw_log, error_details) VALUES (%s, %s)"
        self.cursor.executemany(query, data)
        self.connection.commit()
    
    def fetch_logs(self, startTime, endTime, level):
        query = "SELECT * FROM valid_logs WHERE timestamp >= %s AND timestamp <= %s and level = %s"
        temp = (startTime,endTime,level)
        self.cursor.execute(query, temp)
        rows = self.cursor.fetchall()  
        return rows

    
    def get_counts_grouped_by_user(self, action, limit):
        query = """
                SELECT user_id, COUNT(*) AS user_count
                FROM valid_logs
                WHERE action = %s
                GROUP BY user_id
                ORDER BY user_count DESC
                LIMIT %s
                """
        self.cursor.execute(query, (action,limit))
        returnval = self.cursor.fetchall()
        return (returnval)
    
