from reader import file_reader
from parser import log_parser
import requests
import time


filereader = file_reader.FileReader("logs.txt")
parser = log_parser.LogParser()

total_lines = 0
successful_logs = 0
failed_logs = 0
counter = 0
session = requests.Session()
start_time = time.time()
for line in filereader.read_file_lines():

    counter += 1

    if counter % 100 == 0:
        print("Reached", counter)

    total_lines += 1

    result = parser.process_line(line)

    if result.success:

        successful_logs += 1

        data = result.logdata

        payload = {
            "timestamp": data.timestamp,
            "level": data.level,
            "service": data.service,
            "user_id": data.user_id,
            "action": data.action,
            "status": data.status,
            "ip": data.ip
        }

        url = "http://127.0.0.1:8000/logs"

        response = session.post(
            url,
            json=payload,
            timeout=5
        )

    else:
        failed_logs += 1

end_time = time.time()

runtime = end_time - start_time
throughput = successful_logs / runtime if runtime > 0 else 0

print("\n===== SENDER SUMMARY =====")
print("Total Lines:", total_lines)
print("Successful Logs:", successful_logs)
print("Failed Logs:", failed_logs)
print(f"Runtime: {runtime:.2f} seconds")
print(f"Throughput: {throughput:.2f} logs/sec")