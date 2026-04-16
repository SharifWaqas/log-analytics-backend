from fastapi import FastAPI
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
def top_users(limit: int=10):
    user_count = analysis.get_login_counts_per_user(limit)
    if len(user_count) == 0:
        return {"message": "No data available"}
    else:
        result = []
        for data in user_count:
            result.append({"user_id": data[0], "count": data[1]})        
        return result

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
