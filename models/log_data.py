class LogData:
    def __init__(
        self,
        timestamp,
        level,
        service,
        user_id,
        action,
        status,
        ip,
        route=None,
        method=None,
        duration_ms=None,
        request_id=None,
        deployment=None,
    ):
        self.timestamp = timestamp
        self.level = level
        self.service = service
        self.user_id = user_id
        self.action = action
        self.status = status
        self.ip = ip

        self.route = route
        self.method = method
        self.duration_ms = duration_ms
        self.request_id = request_id
        self.deployment = deployment