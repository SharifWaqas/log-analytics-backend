# Log Ingestion & Analytics Engine

A high-throughput backend log ingestion and analytics system built in Python using FastAPI, PostgreSQL, queue-based buffering, batching, and threaded background workers.

This project was built to explore backend systems engineering concepts such as asynchronous processing, concurrency, ingestion pipelines, batching, retry handling, and analytics infrastructure.

---

# Architecture

<p align="center">
  <img src="assets/architecture.png" width="850">
</p>

---

# System Flow

```text
Log Sender
→ FastAPI API
→ Shared In-Memory Queue
→ Background Worker Thread
→ PostgreSQL Database
→ Analytics Endpoints
```

---

# Features

- FastAPI-based ingestion API
- Queue-based buffering architecture
- Shared in-memory queue system
- Threaded background worker processing
- Batch PostgreSQL inserts
- Retry handling for failed database writes
- Analytics and monitoring endpoints
- Cursor-based pagination for large query results
- Modular layered backend architecture

---

# Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQL
- Threading
- REST APIs
- Object-Oriented Programming (OOP)

---

# API Endpoints

## Ingestion

### POST `/logs`

Accepts structured log events and enqueues them for background processing.

Example payload:

```json
{
  "timestamp": "2026-05-23T12:00:00",
  "level": "INFO",
  "service": "auth-service",
  "user_id": 42,
  "action": "login",
  "status": 200,
  "ip": "127.0.0.1"
}
```

---

# Analytics Endpoints

### GET `/stats/logs-per-second`

Returns ingestion throughput metrics.

---

### GET `/stats/queue-size`

Returns current queue size.

---

### GET `/stats/error-rate`

Returns system error rate metrics.

---

### GET `/stats/top-users`

Returns top users based on log activity with filtering and pagination support.

---

### GET `/stats/failed-logins`

Returns failed login statistics.

---

# Project Structure

```text
log-engine/
│
├── api/
├── analytics/
├── ingestion/
├── models/
├── parser/
├── storage/
├── assets/
├── sample_data/
│
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

---

# Running The Project

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Start FastAPI Server

```bash
python -m uvicorn api.server:app --reload
```

## 3. Start Synthetic Traffic Generator

```bash
python -m ingestion.sender
```

After starting the FastAPI server, open:

```text
http://127.0.0.1:8000/docs
```
<p align="center">
  <img src="assets/swagger-ui.jpeg" width="850" alt="Swagger UI Documentation">
</p>

This launches the interactive Swagger UI where you can:
- test ingestion endpoints
- query analytics endpoints
- inspect request/response schemas
- explore API functionality directly from the browser
---
## Sample Analytics Response

```json
{
  "logs_per_second": 142,
  "queue_size": 18,
  "error_rate": 0.03
}
```
## Example Analytics Endpoints

```text
GET /stats/logs-per-second
GET /stats/queue-size
GET /stats/error-rate
GET /stats/top-users
GET /stats/failed-logins
```

Example:

```text
http://127.0.0.1:8000/stats/top-users
```

# Key Concepts Explored

- Backend ingestion pipelines
- Queue-based architectures
- Multithreaded worker systems
- Shared-memory concurrency
- Batch database processing
- Retry handling strategies
- Analytics query optimization
- API design and validation

---

# Future Improvements

- Thread-safe queue implementation
- Redis/Kafka integration
- Docker deployment
- Load and stress testing
- Monitoring dashboards
- Multiple worker scaling
- Distributed ingestion architecture

---

# Learning Goals

This project was built as a hands-on way to learn backend systems engineering by designing and implementing infrastructure-focused systems from scratch rather than relying solely on tutorials or simple CRUD applications.