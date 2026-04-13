from models import log_data
from parser.parse_result import result
class LogParser:    
    def valid_input(self, dataVal, DataKey):
        tempVal = dataVal.split("=")
        if len(tempVal) == 2:
            if tempVal[1]:
                if tempVal[0] == DataKey:
                    return (tempVal[1], "Valid")
                else:
                    return (None, "Incorrect Key")
            else:
                return (None, "Missing Value")
        else:
            return (None, "Invalid Format")
    def process_line(self, Logs):
        
        errors = []

        logsT = Logs.strip()
        datasingle = logsT.split(",")
        
        if len(datasingle) == 7:
                        
            timestamp = datasingle[0]
            level = datasingle[1]
            service = datasingle[2]

            usertemp = self.valid_input(datasingle[3], "user")
            userid_value = usertemp[0]
            userid_status = usertemp[1]
            
            actiontemp = self.valid_input(datasingle[4], "action")
            action_value = actiontemp[0]
            action_status = actiontemp[1]

            statustemp = self.valid_input(datasingle[5], "status")
            status_value = statustemp[0]
            status_status = statustemp[1]
            
            iptemp = self.valid_input(datasingle[6], "ip")
            ip_value = iptemp[0]
            ip_status = iptemp[1]

            logobject = log_data.LogData(timestamp,level,service,userid_value,action_value,status_value,ip_value)

            if userid_status != "Valid":
                idtoappend = ("User Id", userid_status)
                errors.append(idtoappend)
            
            if action_status != "Valid":
                actiontoappend = ("Action", action_status)
                errors.append(actiontoappend)

            if status_status != "Valid":
                statustoappend = ("Status", status_status)
                errors.append(statustoappend)
            
            if ip_status != "Valid":
                iptoappend = ("Ip", ip_status)
                errors.append(iptoappend)

            if errors:
                parseobject = result(False, logobject, "Errors", errors, logsT)
            else:
                parseobject = result(True, logobject, None, None, None)
        else:
            parseobject = result(False, None, "Not Correct Lenght", "The lenght of Log isnt correct", logsT)
        return parseobject
