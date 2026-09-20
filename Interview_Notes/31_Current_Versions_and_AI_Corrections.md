# 31. Current-Version Guardrails and AI Corrections

**Audit date:** 2026-09-14  
**Status:** Reference note; verify versions again before starting a project.

## 1. Version policy

Framework examples are not timeless. Record the exact versions in `pom.xml`, lock the BOM, and read the matching documentation.

- Oracle's Java documentation currently lists JDK 26, 25, 21, 17, 11, and 8 as current release documentation. Your original resume proves Java 17; study Java 21/25/26 as interview context, not as experience.
- The current Spring Boot documentation lists Spring Boot 4.1.1 as stable and requires at least Java 17. Boot 3.x examples may still be relevant to existing systems, but do not mix Boot 3 and Boot 4 dependencies casually.
- The current Spring AI reference is on 2.0.x and its getting-started guide describes Boot 4.0.x/4.1.x support. Pin a compatible pair; annotate older 1.x examples as legacy.
- MCP is versioned and has breaking changes. The 2026-07-28 release changed the remote protocol core toward stateless HTTP and deprecated legacy HTTP+SSE for new implementations. Learn resources, prompts, tools, JSON-RPC, consent, authorization, and version negotiation; never present an old SSE sample as current by default.
- OWASP's current GenAI guidance has moved beyond the archived LLM Top 10 entry point. Check the current GenAI Security Project and label older 2023/2025 lists as historical when comparing interview material.

Official references:

- [Oracle Java SE releases](https://docs.oracle.com/en/java/javase/)
- [Spring Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html)
- [Spring AI getting started](https://docs.spring.io/spring-ai/reference/getting-started.html)
- [Spring AI tool calling](https://docs.spring.io/spring-ai/reference/api/tools.html)
- [MCP specification](https://modelcontextprotocol.io/specification/)
- [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [OWASP GenAI Security Project](https://genai.owasp.org/)

## 2. Corrections to remember

### RAG is not a guarantee

RAG retrieves context and gives the model evidence. It does not guarantee truth, complete retrieval, correct citations, or absence of hallucination. A robust design combines access-controlled retrieval, source IDs, answer abstention, schema validation, citation verification, human review for high-risk actions, and measured evaluation.

### Evaluation scores are not proof

Faithfulness, answer relevance, context precision, and retrieval recall depend on the dataset, evaluator, model, prompt, sampling, and metric definition. A score of 1.0 on a benchmark does not prove zero hallucinations in the open world. Some metrics need reference answers; others can be reference-free but are still imperfect. Report dataset size, version, threshold, failure examples, and human review.

### Tool calling is application-controlled

The model can request a tool, but the application validates arguments, checks authorization, applies timeouts and idempotency, executes the tool, redacts results, and decides whether to continue. Never let a model directly own database credentials or unrestricted side effects.

### An agent is not automatically better

Use a deterministic workflow for known states, approvals, retries, SLAs, and financial/provisioning actions. Use agentic behavior where the problem genuinely needs dynamic selection or investigation. Bound iterations, tools, time, tokens, permissions, and cost. Add human approval for high-impact actions.

### Metrics need evidence

Claims such as “reduced cost by 70%,” “zero double-charging,” “94% accuracy,” or “sub-second latency” require a baseline, sample, measurement method, time window, and scope. Without those, rewrite as a goal, a lab result, or an illustrative scenario.

## 3. Minimum enterprise AI architecture

```text
request -> identity/tenant authorization -> input validation/PII policy
         -> retrieval or tool selection -> model call with deadline
         -> schema/output validation -> citation/action policy
         -> human approval for high risk -> audited side effect
         -> trace, token/cost metric, feedback, evaluation dataset
```

Security controls are independent layers. A prompt saying “do not reveal secrets” is not authorization. Enforce tenant filters in the data layer and tool permissions in application code.

## 4. AI interview checklist

Be able to explain:

1. Tokenization, context limits, temperature, and latency.
2. Embeddings, cosine/distance choice, chunking, and metadata filters.
3. Why naive RAG fails and how hybrid retrieval/reranking helps.
4. Retrieval precision/recall versus answer groundedness.
5. Structured output and validation.
6. Tool calling versus an agent loop.
7. Deterministic workflow versus autonomous planning.
8. Prompt injection and indirect injection.
9. Tenant isolation and sensitive-data handling.
10. Model fallback, rate limits, caching, cost, and observability.
11. Model/prompt/version regression testing.
12. How you would say “I have studied this” honestly when you have not operated it in production.

