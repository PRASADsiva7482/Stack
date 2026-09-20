# 06. Redis & Distributed Caching: Architecture & Senior Guide
> **Evidence warning:** Redis is a learning target, not production experience verified by the original resume. Scenarios and numbers are illustrative.
**Target Profile:** Senior Product Software Engineer (In-Memory Architecture, Distributed Locking, Redisson, Cache Invalidation)  
**Author:** Siva Prasad Vajja  
**Domain Alignment:** Telecom Session Management, Prepaid Balance Caching, High-Speed Rate Limiting  

---

## 1. Definition
**Redis (Remote Dictionary Server)** is an open-source, in-memory, key-value data structure store used as a distributed cache, message broker, and in-memory database. Rather than functioning as a simplistic string cache, Redis provides rich native data structures (Strings, Hashes, Lists, Sets, Sorted Sets, Streams, Bitmaps, and HyperLogLogs). At the senior level, it requires mastery of the **single-threaded I/O multiplexed event loop, eviction algorithms, persistence mechanisms (RDB/AOF), distributed locking protocols (Redlock/Watchdog), and cache invalidation architectures (Cache Stampede, Penetration, Avalanche)**.

---

## 2. Why It Exists
Disk-based relational databases (MySQL, PostgreSQL) hit physical I/O limits under high concurrency:
1. **Disk Latency:** Relational queries reading from disk take 5ms–50ms. Redis operates entirely in RAM, delivering sub-millisecond responses ($<1$ms).
2. **Read Concurrency Limits:** A standard database instance struggles past 5,000–10,000 queries per second (QPS). Redis easily services **100,000+ QPS** on a single core.
3. **Complex Atomic Operations:** Operations like atomic counters, rate limiting sliding windows, and leaderboard rankings are slow in SQL but executed natively in Redis with $O(1)$ or $O(\log N)$ time complexity.

---

## 3. Problem It Solves
* **Database Overload & Query Latency:** Offloads 80%–95% of read traffic from relational databases.
* **Distributed Race Conditions:** Provides distributed mutex locks (`SETNX`, Redisson) across clustered microservices.
* **API Throttling & DDoS:** Solves high-speed rate limiting via sliding window algorithms in memory.
* **Session State in Stateless Microservices:** Stores user sessions centrally across horizontally scaled backend pods.

---

## 4. Internal Working

### 4.1 Why Redis is Fast: The Single-Threaded Event Loop
A common misconception is that high concurrency requires hundreds of threads. Redis uses a **Single-Threaded Reactor Model** powered by OS I/O multiplexing (`epoll` on Linux, `kqueue` on macOS):
1. **Zero Context Switching:** Eliminates CPU thread context switching and thread synchronization mutex locks.
2. **Pure In-Memory Operations:** All operations execute directly against main RAM.
3. **I/O Multiplexing:** A single OS thread monitors thousands of client sockets via `epoll_wait()`. When a socket becomes readable, the event loop dispatches the command, executes it sequentially, and writes the response.
*(Note: Redis 6.0+ introduced multi-threaded I/O for network read/write operations, but command execution remains strictly single-threaded and atomic).*

```
[ Client 1 ] [ Client 2 ] [ Client 3 ] ... [ Client N ]
           │          │          │                    │
           ▼          ▼          ▼                    ▼
     +------------------------------------------------------+
     |          OS I/O Multiplexing (epoll / kqueue)        |
     +------------------------------------------------------+
                                │ (File Event Demultiplexer)
                                ▼
     +------------------------------------------------------+
     |           Sequential Event Dispatcher Loop           |
     |  1. Parse Command -> 2. Execute in RAM -> 3. Return   |
     +------------------------------------------------------+
```

### 4.2 Core Data Structures & Internal Encodings
* **Strings:** Simple Dynamic String (SDS). Binary-safe, tracks length in $O(1)$, prevents buffer overflows.
* **Hashes:** Stored as `ziplist`/`listpack` when small ($<512$ entries); switches to a hash table (`dict`) when large.
* **Sorted Sets (ZSet):** Combines a **Hash Map** ($O(1)$ score lookup) and a **SkipList** ($O(\log N)$ range queries and ranking).
* **HyperLogLog:** Probabilistic data structure counting unique items (cardinality) up to billions with a fixed memory footprint of only **12 KB** with a standard error of 0.81%.

### 4.3 Persistence: RDB vs. AOF
* **RDB (Redis Database Backup):** Point-in-time snapshots of the dataset saved to disk at specified intervals.
  - *Mechanism:* Uses `fork()` system call to create a child process. The child process writes data to a temporary file utilizing OS **Copy-On-Write (COW)** memory semantics while the parent continues serving traffic.
  - *Trade-off:* Fast restarts, compact format, but potential data loss between snapshot intervals (e.g., last 5 minutes).
* **AOF (Append-Only File):** Logs every write command received by the server to an append-only file.
  - *Fsync Policies:* `appendfsync always` (slow, zero loss), `everysec` (recommended default, max 1 second loss), `no` (OS decides).
  - *AOF Rewrite:* Background process rewrites the log to the minimal set of commands needed to rebuild the current state.

### 4.4 Cache Failure Modes & Senior Invalidation Patterns
1. **Cache Stampede (Thundering Herd):** A popular cached key expires under heavy traffic. Thousands of concurrent requests experience a cache miss simultaneously and hammer the database together.
   - *Fix:* Mutual exclusion using a distributed lock (`Redisson`), or probabilistic early expiration (XFetch algorithm).
2. **Cache Penetration:** Requests query non-existent keys (e.g., `id = -9999`). Requests bypass cache and hit the database repeatedly.
   - *Fix:* Cache null values with a short TTL (e.g., 60s) or employ a **Bloom Filter** in front of Redis to reject non-existent keys instantly.
3. **Cache Avalanche:** Thousands of keys expire at the exact same second, causing a sudden traffic tidal wave onto the database.
   - *Fix:* Add random jitter to key TTLs (`TTL = baseTTL + random(0, 300)`).

---

## 5. Architecture

```
+-------------------------------------------------------------------------+
|                       Redis Cluster Architecture                        |
+-------------------------------------------------------------------------+
|  [ Microservices (Lettuce / Redisson Cluster Client) ]                  |
|           │                                                             |
|           ▼ (CRC16(key) % 16384 Hash Slot Routing)                     |
|  +-------------------------------------------------------------------+  |
|  | Master Node A (Slots 0 - 5460)      <-- Replication --> Replica A |  |
|  | Master Node B (Slots 5461 - 10922)  <-- Replication --> Replica B |  |
|  | Master Node C (Slots 10923 - 16383) <-- Replication --> Replica C |  |
|  +-------------------------------------------------------------------+  |
|  Node Inter-Communication: Cluster Bus over TCP (Gossip Protocol)       |
|  Automatic Failover: Master failure detected by gossip quorum voting   |
+-------------------------------------------------------------------------+
```

---

## 6. Important Components
1. **Redis Cluster Hash Slots:** Keyspace is divided into exactly **16,384 slots**. The master node for a key is calculated via: `slot = CRC16(key) % 16384`. Hash tags (e.g., `{user:101}:profile`) force multiple keys into the same slot to allow multi-key transactions.
2. **Redisson:** Feature-rich Java Redis driver providing advanced distributed Java objects (`RLock`, `RMapCache`, `RRateLimiter`) with automatic lease renewal.
3. **Watchdog Mechanism (Redisson):** Automatically renews a distributed lock's expiration time every 10 seconds as long as the holding thread is still executing, preventing premature lock release during long tasks.
4. **Eviction Policies (`maxmemory-policy`):**
   - `allkeys-lru`: Evicts Least Recently Used keys regardless of TTL.
   - `volatile-lru`: Evicts LRU keys among those with an expiration set.
   - `allkeys-lfu`: Evicts Least Frequently Used keys.
   - `noeviction`: Returns an error on write when memory is full.

---

## 7. Example: Atomic Distributed Lock via Redis Lua Script

```lua
-- ACQUIRE LOCK (Single Atomic Command via String):
-- SET lock:subscriber:101 <unique_uuid> NX PX 30000

-- RELEASE LOCK ATOMICALLY VIA LUA:
-- Guarantees a thread only releases the lock if it STILL holds it (matches UUID)
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

---

## 8. Java/Spring Example: Redisson Distributed Lock & Cache-Aside

### 8.1 Redisson Distributed Lock Implementation
```java
@Service
public class SubscriberRechargeService {

    private static final Logger log = LoggerFactory.getLogger(SubscriberRechargeService.class);
    private final RedissonClient redissonClient;
    private final SubscriberRepository subscriberRepository;

    public SubscriberRechargeService(RedissonClient redissonClient, SubscriberRepository subscriberRepository) {
        this.redissonClient = redissonClient;
        this.subscriberRepository = subscriberRepository;
    }

    public void processRecharge(String msisdn, double amount) {
        String lockKey = "lock:recharge:" + msisdn;
        RLock lock = redissonClient.getLock(lockKey);

        try {
            // Try acquiring lock: wait up to 5s, auto-lease 10s (or -1 for Watchdog renewal)
            boolean isLocked = lock.tryLock(5, TimeUnit.SECONDS);
            if (!isLocked) {
                throw new ConcurrencyException("Recharge already in progress for MSISDN: " + msisdn);
            }

            log.info("Acquired distributed lock for MSISDN: {}. Processing balance...", msisdn);
            // Execute business logic with protected isolation
            Subscriber sub = subscriberRepository.findByMsisdn(msisdn)
                .orElseThrow(() -> new NotFoundException("Subscriber not found"));
            sub.setBalance(sub.getBalance() + amount);
            subscriberRepository.save(sub);

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Lock acquisition interrupted", e);
        } finally {
            // Ensure lock is unlocked ONLY if current thread holds it
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
                log.info("Released distributed lock for MSISDN: {}", msisdn);
            }
        }
    }
}
```

### 8.2 Spring `@Cacheable` with Dynamic TTL & Jitter
```java
@Service
public class PlanCatalogService {

    @Cacheable(value = "plans", key = "#planCode", unless = "#result == null")
    public PlanDetailsDto getPlanDetails(String planCode) {
        // Slow database query:
        return planRepository.findDetailedPlanByCode(planCode)
            .map(PlanDetailsDto::fromEntity)
            .orElse(null);
    }

    @CacheEvict(value = "plans", key = "#planCode")
    public void updatePlanDetails(String planCode, PlanUpdateDto update) {
        planRepository.updatePlan(planCode, update);
        // Evicts cache on write (Cache-Aside pattern)
    }
}
```

---

## 9. Production Use Case: High-Speed Telecom API Rate Limiter
* **Problem:** During major promotional campaigns, unauthorized bots hammer the SIM activation endpoint with 30,000 requests per second, threatening to crash the legacy billing backend.
* **Implementation:** Deploy a **Sliding Window Rate Limiter** using Redis **Sorted Sets (ZSet)**:
  1. Record request timestamps as members in a ZSet keyed by client IP: `ZADD ratelimit:ip:10.0.1.5 <current_timestamp> <unique_request_id>`.
  2. Remove entries older than 60 seconds: `ZREMRANGEBYSCORE ratelimit:ip:10.0.1.5 0 <current_timestamp - 60000>`.
  3. Count remaining requests: `ZCARD ratelimit:ip:10.0.1.5`.
  4. If count $>100$, reject with HTTP 429 Too Many Requests.
  5. Packaged inside a Lua script to execute atomically in $<0.5$ms.

---

## 10. Common Mistakes
1. **Running `KEYS *` in Production:** `KEYS *` performs an $O(N)$ full keyspace scan. Because Redis is single-threaded, running `KEYS *` on a database with 10 million keys **freezes all Redis operations for several seconds**, taking down dependent microservices. Always use `SCAN`.
2. **Missing Key Expirations (TTLs):** Writing temporary cached data without setting an explicit TTL causes memory to grow monotonically until `maxmemory` is reached, triggering aggressive evictions or crashing with OOM.
3. **Big Keys (Huge Hash Maps or Sets):** Storing 100,000 elements in a single Set or Hash causes network latency spikes and blocks the single thread when the key is updated or deleted. Split big keys across multiple shards (e.g., `user:101:orders:2026-09`).
4. **Ignoring Redis Cluster Hash Tags:** Attempting multi-key transactions (`MGET`, Lua scripts) across keys that hash to different slots fails with `CROSSSLOT Keys in request don't hash to the same slot`. Use hash tags: `{user:101}:profile` and `{user:101}:orders`.

---

## 11. Performance Considerations
* **Pipelining:** When executing multiple independent commands (e.g., setting 50 keys), do not execute them one by one. Use **Redis Pipelining** to send all 50 commands in a single network socket packet, reducing 50 network round-trips to exactly 1 round-trip.
* **Serialization Choice:** Avoid default Java native serialization (`JdkSerializationRedisSerializer`) which produces bloated binary payloads. Use **Jackson JSON** or **Protobuf/Kryo** for ultra-compact payloads, saving 60% of memory.

---

## 12. Security Considerations
* **Disable/Rename Dangerous Commands:** In `redis.conf`, rename or disable dangerous administrative commands:
  ```text
  rename-command FLUSHALL ""
  rename-command FLUSHDB ""
  rename-command CONFIG "SYS_CONFIG_SECURE"
  ```
* **Authentication & TLS:** Enforce `requirepass` with strong passwords or ACL users (`ACL SETUSER crm-service on >password ~crm:* +@read +@write`) and enable TLS over port 6379.

---

## 13. Core Interview Questions & Answers

### Q1: What is the difference between Cache-Aside, Write-Through, and Write-Behind?
**Answer:**
* **Cache-Aside (Most Common):** Application queries cache. On miss, it reads from database and updates cache. Application updates database directly and evicts cache.
* **Write-Through:** Application writes to cache. The cache synchronously updates the database before returning.
* **Write-Behind (Write-Back):** Application writes to cache, which immediately returns. The cache asynchronously batches and writes updates to the database in the background (risk of data loss if cache crashes).

### Q2: How does Redisson's Watchdog prevent premature lock release?
**Answer:** If you acquire an `RLock` without specifying a `leaseTime`, Redisson assigns a default lease of 30 seconds and launches a background timer thread called the **Watchdog**. Every 10 seconds (one-third of the lease time), the Watchdog issues an asynchronous command to Redis extending the lock expiration back to 30 seconds. If the application crashes, the Watchdog dies, and the lock automatically expires after 30 seconds, preventing deadlocks.

### Q3: How do you handle Cache Stampede (Thundering Herd)?
**Answer:**
1. **Distributed Mutex:** The first thread that experiences a cache miss acquires a Redis lock to query the database and populate the cache. All other threads wait or return stale data.
2. **Probabilistic Early Expiration (XFetch):** Background threads probabilistically recompute and refresh the cached key *before* it physically expires, based on remaining TTL and computation cost.

### Q4: What is the difference between RDB and AOF persistence?
**Answer:**
* **RDB:** Periodic compact point-in-time binary snapshots generated via child process `fork()`. Fast restarts, but risks losing minutes of data.
* **AOF:** Append-only log recording every write command. Safer with minimal data loss (`appendfsync everysec`), but larger file size and slower restarts.

### Q5: Why does Redis Cluster use 16,384 hash slots instead of 65,536?
**Answer:** Redis Cluster nodes continuously exchange heartbeat packets containing a slot bitmap using the Gossip protocol. A bitmap for 16,384 slots takes exactly **2 KB** of packet overhead. Scaling to 65,536 slots would quadruple heartbeat packet sizes to 8 KB, saturating network bandwidth across hundreds of nodes. Furthermore, 16,384 slots is more than sufficient for the recommended maximum cluster size of 1,000 nodes.

---

## 14. Deep Interview Questions (Staff / Principal Level)

### Q1: Explain the Redlock Algorithm and the academic critique against it.
**Answer:** Redlock was proposed by Salvatore Sanfilippo (antirez) for distributed locking across $N$ independent master nodes (typically 5):
1. Client gets current timestamp.
2. Tries to acquire the lock across all 5 nodes sequentially using a short timeout.
3. Lock is considered acquired only if acquired on a majority ($> N/2$, e.g., 3 nodes) within a total elapsed time less than lock validity time.
* **Critique (Martin Kleppmann):** In real distributed systems with unpredictable OS clock drift, Stop-The-World GC pauses, and network delays, Redlock is unsafe for mutual exclusion unless paired with **Fencing Tokens** (monotonically increasing IDs verified by the storage backend on write).

### Q2: What is a Redis Hash Tag and what problem does it solve in Redis Cluster?
**Answer:** In Redis Cluster, multi-key operations (transactions, Lua scripts) require all keys to reside on the exact same node (same hash slot). By default, keys are hashed by their entire string, placing different keys on different nodes.  
A **Hash Tag** is text enclosed in `{}` inside the key: e.g., `{subscriber:101}:balance` and `{subscriber:101}:plans`. Redis calculates the CRC16 hash **only on the text inside the braces**, guaranteeing that all keys with `{subscriber:101}` map to the exact same hash slot and physical master node.

### Q3: What happens under the hood during memory eviction with `allkeys-lru`?
**Answer:** Redis does **not** maintain a true doubly-linked list of all keys in order of usage (which would consume massive memory and cause lock contention). Instead, it uses an **Approximated LRU algorithm**:
* Every Redis object has a 24-bit field storing the timestamp of its last access (`lru`).
* When memory limit is reached, Redis samples $N$ random keys (default 5 or 10) from the keyspace.
* It evaluates the oldest key among the sample pool and evicts it. This approximated algorithm matches true LRU behavior within 99% accuracy while consuming zero additional memory.

---

## 15. Comparison with Alternatives

| Feature | Redis | Memcached | Hazelcast | Aerospike |
|---|---|---|---|---|
| **Data Structures** | Rich (Hashes, Sets, ZSets, Streams) | Simple Key-Value Strings | Java Collections / Distributed Objects | Key-Value / Document |
| **Thread Model** | Single-Threaded Core + Multi-I/O | Multi-Threaded | Multi-Threaded (JVM) | Multi-Threaded Native C |
| **Persistence** | RDB & AOF | Purely Volatile (No persistence) | Optional Persistence | Hybrid Memory (RAM index + NVMe SSD) |
| **Clustering** | Hash Slots (16,384) | Client-side Consistent Hashing | Dynamic P2P Clustering | Automated Mesh Clustering |
| **Primary Use** | Distributed Cache & Locks | Ultra-simple high-volume cache | In-memory Data Grid (IMDG) | Massive scale (Terabytes of SSD RAM) |

---

## 16. When NOT to Use It
1. **Cold Data Exceeding RAM Budget:** Storing 50 Terabytes of historical logs or dormant customer profiles in Redis is cost-prohibitive. Use SSD-optimized databases like Cassandra or PostgreSQL.
2. **Complex Multi-Table Joins & Foreign Keys:** Redis is not a relational database; modeling complex entity graphs with joins requires cumbersome manual application-level queries.
3. **Zero-Tolerance Single-Node Financial Durability:** Even with `appendfsync always`, Redis is an in-memory database designed for speed. For mission-critical banking ledgers requiring immediate non-volatile ACID commit guarantees, use PostgreSQL or Oracle.

---

## 17. Hands-on Exercise: Implement a Sliding Window Rate Limiter via Lua
**Task:** Write an atomic Redis Lua script enforcing a rate limit of 100 requests per 60 seconds per customer MSISDN.

```java
@Component
public class RedisSlidingWindowRateLimiter {

    private final StringRedisTemplate redisTemplate;
    private final DefaultRedisScript<Long> rateLimitScript;

    public RedisSlidingWindowRateLimiter(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;

        // Atomic Sliding Window Algorithm via Lua
        String lua = """
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])
            local clearBefore = now - window

            redis.call('ZREMRANGEBYSCORE', key, 0, clearBefore)
            local currentRequests = redis.call('ZCARD', key)

            if currentRequests < limit then
                redis.call('ZADD', key, now, now .. '-' .. math.random(1000, 9999))
                redis.call('EXPIRE', key, math.ceil(window / 1000))
                return 1 -- ALLOWED
            else
                return 0 -- BLOCKED (RATE LIMITED)
            end
        """;

        this.rateLimitScript = new DefaultRedisScript<>(lua, Long.class);
    }

    public boolean isAllowed(String msisdn, int limit, long windowMillis) {
        String key = "ratelimit:" + msisdn;
        long now = System.currentTimeMillis();
        Long result = redisTemplate.execute(
            rateLimitScript,
            Collections.singletonList(key),
            String.valueOf(now),
            String.valueOf(windowMillis),
            String.valueOf(limit)
        );
        return result != null && result == 1L;
    }
}
```

---

## 18. Project Application: Telecom CRM Core Platform
How this could connect to a future CRM project (Redis is a learning target; verify actual implementation):
* **Where this applies:**
  1. **Subscriber Balance & Quota Fast Cache:** Caching prepaid data and voice balance in Redis Hashes (`HSET sub:9182373491 data_mb 1024 voice_min 500`). Sub-millisecond reads prevent network gateways from overloading core billing engines.
  2. **Preventing Concurrent Recharge Collisions:** Wrapping the account recharge endpoint with Redisson distributed locks using `msisdn` as the lock key, ensuring a customer cannot trigger multiple simultaneous recharges that corrupt account ledgers.
  3. **Centralized User Session Store:** Storing CRM customer support agent JWT tokens and permissions in Redis with a 30-minute rolling TTL, allowing instant session revocation during security lockouts.

---

## 19. Senior-Level Interview Answer (The "Gold Standard")

> *"In high-throughput distributed systems, Redis serves as our primary acceleration layer, operating on an in-memory single-threaded event loop driven by OS I/O multiplexing (`epoll`). This design delivers sub-millisecond latency and eliminates multi-threaded locking overhead.*  
> *When designing distributed caching, we protect the underlying database against failure modes: we eliminate **Cache Stampedes** using Redisson distributed locks with Watchdog auto-renewal, mitigate **Cache Penetration** by combining Bloom filters with short-lived null caching, and prevent **Cache Avalanches** by adding random jitter to TTL expirations.*  
> *In clustered enterprise topologies, we utilize Hash Tags (`{subscriber:id}:*`) to ensure related keys map to the same hash slot for atomic Lua script executions, while configuring `allkeys-lru` eviction policies to maintain bounded memory consumption under heavy traffic."*

---

## 20. Real-World Troubleshooting Scenarios

### Scenario A: `OOM command not allowed when used memory > 'maxmemory'`
* **Symptom:** Application writes fail with `RedisSystemException: Error in execution; OOM command not allowed`.
* **Root Cause:** Total memory consumed exceeded the `maxmemory` directive in `redis.conf`, and the eviction policy was set to `noeviction` (the default in some managed setups).
* **Investigation:**
  1. Run `redis-cli INFO memory` to inspect `used_memory_human` and `maxmemory_human`.
  2. Identify memory consumers via `redis-cli --bigkeys` or memory analysis tools like `redis-rdb-tools`.
* **Remediation:**
  1. Set an eviction policy: `CONFIG SET maxmemory-policy allkeys-lru`.
  2. Audit application code for keys created without TTL.
  3. Scale up instance RAM or add cluster shards to distribute memory across nodes.

### Scenario B: High Latency & Slowdown due to Slow Commands
* **Symptom:** Microservice API latency jumps from 2ms to 450ms.
* **Diagnosis:** Connect via `redis-cli` and run `SLOWLOG GET 10`.
* **Finding:** The slow log reveals expensive $O(N)$ operations being executed during peak hours:
  - `KEYS crm:subscriber:*` executed by a scheduled reporting job.
  - `SMEMBERS huge_subscriber_group` on a Set containing 500,000 members.
* **Fix:**
  - Replace `KEYS` with iterative cursor-based `SCAN`.
  - Replace `SMEMBERS` with `SSCAN` or redesign the collection into partitioned batches.
