from reader import file_reader
from parser import log_parser
import requests

filereader = file_reader.FileReader("logs.txt")
parser = log_parser.LogParser()
for line in filereader.read_file_lines(1000):
    result = parser.process_line(line)
    if result.success:
        data = result.logdata
        payload = {
            "timestamp" : data.timestamp,
            "level" : data.level,
            "service" : data.service,
            "user_id" : data.user_id,
            "action" : data.action,
            "status" : data.status,
            "ip" : data.ip 
        }
        url = "http://localhost:8000/logs"
        response = requests.post(url,json=payload)
        print(response.status_code)