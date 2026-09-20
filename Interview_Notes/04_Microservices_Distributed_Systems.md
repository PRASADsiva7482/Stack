# 04. Microservices & Distributed Systems: Architecture & Senior Guide
> **Evidence warning:** This is study material. Telecom scenarios, metrics, and first-person examples are illustrative unless independently evidenced.
**Target Profile:** Senior Product Software Engineer (Distributed Systems, Saga Pattern, Outbox, Resilience4j, Event-Driven Architecture)  
**Author:** Siva Prasad Vajja  
**Domain Alignment:** Telecom CRM, BSS/OSS Integration, High-Availability SaaS Platforms  

---

## 1. Definition
**Microservices Architecture** is an architectural style that structures an enterprise system as a suite of small, autonomous, loosely coupled services organized around specific business domains. Each microservice owns its private database (Database-per-Service), communicates via well-defined APIs (REST/gRPC) or asynchronous event streams (Kafka), and is independently deployable. At the senior level, it requires mastery of **distributed data consistency** (Saga, Outbox, Idempotency), **fault tolerance** (Circuit Breakers, Bulkheads), and **distributed observability**.

---

## 2. Why It Exists
Monolithic architectures degrade as organizations and codebases scale:
1. **Coupled Deployment Risky:** A single bug in reporting can crash the entire core CRM and billing system.
2. **Team Scalability Bottlenecks:** Multiple cross-functional teams touching the same monolithic database produce merge conflicts, release coordination meetings, and slow deployment cycles.
3. **Inflexible Scaling:** You cannot scale only the high-traffic subscriber search component without scaling the entire monolith.
4. **Technology Lock-In:** The entire application is tied to a single programming language and runtime framework.

---

## 3. Problem It Solves
* **Independent Scalability:** Compute resources can be allocated specifically to high-traffic services.
* **Autonomous Release Lifecycles:** Continuous delivery with zero-downtime rolling updates.
* **Fault Isolation:** Failure in a non-critical microservice (e.g., promotional SMS) does not impair the core platform (subscriber authentication).

---

## 4. Internal Working

### 4.1 The Dual-Write Problem & The Transactional Outbox Pattern
* **The Dual-Write Problem:** In a microservice, you must both update your local relational database AND send an event to a message broker (Kafka).
  ```java
  // FUNDAMENTALLY BROKEN:
  @Transactional
  public void updateSubscriber(Subscriber sub) {
      dbRepository.save(sub);          // 1. DB Commit
      kafkaTemplate.send("events", sub); // 2. Kafka send (Can fail or network timeout!)
  }
  ```
  If Kafka fails, the DB has committed (inconsistency). If you send to Kafka first and the DB transaction fails to commit, the outside world acts on phantom data!
* **The Solution — Transactional Outbox Pattern:**
  1. Store the domain state and an event record inside the **same local database transaction** (in an `outbox_events` table).
  2. A separate background process (Change Data Capture / Debezium reading the database Write-Ahead Log, or a polling worker) reads the `outbox_events` table and publishes them to Kafka.
  3. Provides an at-least-once publication path and removes the database/event dual-write window; the relay can still publish duplicates, so consumers must be idempotent.

```
+-------------------------------------------------------------+
|                     Local DB Transaction                    |
|  1. UPDATE crm_subscribers SET status = 'ACTIVE'            |
|  2. INSERT INTO outbox_events (id, topic, payload, status)  |
+-------------------------------------------------------------+
                              │ (Transaction Committed)
                              ▼
                [ Debezium CDC / Polling Worker ]
                              │
                              ▼ (Publishes to Message Broker)
                  [ Apache Kafka / RabbitMQ ]
```

### 4.2 Distributed Transactions: 2-Phase Commit (2PC) vs. Saga Pattern
* **Why 2PC Fails in Microservices:** 2PC (XA transactions) requires a centralized coordinator locking database rows across multiple services simultaneously. In distributed cloud environments, network latency and node failures make 2PC brittle, slow, and non-scalable (violating the CAP theorem).
* **The Saga Pattern:** A sequence of local transactions coordinated across services. If a local step fails, the Saga executes **Compensating Transactions** in reverse order to undo changes.
  - **Choreography-based Saga:** Services publish and listen to domain events without a central coordinator. Best for simple 2–3 step workflows.
  - **Orchestration-based Saga:** A central orchestrator (e.g., **Camunda BPM** or a dedicated Saga state machine) sends explicit commands to participant services and monitors status. Best for complex enterprise workflows with 4+ steps.

### 4.3 Idempotency Pattern
Because network failures force retries, consumers **will** receive duplicate events. An idempotent consumer guarantees that receiving the same message $N$ times has the exact same outcome as receiving it once.
* **Implementation:**
  1. Producer attaches a unique `idempotency_key` (UUID).
  2. Consumer attempts to insert the key into a dedicated `processed_events` database table with a unique constraint (or Redis `SETNX`).
  3. If insertion succeeds, process the transaction.
  4. If unique key violation occurs, acknowledge the message and skip processing.

### 4.4 Circuit Breaker States (Resilience4j)
A circuit breaker protects downstream services from cascading collapse:
* **CLOSED (Normal):** Requests pass through. Failure count/percentage is measured over a sliding window.
* **OPEN (Tripped):** When failure rate exceeds threshold (e.g., $>50\%$), the breaker trips. All calls immediately fail fast (fallback executed) without hitting the struggling downstream service.
* **HALF-OPEN (Testing):** After a cooldown period (`waitDurationInOpenState`), the breaker lets a limited number of test requests through. If successful, it transitions back to **CLOSED**; if any fail, it reverts to **OPEN**.

---

## 5. Architecture

```
                                  [ Client Apps / Web / Mobile ]
                                                │
                                                ▼ (HTTPS / TLS)
                                  [ API Gateway (Routing / Auth) ]
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 │ (mTLS)                       │ (mTLS)                       │ (mTLS)
                 ▼                              ▼                              ▼
    [ Subscriber Microservice ]      [ Billing Microservice ]       [ Provisioning Microservice ]
    ┌─────────────────────────┐      ┌──────────────────────┐       ┌───────────────────────────┐
    │  Spring Boot            │      │  Spring Boot         │       │  Spring Boot              │
    │  Database: MySQL (Sub)  │      │  Database: PostgreSQL│       │  Database: Oracle         │
    │  Outbox Table           │      │  Outbox Table        │       │  Outbox Table             │
    └───────────┬─────────────┘      └──────────┬───────────┘       └─────────────┬─────────────┘
                │ (Debezium CDC)                │ (Debezium CDC)                  │ (Debezium CDC)
                └───────────────────────┬───────┴─────────────────────────────────┘
                                        │
                                        ▼ (Asynchronous Event Streaming)
                           [ Apache Kafka Cluster / Topics ]
                                        ▲
                                        │ (Workflow Commands & Events)
                         [ Camunda Saga Orchestrator ]
```

---

## 6. Important Components
1. **API Gateway (Spring Cloud Gateway / Kong):** Acts as single entry point; handles SSL termination, rate limiting, JWT token validation, and path routing.
2. **Resilience4j:** Modern lightweight fault tolerance library providing Circuit Breaker, Rate Limiter, Retry, and Bulkhead decorators.
3. **Distributed Tracing (OpenTelemetry + W3C TraceContext):** Propagates `traceparent` headers (`trace-id`, `span-id`) across all inter-service HTTP/Kafka boundaries.
4. **Camunda BPM (Saga Orchestrator):** Manages long-running state machines, timer boundaries, human approval gates, and automated compensation tasks.
5. **Debezium CDC:** Distributed platform turning database transaction logs (MySQL binlog / Postgres WAL) into streaming event pipelines.

---

## 7. Example: Telecom Postpaid Activation Saga Flow

```
[Customer Request] ──► [Saga Orchestrator]
                              │
                              ├── Step 1: Create Subscriber Profile (CRM)
                              │           Status: COMPLETED
                              │
                              ├── Step 2: Reserve Credit Limit (Billing Service)
                              │           Status: COMPLETED
                              │
                              ├── Step 3: Provision 5G SIM on HLR/HSS Network
                              │           Status: FAILED (SIM Barred on Network)
                              │
                              ▼ [TRIGGER COMPENSATION]
                              ├── Compensate Step 2: Release Reserved Credit (Billing)
                              └── Compensate Step 1: Mark Subscriber 'ACTIVATION_FAILED' (CRM)
```

---

## 8. Java/Spring Example: Resilience4j Circuit Breaker & Idempotent Consumer

### 8.1 Circuit Breaker Configuration in `application.yml`
```yaml
resilience4j:
  circuitbreaker:
    instances:
      billingService:
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 20
        minimumNumberOfCalls: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 10000ms
        permittedNumberOfCallsInHalfOpenState: 5
        automaticTransitionFromOpenToHalfOpenEnabled: true
  retry:
    instances:
      billingService:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
```

### 8.2 Service Implementation with Fallback
```java
@Service
public class BillingClientService {

    private static final Logger log = LoggerFactory.getLogger(BillingClientService.class);
    private final RestClient restClient;

    public BillingClientService(RestClient.Builder builder) {
        this.restClient = builder.baseUrl("https://billing-service.internal").build();
    }

    @CircuitBreaker(name = "billingService", fallbackMethod = "reserveCreditFallback")
    @Retry(name = "billingService")
    public CreditReservationResponse reserveCredit(String subscriberId, double amount) {
        return restClient.post()
            .uri("/api/v1/credit/reserve")
            .body(new ReserveRequest(subscriberId, amount))
            .retrieve()
            .body(CreditReservationResponse.class);
    }

    // Fallback method must have the identical method signature + Throwable parameter
    public CreditReservationResponse reserveCreditFallback(String subscriberId, double amount, Throwable ex) {
        log.error("Billing service unreachable or failing. Tripping circuit breaker for subscriber: {}", subscriberId, ex);
        // Return degraded or queued state
        return new CreditReservationResponse(subscriberId, "QUEUED_OFFLINE", "Billing temporarily unavailable");
    }
}
```

### 8.3 Idempotent Kafka Consumer Pattern
```java
@Component
public class PaymentEventConsumer {

    private final ProcessedEventRepository eventRepo;
    private final SubscriberService subscriberService;

    public PaymentEventConsumer(ProcessedEventRepository eventRepo, SubscriberService subscriberService) {
        this.eventRepo = eventRepo;
        this.subscriberService = subscriberService;
    }

    @KafkaListener(topics = "telecom-payments", groupId = "crm-payment-group")
    @Transactional
    public void handlePaymentReceived(PaymentEvent event, Acknowledgment ack) {
        // Step 1: Idempotency Check via Unique DB Constraint
        if (eventRepo.existsByEventId(event.eventId())) {
            log.info("Duplicate event detected: {}. Skipping execution.", event.eventId());
            ack.acknowledge();
            return;
        }

        // Step 2: Record Event Idempotency Key
        eventRepo.save(new ProcessedEvent(event.eventId(), Instant.now()));

        // Step 3: Execute Business Logic
        subscriberService.unbarSubscriber(event.subscriberId());

        ack.acknowledge();
    }
}
```

---

## 9. Illustrative Exercise: CRM Subscriber Lifecycle Decoupling
* **Problem:** Direct synchronous REST calls from CRM to Billing, Provisioning, and Notification services during subscriber onboarding created tight coupling; if SMS gateway was slow, the subscriber onboarding API timed out after 30 seconds.
* **Architecture:** Decouple via **Choreography/Orchestration**:
  1. CRM commits subscriber to MySQL and writes to `outbox_events`.
  2. Debezium streams `SubscriberCreatedEvent` to Kafka.
  3. Billing service consumes event and allocates account balance.
  4. Notification service consumes event and dispatches SMS asynchronously.
* **Result:** CRM API response time plummeted from 4,200ms to **180ms**. Complete failure isolation achieved.

---

## 10. Common Mistakes
1. **The "Distributed Monolith" Anti-Pattern:** Creating dozens of microservices that all synchronously call each other via REST in a deep dependency chain ($A \to B \to C \to D$). Latency sums up, and availability becomes the product of all service availabilities ($0.99^4 = 0.96$).
2. **Shared Database across Services:** Multiple services reading and writing to the same database table breaks encapsulation, produces hidden schema couplings, and eliminates independent deployment.
3. **Unbounded Retries (Thundering Herd / Stampede):** Retrying failed requests without exponential backoff and jitter overloads already struggling downstream servers, turning a temporary slowdown into a total outage.
4. **Missing Distributed Tracing Context:** Failing to propagate `traceparent` headers makes debugging production errors across 10 microservices virtually impossible.
5. **Ignoring Eventual Consistency in UI Design:** Expecting an asynchronous background operation to reflect immediately in the database. Fix: Design UI with optimistic updates or polling/WebSocket state updates.

---

## 11. Performance Considerations
* **gRPC / Protobuf for East-West Traffic:** For internal communication between backend microservices, replace JSON/HTTP with gRPC. Protocol Buffers serialization is $5\times$ to $10\times$ faster than Jackson JSON and significantly reduces network bandwidth.
* **Connection Pooling for HTTP Clients:** Configure Spring's `RestClient` / `WebClient` with a pooled connection manager (Apache HttpComponents or Netty) with high `maxConnTotal` (e.g., 500) and `maxConnPerRoute` (e.g., 100). Default HTTP clients open and close TCP connections per request, causing socket exhaustion.

---

## 12. Security Considerations
* **Zero-Trust Network Architecture:** Do not assume internal network traffic is safe. Enforce **Mutual TLS (mTLS)** between all microservices via an Envoy Service Mesh (Istio).
* **Token Relay Pattern:** The API Gateway validates incoming user credentials, exchanges them for a cryptographically signed internal JWT, and relays it in the `Authorization: Bearer <JWT>` header to downstream services.
* **Sensitive Data Redaction in Logging:** Never log PII (Personally Identifiable Information like MSISDN, credit card numbers, or passwords) in distributed logs or tracing spans.

---

## 13. Core Interview Questions & Answers

### Q1: What is the difference between Orchestration and Choreography in Sagas?
**Answer:**
* **Choreography:** Decentralized. Services listen to domain events and decide autonomously when to act. Best for simple workflows (2–3 steps) with few participants. Disadvantage: Hard to monitor, risk of cyclic dependencies.
* **Orchestration:** Centralized. A single orchestrator (e.g., Camunda) coordinates the workflow by sending explicit command messages and executing compensations if steps fail. Best for complex, mission-critical enterprise workflows.

### Q2: How does the Transactional Outbox pattern solve the dual-write problem?
**Answer:** It guarantees atomicity between database mutations and event publication by recording both the business entity update and an outbox event record within the **same local ACID database transaction**. A separate process (Debezium CDC or polling worker) reads the outbox table and streams the events to Kafka with At-Least-Once delivery guarantees.

### Q3: What is the difference between a Circuit Breaker and a Rate Limiter?
**Answer:**
* **Circuit Breaker:** Protects your system from failures in **downstream external dependencies** by failing fast when downstream services become unhealthy.
* **Rate Limiter:** Protects your system from being overwhelmed by **incoming client requests** by enforcing traffic quotas (e.g., 100 requests/sec per client IP).

### Q4: Why is 2-Phase Commit (2PC) rarely used in cloud microservices?
**Answer:** 2PC is a blocking protocol. While the coordinator queries participants and waits for votes, database locks are held. In distributed cloud environments with unpredictable network partitions and node crashes, locks can be held indefinitely, crippling throughput and violating availability (CAP theorem).

### Q5: How do you achieve Exactly-Once processing in event-driven microservices?
**Answer:** True end-to-end exactly-once is practically impossible without distributed coordination. Instead, we achieve **Effective Exactly-Once** by combining:
1. **At-Least-Once Delivery** (Message broker retries until acknowledged).
2. **Idempotent Consumers** (Tracking processed message IDs in a database unique table or using deduplicating state).

---

## 14. Deep Interview Questions (Staff / Principal Level)

### Q1: How do you handle a scenario where a Saga Compensating Transaction itself fails?
**Answer:** Compensating transactions **must never fail permanently**. They must be designed to be idempotent and retried indefinitely until they succeed. If a compensating transaction encounters an unrecoverable failure (e.g., third-party API permanently unavailable):
1. The Saga state machine pauses and routes the workflow to a **Dead-Letter Queue (DLQ)** or administrative alert.
2. The orchestrator flags the transaction for **Human-in-the-Loop (HITL)** manual intervention via an administrative operations console.
3. System logs critical alerts to PagerDuty/Slack for incident remediation.

### Q2: What is the "Bulkhead" pattern in Resilience4j and how does it prevent thread pool starvation?
**Answer:** Inspired by the watertight compartments of a ship. If one downstream service starts hanging, all incoming worker threads could be consumed waiting for timeouts, starving all other unrelated APIs on the same host.  
* **ThreadPool Bulkhead:** Assigns a separate, dedicated bounded thread pool to each external dependency (e.g., 10 threads for Billing, 10 threads for Notification). If Billing hangs, only its 10 threads are blocked; Notification continues to operate normally.

### Q3: Explain CQRS (Command Query Responsibility Segregation) and when it should be introduced.
**Answer:** CQRS splits the application into two distinct paths:
* **Command Side:** Handles writes, updates, and deletes; enforces strict domain invariants and validation; writes to a normalized relational database.
* **Query Side:** Handles complex reads and reporting; reads from a denormalized read-optimized store (e.g., Elasticsearch or read-replicas) populated asynchronously via domain events.
* **When to use:** When read and write performance requirements diverge dramatically (e.g., 99% reads, 1% writes with complex aggregations).

---

## 15. Comparison with Alternatives

| Feature | Microservices | Modular Monolith | Serverless (Lambda) |
|---|---|---|---|
| **Deployment** | Independent containers | Single deployable artifact | Ephemeral functions |
| **Data Consistency** | Eventual (Sagas) | Immediate (ACID) | Eventual |
| **Operational Overhead**| High (K8s, mesh, tracing) | Low (Single deployment) | Low/Medium (Cloud-managed) |
| **Fault Isolation** | High | Low (Shared process) | High |
| **Latency** | Network hops between services | In-memory method calls | Cold starts + network hops |
| **Team Fit** | Multiple independent teams | Small-to-medium teams | Event-driven micro-tasks |

---

## 16. When NOT to Use It
1. **Early-Stage Startups / Unclear Domain Boundaries:** Splitting domains before understanding business boundaries leads to incorrect service cuts, resulting in a high-maintenance distributed monolith.
2. **Small Engineering Teams ($<10$ Engineers):** The operational tax (Kubernetes, distributed tracing, network security, CI/CD pipelines) drains engineering velocity. A **Modular Monolith** is vastly superior.
3. **Ultra-Low Latency Workflows ($<10$ms):** Workflows requiring immediate atomic consistency and sub-millisecond roundtrips cannot afford the network latency of inter-service REST/Kafka hops.

---

## 17. Hands-on Exercise: Implement the Transactional Outbox Pattern
**Task:** Build a Spring Data JPA service that saves a `Subscriber` entity and writes an `OutboxEvent` in a single transaction.

```java
@Entity
@Table(name = "outbox_events")
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String aggregateType;

    @Column(nullable = false)
    private String aggregateId;

    @Column(nullable = false)
    private String eventType;

    @Lob
    @Column(nullable = false)
    private String payload;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();
    // Getters and Setters
}

@Service
public class SubscriberService {

    private final SubscriberRepository subRepo;
    private final OutboxEventRepository outboxRepo;
    private final ObjectMapper objectMapper;

    public SubscriberService(SubscriberRepository subRepo, 
                             OutboxEventRepository outboxRepo, 
                             ObjectMapper objectMapper) {
        this.subRepo = subRepo;
        this.outboxRepo = outboxRepo;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public Subscriber createSubscriber(CreateSubscriberDto dto) throws JsonProcessingException {
        // 1. Mutate Domain State
        Subscriber subscriber = new Subscriber(dto.msisdn(), SubscriberStatus.PENDING_ACTIVATION);
        subRepo.save(subscriber);

        // 2. Create Outbox Event in the SAME ACID Transaction
        SubscriberCreatedPayload payload = new SubscriberCreatedPayload(subscriber.getId(), subscriber.getMsisdn());
        OutboxEvent outboxEvent = new OutboxEvent(
            "SUBSCRIBER",
            subscriber.getId().toString(),
            "SUBSCRIBER_CREATED",
            objectMapper.writeValueAsString(payload)
        );
        outboxRepo.save(outboxEvent);

        return subscriber;
    }
}
```

---

## 18. Project Application: Telecom CRM Core Platform
How this could connect to your current resume (verify actual implementation):
* **Where this applies:**
  1. **Subscriber Onboarding Saga:** Using Camunda BPM as an orchestration engine coordinating CRM subscriber record creation, Billing account reservation, and HLR/HSS SIM provisioning, with automated compensating handlers if provisioning fails.
  2. **Decoupling SMS Notifications:** Moving from synchronous HTTP calls to an event-driven model where the CRM emits `SubscriberEvent` to Kafka, and a dedicated Notification microservice handles delivery with exponential retries.
  3. **Resilience against Downstream Billing Outages:** Wrapping billing payment verifications with Resilience4j Circuit Breakers to prevent CRM UI freezes when the legacy billing platform is under maintenance.

---

## 19. Senior-Level Interview Answer (The "Gold Standard")

> *"In distributed enterprise systems like Telecom BSS, the core challenge is balancing autonomy with consistency.*  
> *Because distributed transactions via 2-Phase Commit are brittle and hold blocking locks across network boundaries, I design our architectures around **Eventual Consistency** using the **Saga Pattern**. For complex telecom lifecycle workflows—like SIM provisioning and postpaid activations—we utilize orchestration via Camunda to explicitly manage state and execute compensating transactions upon failure.*  
> *To eliminate the dual-write problem between our relational database and Kafka, we mandate the **Transactional Outbox Pattern** with Debezium CDC, ensuring at-least-once delivery without distributed locks. On the consumer side, we enforce idempotency via unique deduplication keys. Finally, we safeguard inter-service stability using **Resilience4j Circuit Breakers** and Bulkheads, ensuring that a downstream billing outage degrades gracefully rather than cascading across our CRM."*

---

## 20. Real-World Troubleshooting Scenarios

### Scenario A: Cascading System Collapse due to Downstream Slowness
* **Symptom:** Microservice C experiences a database lock spike, increasing response time from 50ms to 8,000ms. Within 2 minutes, Microservice B and Microservice A exhaust all worker threads and crash with 504 Gateway Timeouts.
* **Root Cause:** Synchronous REST calls without circuit breakers and timeouts. All upstream Tomcat threads became blocked waiting on downstream responses.
* **Remediation:**
  1. Set strict HTTP client connection and read timeouts (e.g., connect: 500ms, read: 1,500ms).
  2. Deploy a **Resilience4j Circuit Breaker** on the client calling Service C. As soon as failure rate exceeds 50%, the breaker trips to OPEN, immediately returning cached/fallback responses in 1ms, preserving upstream threads.

### Scenario B: Phantom Duplicate Subscriber Activations
* **Symptom:** Customers report being billed twice for a single plan change, and two active plan records appear in the database.
* **Root Cause:** A temporary network timeout occurred between the API Gateway and the CRM service. The mobile app timed out and retried the request. The CRM service processed both requests independently because no unique idempotency key was enforced.
* **Remediation:**
  1. Mandate an `X-Idempotency-Key` header generated by the frontend on all mutation requests (`POST`, `PUT`).
  2. The CRM service uses Redis or a database unique index to lock the idempotency key for 60 seconds. Subsequent duplicate requests return the cached result of the original execution without re-executing business logic.
