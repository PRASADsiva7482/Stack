# 33. LLD and Machine-Coding Workbook

**Status:** Practice workbook.  
**Goal:** Turn Java design knowledge into clean, extensible, testable code under interview time limits.

## 1. LLD interview sequence

1. Clarify actors, use cases, constraints, and out-of-scope behavior.
2. Identify nouns as candidate objects and verbs as operations.
3. Separate domain state from infrastructure concerns.
4. Choose interfaces at points of variation, not everywhere.
5. Define invariants and invalid transitions.
6. Design for testability and thread-safety only where required.
7. Implement the smallest working flow, then extend.
8. Write tests for normal, invalid, duplicate, concurrent, and failure cases.
9. Explain a future extension and the trade-off of the current design.

## 2. Pattern selection guide

| Need | Useful pattern | Warning |
|---|---|---|
| Select behavior by type/configuration | Strategy | Avoid a class for every trivial branch |
| Construct valid complex object | Builder/factory | Keep validation close to construction |
| Add cross-cutting behavior | Decorator/proxy | Avoid hidden ordering and deep chains |
| Notify subscribers | Observer | Handle lifecycle, ordering, and failure |
| Convert one API to another | Adapter | Do not leak external types into the domain |
| Sequence states/transitions | State machine | Make illegal transitions explicit |
| Queue a command for retry/audit | Command | Idempotency still belongs to execution |
| Process through ordered handlers | Chain of Responsibility | Define stop/continue behavior |

Singleton is rarely the best interview answer: it hides dependencies, complicates tests, and introduces lifecycle/global-state problems. In Spring, prefer a container-managed bean with constructor injection.

## 3. Ten machine-coding problems

| Problem | Core objects | Senior concerns |
|---|---|---|
| Parking lot | Vehicle, spot, ticket, pricing | allocation policy, concurrency, payment failure |
| Vending machine | Product, inventory, state, payment | invalid transitions, refunds, exact money |
| Elevator | Elevator, request, scheduler, state | scheduling policy, concurrent requests |
| Payment processor | Payment, provider, state, ledger | idempotency, callback, retry, reconciliation |
| Notification service | Channel, template, preference, delivery | rate limits, retry, ordering, fan-out |
| Workflow engine | Definition, node, token, transition | durable state, retries, timers, compensation |
| Rate limiter | Bucket, clock, policy, key | thread safety, distributed coordination |
| Logging framework | Logger, appender, formatter, level | async queue, backpressure, ordering |
| Cache | Entry, policy, eviction, loader | TTL, LRU, concurrency, stampede |
| Task scheduler | Task, queue, worker, retry policy | persistence, cancellation, fairness |

## 4. Example: extensible notification design

```java
public record Notification(String recipient, String body, Channel channel) {
    public enum Channel { EMAIL, SMS, PUSH }
}

public interface NotificationSender {
    Notification.Channel channel();
    void send(Notification notification);
}

public final class NotificationService {
    private final Map<Notification.Channel, NotificationSender> senders;

    public NotificationService(List<NotificationSender> senderList) {
        this.senders = senderList.stream().collect(Collectors.toUnmodifiableMap(
            NotificationSender::channel, Function.identity()));
    }

    public void send(Notification notification) {
        NotificationSender sender = senders.get(notification.channel());
        if (sender == null) {
            throw new IllegalArgumentException("Unsupported channel: " + notification.channel());
        }
        sender.send(notification);
    }
}
```

Why this works: adding a channel does not modify the service’s selection logic. Production additions would include validation, authorization, idempotency, timeout, retry policy, delivery status, metrics, and a durable outbox. Do not put network calls directly into a domain object.

## 5. Example: thread-safe token bucket

For an in-memory exercise:

```java
final class TokenBucket {
    private final long capacity;
    private final double refillPerNano;
    private long tokens;
    private long lastNanos;

    TokenBucket(long capacity, double tokensPerSecond, long nowNanos) {
        if (capacity <= 0 || tokensPerSecond <= 0) throw new IllegalArgumentException();
        this.capacity = capacity;
        this.refillPerNano = tokensPerSecond / 1_000_000_000.0;
        this.tokens = capacity;
        this.lastNanos = nowNanos;
    }

    synchronized boolean tryAcquire(long nowNanos) {
        long elapsed = Math.max(0, nowNanos - lastNanos);
        tokens = Math.min(capacity, tokens + (long) (elapsed * refillPerNano));
        lastNanos = nowNanos;
        if (tokens == 0) return false;
        tokens--;
        return true;
    }
}
```

This is a single-process exercise. A distributed limiter needs a shared atomic state or a gateway policy, clock considerations, failure behavior, and a clear decision about fail-open versus fail-closed.

## 6. Machine-coding rubric

Score each problem from 0-4:

- 0: cannot model the problem.
- 1: partial code with broken invariants.
- 2: happy path works but weak extension/tests.
- 3: correct, readable, extensible, tested solution.
- 4: also handles concurrency, failure, observability, and trade-offs appropriately.

Do not over-engineer before the happy path works. Do not claim thread safety unless you identify the shared mutable state and the synchronization strategy.

## 7. Practice schedule

| Week | Problems | Deliverable |
|---:|---|---|
| 1 | Parking lot, vending machine | class diagram and happy-path tests |
| 2 | Notification, payment | interfaces, idempotency and failure tests |
| 3 | Cache, rate limiter | eviction/time tests and concurrency test |
| 4 | Workflow engine, scheduler | state model, retry, cancellation |
| 5 | Elevator, logging | policy abstraction and backpressure |
| 6 | Random unseen design | 90-minute machine-coding simulation |

## 8. Interview questions

1. Why use composition instead of inheritance here?
2. Where is the variation point in your design?
3. Which invariants must never be violated?
4. How would you make the design thread-safe?
5. What happens if the external provider times out after accepting the request?
6. How do you make retries idempotent?
7. What should be persisted and what can remain in memory?
8. How would you test time-dependent behavior?
9. Where would you add observability?
10. What would you change at ten times the scale?

