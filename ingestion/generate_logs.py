from reader import file_reader
from parser import log_parser
import requests
import threading
import time

parser = log_parser.LogParser()
filereader = file_reader.FileReader("logs.txt")
log_list = list(filereader.read_file_lines())
lst_one = log_list[0:2500]
lst_two = log_list[2500:5000]
lst_three = log_list[5000:7500]
lst_four = log_list[7500:10000]
results = []


def send_logs(chunk):
    success_count = 0
    failed_count = 0
    session = requests.Session()
    for log in chunk:
        result = parser.process_line(log)
        if result.success:
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
            try:

                response = session.post(
                    "http://127.0.0.1:8000/logs",
                    json=payload,
                    timeout=5
                )

                if response.status_code == 200:
                    success_count += 1
                else:
                    failed_count += 1

            except:
                failed_count += 1

        else:
            failed_count += 1

    results.append((success_count, failed_count))


start_time = time.time()

t1 = threading.Thread(target=send_logs, args=(lst_one,))
t2 = threading.Thread(target=send_logs, args=(lst_two,))
t3 = threading.Thread(target=send_logs, args=(lst_three,))
t4 = threading.Thread(target=send_logs, args=(lst_four,))

t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()

end_time = time.time()

total_success = 0
total_failed = 0

for success, failed in results:
    total_success += success
    total_failed += failed

runtime = end_time - start_time
throughput = total_success / runtime if runtime > 0 else 0

print("\n===== MULTI-THREAD BENCHMARK =====")
print("Successful Logs:", total_success)
print("Failed Logs:", total_failed)
print(f"Runtime: {runtime:.2f} seconds")
print(f"Throughput: {throughput:.2f} logs/sec")