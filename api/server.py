from fastapi import FastAPI
from fastapi import Query
from analytics.queries import AnalyticsService
from storage.postgres_db import PostgreSQLDB


app = FastAPI()
db = PostgreSQLDB()
analysis = AnalyticsService(db)

@app.get("/stats/error-rate")
def error_rate():
    error_val = analysis.get_error_rate()
    if error_val is None:
        return {"message": "No data available"}
    else:
        return {"error_rate": error_val}

@app.get("/stats/top-users")
def top_users(limit: int = Query(10, ge=1, le=100),last_user_count: int |None = Query(None), last_user_id: int | None = Query(None),hours: int = Query(24,ge=1,le=168), service: str | None = Query(None), status: int | None = Query(None)):
    user_count = analysis.get_login_counts_per_user(limit,hours,service,status,last_user_count,last_user_id)
    len_user_count = len(user_count)
    meta_info = {"limit":limit, "hours":hours,"service":service,"status":status, "result_count":len_user_count}
    result = []
    for data in user_count:
        result.append({"user_id": data[0], "count": data[1]})
    if len_user_count == 0:
        next_cursor = None       
    else:
        last_row = user_count[-1]
        next_cursor = {
        "user_count": last_row[1],
        "user_id": last_row[0]
        }
    
    return {"data": result,
            "meta": meta_info,
            "next_cursor": next_cursor,
            "error": None}
        

@app.get("/stats/failed-logins")
def failed_logins():
    user_failed_login = analysis.get_failed_login_counts_per_user()
    if len(user_failed_login) == 0:
        return {"message": "No data available"}
    else:
        result = []
        for data in user_failed_login:
            result.append({"user_id": data[0], "failure_count": data[1]})        
    return result
