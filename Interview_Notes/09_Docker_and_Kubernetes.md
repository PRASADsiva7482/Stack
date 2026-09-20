# 09. Docker & Kubernetes: Containerization & Cloud Orchestration
> **Evidence warning:** Docker/Kubernetes are learning targets, not production ownership verified by the original resume. Scenarios and numbers are illustrative.
**Target Profile:** Senior Product Software Engineer (Container Internals, K8s Architecture, Zero-Downtime Deployments, HPA)  
**Author:** Siva Prasad Vajja  
**Domain Alignment:** Telecom CRM Microservices, Resilient Cloud Orchestration, Production Scalability  

---

## 1. Definition
**Docker and Kubernetes** form the standard runtime foundation of modern cloud-native software. **Docker** provides lightweight container virtualization by packaging applications with all runtime dependencies into immutable images, leveraging Linux kernel primitives (**Namespaces** and **Cgroups**). **Kubernetes (K8s)** is an open-source container orchestration platform that automates container deployment, scaling, healing, service discovery, and rolling updates across distributed server clusters. At the senior level, it requires mastery of **control plane mechanics, pod lifecycle probes, layered JAR caching, cgroup-aware JVM tuning, and zero-downtime rolling updates**.

---

## 2. Why It Exists
Before containers and orchestration:
1. **"Works on My Machine" Syndrome:** Discrepancies between local developer machines and production Linux servers caused environment-specific deployment bugs.
2. **Resource Inefficiency of Virtual Machines (VMs):** VMs run full guest operating systems, consuming gigabytes of RAM and taking minutes to boot. Containers share the host kernel, boot in milliseconds, and consume minimal overhead.
3. **Manual Production Operations:** Manually restarting failed processes, scaling servers during traffic surges, and balancing traffic across nodes is error-prone and unscalable.

---

## 3. Problem It Solves
* **Environment Drift:** Solved by immutable Docker container images.
* **Service Crashes & Outages:** Solved by Kubernetes auto-healing (restarts crashed containers automatically).
* **Traffic Spikes & Idle Capacity:** Solved by Horizontal Pod Autoscaler (HPA) and Cluster Autoscaler.
* **Deployment Downtime:** Solved by rolling updates with readiness probe traffic gatekeeping.

---

## 4. Internal Working

### 4.1 How Containers Work: Linux Kernel Primitives
Containers are **not** virtual machines. A container is simply an ordinary Linux process running in isolation enforced by two kernel features:
1. **Linux Namespaces (Isolation Boundary):**
   - `pid`: Isolates process IDs (container process sees itself as PID 1).
   - `net`: Isolates network interfaces, IP addresses, and routing tables.
   - `mnt`: Isolates filesystem mount points.
   - `ipc`: Isolates Inter-Process Communication and shared memory.
   - `uts`: Isolates hostname and domain name.
   - `user`: Isolates user and group IDs.
2. **Control Groups (cgroups - Resource Limiting):**
   - Enforces strict hardware limits on CPU, Memory, Disk I/O, and Network bandwidth.
   - If a container exceeds its memory cgroup limit, the Linux kernel terminates it with an **OOMKill (Exit Code 137)**.
3. **OverlayFS (Layered Filesystem):**
   - Uses Union Mount to stack read-only image layers on top of each other. A thin writable layer is placed on top (Copy-on-Write).

### 4.2 Kubernetes Control Plane & Worker Architecture
```
+-------------------------------------------------------------------------+
|                         Kubernetes Control Plane                        |
|  +-------------------------------------------------------------------+  |
|  |                 kube-apiserver (REST API Gateway)                 |  |
|  +-----------------------------------+-------------------------------+  |
|          │                           │                           │      |
|          ▼                           ▼                           ▼      |
|  +---------------+          +-------------------+       +-------------+ |
|  |  etcd Cluster |          |   kube-scheduler  |       |  controller | |
|  |  (Distributed |          | (Assigns Pods to  |       |   manager   | |
|  |   Key-Value)  |          |  Optimal Nodes)   |       |  (Healer)   | |
|  +---------------+          +-------------------+       +-------------+ |
+-------------------------------------------------------------------------+
                                       │ (HTTPS / TLS)
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
+---------------------------------------+ +---------------------------------------+
|             Worker Node 1             | |             Worker Node 2             |
|  +---------------------------------+  | |  +---------------------------------+  |
|  |  kubelet (Node Agent)           |  | |  |  kubelet (Node Agent)           |  |
|  +---------------------------------+  | |  +---------------------------------+  |
|  |  kube-proxy (iptables / IPVS)   |  | |  |  kube-proxy (iptables / IPVS)   |  |
|  +---------------------------------+  | |  +---------------------------------+  |
|  |  containerd (CRI Runtime)       |  | |  |  containerd (CRI Runtime)       |  |
|  +---------------------------------+  | |  +---------------------------------+  |
|  [ Pod 1 (CRM) ]  [ Pod 2 (Redis) ]  | | [ Pod 3 (CRM) ]  [ Pod 4 (Kafka) ]  | |
+---------------------------------------+ +---------------------------------------+
```

### 4.3 Pod Lifecycle & Health Probes
A **Pod** is the smallest deployable unit in Kubernetes, consisting of one or more tightly coupled containers sharing the same network namespace (IP) and storage volumes.
* **Startup Probe:** Determines if the application has completed initialization. Disables liveness and readiness checks until it succeeds. Essential for Spring Boot apps that take 20–40 seconds to warm up.
* **Readiness Probe:** Determines if the pod is ready to accept user traffic. If it fails, Kubernetes **removes the pod from the Service Load Balancer endpoints**. Traffic is never routed to an unready pod.
* **Liveness Probe:** Determines if the pod is healthy. If it fails, Kubernetes **kills the container and restarts it**. (Warning: Never point liveness probes to external dependencies like databases, or a database outage will cause all pods to restart simultaneously).

---

## 5. Architecture: K8s Networking & Service Discovery
* **ClusterIP:** Default internal virtual IP. Accessible only within the K8s cluster. `kube-proxy` programs Linux kernel `iptables` or `IPVS` rules to distribute traffic across matching pod IPs.
* **NodePort:** Exposes the service on a static port (30000–32767) on every node's physical IP.
* **LoadBalancer:** Provisions an external cloud load balancer (e.g., AWS ALB/NLB) routing traffic to NodePorts.
* **Ingress:** Layer 7 HTTP reverse proxy (NGINX / Envoy) managing path-based routing (`/api/crm $\to$ crm-service`) and TLS termination.

---

## 6. Important Components
1. **`kube-apiserver`:** Exposes the K8s API. All internal components and `kubectl` interact exclusively through the API server.
2. **`etcd`:** Highly available, distributed Raft-based key-value store holding the complete state of the cluster.
3. **`kubelet`:** Agent running on each worker node ensuring that containers described in `PodSpecs` are running and healthy.
4. **Horizontal Pod Autoscaler (HPA):** Dynamically scales pod replica counts based on CPU, memory, or custom metrics (e.g., Kafka consumer lag).
5. **ConfigMaps & Secrets:** Decouples configuration artifacts and encrypted credentials from container images.

---

## 7. Example: Production Multi-Stage Dockerfile for Spring Boot 3

```dockerfile
# Stage 1: Dependency Extraction using Spring Boot Layer Tools
FROM eclipse-temurin:17-jre-jammy AS builder
WORKDIR /builder
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} application.jar
# Extracts layered JAR for extreme caching speed
RUN java -Djarmode=layertools -jar application.jar extract

# Stage 2: Final Secure Production Runtime
FROM eclipse-temurin:17-jre-jammy
WORKDIR /application

# Create non-root user for security (Principle of Least Privilege)
RUN useradd -u 10001 -m crmuser && chown -R crmuser:crmuser /application
USER 10001

# Copy layers separately: Dependencies change rarely; Application code changes frequently!
COPY --from=builder /builder/dependencies/ ./
COPY --from=builder /builder/spring-boot-loader/ ./
COPY --from=builder /builder/snapshot-dependencies/ ./
COPY --from=builder /builder/application/ ./

# SENIOR JVM TUNING FOR CONTAINERS:
# -XX:+UseContainerSupport: Tells JVM to read cgroup memory/CPU limits instead of physical host
# -XX:MaxRAMPercentage: Reserves 25% of container RAM for OS/metaspace/thread stacks
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"

EXPOSE 8080
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
```

---

## 8. Java/Spring Example: Production Kubernetes Deployment with Actuator Probes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-core-platform
  namespace: production
  labels:
    app: crm-core-platform
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%        # Spin up 25% new pods before terminating old ones
      maxUnavailable: 0     # Keeps old capacity available during the rollout; not an absolute zero-downtime guarantee
  selector:
    matchLabels:
      app: crm-core-platform
  template:
    metadata:
      labels:
        app: crm-core-platform
    spec:
      containers:
        - name: crm-backend
          image: 6dtech/crm-core:v1.4.2
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "production"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: crm-db-secret
                  key: password
          resources:
            requests:
              cpu: "500m"        # 0.5 Core guaranteed
              memory: "1024Mi"   # 1 GB RAM guaranteed
            limits:
              cpu: "2000m"       # 2 Cores max
              memory: "2048Mi"   # 2 GB RAM max (OOMKilled if exceeded)
          
          # INTEGRATION WITH SPRING BOOT ACTUATOR PROBES:
          startupProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            failureThreshold: 30
            periodSeconds: 2     # Allows up to 60s for slow Spring bootstrap
          
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            periodSeconds: 10
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: crm-core-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: crm-core-platform
  minReplicas: 3
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 9. Illustrative Exercise: Resilient Telecom CRM Deployment
* **Challenge:** Deploying a new release of the CRM Core Platform without interrupting customer support agents or failing active telecom subscriber recharge requests.
* **Implementation:**
  1. Configured Spring Boot graceful shutdown: `server.shutdown=graceful` with a 30s timeout.
  2. Set `maxUnavailable: 0` and `maxSurge: 1` in the K8s RollingUpdate strategy.
  3. Mapped Readiness Probes to `/actuator/health/readiness`.
* **Execution:** K8s spins up Pod B (v2) and waits until its readiness probe returns HTTP 200. Only then does K8s route live traffic to Pod B and issue a `SIGTERM` signal to Pod A (v1). Pod A stops accepting new requests, finishes active in-flight recharges within 15 seconds, and terminates cleanly. **Zero dropped calls. Zero 502 Bad Gateways.**

---

## 10. Common Mistakes
1. **Running Containers as Root:** Default container configuration runs as `root` (UID 0). A container breakout vulnerability gives the attacker root privileges over the host physical server. Always define `USER 10001`.
2. **Setting Memory Limits Lower than JVM Heap:** If you set K8s limit `memory: 1024Mi` and JVM flag `-Xmx1024m`, the JVM will allocate 1024MB for heap PLUS extra for Metaspace, thread stacks, and native buffers ($>1200$MB total). The Linux kernel cgroup detects the breach and terminates the container with **OOMKilled (Exit Code 137)**.
3. **Using `latest` Image Tags in Production:** `image: crm:latest` makes rollbacks non-deterministic and prevents Kubernetes from detecting when a new image was pushed. Always use immutable semantic tags or Git commit SHA hashes (`crm:v1.4.2-b89fa1`).
4. **Pointing Liveness Probes to Database Connections:** If the database goes down for 30 seconds, all Spring Boot pods fail their liveness probes simultaneously. Kubernetes kills all pods, triggering an endless crash-loop restart storm. Point liveness *only* to internal JVM state!

---

## 11. Performance Considerations
* **Spring Boot Layer Tools in Docker:** By separating static dependencies from application code using `jarmode=layertools`, image rebuilds on code changes only re-upload a 200KB application layer instead of re-uploading a 150MB monolithic JAR, slashing CI/CD pipeline build times from 4 minutes to **12 seconds**.
* **Graceful Termination Timing:** In Kubernetes, when a pod is terminated:
  - Pod status set to `Terminating` and removed from Service endpoints.
  - Container receives `SIGTERM`.
  - Kubernetes waits for `terminationGracePeriodSeconds` (default 30s) before issuing `SIGKILL`.
  - Ensure `spring.lifecycle.timeout-per-shutdown-phase` is set to 25s, leaving 5 seconds for network draining.

---

## 12. Security Considerations
* **Read-Only Root Filesystem:** Configure container security contexts with `readOnlyRootFilesystem: true`. Force all temporary file writes to mounted `emptyDir` volumes.
* **Network Policies:** By default, all pods in a Kubernetes cluster can communicate with all other pods across all namespaces. Deploy **Calico / Cilium NetworkPolicies** restricting traffic so that only the CRM API Gateway can connect to the core CRM pods on port 8080.

---

## 13. Core Interview Questions & Answers

### Q1: What is the difference between a Container and a Virtual Machine?
**Answer:**
* **Virtual Machine:** Virtualizes the underlying hardware. Includes a full guest OS, hypervisor (VMware/KVM), and dedicated virtualized memory. Heavyweight (Gigabytes), slow boot (minutes).
* **Container:** Virtualizes at the OS kernel level. Containers share the host Linux kernel and isolate processes using Namespaces and Cgroups. Lightweight (Megabytes), near-instantaneous boot (milliseconds).

### Q2: What is the difference between `ReadinessProbe` and `LivenessProbe`?
**Answer:**
* **`ReadinessProbe`:** Checks if the container is ready to serve client requests. If it fails, Kubernetes stops sending network traffic to the pod by removing its IP from the Service endpoint list.
* **`LivenessProbe`:** Checks if the container is alive or stuck in a deadlock. If it fails, Kubernetes forcefully kills and restarts the container.

### Q3: What is Exit Code 137 in Kubernetes?
**Answer:** Exit Code 137 ($128 + 9$) indicates that the container was forcefully killed by the OS kernel using `SIGKILL` (signal 9) because it violated its **Cgroup Memory Limit** (**OOMKilled**). To resolve, increase K8s container memory limits or tune `-XX:MaxRAMPercentage`.

### Q4: How does `ClusterIP` work under the hood without having a physical network card?
**Answer:** A `ClusterIP` is a virtual IP that does not belong to any physical network interface. Instead, **`kube-proxy`** manages Linux kernel packet-filtering rules (`iptables` or `IPVS`). When a packet is addressed to a ClusterIP, the kernel intercepts it at the network layer and rewrites the destination IP (DNAT) to the physical IP address of one of the healthy backend pods matching the service selector.

### Q5: What is the difference between `Requests` and `Limits` in Kubernetes?
**Answer:**
* **`Requests`:** The minimum guaranteed compute resources required to schedule a pod. The `kube-scheduler` uses requests to decide which worker node has sufficient capacity to host the pod.
* **`Limits`:** The maximum hard ceiling the container is permitted to consume. If CPU exceeds limits, the process is throttled. If memory exceeds limits, the container is OOMKilled.

---

## 14. Deep Interview Questions (Staff / Principal Level)

### Q1: Walk through the exact step-by-step lifecycle from running `kubectl apply -f deployment.yaml` to the pod running on a node.
**Answer:**
1. `kubectl` sends an authenticated, authorized JSON manifest to `kube-apiserver`.
2. `kube-apiserver` validates the manifest and persists it to `etcd`.
3. **Deployment Controller** detects the new deployment and creates a `ReplicaSet`.
4. **ReplicaSet Controller** creates the specified number of Pod definitions with `nodeName: null`.
5. **`kube-scheduler`** detects unassigned pods, filters nodes based on resource requests and affinity, scores healthy nodes, and binds the pod to the optimal node by updating `nodeName` in `etcd`.
6. **`kubelet`** running on that target worker node detects the pod assignment via API server watch.
7. `kubelet` calls the **Container Runtime (containerd)** via CRI (Container Runtime Interface) to pull the image and create containers.
8. `kubelet` invokes the **CNI Plugin (Calico/Flannel)** to allocate an IP address and configure network namespaces.
9. Containers start; `kubelet` monitors startup, readiness, and liveness probes.

### Q2: Why can a misconfigured Liveness Probe cause a "Death-Spiral" restart storm?
**Answer:** If a liveness probe checks a downstream shared database or if the probe timeout is set too aggressively (e.g., 1 second timeout during high CPU load):
1. Under heavy traffic, CPU saturates, causing the health probe to time out.
2. K8s marks the pod dead and restarts it.
3. As the pod restarts, remaining healthy pods absorb the redirected traffic, increasing their CPU utilization.
4. Their liveness probes begin timing out as well.
5. Within minutes, **every single pod in the cluster is continuously killed and restarted**, completely destroying system availability.

### Q3: How do you achieve zero-downtime rolling updates when an application takes 30 seconds to warm up?
**Answer:**
1. Configure a **Startup Probe** with `failureThreshold: 30` and `periodSeconds: 2`, shielding the application for up to 60 seconds of bootstrap time.
2. Configure a **Readiness Probe** mapped to Spring Actuator `/actuator/health/readiness`, which only flips to `UP` after Spring beans and connection pools are warm.
3. Set the Deployment strategy to `maxSurge: 25%` and `maxUnavailable: 0`.
4. Enable `server.shutdown=graceful` in Spring Boot, and set K8s `terminationGracePeriodSeconds: 45` to allow in-flight connections to drain.

---

## 15. Comparison with Alternatives

| Feature | Kubernetes (K8s) | AWS ECS | Docker Swarm | Nomad (HashiCorp) |
|---|---|---|---|---|
| **Ecosystem & Community**| Industry Gold Standard | AWS Specific | Stagnant | Moderate |
| **Complexity** | High (Steep learning curve)| Low / Medium | Low | Low / Medium |
| **Multi-Cloud Portability**| Absolute (Runs anywhere) | Locked into AWS | High | High |
| **Workload Types** | Microservices, Stateful, Batch | Containers only | Containers only | Containers, VMs, Binaries |
| **Best For** | Large Enterprise Distributed Apps| Fast AWS Container Setup | Small Simple Setups | Non-containerized workloads |

---

## 16. When NOT to Use It
1. **Simple Monolithic Applications:** If you have a single web app with low traffic, running a 3-node Kubernetes control plane is an unnecessary operational overhead. Use AWS Elastic Beanstalk or App Runner.
2. **Small Teams without Dedicated DevOps:** Managing etcd backups, CNI upgrades, and RBAC security policies requires dedicated platform engineering. A managed container service (AWS ECS) is vastly more cost-effective.

---

## 17. Hands-on Exercise: Multi-Stage Dockerfile Size Comparison
**Task:** Measure the size and layer count between a naive Dockerfile and an optimized layered JAR build.

```bash
# Naive Build (Copies entire fat JAR - 180 MB image rebuilt every code change)
# Optimized Layered Build:
# Layer 1: OS + JRE (120 MB - Cached indefinitely)
# Layer 2: Spring Dependencies (50 MB - Cached until pom.xml changes)
# Layer 3: Application Code (300 KB - ONLY this layer rebuilds on git commit!)
# CI/CD Image Push Time: Reduced from 45 seconds to 0.8 seconds!
```

---

## 18. Project Application: Telecom CRM Core Platform
How this could connect to a future containerized project (Docker/Kubernetes are learning targets; verify actual implementation):
* **Where this applies:**
  1. **Autoscaling CRM During Tariff Launches:** Configuring an HPA rule scaling CRM pods from 3 to 15 replicas when CPU utilization exceeds 70% during national telecom marketing campaigns.
  2. **Pod Disruption Budgets (PDB):** Enforcing `minAvailable: 2` on CRM deployments to guarantee that Kubernetes node upgrades or cloud maintenance never evict all CRM pods simultaneously.
  3. **Zero-Downtime Releases:** Eliminating scheduled midnight maintenance windows by utilizing Kubernetes rolling updates with Actuator readiness probes.

---

## 19. Senior-Level Interview Answer (The "Gold Standard")

> *"In enterprise production architectures, containerization and orchestration are about deterministic runtime isolation and automated resilience.*  
> *When packaging Spring Boot applications with Docker, I build multi-stage images utilizing Spring's layered JAR tooling to decouple third-party libraries from application code. This slashes CI/CD image upload sizes to sub-megabytes. Inside the container, I enforce the Principle of Least Privilege by running under a non-root user and tuning the JVM for container awareness via `-XX:+UseContainerSupport` and `-XX:MaxRAMPercentage=75.0` to eliminate OOMKilled crashes.*  
> *In Kubernetes, I would aim for uninterrupted service during rolling updates with `maxUnavailable: 0`, correctly designed readiness/startup probes, graceful shutdown, capacity headroom, and backward-compatible changes. These controls reduce risk but do not guarantee zero downtime in every failure.*

---

## 20. Real-World Troubleshooting Scenarios

### Scenario A: Pod Stuck in `CrashLoopBackOff`
* **Investigation:** Run `kubectl describe pod <pod-name>` followed by `kubectl logs <pod-name> --previous`.
* **Finding:**
  - `describe` shows: `Last State: Terminated, Reason: OOMKilled, Exit Code: 137`.
  - Logs show the JVM attempted to allocate a large array during startup that exceeded the K8s container memory limit of 512MB.
* **Fix:**
  - Increase memory limit to 1024Mi in deployment YAML.
  - Set `-XX:MaxRAMPercentage=75.0` so the JVM dynamically sizes heap memory proportional to the container limit.

### Scenario B: 502 Bad Gateway Errors during Rolling Deployment
* **Symptom:** During a midday deployment, 0.5% of live customer requests fail with HTTP 502 Bad Gateway.
* **Root Cause:** When K8s terminated the old pod, it sent `SIGTERM` and immediately removed the pod from iptables. However, the application process terminated before in-flight TCP connections finished processing.
* **Remediation:**
  1. Add a `preStop` lifecycle hook with a 5-second sleep in the pod spec to allow iptables rules to propagate across all nodes before the container begins shutting down:
     ```yaml
     lifecycle:
       preStop:
         exec:
           command: ["/bin/sh", "-c", "sleep 5"]
     ```
  2. Enable graceful shutdown in `application.yml`: `server.shutdown=graceful`.
