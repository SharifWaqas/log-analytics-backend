import datetime
class AnalyticsService:

    def __init__(self, db):
        self.db = db
    
    def get_last_hour_errors(self):
        currentTime = datetime.datetime.now()
        endtime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        starttime = (currentTime - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        raw_logs = self.db.fetch_logs(starttime,endtime,"ERROR")
        return raw_logs

    def get_login_counts_per_user(self, limit):
        return (self.db.get_counts_grouped_by_user(("login"), limit))

    def get_error_rate(self):
        total_logs = self.db.get_total_log_count()        
        if total_logs == 0:
            return None
        else:
            error_logs = self.db.get_error_log_count()
            return (error_logs/total_logs)

    def get_failed_login_counts_per_user(self):
        return(self.db.get_failed_login_counts_per_user())
