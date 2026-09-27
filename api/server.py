from fastapi import FastAPI
from fastapi import Query
from fastapi import HTTPException
from analytics.queries import AnalyticsService
from storage.postgres_db import PostgreSQLDB
from parser import log_parser
from models import log_data
from app import shared_queue
from app import metric_object
import time
from pydantic import BaseModel


app = FastAPI()
db = PostgreSQLDB()
analysis = AnalyticsService(db)
parser = log_parser.LogParser()

class StructuredLog(BaseModel):
    timestamp: str
    level: str
    service: str
    user_id: int | None = None
    action: str
    status: int
    ip: str | None = None
    route: str | None = None
    method: str | None = None
    duration_ms: float | None = None
    request_id: str | None = None
    deployment: str | None = None


@app.post("/logs/structured")
def receive_structured_log(log: StructuredLog):
    log_object = log_data.LogData(
        timestamp=log.timestamp,
        level=log.level,
        service=log.service,
        user_id=log.user_id,
        action=log.action,
        status=log.status,
        ip=log.ip,
        route=log.route,
        method=log.method,
        duration_ms=log.duration_ms,
        request_id=log.request_id,
        deployment=log.deployment,
    )

    enqueue_success = shared_queue.enqueue(log_object)

    if not enqueue_success:
        raise HTTPException(
            status_code=503,
            detail="Queue Full"
        )

    return {"status": "accepted"}

@app.post("/logs")
def recieve_log(log: dict):
    required_fields = ["timestamp","level","service","user_id","action","status","ip"]
    missing_fields = []
    for field in required_fields:
        if field not in log:
            missing_fields.append(field)
    if len(missing_fields) == 0: 
        timestamp = str(log["timestamp"])
        level = str(log["level"])
        service = str(log["service"])
        user_id = str(log["user_id"])
        action = str(log["action"])
        status = str(log["status"])
        ip = str(log["ip"])
        
        line = timestamp+ "," + level + "," + service + "," + "user=" + user_id + "," + "action=" + action + "," + "status=" + status + "," + "ip=" + ip
        return_line = parser.process_line(line)  
        if not return_line.success:
            raise HTTPException(status_code=400, detail="Invalid log")
        else:
            enqueue_success = shared_queue.enqueue(return_line.logdata)
            if enqueue_success:
                return {"status": "accepted"}
            else:
                raise HTTPException(status_code=503, detail="Queue Full")
    else:
        raise HTTPException(status_code=400, detail={"missing_Field": missing_fields})

@app.get("/stats/total-logs")
def total_logs():
    return {
        "total_logs": metric_object.total_processed_logs,
        "recent_logs": metric_object.recent_logs
    }

@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/stats/logs-per-second")
def logs_per_second():
    elapsed_time = time.time() - metric_object.last_reset_time
    if elapsed_time == 0:
        return {"Logs-per-second": 0}
    result = metric_object.recent_logs / elapsed_time
    metric_object.recent_logs = 0
    metric_object.last_reset_time = time.time()
    return {"Logs-per-second": round(result, 2)}

@app.get("/stats/queue-size")
def queue_size():
    return {"Queue_Size": shared_queue.get_number_of_logs()}

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


@app.get("/stats/safestep/request-latency")
def safestep_request_latency(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_request_latency(
            hours
        ),
    }


@app.get("/stats/safestep/analysis-latency")
def safestep_analysis_latency(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_analysis_latency(
            hours
        ),
    }


@app.get("/stats/safestep/ai-latency")
def safestep_ai_latency(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_ai_latency(
            hours
        ),
    }


@app.get("/stats/safestep/endpoints")
def safestep_endpoints(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_endpoint_latency(
            hours
        ),
    }


@app.get("/stats/safestep/errors")
def safestep_errors(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_error_rate(
            hours
        ),
    }


@app.get("/stats/safestep/analysis")
def safestep_analysis(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_analysis_success_rate(
            hours
        ),
    }


@app.get("/stats/safestep/ai-providers")
def safestep_ai_providers(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_ai_provider_stats(
            hours
        ),
    }


@app.get("/stats/safestep/fallback")
def safestep_fallback(
    hours: int = Query(24, ge=1, le=720),
):
    return {
        "service": "safestep-api",
        "hours": hours,
        "data": analysis.get_safestep_ai_fallback_rate(
            hours
        ),
    }