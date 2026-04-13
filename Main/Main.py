from reader import file_reader
from parser import log_parser
from storage import sqlite_db
from analytics import AnalyticsService
import argparse



def run_ingestion(filepath, batchsize):
    totalcount = 0
    errors = 0
    db = sqlite_db.SQLiteDB("logs.db")
    valid_batch = []
    failed_batch = []
    db.create_valid_logs_table()
    db.create_failed_logs_table()
    logset = set()    

    data = file_reader.FileReader(filepath).read_file_lines(batchsize)
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
        if len(valid_batch) >= batchsize:
            db.insert_valid_logs(valid_batch)
            valid_batch.clear()
        if len(failed_batch) >= batchsize:
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
    file_path = args.file
    batch_size = args.batch_size
    ingestionresult = run_ingestion(file_path, batch_size)
    print("Ingestion Summary")
    print("-----------------")
    for key,value in ingestionresult.items():
        print(key,"     : ",value)

def handle_top_users(args):
    db = sqlite_db.SQLiteDB("logs.db")
    analysis = AnalyticsService(db)
    user_count = analysis.get_login_counts_per_user()
    print("Top Users")
    print("---------")
    for i in user_count:
        print(i[0] + " : " + str(i[1]))


def handle_error(args):
    db = sqlite_db.SQLiteDB("logs.db")
    analysis = AnalyticsService(db)
    error_rate = analysis.get_error_rate()
    if error_rate is None:
        print ("No Data Available")
    else:
        print(f"Error Rate: {error_rate*100:.2f}%")

def handle_log_failures(args):
    db = sqlite_db.SQLiteDB("logs.db")
    analysis = AnalyticsService(db)
    results = analysis.get_failed_login_counts_per_user()
    if results :
        print("Log Failures Per User")
        print("---------------------")
        for data in results:
            print(f"{data[0]} : {data[1]}")
    else:
        print("No data available")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command", required=True)
    

    ingest_parser = subparser.add_parser("ingest")
    top_user_parser = subparser.add_parser("top-users")
    error_rate_parser = subparser.add_parser("error-rate")
    log_failures_parser = subparser.add_parser("log-failures")
    

    ingest_parser.add_argument("--batch-size",type=int,default=1000,help="Number of logs processed per batch")
    ingest_parser.add_argument("--file",type=str,required=True, help="Path to the log file")
    ingest_parser.set_defaults(func=handle_ingest)
    

    top_user_parser.set_defaults(func=handle_top_users)    


    error_rate_parser.set_defaults(func=handle_error)

    log_failures_parser.set_defaults(func=handle_log_failures)
    
    args = parser.parse_args()    
    args.func(args)
