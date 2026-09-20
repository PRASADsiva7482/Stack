# 29. Production Troubleshooting Playbook

**Status:** Learning target.  
**Rule:** Diagnose with evidence before changing configuration. In an interview, narrate the investigation in time order.

## 1. Universal incident path

1. Confirm impact: affected endpoint, tenant, region, version, start time, and customer symptom.
2. Protect users: stop a rollout, shed optional work, disable a feature flag, or apply a safe rate limit.
3. Build a timeline from metrics, logs, traces, deployment events, and dependency health.
4. Form two or three hypotheses and test the cheapest one first.
5. Fix or mitigate with the smallest reversible action.
6. Verify recovery with user and business metrics, not only a green health endpoint.
7. Record root cause, contributing factors, detection gap, and prevention work.

Never expose customer data in commands, logs, screenshots, or interview examples. Use IDs such as `tenant-a` and `subscriber-1`.

## 2. Scenario matrix

| Symptom | Evidence to collect | Common root causes |
|---|---|---|
| API latency increased | p50/p95/p99, traces, thread and pool wait | Slow SQL, downstream timeout, lock, GC, saturation |
| CPU near 100% | process/thread CPU, profile, GC | Hot loop, serialization, regex, GC, contention |
| Heap grows | heap trend, GC, histogram, dump | Cache, collection, ThreadLocal, unclosed resource |
| OOM | error type, dump, cgroup limit | Heap leak, native memory, direct buffers, too many threads |
| Thread pool exhausted | active/queued/rejected, thread dump | Blocking I/O, deadlock, unbounded work, slow dependency |
| DB pool exhausted | active/idle/pending, transaction time | Leaks, long transactions, slow query, pool too small |
| Slow SQL | `EXPLAIN`, rows examined, locks, query history | Missing index, bad join, stale stats, offset scan |
| Deadlock | database deadlock report, transaction order | Opposite lock order, large transaction, missing index |
| Kafka lag | consumer lag, poll time, partitions, errors | Slow handler, rebalance, poison message, under-partitioning |
| Duplicate events | key, offset, processing record | At-least-once delivery, retry, non-idempotent handler |
| Redis unavailable | timeout/error rate, memory, evictions | Node failure, network, maxmemory, hot key, pool |
| Downstream unavailable | status, connect/read timeout, retries | Outage, DNS/TLS, retry storm, bad endpoint |
| Pod restarts | events, exit code, probes, limits | OOMKill, liveness failure, crash, rollout |
| Auth failures | issuer/audience/clock, JWKS, Keycloak health | Wrong config, key rotation, expiry, mapping |
| Deployment regression | version, flags, error diff, schema | Incompatible API/schema, config, untested path |

## 3. Complete examples

### A. API latency after deployment

**Symptoms:** p99 and timeout rate rise after a version change.

**Investigation:** Compare old/new instances; inspect traces for the first slow span; check SQL time, downstream time, connection-pool pending, thread states, GC pause, request size, and error logs. Compare query plans and configuration. Do not assume the application code is the only change.

**Mitigation:** Stop rollout or shift traffic back if safe, disable the feature, reduce optional fan-out, or apply a bounded timeout. Fix the measured bottleneck, add a regression/load test, and add a dashboard linking endpoint -> trace -> SQL/dependency.

### B. CPU at 100%

Use `top -H -p PID`, map the hot thread ID to a Java dump, then profile before killing the process. Check GC CPU, busy loops, lock contention, JSON/regex parsing, compression, and traffic volume. A scale-out may hide the symptom but not fix a hot algorithm.

### C. Memory growth or OOM

Distinguish Java heap, native memory, direct buffers, metaspace, and container cgroup OOM. Capture a histogram and, when safe, a heap dump. Use a dominator tree to find retained objects. Common fixes are bounded caches with TTL, correct `ThreadLocal` cleanup, streaming/paging, closing resources, and setting JVM memory percentages consistently with the container limit.

### D. Thread pool exhaustion

Inspect active count, queue depth, rejection count, task duration, and thread dumps. If many threads wait on a downstream call, fix timeouts and bulkheads rather than blindly increasing the pool. Bound the queue, classify work, propagate cancellation/deadlines, and test behavior when the dependency is slow.

### E. Database connection pool exhaustion

Check active/pending/idle connections, transaction duration, leak detection, slow queries, and database wait events. Confirm every connection returns on success and exception. Long transactions, streaming results held open, and a pool larger than the database capacity are frequent causes.

### F. Slow query or deadlock

Capture the exact SQL and parameters safely, run `EXPLAIN`, examine estimated versus actual rows, indexes, lock waits, and query duration. For deadlocks, inspect the cycle and ensure transactions acquire resources in a consistent order. Reduce transaction scope, index the predicate, process in stable chunks, and retry only transactions known to be safely retryable.

### G. Kafka lag and duplicates

Measure lag by partition, consumer processing time, poll interval, rebalance events, batch size, and downstream waits. Preserve ordering only within a partition. Commit after successful processing when reprocessing is acceptable; make handlers idempotent with an event ID or business key. Use retry topics/DLQ for poison messages and monitor DLQ age.

### H. Redis failure or stampede

Decide whether Redis is a cache or a correctness dependency. For a cache, fail open to the database only with a bounded fallback and rate protection. For a lock or idempotency record, fail closed for unsafe writes. Use TTL jitter, single-flight/mutex where appropriate, key namespaces, and memory/eviction monitoring.

### I. Kubernetes pod restart

Run `kubectl describe pod`, inspect events and previous logs, check exit code, `OOMKilled`, probes, requests/limits, startup duration, and dependency readiness. Liveness must not be a database health check. Fix the actual failure; raising probe thresholds without understanding startup can mask a crash.

### J. Authentication failures

Check token issuer, audience, signature/JWKS availability, expiry, clock skew, required scopes/roles, CORS, and the resource-server filter chain. A valid JWT is not automatically authorized for every endpoint. Avoid logging full tokens.

## 4. RCA template

```text
Impact:
Detection:
Timeline:
Trigger:
Root cause:
Contributing factors:
Mitigation:
Permanent fix:
How verified:
Detection/prevention:
Owner and due date:
```

Root cause is the condition that explains the evidence, not the last visible error. “Database was slow” is a symptom; “a new query caused a full scan because the predicate lacked the intended composite index” is a testable cause.

## 5. Interview questions

1. API p99 doubled after deployment. What do you do first?
2. CPU is high but traffic is normal. How do you distinguish GC from code?
3. Heap rises every hour. What evidence do you capture?
4. Why not increase the thread pool?
5. How do you diagnose a connection-pool leak?
6. How do you prove a SQL index helped?
7. How do you resolve a deadlock safely?
8. What causes Kafka duplicates and how do you prevent double effects?
9. What is the difference between lag and consumer downtime?
10. Should a cache outage fail the request?
11. Why can a liveness probe cause an outage?
12. How do you investigate JWT failures without logging secrets?

## 6. Practice

Create a local service with deliberately slow SQL, a delayed downstream, a bounded executor, a Kafka-like queue, and a cache. For each fault, capture a timestamped incident note, one metric, one log, one trace or stack signal, the hypothesis, mitigation, and regression test.

