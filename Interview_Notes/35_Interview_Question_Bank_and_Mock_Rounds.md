# Interview Question Bank and Mock Rounds

This workbook is the practice companion for the technical notes. It is not a list to memorize. For each question, first answer aloud, then check the answer shape and connect it to a real example, a lab, or an explicitly labelled learning example.

## 1. The answer method

Use this structure for most technical questions:

1. Define the concept in one or two sentences.
2. Explain the mechanism or request/data flow.
3. State the trade-off, failure mode, or limitation.
4. Give a small example.
5. Connect it to verified experience only when the resume supports it.
6. Say how you would test, measure, or troubleshoot it.

For a question you have not used in production, say: “I have not owned that in production yet. My understanding is … I would validate it by …” That is stronger than inventing an experience claim.

## 2. Resume and behavioral bank

| # | Question | Strong answer must cover |
|---:|---|---|
| 1 | Tell me about yourself. | Present role, Java/Spring/CRM platform scope, production-support mindset, next product-company direction; keep it to 90 seconds. |
| 2 | Walk me through your most important project. | Business problem, users, architecture, your ownership, one hard decision, validation, result. |
| 3 | What exactly did you own? | Separate personal contribution from team output; name modules, APIs, workflows, tests, reviews, and support you actually handled. |
| 4 | Describe a production incident. | Impact, timeline, evidence, containment, root cause, permanent fix, regression prevention. |
| 5 | Tell me about a disagreement. | Different technical views, decision criteria, communication, result, lesson. |
| 6 | A requirement is ambiguous. What do you do? | Clarify actor/state/rules, examples, acceptance criteria, edge cases, written confirmation. |
| 7 | Tell me about a mistake. | What was missed, how it was detected, recovery, process/code change, no blame shifting. |
| 8 | How do you prioritize defects and features? | Customer impact, severity, risk, dependencies, reversibility, deadlines, stakeholder alignment. |
| 9 | How do you review code? | Correctness, failure paths, readability, security, transactions, performance, tests, operability. |
| 10 | How do you learn an unfamiliar technology? | Narrow problem, official docs, small spike, failure tests, review, production-readiness checklist. |
| 11 | Why move from consulting/enterprise delivery to product? | Long-term ownership, feedback loops, domain depth, measurable quality; never criticize prior employer. |
| 12 | Why this company or role? | Specific product/user problem, role fit, relevant evidence, thoughtful question. |

## 3. Core Java, JVM, and concurrency

| # | Question | Strong answer must cover |
|---:|---|---|
| 13 | Explain `equals()` and `hashCode()`. | Contract, equal objects require equal hash codes, immutability while hashed, `HashMap` lookup consequences. |
| 14 | `ArrayList` versus `LinkedList`? | Array locality/random access, insertion cost depends on position and traversal, why `ArrayList` is usually the default. |
| 15 | How does `HashMap` work? | Hash spread, bucket selection, equality check, collisions, resize/load factor; avoid promising exact internals across JDKs. |
| 16 | What is type erasure? | Generic checks mainly at compile time, runtime limitations, raw types, why casts can still fail. |
| 17 | Checked versus unchecked exceptions? | Recoverable contract versus programming/state/configuration failures; consistent boundary handling and useful context. |
| 18 | Why are immutable objects useful? | Safe sharing, stable keys, simpler concurrency, defensive copying, final fields and construction invariants. |
| 19 | Stream versus loop? | Declarative transformations, laziness, readability, debugging, side effects, parallel-stream caution. |
| 20 | `map`, `flatMap`, `filter`, and `reduce`? | Cardinality and data flow; empty inputs; avoid reduction with non-associative or stateful operations. |
| 21 | `synchronized` versus `Lock`? | Mutual exclusion/visibility, interruptible/timed lock and conditions, always release explicit locks. |
| 22 | `volatile` versus atomic classes? | Visibility/order versus atomic compound operations; `volatile++` is not atomic. |
| 23 | What is a race condition? | Interleaving-dependent result, shared mutable state, minimal reproduction, lock/atomic/ownership fix. |
| 24 | What causes deadlock? | Mutual exclusion, hold-and-wait, no preemption, circular wait; global lock order, timeout, smaller critical sections. |
| 25 | How does `ExecutorService` work? | Queue, worker threads, saturation, rejection, shutdown, bounded resources, context propagation. |
| 26 | `CompletableFuture` pitfalls? | Exception path, timeout, executor choice, blocking joins, cancellation, request-scope context. |
| 27 | Heap, stack, metaspace, and off-heap? | Object allocation/lifetime, per-thread stacks, class metadata, native/direct memory; distinguish symptom from cause. |
| 28 | What is GC pressure? | Allocation rate, object retention, live set, pauses/CPU, measurement with JFR/GC logs/heap evidence. |
| 29 | How would you investigate high CPU? | Process/thread evidence, hot thread to stack, GC/compiler possibility, recent change, safe mitigation. |
| 30 | Why can a correct algorithm still be slow? | Allocation, cache locality, I/O, contention, poor constant factors, database/network behavior, measurement. |

## 4. Spring, JPA, SQL, and REST

| # | Question | Strong answer must cover |
|---:|---|---|
| 31 | What does Spring dependency injection solve? | Inversion of control, composition, test seams, lifecycle; avoid service-locator coupling. |
| 32 | Constructor injection versus field injection? | Required dependencies, immutability, early failure, testability, explicit design. |
| 33 | Explain a Spring request path. | Filter/security chain, dispatcher, controller, validation, service, repository, transaction, serialization, error mapping. |
| 34 | What does `@Transactional` actually mean? | Proxy boundary, transaction manager, commit/rollback, propagation/isolation, self-invocation caveat. |
| 35 | Why might a transaction not roll back? | Checked exception rules, caught exception, proxy bypass, wrong transaction manager, async boundary, database engine. |
| 36 | Lazy versus eager loading? | Query timing, session boundary, N+1 risk, fetch join/entity graph, payload and memory trade-offs. |
| 37 | What is the N+1 problem? | One parent query plus per-parent child queries; detect in SQL logs/metrics; batch/fetch/projection alternatives. |
| 38 | Optimistic versus pessimistic locking? | Conflict frequency, version check, blocking/DB lock, retries, user-visible conflict behavior. |
| 39 | JPA entity versus DTO? | Persistence identity/lifecycle versus API contract; avoid leaking entities and accidental lazy loads. |
| 40 | How do you tune a slow query? | Reproduce, inspect plan, cardinality/selectivity, indexes, predicates, joins, returned columns, lock/wait, regression test. |
| 41 | What makes an index useful? | Leading columns, selectivity, query shape, sort/join use, write/storage cost; verify with plan. |
| 42 | Isolation levels? | Dirty/non-repeatable/phantom reads, database-specific behavior, correctness versus concurrency. |
| 43 | What is idempotency? | Repeating a request has one intended effect; idempotency key/unique constraint/state machine; response semantics. |
| 44 | PUT versus PATCH? | Replacement versus partial update, idempotency expectations, validation and concurrency. |
| 45 | How should APIs report errors? | Stable error code, safe message, correlation ID, field errors, status mapping, no secrets/internal stack traces. |
| 46 | How do you version an API? | Compatibility policy, additive changes, deprecation, contract tests, consumer migration. |

## 5. Microservices, Kafka, Redis, and distributed systems

| # | Question | Strong answer must cover |
|---:|---|---|
| 47 | When should a system be split into services? | Bounded context, ownership, scaling/failure isolation, deployment needs; cost of network and operations. |
| 48 | What happens when a downstream service is slow? | Timeout, bounded retries, backoff/jitter, circuit breaker, bulkhead, fallback, propagation of deadlines. |
| 49 | Why are retries dangerous? | Load amplification, duplicate effects, synchronized storms; retry only transient/idempotent operations. |
| 50 | Distributed transaction options? | Local transactions plus events/outbox, saga compensation, workflow; consistency and recovery trade-offs. |
| 51 | What is the outbox pattern? | Atomic business write plus outbox row, relay, idempotent consumer, cleanup/monitoring; not magic exactly-once. |
| 52 | Kafka partition and consumer group? | Partition ordering scope, group ownership, offset, rebalance, parallelism and key choice. |
| 53 | At-least-once delivery implications? | Duplicates are possible; idempotent consumer, dedupe key, transactional boundaries, poison-message handling. |
| 54 | How do you investigate consumer lag? | Partition-level lag, consumer health, processing latency, rebalances, downstream bottleneck, producer burst. |
| 55 | What does a Kafka key control? | Partition routing and per-key ordering; skew/hot partition risk; key must match ordering requirement. |
| 56 | Redis cache-aside flow? | Read cache, miss to DB, populate with TTL; invalidation, stampede, stale data, serialization, failure behavior. |
| 57 | Cache invalidation strategies? | TTL, write-through, explicit invalidation, versioned keys, event-driven invalidation; state correctness first. |
| 58 | Why use a bounded cache? | Memory protection, eviction policy, hot-key behavior, hit ratio and staleness measurement. |
| 59 | What is a circuit breaker? | Closed/open/half-open states, failure thresholds, cooldown, fallback, false positives and recovery. |
| 60 | What is eventual consistency? | Replicas/read models converge later; define acceptable staleness and user-visible reconciliation. |

## 6. Testing, security, delivery, and production

| # | Question | Strong answer must cover |
|---:|---|---|
| 61 | Unit versus integration versus end-to-end test? | Isolation/speed/confidence; use the smallest test that proves the behavior and keep critical boundaries covered. |
| 62 | What makes a test valuable? | Deterministic, focused, readable, failure-localizing, realistic boundary assumptions, maintained with code. |
| 63 | What should be mocked? | Unstable/external boundaries; do not mock every internal class or verify implementation details. |
| 64 | What is contract testing? | Provider/consumer expectations, compatibility, CI feedback, versioned contracts. |
| 65 | Authentication versus authorization? | Identity proof versus permission decision; enforce server-side at endpoint and domain boundaries. |
| 66 | JWT pitfalls? | Signature/issuer/audience/expiry, key rotation, revocation limitations, sensitive claims, algorithm configuration. |
| 67 | How do you prevent SQL injection? | Parameterized queries/ORM binding, validation, least privilege, logging without secrets; never string-concatenate input. |
| 68 | What belongs in a CI pipeline? | Compile, unit, static/security checks, integration, artifact, deploy gate, smoke/rollback evidence. |
| 69 | How do you roll back safely? | Immutable artifact, backward-compatible schema, feature flag, health checks, data migration plan, communication. |
| 70 | What are useful SLO signals? | Availability, latency percentiles, correctness, freshness/lag, error budget and alert action. |
| 71 | Logs versus metrics versus traces? | Event detail, aggregate trend, request path; correlation IDs and cardinality discipline. |
| 72 | What is your incident workflow? | Detect, scope, contain, diagnose, recover, communicate, verify, RCA and prevention. |

## 7. DSA, LLD, and system design prompts

| # | Prompt | What to demonstrate |
|---:|---|---|
| 73 | Two-sum / frequency lookup | Clarify duplicates, map invariant, O(n) time/O(n) space. |
| 74 | Longest substring without repeated characters | Sliding-window invariant and pointer movement. |
| 75 | Merge overlapping intervals | Sort by start, merge invariant, complexity. |
| 76 | Top K frequent items | Frequency map plus heap/bucket trade-off. |
| 77 | Number of islands | Grid traversal, visited strategy, complexity. |
| 78 | Course schedule | Cycle detection or topological ordering. |
| 79 | LRU cache | Hash map plus doubly linked list; O(1) operations and eviction invariant. |
| 80 | Rate limiter | Token/leaky/fixed window choice, clock, concurrency, distributed state. |
| 81 | Notification service | Channels, preferences, retries, dedupe, provider abstraction, delivery status. |
| 82 | Parking lot or elevator | Entities, state transitions, policies, extensibility; do not over-pattern. |
| 83 | Design URL shortener | Key generation, redirect path, expiry, abuse, availability, analytics. |
| 84 | Design order processing | State machine, idempotency, inventory/payment boundaries, events and reconciliation. |
| 85 | Design multi-tenant SaaS | Tenant isolation, authorization, data model, noisy neighbors, quotas, operations. |
| 86 | Design a RAG assistant | Ingestion, chunking, retrieval, grounding, citations, access control, evaluation, cost. |

## 8. Applied AI questions

| # | Question | Strong answer must cover |
|---:|---|---|
| 87 | What is an embedding? | Vector representation, semantic similarity, model/domain dependence, versioning. |
| 88 | How do you improve RAG retrieval? | Query normalization, chunk metadata, hybrid search, filters, reranking, evaluation before tuning. |
| 89 | What causes hallucination? | Missing/ambiguous context, model prior, weak constraints, retrieval failure, prompt injection; grounding and refusal. |
| 90 | How do you evaluate a RAG system? | Retrieval recall/precision proxies, answer correctness, citation faithfulness, refusal, latency, cost; curated dataset. |
| 91 | Tool calling versus an agent? | Structured request/response versus planning loop; bounded steps, permissions, timeouts, audit. |
| 92 | How do you secure AI tools? | Tool allowlist, schema validation, authorization, tenant scope, approval for side effects, redacted audit logs. |
| 93 | How do you reduce LLM cost? | Smaller model routing, token budgets, caching where safe, batching, prompt reduction, quotas and measurement. |
| 94 | What is MCP? | Protocol concepts and boundaries; inspect current specification/version and secure each server/tool. |
| 95 | How would you add AI to a workflow? | Deterministic state machine owns business transitions; AI produces bounded proposal; validation/approval/audit before effect. |
| 96 | What is your real AI experience? | GitHub Copilot/Cascade/LLM assistants for development and academic CNN+LSTM project; clearly label learning targets such as RAG or agents. |

## 9. Mock-round protocol

Run each round without looking at notes. A partner should ask follow-ups rather than helping.

| Round | Duration | Format | Pass condition |
|---|---:|---|---|
| Recruiter and resume | 30 min | Intro, project, move, notice, compensation, logistics | Clear 90-second story and no unsupported claim. |
| Java and coding | 60 min | One medium problem plus five Java questions | Correct solution, tests, complexity, calm debugging. |
| Spring/data | 60 min | Request flow, transaction, JPA query, SQL tuning | Explains boundary and failure mode, not annotations only. |
| Distributed systems | 60 min | Kafka/Redis/resilience scenario | States delivery/consistency assumptions and operational signals. |
| LLD/machine coding | 75 min | Requirements, model, interfaces, code/pseudocode, tests | Coherent design with extensibility and edge cases. |
| System design | 75 min | One open-ended product design | Requirements, estimate, architecture, data flow, failure handling, trade-offs. |
| Production incident | 45 min | Latency, OOM, lag, DB, or auth scenario | Evidence-driven diagnosis and safe mitigation. |
| AI application | 45 min | RAG/tool/workflow design and experience boundary | Secure, measurable, bounded design; no inflated project claim. |
| Full loop | 3-4 hr | Recruiter + coding + technical + design + behavioral | No category below 3/4 and consistent communication. |

## 10. Scoring rubric

Score each answer from 0 to 4:

- `0`: no answer or materially incorrect.
- `1`: definition only, with major gaps.
- `2`: mostly correct but misses mechanism, trade-off, or edge cases.
- `3`: correct, structured, and testable with a relevant example.
- `4`: clear senior answer including assumptions, failure handling, measurement, and alternatives.

Record the question, score, missing point, corrected answer, and date. Re-answer scores 0-2 after 24 hours and again after one week.

## 11. Follow-up pressure questions

Use these after every answer:

- What assumption are you making?
- What fails first at 10x traffic?
- How do you know this is the bottleneck?
- What happens during a retry or timeout?
- What is the consistency guarantee?
- How would you test this without production data?
- What would you log and what must never be logged?
- How would you roll it back?
- What would you choose if the team were half the size?
- Which part have you personally implemented?

## 12. Weekly question practice

Each week select 20 questions: five resume/behavioral, five Java/data, five backend/distributed, and five design/AI. Answer them aloud, write only the missing points, and repeat the weakest five. The objective is transferable reasoning, not a memorized script.

