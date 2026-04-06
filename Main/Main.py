from reader import file_reader
from parser import log_parser
from storage import sqlite_db
import argparse



def run_ingestion():
    totalcount = 0
    errors = 0
    db = sqlite_db.SQLiteDB("logs.db")
    valid_batch = []
    failed_batch = []
    db.create_valid_logs_table()
    db.create_failed_logs_table()
    logset = set()    

    data = file_reader.FileReader().read_file_lines(1000)
    for line in data:
        parsed = log_parser.LogParser().process_line(line)
        totalcount += 1
        if parsed.success:
            logset.add(parsed.logdata.user_id)
            valid_batch.append(parsed.logdata)
            if parsed.logdata.level == "ERROR":
                errors += 1
        else:
            failed_batch.append(parsed)    
        if len(valid_batch) >= 1000:
            db.insert_valid_logs(valid_batch)
            valid_batch.clear()
        if len(failed_batch) >= 1000:
            db.insert_failed_logs(failed_batch)
            failed_batch.clear()
    if len(valid_batch) != 0:
        db.insert_valid_logs(valid_batch)
        valid_batch.clear()
    if len(failed_batch) != 0:
        db.insert_failed_logs(failed_batch)
        failed_batch.clear()

    returnDict = {"total_log_count": totalcount,
                 "error_count": errors,
                 "unique_user_count": len(logset)}
    return(returnDict)

def handle_ingest(args):
    ingestionresult = run_ingestion()
    print("Ingestion Summary")
    print("-----------------")
    for key,value in ingestionresult.items():
        print(key,"     : ",value)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    args = parser.parse_args()
    command_dictionary = {"ingest": handle_ingest}
    if args.command in command_dictionary:
        function = command_dictionary[args.command]
        function(args)
    else:
        print("Available Commands")
        print("-----------------")
        for key in command_dictionary:
            print(key + "\n")

    

