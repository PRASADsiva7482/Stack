# 00. Audit, Evidence Rules, and Master Study Plan

**Candidate:** Siva Prasad Vajja  
**Audit date:** 2026-09-14  
**Primary goal:** Move from the current Senior Software Engineer role into a strong product-engineering role, with Java/Spring backend as the primary lane and AI-enabled application engineering as a specialization.

## 1. What was requested and what the attached prompt means

Your direct request is the outcome: complete the roadmap, correct material that is wrong or unsafe, and give you detailed notes that can be studied for interviews.

The attached master prompt is the work specification. Its instruction to stop after a first-run audit is treated as an intermediate checkpoint, not the final outcome, because you explicitly asked to go ahead and complete the work.

This folder is therefore organized as a complete study system. It is not a claim that reading notes makes a topic interview-ready.

## 2. Evidence rules

Use these labels while studying and while speaking in interviews:

| Label | Meaning | How to use it |
|---|---|---|
| `RESUME-VERIFIED` | Explicitly present in the original PDF resume | Safe to say as experience, but prepare depth and scope |
| `EXPOSURE` | Mentioned as integration/support/participation | Say exactly what you owned and what another team owned |
| `LEARNING TARGET` | A topic in this roadmap | Never present it as production experience until you build and verify it |
| `ILLUSTRATIVE` | Example architecture, number, incident, or code scenario | Do not reuse as a personal achievement |
| `NEEDS EVIDENCE` | A claim requiring tickets, dashboards, code, release notes, or a manager-confirmed result | Replace or remove from a resume until evidence exists |

Rule: a generated note is not evidence. A metric in an example is not your metric. A technology in a project design is not your production technology.

## 3. Source-of-truth resume audit

The original file audited was `Siva Prasad Vajja.pdf`, not the previously transformed resume draft.

### 3.1 Current profile assessment

This is an evidence assessment, not a skill test. “Unknown” means the resume does not prove depth.

| Area | Resume evidence | Assessment | Preparation need |
|---|---|---|---|
| Java / OOP / collections / streams / exceptions | Listed skills and responsibilities | Moderate claimed, depth unknown | Core Java internals, coding, trade-offs |
| Java 17 | Project environment | Resume-verified version exposure | Explain language/runtime features actually used |
| Spring Boot / MVC / REST | Designed and developed services/APIs | Moderate claimed | DI, lifecycle, MVC pipeline, validation, errors |
| JPA / Hibernate / transactions | Implemented persistence and transaction management | Moderate claimed | Persistence context, locking, query behavior, boundaries |
| SQL / MySQL | Listed and used for optimization | Moderate claimed | Joins, indexes, plans, isolation, deadlocks |
| Microservices | Listed; designed/developed services | Moderate claimed | Boundaries, failure, idempotency, consistency |
| Camunda BPM | Built workflows | Strongest domain differentiator, depth still to validate | Engine model, retries, workers, versioning, compensation |
| Spring Batch | Built jobs for bulk processing | Moderate claimed | Chunk model, restartability, skip/retry, transaction scope |
| React | Frontend integration | Exposure, not frontend-specialist evidence | Hooks, API states, auth, performance basics |
| Git/GitLab/Maven | Used; CI/CD support | Exposure to moderate | Explain commands and pipeline contribution honestly |
| JUnit | Wrote unit tests | Moderate claimed | Test boundaries, Mockito limits, integration tests |
| Production support / RCA | Explicitly listed | Moderate claimed | Evidence-based incident narrative and debugging workflow |
| Agile / collaboration | Explicitly listed | Resume-verified | Behavioral stories with personal contribution |
| Kafka / Redis / AWS / Kubernetes | Not in original PDF | Learning targets only | Build a project before claiming |
| OpenTelemetry / Prometheus / Grafana | Not in original PDF | Learning targets only | Operability labs and evidence |
| Spring AI / RAG / agents / MCP | Not in original PDF | Learning targets only | Portfolio project plus evaluation/security evidence |
| CNN/LSTM image captioning | Academic project | Academic exposure | Explain the pipeline; do not present as current AI engineering |

### 3.2 What the original resume does not prove

Do not currently claim any of the following as production ownership unless you can provide independent evidence:

- 50M subscribers, 15,000 requests/sec, 99.99% availability, or five-nines reliability.
- Kafka architecture or event-driven migration.
- Redis distributed locks, caching, or semantic caching.
- AWS, EKS, Kubernetes, Docker, OpenTelemetry, Prometheus, or Grafana ownership.
- Spring AI, vector databases, RAG, reranking, autonomous agents, MCP, or AI compliance outcomes.
- Exact payment volumes, zero double-charging, cost reductions, latency reductions, or percentage improvements.
- Leading a five-person squad, sprint-velocity improvements, or MTTR reductions unless documented.

These are excellent portfolio scenarios and study exercises. They are not current resume facts.

## 4. Audit of the existing notes

The existing modules 01-23 are retained because their concepts and examples are useful. They are now classified as **draft learning notes**, not completed evidence. Modules 24 and 25 were substantially unsafe as written and are replaced.

### Useful material retained

- Core Java, Spring Boot, JPA/Hibernate, SQL, microservices, Kafka, Redis, system design, Docker/Kubernetes, AWS, observability, LLMs, embeddings, RAG, Spring AI, agents, Camunda/AI, MCP, AI security, DSA, security, React, and system-design catalogs.
- Java-oriented examples and telecom-shaped exercises.
- The recurring pattern of concept, internals, production scenario, interview questions, and exercise.

### Corrections made or required

1. “Completed” status was not justified by generated notes. The canonical tracker below starts at `NOT STARTED` for learning evidence.
2. The transformed resume used technologies and metrics absent from the original PDF. It is replaced by an honest positioning guide.
3. Company dossiers used unsupported technology, location, salary, hiring, and interview claims. They are replaced by a source-led target strategy.
4. Hypothetical incidents were written in first person or as “in 6D.” They must be read as `ILLUSTRATIVE` unless you attach evidence.
5. AI evaluation cannot guarantee zero hallucinations. Metrics are signals with dataset, judge, and sampling limitations.
6. Current framework APIs are version-sensitive. Pin a project version and read the matching official documentation.
7. MCP is a fast-moving protocol. Do not treat an old SSE example as the current production default; check the protocol version in the project.
8. Missing areas were added: testing strategy, Maven/Git/CI/CD, networking, Linux, product engineering, SaaS, telecom/BSS, systematic production troubleshooting, resume deep dive, behavioral interviews, and mock-interview scoring.

## 5. Final learning order

Study in this order. Keep DSA running in parallel from Phase 1; do not postpone it to the end.

| Phase | Sequence | Exit capability |
|---:|---|---|
| 0 | Resume evidence, Java setup, baseline coding test | Explain every resume bullet without exaggeration |
| 1 | Core Java: object model, OOP, equality, collections, generics, exceptions, streams, Java 17 | Implement and explain safe Java components |
| 2 | Concurrency, JMM, JVM memory, GC, profiling | Diagnose visibility, contention, thread-pool, and memory failures |
| 3 | DSA patterns: arrays, hash, two pointers, windows, stack/queue, trees, graphs, DP | Solve and explain common medium problems under time pressure |
| 4 | Spring Framework and Boot internals | Trace request, bean, proxy, configuration, and transaction behavior |
| 5 | JPA/Hibernate, JDBC, SQL, indexes, isolation, locking | Explain query behavior and fix realistic persistence failures |
| 6 | REST/API design, networking, authentication and authorization | Design safe, compatible APIs and explain HTTP behavior |
| 7 | Microservices and distributed systems | Reason about partial failure, retries, idempotency, and consistency |
| 8 | Kafka and event-driven design | Design partitions, consumers, retries, replay, and outbox flows |
| 9 | Redis and caching | Choose cache patterns and handle invalidation, stampede, and failure |
| 10 | Testing, Maven, Git, CI/CD | Build a test pyramid and explain delivery contribution |
| 11 | Docker, Kubernetes/OpenShift, AWS architecture | Deploy and troubleshoot a small service without claiming platform ownership |
| 12 | Observability and performance | Move from symptom to measured root cause |
| 13 | LLD and design patterns | Produce extensible, testable object designs |
| 14 | System design | Run a senior interview from requirements to trade-offs |
| 15 | Product engineering, SaaS, telecom/BSS | Connect technical choices to customers, tenants, money, and operations |
| 16 | LLM fundamentals, embeddings, vector search, RAG | Explain and build a grounded AI application |
| 17 | Spring AI/LangChain4j concepts, tool calling, workflows, agents | Build bounded tool-using AI features |
| 18 | MCP, AI security, evaluation, cost, observability | Discuss enterprise AI safely and quantitatively |
| 19 | Portfolio projects and evidence | Demonstrate working code, tests, measurements, and trade-offs |
| 20 | Interview loops and mock interviews | Answer one question at a time with clear senior reasoning |

### Suggested weekly cadence

For a 2-hour weekday schedule:

- 45 minutes concept and handwritten recall.
- 45 minutes Java/SQL/design coding.
- 20 minutes interview answer aloud.
- 10 minutes progress log and unresolved questions.

On one weekend day, do a 90-minute lab or mock interview. On the other, revise mistakes. If you have less time, preserve the same proportions rather than dropping coding and recall.

## 6. Canonical progress tracker

Statuses are deliberately conservative:

- `NOT STARTED`: no personal evidence yet.
- `IN PROGRESS`: actively studying or building.
- `REVISED`: can explain and has corrected mistakes.
- `INTERVIEW READY`: timed answers/coding/design have passed self-checks.
- `PRODUCTION READY`: has a working lab/project with tests, failure handling, observability, and documented trade-offs.

| Module | Notes | Theory | Coding | Production | Interview | Project |
|---|---|---|---|---|---|---|
| 01 Core Java | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 02 Spring Boot | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 03 JPA/Hibernate | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 04 Microservices | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 05 Kafka | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 06 Redis | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 07 SQL | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 08 System design | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 09 Docker/Kubernetes | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 10 AWS | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 11 Observability | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 12-19 AI sequence | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 20 DSA | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 21 Security | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 22 React | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 23 Design catalog | Exists | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 24 Target strategy | Replaced | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 25 Honest resume | Replaced | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 26 Testing/build/delivery | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 27 Networking/Linux | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 28 Product/SaaS/telecom | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 29 Troubleshooting | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 30 Behavioral/mock interviews | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 31 Version and AI corrections | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 32 Coding interview workbook | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 33 LLD/machine coding workbook | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 34 System design interview workbook | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 35 Question bank/mock rounds | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 36 Resume evidence/application | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 37 Readiness tracker | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |
| 38 LLM/SLM application integration | Added | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED | NOT STARTED |

## 7. Interview coverage matrix

| Interview category | Primary notes | Resume connection |
|---|---|---|
| Resume/project deep dive | 25, 30 | Every original bullet |
| Core Java and concurrency | 01, 20, 29 | Java 17, multithreading, collections, streams |
| Spring/Spring Boot | 02, 21 | Spring Boot, MVC, REST, security |
| Persistence and SQL | 03, 07, 26, 29 | JPA, Hibernate, MySQL, transactions, tuning |
| Microservices/distributed systems | 04, 05, 06, 08 | Microservices and API integration |
| Camunda/workflow/batch | 17, 28 | Camunda BPM and Spring Batch |
| Testing/build/delivery | 26 | JUnit, Maven, GitLab CI/CD support |
| Cloud/operations | 09, 10, 11, 27, 29 | Production support and future product roles |
| Security | 21, 31 | Secure coding; future Keycloak/OAuth2 depth |
| DSA/LLD/system design | 20, 08, 23 | Core CS and senior interviews |
| Timed coding practice | 20, 32 | Pattern recognition, implementation, testing, complexity |
| LLD/machine coding practice | 23, 33 | Object modeling, interfaces, extensibility, code quality |
| Timed system design practice | 08, 23, 34 | Requirements, estimates, architecture, failure handling |
| React/full stack | 22 | React frontend integration |
| Product/SaaS/telecom | 28 | CRM/BSS and product transition |
| AI application engineering | 12-19, 31 | AI-assisted development plus academic CNN/LSTM |
| LLM/SLM app integration | 15, 16, 18, 19, 34, 38 | Model gateway, routing, RAG, tools, workflow, security, evaluation |
| Behavioral/leadership | 30 | Collaboration, stakeholders, RCA, Agile |
| Question bank and mock execution | 35, 37 | Repeated timed retrieval and readiness evidence |
| Resume/application evidence | 25, 30, 36 | Truthful claims, stories, role-specific positioning |

## 8. Interview answer contract

For every important answer, use this sequence:

1. Give a direct 20-40 second answer.
2. Explain the internal mechanism.
3. Give an example you genuinely know. If it is a lab, say “in my lab/project.”
4. State failure modes and how you would measure them.
5. State a trade-off and when you would not use the approach.
6. Stop and invite the follow-up instead of reciting a memorized essay.

For your own experience, use: context -> responsibility -> decision -> implementation -> verification -> outcome -> lesson. Do not invent the outcome; say what you measured or what remains unknown.

## 9. Acceptance gates before applying

You are ready for a target role only when the relevant lane passes these checks:

- Explain the original resume bullets and ownership boundaries in under five minutes.
- Solve 30-40 representative DSA problems with patterns, not memorized code.
- Write SQL joins, aggregates, windows, pagination, and index reasoning without notes.
- Trace a Spring request and a transaction through proxies and persistence.
- Design one workflow, one event-driven system, one multi-tenant SaaS system, and one AI/RAG system.
- Debug at least eight failures from module 29 using measurements before fixes.
- Show one project with tests, Docker, a README, a failure drill, and an architecture decision record.
- Run two mock loops with no unsupported claims.

## 10. First study topic

Start with **Core Java: object model, equality/hashCode, collections, generics, exceptions, and streams**, then immediately do a timed coding baseline. These topics are explicitly on the resume, appear in almost every Java interview, and form the vocabulary needed for Spring, JPA, concurrency, and DSA. The first lesson should use Java 17 and label all examples as study code unless they are actually built in your project.
