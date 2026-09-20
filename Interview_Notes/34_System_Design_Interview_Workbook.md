# 34. System Design Interview Workbook

**Status:** Practice workbook.  
**Goal:** Produce a complete senior-level design answer in 35-50 minutes and defend every major trade-off.

## 1. The answer structure

```text
requirements -> scale -> APIs -> data model -> high-level architecture
             -> consistency/failure -> scaling -> security/observability
             -> trade-offs and follow-ups
```

### Requirements (first 5 minutes)

Ask about users, core actions, read/write ratio, ordering, latency, availability, retention, correctness, privacy, regions, and cost. Separate functional requirements from non-functional requirements.

### Estimation (next 5 minutes)

Write assumptions before numbers:

```text
average RPS = daily requests / 86,400
peak RPS = average RPS * peak factor
storage = records/day * record size * retention * replication factor
bandwidth = RPS * payload size
```

Use round numbers and explain uncertainty. A wrong assumption is safer than an unexplained precise number.

### Design and deep dive

Start with the simplest architecture that meets requirements. Then choose database, cache, queue/event log, partitioning, replication, and failure handling based on stated constraints. Do not add Kafka, Redis, sharding, or microservices by reflex.

## 2. Twelve design drills

| Drill | Core requirements | Deep-dive topics |
|---|---|---|
| URL shortener | create/redirect links | ID generation, cache, hot keys, abuse |
| Notification platform | email/SMS/push delivery | preferences, retries, quotas, DLQ |
| Payment gateway | authorize/capture/refund | idempotency, ledger, callbacks, reconciliation |
| Order system | order, inventory, fulfillment | consistency, Saga, outbox, state machine |
| File storage | upload/download/share | object storage, metadata, permissions, multipart |
| Chat system | one-to-one/group messages | ordering, delivery, offline, fan-out |
| Rate limiter | per-user/tenant limits | token bucket, distributed state, fail-open |
| Job scheduler | delayed/repeated tasks | leasing, retries, fairness, cancellation |
| Audit platform | immutable searchable audit | schema, retention, PII, tamper evidence |
| Multi-tenant SaaS | tenant isolation and quotas | tenancy model, noisy neighbors, billing |
| Telecom onboarding | order to provisioning | workflow, compensation, external systems |
| RAG assistant | ingest and answer with sources | access filters, retrieval, evaluation, cost |

## 3. Reusable architecture checklist

- API gateway/load balancing and request authentication.
- Stateless application instances and session strategy.
- Database choice, keys, constraints, indexes, and transaction boundaries.
- Cache key, TTL, invalidation, stampede protection, and cache failure policy.
- Synchronous calls with deadlines and bounded retries.
- Async events with schema, partition key, delivery semantics, replay, and DLQ.
- Idempotency for commands, consumers, callbacks, and jobs.
- Consistency expectation for each read and write.
- Backpressure and resource limits.
- Multi-region, backup/restore, RPO, and RTO if required.
- Authorization, tenant isolation, encryption, secrets, and audit.
- Logs, metrics, traces, SLOs, alerts, and dashboards.
- Deployment, migration, rollback, and operational ownership.

## 4. Telecom onboarding answer skeleton

```text
React/consumer -> CRM API -> Order service -> workflow engine
                         |             |
                         v             v
                    catalog        provisioning adapter
                         |             |
                         v             v
                   billing/charging <- event bus
```

Requirements: create an order, validate eligibility, reserve resources, provision service, create billing state, notify the customer, and support retry/manual review. Make every external command idempotent by order ID and step key. Use a workflow state machine for timers and compensation. Use events for notifications and projections, but keep the source of truth explicit. Explain what happens if provisioning succeeds and billing fails.

## 5. Multi-tenant SaaS deep dive

Start with shared schema unless isolation requirements justify a stronger model. Every request carries trusted tenant context from authentication. Enforce it in queries, cache keys, event payloads, object paths, search filters, background jobs, and audit records. Add quotas and per-tenant rate limits. Design a noisy-neighbor policy and measure tenant-level latency, errors, usage, and cost without putting high-cardinality tenant IDs into every metric label.

## 6. RAG design deep dive

```text
documents -> parse/version -> chunk/metadata -> embed -> vector/lexical index
query -> authorize -> retrieve -> rerank -> bounded context -> model
      -> validate citations/answer -> abstain or respond -> trace/evaluate
```

Explain ingestion freshness, deletion, tenant filters, access revocation, prompt injection in documents, retrieval recall/precision, citation verification, model fallback, token budgets, and human approval for actions. Never promise zero hallucinations.

## 7. Common follow-ups

1. What is the single point of failure?
2. What happens when the database is slow or unavailable?
3. How do retries avoid duplicate effects?
4. How do you handle an out-of-order event?
5. How do you scale one hot key or tenant?
6. What data can be eventually consistent?
7. How do you migrate the schema without downtime?
8. How do you restore after corruption or region loss?
9. What metrics alert you before customers complain?
10. How is authorization enforced across asynchronous work?
11. What would you simplify for a smaller scale?
12. What would you redesign at ten times the traffic?

## 8. Scoring rubric

| Area | 0 | 1 | 2 |
|---|---|---|---|
| Requirements/assumptions | Missing | Vague | Explicit and testable |
| APIs/data model | Missing | Happy path only | Correct boundaries and constraints |
| Scale/performance | Hand-wavy | Components named | Measured bottlenecks and capacity logic |
| Reliability | Ignored | Retries only | Partial failure, idempotency, recovery |
| Security | Ignored | Authentication only | Authorization, privacy, secrets, audit |
| Operations | Ignored | Logs only | SLO, metrics, tracing, deploy/rollback |
| Trade-offs | One answer | Alternatives named | Decision tied to requirements |

Target at least 12/14 on each design before calling it interview-ready.

## 9. Practice schedule

Complete one design per week: first 60 minutes with notes, then 45 minutes without notes, then a 20-minute follow-up drill. Record the assumptions, diagram, weak answer, and one improvement.

