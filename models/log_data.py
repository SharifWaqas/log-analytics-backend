class LogData:
    def __init__(self, 
                timestamp,
                level,
                service,
                user_id,
                action,
                status,
                ip
                ):
        self.timestamp = timestamp
        self.level = level
        self.service = service
        self.user_id = user_id
        self.action = action
        self.status = status
        self.ip = ip
    
