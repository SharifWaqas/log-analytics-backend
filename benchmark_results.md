# Performance Results

## Benchmark 1: Naive HTTP Client
Single requests.post() per request

Throughput: 46.63 logs/sec

## Benchmark 2: Session Reuse
Single-thread requests.Session()

Throughput: 246.29 logs/sec

Improvement:
~5.3x increase over Benchmark 1

## Benchmark 3: 4-Thread Concurrent Sender
4 concurrent sender threads
requests.Session() per thread

Throughput: 921.43 logs/sec

Improvement:
~3.7x increase over Benchmark 2
~19.8x increase over Benchmark 1

## Key Findings

- Reusing HTTP connections significantly reduced overhead.
- Concurrent request generation increased throughput substantially.
- The combination of connection pooling and concurrency achieved nearly 20x higher throughput than the baseline implementation.