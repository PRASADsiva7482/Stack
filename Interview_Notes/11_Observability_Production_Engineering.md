# 11. Observability & Production Engineering: SRE & Senior Guide
> **Evidence warning:** Observability tools and metrics here are learning targets, not current production ownership verified by the original resume.
**Target Profile:** Senior Product Software Engineer (OpenTelemetry, Prometheus, Distributed Tracing, Root Cause Analysis, SLAs/SLOs)  
**Author:** Siva Prasad Vajja  
**Domain Alignment:** Telecom Production Support, Incident Management, SLA Commitments, High-Reliability Operations  

---

## 1. Definition
**Observability at the Senior Level** is the degree to which the internal execution states of a distributed software system can be inferred solely by examining its external outputs (Telemetry Data). It transcends passive monitoring ("is the server up?") by providing actionable context to diagnose unexpected failure states. The foundation rests upon the **Three Pillars of Observability: Metrics, Distributed Tracing, and Structured Logging**, unified by open industry standards (**OpenTelemetry - OTel**). It requires mastery of **W3C Trace Context propagation, Micrometer instrumentation, SLI/SLO error budgets, and blameless Root Cause Analysis (RCA)**.

---

## 2. Why It Exists
In a monolithic system, debugging an error requires checking a single log file on a single server. In distributed microservices:
1. **The "Needle in a Haystack" Problem:** A single user request traverses 12 independent microservices, Kafka topics, and databases. Finding where a failure occurred across 500 pods is impossible with traditional logging.
2. **Cascading Failure Blindness:** A slow query in Service C causes thread pool exhaustion in Service B, which manifests as a 504 Gateway Timeout in Service A. Only distributed tracing reveals that Service C was the true root cause.
3. **Alert Fatigue:** Being woken up at 3 AM by noisy CPU alerts when user requests are healthy wastes engineering morale. Observability shifts focus from infrastructure symptoms to **user-facing SLOs**.

---

## 3. Problem It Solves
* **Mean Time to Detection (MTTD) & Resolution (MTTR):** Slashing incident diagnosis times from hours to minutes.
* **Trace Context Fragmentation:** Solved by OpenTelemetry W3C trace propagation.
* **High Metric Cardinality & Memory Crashes:** Solved by disciplined Prometheus metric dimensional design.
* **Unclear SLA Compliance:** Solved by quantitative Service Level Indicators (SLIs) and Error Budgets.

---

## 4. Internal Working

### 4.1 The Three Pillars of Observability
```
+-------------------------------------------------------------------------+
|                       The Three Pillars of Telemetry                    |
+-------------------------------------------------------------------------+
|  1. METRICS (Aggregable, Numeric, Time-Series)                          |
|     - "What is broken and at what rate?"                                |
|     - Low storage overhead; powers real-time alerts and Grafana graphs. |
|     - Types: Counter, Gauge, Histogram, Summary.                        |
+-------------------------------------------------------------------------+
|  2. TRACES (Request Waterfall Lifecycle across Microservices)           |
|     - "Where did the bottleneck or failure occur in the call graph?"     |
|     - Tracks timing and spans across HTTP, gRPC, and Kafka boundaries.  |
|     - Formats: OpenTelemetry, W3C Trace Context (traceparent).          |
+-------------------------------------------------------------------------+
|  3. LOGS (Event Context & Detailed State Snapshots)                     |
|     - "Why did it break? What were the exact error variables?"          |
|     - Structured JSON logs enriched with trace_id and span_id via MDC.  |
|     - Ingested by Loki, Elasticsearch, or OpenSearch.                   |
+-------------------------------------------------------------------------+
```

### 4.2 Distributed Tracing & W3C Trace Context Mechanics
When a client sends an HTTP request, the API Gateway initiates a **Trace**:
* **Trace ID:** A unique 16-byte (32-character hex) identifier representing the entire end-to-end journey of the request.
* **Span ID:** An 8-byte (16-character hex) identifier representing a single segment of work inside a specific microservice (e.g., executing an SQL query, calling a REST API).
* **W3C `traceparent` Header:** Propagated across all network boundaries:
  ```text
  traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
               │  │                                │                │
               │  └── Trace ID (Global)            └── Parent Span  └── Flags (Sampled)
               └── Version
  ```

### 4.3 Prometheus Metric Types & The Cardinality Trap
1. **Counter:** Monotonically increasing number (only resets on restart). E.g., `http_requests_total`.
2. **Gauge:** Value that goes up and down. E.g., `jvm_threads_active`, `hikari_pool_active_connections`.
3. **Histogram:** Samples observations (usually request durations) and counts them in configurable buckets (`le`). Enables calculating **p95 and p99 percentiles**.
* ⚠️ **The Cardinality Trap:** Cardinality is the total number of unique time series generated by a metric's label combinations:
  $$\text{Total Series} = \prod \text{unique\_values}(\text{label}_i)$$
  If you add `user_id` or `msisdn` as a label on `http_requests_total` with 10 million users, Prometheus attempts to maintain **10,000,000 separate time-series streams in RAM**, causing immediate out-of-memory crashes! **Never put high-cardinality keys in metric labels; put them in logs and trace spans.**

### 4.4 SRE Principles: SLA, SLO, SLI, and Error Budgets
* **SLI (Service Level Indicator):** A quantitative measure of service performance.
  - *Example:* $\text{SLI} = \frac{\text{Successful HTTP requests (Status } < 500\text{ with Latency } < 200\text{ms)}}{\text{Total HTTP requests}} \times 100\%$
* **SLO (Service Level Objective):** The internal target agreed upon by engineering and product teams.
  - *Example:* "99.9% of CRM subscriber lookups must succeed in $<200$ms over any rolling 30-day window."
* **SLA (Service Level Agreement):** The contractual commitment to external clients with financial penalties if breached (typically looser than the SLO, e.g., 99.5%).
* **Error Budget:** The allowable unreliability: $100\% - \text{SLO}$. For a 99.9% SLO, you have a **0.1% Error Budget**. If the error budget is exhausted, feature deployments are frozen and all engineering focuses on reliability.

---

## 5. Architecture: Unified OpenTelemetry Pipeline

```
[ Spring Boot Pod 1 ]      [ Spring Boot Pod 2 ]      [ Spring Boot Pod 3 ]
(Micrometer + OTel SDK)    (Micrometer + OTel SDK)    (Micrometer + OTel SDK)
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │ (OTLP Protocol over gRPC / Port 4317)
                                   ▼
        +-----------------------------------------------------+
        |         OpenTelemetry Collector (DaemonSet)         |
        |  1. Receiver (OTLP gRPC)                            |
        |  2. Processor (Batching, Memory Limiter, Redaction) |
        |  3. Exporter (Routes telemetry to target backends)  |
        +-----------------------------------------------------+
                 │                     │                     │
                 ▼ (Prometheus Exporter)▼ (OTLP Exporter)    ▼ (Loki Exporter)
          [ Prometheus ]         [ Grafana Tempo ]      [ Grafana Loki ]
          (TSDB Metrics)         (Distributed Traces)   (Structured Logs)
                 │                     │                     │
                 └─────────────────────┼─────────────────────┘
                                       │
                                       ▼ (Unified Visual Correlated Pane)
                           [ Grafana Dashboard ]
                     (Metric -> Trace -> Logs in 1-Click!)
```

---

## 6. Important Components
1. **Micrometer (Spring Boot):** The application metrics facade for Spring Boot (equivalent to SLF4J for logging). Exports metrics seamlessly to Prometheus, Datadog, or CloudWatch.
2. **OpenTelemetry (OTel) Collector:** Vendor-agnostic proxy that receives, transforms, filters, and exports telemetry data to multiple backends.
3. **Jaeger / Grafana Tempo:** Distributed tracing search engines visualizing end-to-end trace latency waterfalls.
4. **MDC (Mapped Diagnostic Context):** Thread-local map managed by SLF4J/Logback that automatically injects contextual variables (`traceId`, `spanId`, `tenantId`) into every log statement.
5. **Alertmanager:** Handles deduplication, grouping, silences, and routing of alerts from Prometheus to PagerDuty, Slack, or Webhooks.

---

## 7. Example: High-Performance JSON Logback Configuration with MDC

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="CONSOLE_JSON" class="ch.qos.logback.core.ConsoleAppender">
        <encoder class="net.logstash.logback.encoder.LogstashEncoder">
            <!-- Automatically includes MDC fields: traceId, spanId, tenantId -->
            <includeMdcKeyName>traceId</includeMdcKeyName>
            <includeMdcKeyName>spanId</includeMdcKeyName>
            <includeMdcKeyName>msisdn</includeMdcKeyName>
            <fieldNames>
                <timestamp>timestamp</timestamp>
                <message>message</message>
                <logger>logger</logger>
                <level>level</level>
                <thread>thread</thread>
            </fieldNames>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="CONSOLE_JSON" />
    </root>
</configuration>
```

---

## 8. Java/Spring Example: Custom Metric Instrumentation & Distributed Tracing

```java
@Service
public class SubscriberRechargeService {

    private final MeterRegistry meterRegistry;
    private final Counter rechargeSuccessCounter;
    private final Counter rechargeFailureCounter;
    private final Timer rechargeLatencyTimer;
    private final Tracer tracer;

    public SubscriberRechargeService(MeterRegistry meterRegistry, Tracer tracer) {
        this.meterRegistry = meterRegistry;
        this.tracer = tracer;

        // 1. Counter for Business Success/Failure Metrics
        this.rechargeSuccessCounter = Counter.builder("telecom_recharge_total")
            .description("Total number of successfully processed subscriber recharges")
            .tag("status", "success")
            .register(meterRegistry);

        this.rechargeFailureCounter = Counter.builder("telecom_recharge_total")
            .description("Total number of failed subscriber recharges")
            .tag("status", "failed")
            .register(meterRegistry);

        // 2. Timer with Percentiles for SLA Tracking
        this.rechargeLatencyTimer = Timer.builder("telecom_recharge_latency_seconds")
            .description("Execution latency of subscriber recharge workflow")
            .publishPercentiles(0.5, 0.95, 0.99) // p50, p95, p99
            .register(meterRegistry);
    }

    public void processRecharge(String msisdn, double amount) {
        // Enclosing execution inside a custom Tracing Span
        Span newSpan = tracer.nextSpan().name("telecom-recharge-execution").start();

        try (Tracer.SpanInScope ws = tracer.withSpan(newSpan)) {
            // Inject business contextual attribute into Span (NOT into Prometheus metric labels!)
            newSpan.tag("subscriber.msisdn", msisdn);
            newSpan.tag("recharge.amount", String.valueOf(amount));

            rechargeLatencyTimer.record(() -> {
                // Execute core recharge logic...
                executeBillingDeduction(msisdn, amount);
                rechargeSuccessCounter.increment();
            });

        } catch (Exception ex) {
            newSpan.error(ex);
            rechargeFailureCounter.increment();
            throw ex;
        } finally {
            newSpan.end();
        }
    }

    private void executeBillingDeduction(String msisdn, double amount) {
        // Business logic
    }
}
```

---

## 9. Illustrative Exercise: Diagnosing a P1 Telecom CRM Outage
* **Incident:** Customer service agents reported that the subscriber search UI was freezing, resulting in SLA breach penalties.
* **Investigation (1-Click Correlated Triage):**
  1. **Grafana Alert:** Alertmanager fired: `CRMSearchLatencyP99 > 5000ms`.
  2. **Metrics to Traces:** Engineer opened the Grafana latency graph and clicked on the outlier spike ($9,200$ms), which immediately linked to matching **Jaeger Traces**.
  3. **Trace Waterfall:** The trace showed the request took 9,210ms total:
     - `API Gateway`: 5ms
     - `CRM Service`: 12ms
     - `MySQL SELECT crm_subscribers`: **9,190ms** (The exact bottleneck!)
  4. **Trace to Log:** Clicked the trace ID to jump into Loki logs. The log output showed the exact SQL query with parameters.
* **Root Cause:** A database index was accidentally dropped during a nightly migration script, forcing full table scans on 40 million rows.
* **Resolution:** Re-created the index online in 3 minutes. Total MTTR: **8 minutes**.

---

## 10. Common Mistakes
1. **Adding Dynamic IDs to Prometheus Metric Labels:** Writing `Counter.builder("order").tag("userId", userId)` destroys Prometheus memory with millions of metrics. Put dynamic IDs in **Logs** and **Trace Spans**, not metric labels!
2. **Alerting on Symptoms vs. Causes (Alert Fatigue):** Alerting when "Host CPU > 80%" wakes engineers when the application is operating perfectly. **Alert on user impact (High HTTP 5xx error rate or SLO latency breach)**.
3. **Unstructured Plaintext Logging:** Logging `log.info("User " + id + " failed")` forces regular expression parsing during log searches. Always use **structured JSON logging**.
4. **Failing to Mask PII in Logs:** Outputting customer credit card numbers, passwords, or plain MSISDNs into distributed logs violates GDPR and telecom privacy standards.

---

## 11. Performance Considerations
* **Trace Sampling Strategies:** In a system handling 50,000 requests/sec, capturing 100% of all traces will consume terabytes of storage and saturate network bandwidth.
  - **Head-Based Sampling:** Sample a fixed percentage (e.g., 5% of healthy traffic) at the ingress gateway.
  - **Tail-Based Sampling:** The OpenTelemetry Collector buffers spans in memory and samples **100% of errors and high-latency requests**, while sampling only 1% of fast, successful requests.
* **Asynchronous Logging:** Use LMAX Disruptor-backed asynchronous logging in Logback/Log4j2 (`AsyncAppender`). Writing logs synchronously to disk or network sockets blocks worker threads and degrades throughput.

---

## 12. Security Considerations
* **Audit Trail Immutability:** Store compliance audit logs (who accessed customer subscriber records) in an S3 bucket configured with **S3 Object Lock (Compliance Mode)** to prevent deletion or tampering even by cloud administrators.
* **Masking Sensitive Data in MDC:** Implement a Logback `ValueMasker` that automatically regex-detects and masks sensitive fields (`msisdn`, `cvv`, `password`) before serializing JSON log records.

---

## 13. Core Interview Questions & Answers

### Q1: What is the difference between Observability and Monitoring?
**Answer:**
* **Monitoring:** Tells you *when* something is wrong based on predefined rules and static thresholds ("Is CPU > 80%?", "Is server returning 200 OK?"). It is passive and detects known failure modes.
* **Observability:** Provides the rich, contextual telemetry (Metrics, Logs, Traces) necessary to infer *why* the system entered an unexpected, novel state that was never anticipated.

### Q2: What is the difference between Prometheus and Grafana?
**Answer:**
* **Prometheus:** The time-series metrics data collection and storage engine. It actively scrapes HTTP endpoints (`/actuator/prometheus`) via a pull model, stores time-series data, and evaluates PromQL alerting rules.
* **Grafana:** The visualization and dashboarding platform. It connects to Prometheus (metrics), Tempo (traces), and Loki (logs) as data sources to display graphs and dashboards in a single UI.

### Q3: How does Trace Context propagate across an asynchronous Kafka topic?
**Answer:** The producer injects the W3C `traceparent` header into the **Kafka Record Headers** (`record.headers().add("traceparent", bytes)`). The consumer extracts the `traceparent` header from incoming record metadata and sets it as the parent span context in the consumer thread's Tracer, maintaining an unbroken distributed trace waterfall across the asynchronous message queue.

### Q4: What is the difference between p50, p95, and p99 latency?
**Answer:**
* **p50 (Median):** 50% of requests are faster than this number.
* **p95:** 95% of requests are faster than this number; represents typical user experience.
* **p99:** 99% of requests are faster; highlights the worst 1% of tail latency (e.g., requests suffering from GC pauses, database lock contention, or cache misses). Averages hide bottlenecks; percentiles expose them.

### Q5: What is a Blameless Postmortem?
**Answer:** An incident retrospective focused on systemic, architectural, and operational failures rather than punishing human error. It assumes engineers acted in good faith with the information available. It documents the root cause, timeline, impact, and actionable preventative tasks (Five Whys methodology) to prevent recurrence.

---

## 14. Deep Interview Questions (Staff / Principal Level)

### Q1: Explain how Prometheus Pull-based scraping handles dynamic Kubernetes pod autoscaling.
**Answer:** Prometheus uses **Kubernetes Service Discovery (`kubernetes_sd_configs`)**:
1. Prometheus continuously watches the Kubernetes API server for pod lifecycle events.
2. When the HPA scales CRM pods from 3 to 15, Prometheus detects the new pod IPs matching the scrape annotations (`prometheus.io/scrape: "true"`).
3. Prometheus automatically adds the new pod endpoints to its internal scrape target pool and begins polling `/actuator/prometheus` over HTTP.
4. When pods are terminated, Prometheus marks their series as stale and removes them from the target list without manual configuration.

### Q2: How do you calculate Error Budget Burn Rate for predictive alerting?
**Answer:** Alerting on static error thresholds is either too slow or too sensitive. **Burn Rate Alerting** measures how fast the service is consuming its allowable Error Budget:
* For a 99.9% SLO (0.1% budget) over 30 days:
  - **Burn Rate 1:** Consumes 100% of the budget in exactly 30 days.
  - **Burn Rate 14.4:** Consumes 100% of the budget in 2 days (2% consumed in 1 hour).
* **Multi-Window Multi-Burn-Rate Alert:** Page engineers immediately if a $14.4\times$ burn rate is sustained over both a short window (5 mins) and long window (1 hour). This detects severe outages in minutes while eliminating false alarms from brief 30-second blips.

### Q3: What is Tail-Based Sampling in OpenTelemetry and how does it operate?
**Answer:** Head-based sampling decides whether to sample a trace at the moment the request enters the gateway (before knowing whether it will succeed or fail).  
**Tail-Based Sampling** delays the sampling decision until the *entire trace has finished executing*:
1. The OpenTelemetry Collector buffers all spans belonging to a trace in a temporary memory ring buffer.
2. Once the final root span finishes, the collector evaluates sampling rules:
   - Did any span return HTTP 5xx or throw an exception? $\to$ **Sample 100%**.
   - Did the total trace duration exceed 2,000ms? $\to$ **Sample 100%**.
   - Did it succeed in 50ms? $\to$ **Sample 1%**.
3. Can reduce tracing storage and network cost while retaining selected errors, slow traces, and representative healthy traffic; no sampling strategy captures every anomaly automatically.

---

## 15. Comparison with Alternatives

| Feature | OpenTelemetry (Open Source) | Datadog | New Relic | Dynatrace |
|---|---|---|---|---|
| **Cost Model** | Free open-source (Infrastructure cost) | High SaaS cost per host/GB | High SaaS cost per user/GB | High SaaS enterprise cost |
| **Vendor Lock-In** | Zero (Switch backends anytime) | High | High | High |
| **Collector Protocol**| OTLP Standard (Industry default) | Proprietary Agent | Proprietary Agent | OneAgent Proprietary |
| **Best For** | Modern Enterprise Cloud-Native | Wealthy startups & enterprises | Legacy IT monitoring | Complex AI automated root-cause |

---

## 16. When NOT to Use It
1. **Ultra-Verbose Debug Logging in Production:** Leaving `logging.level.root=DEBUG` in production generates gigabytes of disk I/O per minute, degrading CPU performance and filling disks. Keep production at `INFO` or `WARN`.
2. **High-Frequency Inner Loop Tracing:** Adding custom tracing spans inside a loop executing 500,000 times will degrade execution speed by 10x due to object allocation and timestamp lookups.

---

## 17. Hands-on Exercise: Calculate Error Budget for 99.9% SLA
**Scenario:** 6D CRM platform processes 20 million subscriber transactions per month. SLA target is 99.9% availability.

```text
1. Total Monthly Requests: 20,000,000
2. Allowable Unreliability (Error Budget) = 100% - 99.9% = 0.1% = 0.001
3. Total Allowable Failed Transactions:
   20,000,000 * 0.001 = 20,000 failed requests permitted per month.
4. Total Monthly Downtime Permitted:
   30 days * 24 hrs * 60 mins = 43,200 minutes.
   43,200 * 0.001 = 43.2 minutes of total downtime per month.
5. Operating Rule:
   If an incident causes 15,000 failed requests in 2 hours, 
   75% of the monthly error budget is burned! 
   All non-critical feature deployments must be paused until reliability mitigations are shipped.
```

---

## 18. Project Application: Telecom CRM Core Platform
How this could connect to a future observable service (verify actual tooling and ownership):
* **Where this applies:**
  1. **Strict Production SLA Adherence:** Instrumenting subscriber balance checks and billing activations with Micrometer timers to prove 99.9% SLA compliance to telecom operators.
  2. **Production Incident RCA practice:** In a future observable service, use blameless postmortems and distributed traces to distinguish application failures from downstream/network failures; verify actual tools and ownership before presenting this as experience.
  3. **MDC Correlation in Production Support:** Ensuring every customer support agent search automatically injects `traceId` and `msisdn` into Logback MDC, allowing engineers to grep a single trace ID and view the entire multi-service lifecycle of a failed transaction.

---

## 19. Senior-Level Interview Answer (The "Gold Standard")

> *"In enterprise production systems, observability is about minimizing Mean Time to Detection (MTTD) and Resolution (MTTR) by establishing clear correlation across metrics, traces, and logs.*  
> *I design our observability around OpenTelemetry standards. For metrics, we instrument Spring Boot with Micrometer and Prometheus, enforcing strict label hygiene to prevent high-cardinality crashes while defining actionable SLIs and Error Budgets rather than noisy infrastructure alerts.*  
> *Across distributed microservices, we propagate W3C `traceparent` headers through REST calls and Kafka messages. By enriching our structured JSON Logback logging with the active `traceId` and `spanId` via MDC, an on-call engineer can transition from a high-latency metric spike directly to the exact distributed trace waterfall and its corresponding error log in a single click, cutting root-cause diagnosis from hours to minutes."*

---

## 20. Real-World Troubleshooting Scenarios

### Scenario A: High Alert Noise & Alert Fatigue during Night Shifts
* **Symptom:** On-call engineers receive 30 Slack/PagerDuty pages every night for "CPU > 85%" on batch worker nodes, but no customer transactions are failing. Engineers begin ignoring alerts.
* **Root Cause:** Alerts are configured on low-level infrastructure utilization rather than user-impacting business SLIs.
* **Remediation:**
  1. Delete static CPU and RAM alerts.
  2. Re-anchor alerting on **SLO Multi-Window Burn Rates**: alert only if HTTP 5xx error rate exceeds 1% or if p99 latency exceeds 2,000ms over both a 5-minute and 1-hour window.
  3. Nighttime pages dropped by 95%; alert actionable signal reached 100%.

### Scenario B: Tracing Data Overwhelming Network and Storage
* **Symptom:** As telecom traffic scaled to 40,000 TPS, the OpenTelemetry Collector exhausted pod memory, and Grafana Tempo storage bills escalated to $15,000/month.
* **Root Cause:** 100% head-based tracing was enabled in production.
* **Remediation:**
  1. Implement **Tail-Based Sampling** in the OpenTelemetry Collector pipeline.
  2. Configure rules to retain 100% of traces containing HTTP status $\ge 400$, 100% of traces with latency $>1,500$ms, and sample only 2% of normal 200 OK traces.
  3. Storage volume decreased by 88% while retaining every single production failure.
