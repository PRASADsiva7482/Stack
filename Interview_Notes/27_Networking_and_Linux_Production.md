# 27. Networking and Linux Production Basics

**Status:** Learning target.  
**Purpose:** Give a Java backend engineer enough operating knowledge to explain and investigate real failures.

## 1. Request path

```text
client -> DNS -> load balancer/proxy -> TLS -> HTTP server -> application thread
       -> database/cache/downstream -> response
```

Every hop has a queue, timeout, connection limit, and failure mode. “The API is slow” is not a root cause.

## 2. TCP, UDP, DNS, and TLS

- TCP provides an ordered, reliable byte stream. Connection setup, congestion control, retransmission, and flow control add latency but protect correctness.
- UDP is datagram-based and does not provide delivery or ordering. Applications must provide those properties when needed.
- DNS maps names to addresses through recursive resolvers, caching, TTLs, and records such as A/AAAA/CNAME. Stale or split DNS can route only some clients incorrectly.
- TLS authenticates the endpoint with certificates and encrypts traffic. HTTPS is HTTP over TLS over TCP; HTTP/3 uses QUIC over UDP.
- Connection pooling avoids repeating TCP/TLS setup but must have bounded size, timeouts, idle validation, and leak monitoring.

## 3. HTTP interview essentials

HTTP/1.1 commonly uses one request/response per connection at a time, though keep-alive and pipelining exist. HTTP/2 multiplexes streams over one connection and compresses headers; it does not make a slow server fast. HTTP/3 uses QUIC and can reduce head-of-line blocking at the transport layer.

Know safe and idempotent methods:

| Method | Typical meaning | Idempotency expectation |
|---|---|---|
| GET | Read | Safe/idempotent |
| POST | Create/command | Not inherently idempotent; use a key when needed |
| PUT | Replace a known resource | Idempotent by contract |
| PATCH | Partial update | Depends on operation design |
| DELETE | Remove/disable | Should be idempotent at API level |

Timeouts must exist at every client and server boundary. A retry without a deadline can outlive the user request and create a retry storm.

## 4. Linux diagnostic commands

```bash
ps -ef | grep java
top -H -p <pid>
free -m
df -h
du -sh /var/log/*
ss -lntp
ss -s
lsof -p <pid>
curl -v --connect-timeout 2 --max-time 5 https://service.example/health
grep -R "correlation-id" /var/log/app
tail -f /var/log/app/application.log
jcmd <pid> VM.command_line
jcmd <pid> Thread.print
jcmd <pid> GC.heap_info
jstat -gcutil <pid> 1s 10
```

Use `awk` for column extraction and `sed` for controlled text transformation, but avoid destructive edits during an incident. Capture timestamps, command output, and the affected instance.

## 5. Production investigation examples

### DNS or connection failure

Check resolution from the same pod/host, endpoint and port, TLS certificate/hostname, proxy settings, security groups/firewall, pool exhaustion, and server listener. Distinguish “cannot connect” from “connects but times out while reading.”

### High CPU

Find the process and hot OS thread with `top -H`, convert the thread ID to hexadecimal, map it in a Java thread dump, and correlate with a CPU profile or GC metrics. A busy thread may be application code, lock spinning, parsing, encryption, or GC.

### Out of disk

Check `df -h` and `du`, identify log rotation or heap dumps, protect the filesystem from filling completely, and clean only approved files. Then fix retention and alert before capacity reaches the failure threshold.

## 6. Java connection path

For a Spring MVC request, filters run before the controller. The server thread may wait on a database pool, HTTP client pool, Redis socket, or lock. A thread dump shows where it waits; metrics show whether the wait is widespread. Increasing thread count can worsen the problem when the downstream dependency is already saturated.

## 7. Practice checklist

1. Use `curl -v` to explain DNS, TCP, TLS, headers, status, and timing.
2. Run a local Java server and inspect its listening socket with `ss`.
3. Create a slow endpoint, capture a thread dump, and identify blocked workers.
4. Fill a test log directory, detect it, and design safe rotation/retention.
5. Explain the difference among DNS failure, TCP refusal, TLS failure, HTTP 503, and read timeout.

## 8. Interview questions

1. Walk through an HTTPS request from DNS to response.
2. TCP versus UDP?
3. What does keep-alive solve?
4. HTTP/1.1 versus HTTP/2 versus HTTP/3?
5. What is a connection pool and how can it fail?
6. Difference between connect timeout and read timeout?
7. What does a 502, 503, and 504 usually indicate?
8. How do you find the thread consuming CPU in a JVM?
9. How do you investigate a port that is not reachable?
10. What evidence does a thread dump provide?
11. Why can adding application threads reduce throughput?
12. How do you debug intermittent DNS failures?

## 9. Senior answer

> “I decompose latency by hop and by queue: DNS, connection/TLS, server processing, downstream calls, and response transfer. I verify the hypothesis with timestamps, traces, pool metrics, thread dumps, and host/network commands. I do not increase retries or thread counts until I know which resource is saturated.”

