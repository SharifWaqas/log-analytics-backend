class result:
    def __init__(self,
                 success,
                 logdata,
                 error_type,
                 error_details,
                 raw_log):
        self.success = success
        self.logdata = logdata
        self.errortype = error_type
        self.errordetails = error_details
        self.rawlog = raw_log
    