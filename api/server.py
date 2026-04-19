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
def top_users(limit: int = Query(10, ge=1, le=100),offset: int = Query(0, ge=0,le=10000),hours: int = Query(24,ge=1,le=168), service: str | None = Query(None), status: int | None = Query(None), order: str | None = Query(None)):
    order_temp = ["ASC", "DESC"]
    if order.upper() not in order_temp:
        validated_order = "DESC"
    else:
        validated_order = order.upper()
    user_count = analysis.get_login_counts_per_user(limit,hours,service,status,validated_order,offset)
    len_user_count = len(user_count)
    meta_info = {"limit":limit, "offset":offset, "hours":hours,"service":service,"status":status, "result_count":len_user_count, "Order":validated_order}
    result = []
    for data in user_count:
        result.append({"user_id": data[0], "count": data[1]})
    return {"data": result,
            "meta": meta_info,
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
