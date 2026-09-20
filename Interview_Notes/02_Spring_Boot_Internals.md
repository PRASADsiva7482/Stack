# 02. Spring Boot Internals: Architecture & Senior Interview Guide
> **Evidence warning:** This is study material. Telecom scenarios, metrics, and first-person examples are illustrative unless independently evidenced.
**Target Profile:** Senior Product Software Engineer (Spring Boot 3.x, Spring Framework 6.x, Microservices Architecture)  
**Author:** Siva Prasad Vajja  
**Domain Alignment:** Telecom CRM, Enterprise Platforms, Cloud-Native Microservices  

---

## 1. Definition
**Spring Boot Internals at the Senior Level** encompasses the deep mechanical understanding of how the Spring framework operates beneath its abstractions: the bootstrap lifecycle (`SpringApplication.run`), condition evaluation and auto-configuration mechanisms (`@EnableAutoConfiguration`, `AutoConfiguration.imports`), bean lifecycle and post-processing pipelines (`BeanFactoryPostProcessor`, `BeanPostProcessor`), Dynamic Proxies (JDK vs. CGLIB) governing AOP/Transactions, embedded servlet container initialization, and Spring Security filter chains.

---

## 2. Why It Exists
Before Spring Boot, enterprise Java required extensive manual XML configuration, cumbersome web container deployment (`WAR` files into external WebLogic/Tomcat), fragile dependency version resolution, and boilerplate infrastructure setup. Spring Boot provides:
1. **Opinionated Defaults with "Escape Hatches":** Sane production configurations out-of-the-box that can be easily overridden via conditional annotations.
2. **Embedded Web Servers:** Bundles Tomcat, Jetty, or Undertow directly inside the executable JAR, enabling unified containerized deployments.
3. **Automated Dependency Management:** Curated "Starters" (`spring-boot-starter-*`) guaranteeing tested version compatibility across dozens of transitively imported libraries.
4. **Production Readiness:** Out-of-the-box observability, health probes, and runtime metrics via Spring Boot Actuator.

---

## 3. Problem It Solves
* **Configuration Hell & Boilerplate:** Solved by auto-configuration using conditional annotations (`@ConditionalOnClass`, `@ConditionalOnMissingBean`).
* **Dependency Version Mismatches:** Solved by curated BOM (Bill of Materials) dependency management (`spring-boot-dependencies`).
* **Deployment Complexity:** Solved by self-contained executable JARs with embedded servlet containers.
* **Operational Blindness:** Solved by Actuator endpoints (`/health`, `/metrics`, `/prometheus`) integrated directly with container orchestrators like Kubernetes.

---

## 4. Internal Working

### 4.1 The Bootstrap Lifecycle (`SpringApplication.run()`)
When `SpringApplication.run(Application.class, args)` executes:
1. **Bootstrap Initialization:** Creates `SpringApplication` instance, detects application type (SERVLET, REACTIVE, NONE), loads `ApplicationContextInitializer` and `ApplicationListener` instances from `META-INF/spring.factories`.
2. **Environment Preparation:** Creates and configures `ConfigurableEnvironment`, resolves profiles (`application.yml`), and fires `ApplicationEnvironmentPreparedEvent`.
3. **ApplicationContext Creation:** Instantiates `AnnotationConfigServletWebServerApplicationContext` (for standard Spring MVC) or reactive equivalents.
4. **Context Preparation:** Injects Environment, executes Initializers, registers command-line arguments.
5. **Context Refresh (`refresh()` in `AbstractApplicationContext`):** The core Spring engine executes 12 distinct lifecycle phases:
   - Registers and executes `BeanFactoryPostProcessor` (processes `@Configuration`, `@ComponentScan`).
   - Registers `BeanPostProcessor` instances.
   - Initializes message sources and event multicaster.
   - **`onRefresh()`:** Initializes the embedded WebServer (`TomcatServletWebServerFactory`).
   - Instantiates and initializes all remaining singleton beans (dependency injection, `@PostConstruct`).
6. **Runners Execution:** Executes all beans implementing `ApplicationRunner` and `CommandLineRunner`.

```
SpringApplication.run()
       ↓
Prepare Environment & ConfigData
       ↓
Create ApplicationContext
       ↓
Context Refresh (BeanFactoryPostProcessors -> BeanPostProcessors)
       ↓
Start Embedded Tomcat (onRefresh)
       ↓
Instantiate Singletons (DI + @PostConstruct)
       ↓
Fire ApplicationReadyEvent
```

### 4.2 How Auto-Configuration Works Internals
* Auto-configuration is activated via `@EnableAutoConfiguration` (included in `@SpringBootApplication`).
* In Spring Boot 2.7+, it reads configuration class names from:
  `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
* In Spring Boot 3+, auto-configurations are sorted based on `@AutoConfigureBefore`, `@AutoConfigureAfter`, and `@AutoConfigureOrder`.
* **Condition Evaluation:** The `ConditionEvaluator` verifies whether conditions pass before registering beans:
  - `@ConditionalOnClass`: Checks if a specific class exists on the classpath via reflection without loading it.
  - `@ConditionalOnMissingBean`: Registers a default bean only if the developer has not declared their own `@Bean`.
  - `@ConditionalOnProperty`: Activates configuration based on application properties.

### 4.3 Bean Lifecycle Pipeline
Every Spring bean passes through a rigorous multi-stage pipeline:
```
Instantiate (Constructor)
       ↓
Populate Properties (Dependency Injection)
       ↓
Aware Interfaces (BeanNameAware, BeanFactoryAware, ApplicationContextAware)
       ↓
BeanPostProcessor.postProcessBeforeInitialization()
       ↓
Initialization (@PostConstruct -> InitializingBean.afterPropertiesSet() -> custom init())
       ↓
BeanPostProcessor.postProcessAfterInitialization() (AOP & Transactional Proxies Created Here!)
       ↓
Bean is Ready for Use (Singleton Cache in DefaultSingletonBeanRegistry)
       ↓
Destruction (@PreDestroy -> DisposableBean.destroy() -> custom destroy())
```

### 4.4 Proxies: JDK Dynamic Proxies vs. CGLIB
Spring creates proxies to intercept method calls for cross-cutting concerns (`@Transactional`, `@Async`, `@Secured`, `@Cacheable`):
* **JDK Dynamic Proxy:** Used when the target class implements an interface. Proxies are generated dynamically in memory implementing the same interface via `java.lang.reflect.Proxy`.
* **CGLIB (Code Generation Library):** Used when the target class does not implement an interface (or by default in Spring Boot 2.x+ via `spring.aop.proxy-target-class=true`). CGLIB generates a subclass at runtime, overriding public methods.

---

## 5. Architecture

```
+-------------------------------------------------------------------------+
|                       Spring Boot Architecture                          |
+-------------------------------------------------------------------------+
|  [ REST / HTTP Requests ]                                               |
|           ↓                                                             |
|  [ Embedded Web Server: Tomcat / Jetty / Undertow ]                     |
|           ↓                                                             |
|  [ Spring Security Filter Chain (SecurityContextPersistence, JWT, Auth) |
|           ↓                                                             |
|  [ DispatcherServlet (Front Controller) ]                               |
|       ├── HandlerMapping (Finds Controller Method)                      |
|       ├── HandlerAdapter (Invokes Controller Method)                    |
|       └── HandlerExceptionResolver (@RestControllerAdvice)              |
|           ↓                                                             |
|  [ Application Layer: Spring MVC / REST Controllers ]                   |
|           ↓                                                             |
|  [ Proxy Layer: AOP Interceptors (Transaction, Security, Logging) ]     |
|           ↓                                                             |
|  [ Business Layer: @Service Beans ]                                     |
|           ↓                                                             |
|  [ Persistence Layer: Spring Data JPA Repositories / Hibernate ]        |
|           ↓                                                             |
|  [ Database / External Message Brokers (MySQL / Kafka) ]                |
+-------------------------------------------------------------------------+
```

---

## 6. Important Components
1. **`BeanFactory` vs. `ApplicationContext`:** `BeanFactory` provides basic IoC dependency injection using lazy loading. `ApplicationContext` extends `BeanFactory` with eager singleton pre-instantiation, AOP integration, internationalization, and event publishing.
2. **`BeanPostProcessor` (BPP):** Enables custom modification of bean instances. `postProcessAfterInitialization` wraps target beans with dynamic proxies for transactions and caching.
3. **`BeanFactoryPostProcessor` (BFPP):** Operates on the *bean metadata* (definitions) before any bean instances are created (e.g., `PropertySourcesPlaceholderConfigurer` resolves `${...}` properties).
4. **`DispatcherServlet`:** The Front Controller of Spring MVC. Centralizes request handling, routing to controllers, and delegating to view resolvers or message converters (`MappingJackson2HttpMessageConverter`).
5. **Spring Boot Actuator:** Exposes JMX and HTTP endpoints monitoring JVM heap, threads, database connection pools (HikariCP), and health checks.

---

## 7. Example: Custom Auto-Configuration Starter

```java
// 1. Configuration properties
@ConfigurationProperties(prefix = "telecom.crm.audit")
public record AuditProperties(boolean enabled, String destinationQueue, int retryLimit) {}

// 2. The Service Bean
public class CrmAuditLogger {
    private final AuditProperties properties;
    public CrmAuditLogger(AuditProperties properties) {
        this.properties = properties;
    }
    public void logAction(String subscriberId, String action) {
        System.out.printf("[AUDIT] Sub: %s | Action: %s | Queue: %s%n", 
            subscriberId, action, properties.destinationQueue());
    }
}

// 3. Auto-Configuration Class
@AutoConfiguration
@ConditionalOnClass(CrmAuditLogger.class)
@EnableConfigurationProperties(AuditProperties.class)
@ConditionalOnProperty(prefix = "telecom.crm.audit", name = "enabled", havingValue = "true", matchIfMissing = true)
public class CrmAuditAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public CrmAuditLogger crmAuditLogger(AuditProperties properties) {
        return new CrmAuditLogger(properties);
    }
}
```
*Registered in:*  
`src/main/resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`  
containing: `com.sixdee.crm.autoconfigure.CrmAuditAutoConfiguration`.

---

## 8. Java/Spring Example: Global Error Handling & Secure REST Decorator

```java
@RestControllerAdvice
public class GlobalCrmExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalCrmExceptionHandler.class);

    @ExceptionHandler(SubscriberNotFoundException.class)
    public ProblemDetail handleSubscriberNotFound(SubscriberNotFoundException ex, HttpServletRequest request) {
        log.warn("Subscriber lookup failed: URI={}, Message={}", request.getRequestURI(), ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Subscriber Not Found");
        problem.setProperty("timestamp", Instant.now());
        problem.setProperty("errorCode", "CRM_SUB_404");
        return problem;
    }

    @ExceptionHandler(OptimisticLockingFailureException.class)
    public ProblemDetail handleConcurrentUpdate(OptimisticLockingFailureException ex) {
        log.error("Concurrent update collision detected: {}", ex.getMessage());
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, 
            "The subscriber record was modified by another transaction. Please retry.");
        problem.setTitle("Concurrency Conflict");
        problem.setProperty("errorCode", "CRM_CONCURRENT_WRITE");
        return problem;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGenericError(Exception ex) {
        log.error("Unhandled internal server error", ex);
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, 
            "An unexpected internal error occurred. Contact operations.");
        problem.setTitle("Internal Server Error");
        problem.setProperty("errorCode", "CRM_INTERNAL_500");
        return problem;
    }
}
```

---

## 9. Production Use Case: Multi-Tenant Connection Routing in Telecom CRM
Illustrative multi-tenant CRM example: different operators (tenants) store subscriber data in isolated MySQL database schemas.
* **Architecture:** Use Spring's `AbstractRoutingDataSource`.
* **Execution:** A `HandlerInterceptor` extracts the `X-Tenant-ID` header from incoming REST requests and stores it in a `ThreadLocal` context. When Spring Data JPA requests a connection, `AbstractRoutingDataSource.determineCurrentLookupKey()` retrieves the tenant key and fetches a pooled connection from the matching HikariCP pool.
* **Result:** Zero data contamination across telecom tenants with dynamic pool sizing per operator.

---

## 10. Common Mistakes
1. **`@Transactional` Self-Invocation Bypass:** Calling a `@Transactional` method from another method within the *same* class bypasses the Spring CGLIB/JDK proxy, executing the method with **no active transaction**. Fix: Refactor to a separate service class or inject self.
2. **Field Injection (`@Autowired` on fields):** Prevents class immutability, makes unit testing difficult without reflection, and masks circular dependencies. Always use **Constructor Injection**.
3. **Catching `Exception` inside `@Transactional` without Rethrowing:** If you catch an exception and swallow it without rethrowing, Spring's transaction interceptor does not know an error occurred and commits the dirty state anyway.
4. **Heavy Computations inside `@PostConstruct`:** Blocks the `ApplicationContext` refresh pipeline, delaying container startup and causing health check probes to fail in Kubernetes.
5. **Injecting Prototype Beans into Singleton Beans:** The prototype bean is injected only *once* during singleton initialization and is never recreated. Fix: Use `ObjectProvider<T>` or `@Lookup`.

---

## 11. Performance Considerations
* **HikariCP Connection Pool Tuning:** Set `maximumPoolSize` based on physical disk/CPU constraints:  
  $\text{pool\_size} = (\text{core\_count} \times 2) + \text{effective\_spindle\_count}$. Setting it too high ($>100$) causes severe MySQL connection context switching.
* **Spring Boot 3 + GraalVM AOT (Ahead-Of-Time):** Compiles Spring Boot applications into native OS binaries. Reduces memory footprint from 400MB to 40MB and startup time from 4s to 0.05s, ideal for Kubernetes scale-to-zero.
* **Exclude Unnecessary Auto-Configurations:** Accelerate startup time by excluding unused starters:  
  `@SpringBootApplication(exclude = {SecurityAutoConfiguration.class, RabbitAutoConfiguration.class})`.
* **Disable JMX in Production:** `spring.jmx.enabled=false` reduces CPU overhead and memory usage.

---

## 12. Security Considerations
* **Spring Security Filter Chain Execution:** Security is executed entirely in a servlet filter chain (`DelegatingFilterProxy` $\to$ `FilterChainProxy`) **before** reaching `DispatcherServlet`.
* **CORS & CSRF in Microservices:** For stateless REST APIs using JWT tokens in `Authorization: Bearer` headers, CSRF protection should be disabled (`csrf.disable()`), but CORS must be strictly locked down to trusted domain origins.
* **Actuator Endpoint Exposure:** Never expose sensitive Actuator endpoints to the public internet:  
  `management.endpoints.web.exposure.include=health,info,metrics,prometheus`. Endpoints like `env`, `heapdump`, and `restart` must be protected with admin RBAC.

---

## 13. Core Interview Questions & Answers

### Q1: What is the exact difference between `@Component`, `@Service`, and `@Repository`?
**Answer:** At the container level, they are all meta-annotated with `@Component` and treated as Spring-managed beans. However:
* `@Repository` automatically enables exception translation, translating low-level JDBC/Hibernate SQLExceptions into Spring's unified `DataAccessException` hierarchy.
* `@Service` serves as semantic documentation for business logic.
* `@Controller` / `@RestController` registers request mapping handlers and response serialization.

### Q2: Why does Spring recommend constructor injection over field injection?
**Answer:**
1. Allows declaring dependencies as `final`, ensuring immutability.
2. Prevents `NullPointerException` during standalone unit testing (dependencies must be passed via constructor without reflection).
3. Detects circular dependencies at compile/startup time rather than runtime.
4. Prevents violating the Single Responsibility Principle (constructors with 8+ parameters immediately signal bad design).

### Q3: How does `@Transactional` work internally?
**Answer:** Spring wraps the target bean in a dynamic proxy. When a `@Transactional` method is called:
1. `TransactionInterceptor` intercepts the invocation.
2. It looks up the `PlatformTransactionManager`.
3. It opens a database connection, turns off auto-commit (`connection.setAutoCommit(false)`), binds the connection to a `ThreadLocal` storage (`TransactionSynchronizationManager`), and begins the transaction.
4. If the target method completes normally, the interceptor calls `commit()`.
5. If an unhandled `RuntimeException` or `Error` is thrown, it calls `rollback()`.

### Q4: What is the purpose of `@SpringBootApplication`?
**Answer:** It is a convenience combination of three essential annotations:
* `@Configuration`: Identifies the class as a source of bean definitions.
* `@EnableAutoConfiguration`: Triggers auto-configuration discovery from imports files.
* `@ComponentScan`: Scans the current package and sub-packages for `@Component`, `@Service`, etc.

### Q5: How do you handle circular dependencies in Spring Boot 2.6+?
**Answer:** In Spring Boot 2.6+, circular dependencies are disabled by default and fail startup with `BeanCurrentlyInCreationException`. Solutions:
1. **Best Practice:** Redesign the architecture (extract shared logic into a separate third service or use event-driven communication via `ApplicationEventPublisher`).
2. **Workaround:** Annotate one injection point with `@Lazy` (Spring injects a proxy instead of the real instance, resolving the deadlock).

---

## 14. Deep Interview Questions (Senior / Staff Level)

### Q1: Walk through the exact step-by-step resolution of a REST request through Spring MVC.
**Answer:**
1. Incoming HTTP request hits Tomcat worker thread and traverses `SecurityFilterChain`.
2. Request enters `DispatcherServlet.doDispatch(HttpServletRequest, HttpServletResponse)`.
3. `DispatcherServlet` queries `HandlerMapping` (e.g., `RequestMappingHandlerMapping`) to find the matching handler method and returns a `HandlerExecutionChain` (containing interceptors + handler).
4. Executes `preHandle()` on all registered `HandlerInterceptor` instances.
5. `DispatcherServlet` delegates to `HandlerAdapter` (e.g., `RequestMappingHandlerAdapter`).
6. Method arguments are resolved via `HandlerMethodArgumentResolver` (e.g., `@RequestBody` uses Jackson `HttpMessageConverter`).
7. Target controller method executes and returns response object.
8. `HandlerAdapter` handles return value via `HandlerMethodReturnValueHandler`.
9. Executes `postHandle()` on all interceptors.
10. `afterCompletion()` executes on interceptors after response is committed. If an exception occurred, `HandlerExceptionResolver` intercepts before `afterCompletion`.

### Q2: How does Spring Boot ensure that developer beans take precedence over auto-configured beans?
**Answer:** Via two mechanisms:
1. **Conditional Annotations:** Auto-configuration classes mark their bean creation methods with `@ConditionalOnMissingBean`. If a bean of that type is already registered by the developer's `@Configuration` or `@ComponentScan`, the condition evaluates to `false` and the auto-configured bean is discarded.
2. **Configuration Phase Sequencing:** User configurations are processed first during the initial component scan phase. Auto-configurations are deferred and evaluated during a later pass after all user bean definitions exist in the `BeanDefinitionRegistry`.

### Q3: What is the difference between `@Configuration(proxyBeanMethods = true)` vs `false`?
**Answer:**
* `proxyBeanMethods = true` (Default): Spring wraps the `@Configuration` class with a CGLIB proxy. If one `@Bean` method calls another `@Bean` method directly, the proxy intercepts the call and returns the existing cached singleton instance from the container, preserving singleton scope.
* `proxyBeanMethods = false` ("Lite" Mode): No CGLIB proxy is generated. Calling `@Bean` methods directly acts as a standard Java method call, instantiating a brand new object every time. Used to optimize startup time and memory when inter-bean dependencies do not exist.

---

## 15. Comparison with Alternatives

| Feature | Spring Boot 3.x | Quarkus | Micronaut |
|---|---|---|---|
| **Dependency Injection** | Runtime Reflection & CGLIB | Build-time compilation (ArC) | Compile-time AOT |
| **Startup Time (JVM)** | ~2 – 4 seconds | ~0.8 – 1.5 seconds | ~1.0 – 1.8 seconds |
| **Memory Footprint** | ~250 – 400 MB | ~100 – 150 MB | ~100 – 180 MB |
| **Ecosystem & Maturity** | Unrivaled (Massive enterprise adoption) | Fast growing (Red Hat backed) | Strong for microservices |
| **Native Compilation** | GraalVM AOT supported | First-class native citizen | First-class native citizen |
| **Hiring Pool** | Vast (Most standard skillset) | Niche | Niche |

---

## 16. When NOT to Use It
1. **Ultra-Low Latency Trading Applications:** Microsecond algorithmic trading engines cannot tolerate garbage collection pauses or reflection overhead; C++ or zero-GC Java (LMAX Disruptor) is required.
2. **Simple CLI Utilities:** Bootstrapping an entire `ApplicationContext` for a command that runs in 200ms is inefficient; use Golang or Rust.
3. **Severe Memory-Constrained Devices:** Microcontrollers or IoT edge gateways with $<64$MB RAM cannot run a full Spring Boot runtime.

---

## 17. Hands-on Exercise: Implement a Custom BeanPostProcessor for SLA Profiling
**Task:** Build a `BeanPostProcessor` that intercepts all service methods annotated with a custom `@SlaTracked`, measuring execution time and logging warnings if execution exceeds 500ms.

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface SlaTracked {
    long thresholdMillis() default 500;
}

@Component
public class SlaPerformanceBeanPostProcessor implements BeanPostProcessor {

    private static final Logger log = LoggerFactory.getLogger(SlaPerformanceBeanPostProcessor.class);

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        Class<?> targetClass = bean.getClass();
        
        // Check if any method has @SlaTracked
        boolean hasTrackedMethods = Arrays.stream(targetClass.getMethods())
            .anyMatch(m -> m.isAnnotationPresent(SlaTracked.class));

        if (!hasTrackedMethods) {
            return bean;
        }

        // Wrap with CGLIB Proxy
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(targetClass);
        enhancer.setCallback((MethodInterceptor) (obj, method, args, proxy) -> {
            SlaTracked annotation = method.getAnnotation(SlaTracked.class);
            if (annotation == null) {
                return proxy.invoke(bean, args);
            }

            long start = System.currentTimeMillis();
            try {
                return proxy.invoke(bean, args);
            } finally {
                long duration = System.currentTimeMillis() - start;
                if (duration > annotation.thresholdMillis()) {
                    log.warn("SLA BREACH: Bean='{}', Method='{}', Duration={}ms, Threshold={}ms",
                        beanName, method.getName(), duration, annotation.thresholdMillis());
                }
            }
        });

        return enhancer.create();
    }
}
```

---

## 18. Project Application: Telecom CRM Core Platform
How this could connect to your current resume (verify actual implementation):
* **Where this applies:**
  1. **Custom Telecom Tenant Starter:** Creating a shared internal starter that auto-configures database routing, standard audit headers (`X-Correlation-ID`, `X-Operator-ID`), and standardized error response formatting across all microservices.
  2. **Actuator Health Probes in Kubernetes:** Configuring custom `HealthIndicator` beans checking connectivity to billing servers, SMS gateways, and Camunda engines to ensure K8s doesn't route traffic to crippled pods.
  3. **Transaction Boundary Management:** Isolating CRM subscriber updates from notification calls using `@Transactional(propagation = Propagation.REQUIRES_NEW)` to ensure that SMS notification failures do not rollback subscriber profile state changes.

---

## 19. Senior-Level Interview Answer (The "Gold Standard")

> *"Spring Boot is fundamentally an inversion-of-control container paired with an automated condition-evaluation engine. When `SpringApplication.run()` is invoked, it sets up the environment and executes the `refresh()` phase of the `ApplicationContext`.*  
> *Under the hood, auto-configuration is not magic: it leverages `AutoConfiguration.imports` to evaluate conditional annotations like `@ConditionalOnClass` and `@ConditionalOnMissingBean`. This ensures that developer-declared beans always take precedence over framework defaults.*  
> *In production architectures like Telecom CRM, understanding the proxying mechanism is critical: Spring wraps beans using CGLIB or JDK dynamic proxies to provide cross-cutting concerns like `@Transactional` and `@Async`. Knowing that self-invocation bypasses this proxy layer, and that `BeanPostProcessor` instances intercept bean creation to build these proxies, allows us to prevent severe transactional bugs, connection leaks, and subtle concurrency flaws."*

---

## 20. Real-World Troubleshooting Scenarios

### Scenario A: Silent Transaction Rollbacks (`UnexpectedRollbackException`)
* **Symptom:** API returns 500 error: `Transaction rolled back because it has been marked as rollback-only`.
* **Root Cause:** A nested method marked with default `@Transactional(propagation = Propagation.REQUIRED)` caught an exception and handled it, but Spring's inner transaction interceptor already marked the shared physical transaction as `rollback-only`. When the outer method attempts to commit, Spring throws `UnexpectedRollbackException` to protect data consistency.
* **Fix:** If the nested failure should NOT abort the parent transaction, declare the nested method with `@Transactional(propagation = Propagation.REQUIRES_NEW)`.

### Scenario B: High Latency & Thread Exhaustion during Peak Traffic
* **Symptom:** Tomcat request threads (`http-nio-8080-exec-*`) climb to max (200), and incoming requests hang with timeout errors.
* **Diagnosis:** Capture a thread dump using `jcmd <PID> Thread.print`. Inspect what `http-nio` threads are doing.
* **Finding:** All 200 threads are in `WAITING` state on a `HikariPool.getConnection()` call. The database pool size is 10, while 200 threads are competing for connections due to slow, unindexed CRM queries holding connections open.
* **Fix:** Tune database query indexes, reduce connection hold time, decouple external REST calls outside of `@Transactional` blocks, and size HikariCP appropriately.
