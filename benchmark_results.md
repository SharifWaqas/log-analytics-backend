# Benchmark Results

This document records measured performance results and validation data for the Log Ingestion & Analytics Engine.

Historical ingestion benchmarks are preserved separately from SafeStep application telemetry measurements. SafeStep measurements below were collected during local development and are validation results, not production performance or reliability claims.

---

## 1. Historical Log Ingestion Benchmarks

These benchmarks evaluate the log ingestion pipeline itself.

| Benchmark | Throughput |
|---|---:|
| Single `requests.post()` | 46.63 logs/sec |
| Single-thread `requests.Session()` | 246.29 logs/sec |
| 4-thread concurrent sender | 921.43 logs/sec |

### Key Findings

- Reusing HTTP connections significantly reduced request overhead.
- Concurrent request generation substantially increased ingestion throughput.
- The final implementation reached approximately 20× the baseline throughput.

These results describe the ingestion pipeline and should not be conflated with SafeStep API latency measurements.

---

## 2. SafeStep Observability Validation

### Date

September 27, 2026

### Environment

Local development environment using:

- SafeStep backend
- Log Analytics Engine
- PostgreSQL
- Structured telemetry ingestion through `POST /logs/structured`

Telemetry was sent asynchronously so delivery to the analytics engine was not part of the SafeStep request's critical path.

### Validation Objective

The integration was exercised with real SafeStep application telemetry to validate:

- structured log ingestion
- queue-based processing
- PostgreSQL persistence
- percentile latency queries
- endpoint aggregation
- request correlation
- HTTP error analytics
- AI-provider analytics
- fallback analytics

The measurements below come from a small local development dataset.

---

## 3. Request Latency

One local 24-hour analytics snapshot contained:

| Metric | Result |
|---|---:|
| Samples | 18 |
| p50 | 3.59 ms |
| p95 | 2766.17 ms |
| p99 | 8121.90 ms |

These values are a local validation snapshot rather than a representative production latency distribution.

---

## 4. Analysis Latency

One measured SafeStep analysis produced:

| Metric | Result |
|---|---:|
| Samples | 1 |
| p50 | 8714.81 ms |
| p95 | 8714.81 ms |
| p99 | 8714.81 ms |

Because this sample contains only one analysis, the percentile values are identical and should not be interpreted as stable percentile estimates.

---

## 5. AI Latency

The corresponding AI workflow produced:

| Metric | Result |
|---|---:|
| Samples | 1 |
| p50 | 7603.64 ms |
| p95 | 7603.64 ms |
| p99 | 7603.64 ms |

For this observed analysis, AI processing accounted for approximately 87% of the total analysis duration.

### Additional Local Timing Observations

Later local runs showed the following approximate ranges:

| Stage | Observed Duration |
|---|---:|
| OpenAI / AI latency | 9.28–11.06 s |
| Analysis workflow | 11.50–13.48 s |
| HTTP request | 13.45–15.43 s |

These are individual observations rather than representative percentile measurements.

---

## 6. Analysis Reliability

A local validation window recorded:

| Metric | Result |
|---|---:|
| Successful analyses | 4 |
| Failed analyses | 0 |
| Success rate | 100% |

This was a small local validation dataset.

---

## 7. AI Fallback Validation

The same validation window recorded:

| Metric | Result |
|---|---:|
| Analyses | 4 |
| NVIDIA fallback events | 0 |
| Fallback rate | 0% |

No NVIDIA fallback was observed during this validation window.

This result demonstrates that the fallback telemetry path was available for measurement; it does not establish long-term provider reliability.

---

## 8. Error Handling Validation

### Unauthorized Request

A real local unauthorized upload request produced:

```text
HTTP 401
POST /uploads
```

### Controlled Server Error

A controlled local server-error test produced:

```text
HTTP 500
action = request_failed
```

The 500 telemetry event was persisted in PostgreSQL and included in the server-error analytics.

### Resulting Error Analytics Snapshot

| Metric | Result |
|---|---:|
| Total requests | 21 |
| Server errors | 1 |
| Client errors | 1 |
| Server error rate | 4.76% |
| Client error rate | 4.76% |

This was a controlled local validation dataset and must not be interpreted as a production error rate.

---

## 9. Request Correlation Validation

SafeStep generated request IDs in HTTP middleware and propagated the same identifier through the analysis workflow.

A single analysis request could therefore be correlated across:

```text
request_completed
    │
    ├── ai_openai_completed
    ├── ai_analysis_completed
    └── analysis_completed
```

This allowed validation of request-level tracing from the HTTP layer through the analysis service and AI workflow.

---

## 10. Route Normalization Validation

Dynamic SafeStep routes were recorded using FastAPI route templates.

Example:

```text
/analyses/{upload_id}
```

rather than creating a separate analytics endpoint for every analysis UUID.

CORS `OPTIONS` requests were excluded from application request analytics.

---

## 11. Measurement Limitations

The SafeStep measurements in this document were collected from local development traffic and a small number of test requests.

They should not be treated as:

- production SLIs
- production SLOs
- representative user traffic
- production-scale throughput measurements
- production reliability rates

Future production-scale benchmark entries should record:

- date
- environment
- sample count
- measurement window
- metric
- methodology
- measured result
- limitations

Historical benchmark results should be preserved rather than overwritten.

---

## 12. Future Benchmark Work

Future measurements can extend this document with:

- larger SafeStep traffic samples
- sustained concurrent request load
- AI-provider latency distributions
- observed fallback frequency across larger datasets
- endpoint-level latency comparisons
- queue saturation behavior
- ingestion throughput under increasing concurrency
- multi-worker or distributed deployments
- production observability measurements
