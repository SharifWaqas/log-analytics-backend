import random
import datetime

class Generator:
    def Generate_Logs(self, Lines):
        with open("Logs.txt", "w") as file:    
            STARTTIME = datetime.datetime.now()
            LEVEL = ["INFO","ERROR","INFO","INFO","INFO","INFO","INFO","INFO","ERROR", "INFO"]
            SERVICE = ["auth", "orders", "payments"] 
            ACTIONS = {"auth": "login", "orders": "create_order", "payments": "charge"}
            STATUS = [200,401,500,503,200,200,200,200,200,401,401,401,500,200]
            for k in range(Lines):
                randomservice = random.choice(SERVICE)            
                IP = ("192.168.1.") + str(random.randint(1,255))
                USER_ID = random.randint(1,1000)
                returnline = str(STARTTIME + datetime.timedelta(seconds=k)) + "," + random.choice(LEVEL) + "," + randomservice + "," + "user=" + str(USER_ID) + "," + "action=" + ACTIONS[randomservice] + "," + "status=" + str(random.choice(STATUS)) + "," + "ip=" + IP
                file.write(returnline + "\n")


    