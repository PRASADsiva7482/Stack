# LLM and SLM Application Integration

This module explains how to integrate a Large Language Model (LLM) or Small Language Model (SLM) into a real application. It is an interview and portfolio learning guide, not evidence that the supplied resume contains production ownership of these systems.

## 1. What an application integration actually is

An application integration is more than sending a prompt to a model. A production-shaped integration has:

1. A business capability and a clear success condition.
2. A model gateway that hides provider or runtime details.
3. Input validation, authentication, tenant and data-access checks.
4. Prompt or instruction construction with bounded context.
5. Structured output validation.
6. Timeout, retry, circuit-breaker, fallback, and cancellation behavior.
7. Retrieval or tools when the model needs current application data.
8. Human approval before consequential side effects.
9. Evaluation, observability, cost control, and versioned model/prompt artifacts.

The request path should be explainable:

```text
Client
  -> Application API
  -> identity, tenant, quota, input validation
  -> use-case service
  -> model router
       -> rules or deterministic code
       -> SLM for fast/private bounded task
       -> LLM for difficult reasoning or generation
  -> optional retrieval / authorized tools
  -> output schema and safety validation
  -> response, audit event, metrics
```

The model is one fallible dependency inside the application. It must not become the authorization layer, source of truth, or unrestricted database client.

## 2. LLM versus SLM

The boundary is practical rather than a universal parameter-count number.

| Dimension | LLM | SLM |
|---|---|---|
| Capability | Broad reasoning, language coverage, complex generation | Narrower capability, often sufficient for bounded tasks |
| Runtime | Usually remote or GPU-backed service; can also run privately | Often suitable for local, edge, CPU, or smaller GPU deployment |
| Latency | May be higher and less predictable | Often lower for short requests, but benchmark the actual model and hardware |
| Cost | More compute/token cost or provider spend | Lower serving cost is possible, not guaranteed |
| Privacy | Requires careful data boundary with provider or private hosting | Can keep sensitive data closer to the application |
| Context/tool use | Often stronger, but still needs explicit constraints | Can work well for classification, extraction, routing, and simple tool selection |
| Failure mode | More capable incorrect answer and prompt-injection exposure | More omissions, weaker reasoning, and domain drift |
| Best use | Complex synthesis, difficult reasoning, high-value assistance | Classification, routing, extraction, moderation, autocomplete, local fallback |

Do not select a model by size alone. Compare quality, p95 latency, memory, throughput, context limit, structured-output reliability, multilingual behavior, tool-call behavior, privacy, and total cost on a representative evaluation set.

## 3. Choosing the right model for a task

Start with the task, not the model:

| Task | First candidate | Why |
|---|---|---|
| Input validation and deterministic rules | Rules/code | No model uncertainty is needed. |
| Intent classification | SLM or classifier | Small output space, low latency, easy evaluation. |
| Entity or field extraction | SLM/LLM with strict schema | Validate every field and confidence/failure path. |
| Query routing | SLM plus rules | Route easy cases locally and reserve larger model calls. |
| Summarization | SLM for short stable text; LLM for complex synthesis | Compare factuality and omission rate. |
| Enterprise knowledge answer | RAG plus suitable model | Retrieval and authorization matter as much as generation. |
| Financial/order/account side effect | Deterministic service plus approval | Model may propose; application code validates and executes. |
| Open-ended reasoning | LLM or specialist model | Use bounded context and a measurable stopping condition. |
| Offline/private operation | Local SLM or approved private model | Confirm model license, hardware, security, and quality. |

A useful routing policy is:

```text
if request is invalid -> reject
else if deterministic rule handles it -> use rule
else if task is classified as simple/private/low-latency -> SLM
else -> LLM
if confidence, schema, citation, or safety checks fail -> abstain or escalate
```

Confidence must not be invented from a model's friendly tone. Define a calibrated score or an observable validation rule, and measure whether it predicts correctness.

## 4. Integration patterns

### Pattern A: provider API behind a model gateway

The application calls an internal interface such as `ModelGateway`, while an adapter handles the selected provider or private runtime. This protects the domain code from provider-specific request formats.

```java
public interface ModelGateway {
    <T> ModelResult<T> complete(ModelRequest request, Class<T> outputType);
}

public record ModelRequest(
        String useCase,
        String systemInstruction,
        String userInput,
        Map<String, Object> context,
        Duration timeout,
        String tenantId) {}

public record ModelResult<T>(
        T value,
        String modelId,
        String promptVersion,
        int inputTokens,
        int outputTokens,
        Duration latency,
        boolean fallbackUsed) {}
```

The gateway owns timeout, retry policy, model routing, schema conversion, redaction, metrics, and error mapping. The domain service owns business validation and authorization.

### Pattern B: Spring Boot and Spring AI

For a Java application, Spring AI can provide abstractions such as a chat client, advisors, tool callbacks, and vector-store integration. Keep the integration behind an application service so a change of model provider does not leak through controllers and domain code.

```java
@Service
public class CaseSummaryService {
    private final ChatClient chatClient;

    public CaseSummaryService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public CaseSummary summarize(CaseData data) {
        return chatClient.prompt()
                .system("Summarize the case. Never invent a fact. Return only the requested fields.")
                .user(u -> u.text("Case data:\n{data}")
                        .param("data", data.sanitizedText()))
                .call()
                .entity(CaseSummary.class);
    }
}
```

The exact Spring AI API and provider configuration must be checked against the version used by the project. The important interview concepts are the boundary, structured output, failure handling, and tests—not memorizing a particular method chain.

### Pattern C: local SLM or private inference service

The application can call a local or private inference runtime over HTTP, but the same gateway contract should be used:

```text
Java/Spring service
  -> ModelGateway
  -> local/private inference endpoint
  -> tokenizer + model weights + decoder
  -> structured response
```

Deployment choices include a process on the same host, a sidecar, a dedicated inference service, or a managed private endpoint. Compare isolation, resource contention, scaling, model loading time, batching, and failure behavior. A local model is not automatically secure or reliable; protect its endpoint and validate its outputs.

### Pattern D: Python model service

Python is common when the model or evaluation ecosystem is Python-first. Keep the boundary explicit rather than mixing unbounded model logic into every Java service.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    request_id: str

class SummaryResponse(BaseModel):
    summary: str
    model_id: str
    fallback_used: bool = False

@app.post("/internal/summarize", response_model=SummaryResponse)
def summarize(request: SummaryRequest) -> SummaryResponse:
    # Load an approved model at process startup.
    # Apply access control, redaction, timeout, and output validation here.
    result = run_bounded_inference(request.text)
    return SummaryResponse(summary=result.text,
                           model_id=result.model_id,
                           fallback_used=result.fallback_used)
```

The Java service should authenticate this internal call, propagate a correlation ID and deadline, validate the response, and handle the Python service being unavailable. Do not expose an internal inference endpoint directly to browsers.

## 5. Model gateway responsibilities

A useful gateway has these layers:

| Layer | Responsibility |
|---|---|
| Request policy | Authentication, tenant scope, quota, input length, content type |
| Data policy | PII detection/redaction, allowed data sources, retention policy |
| Routing | Rules, SLM, LLM, fallback, model capability selection |
| Prompt/context | Versioned instructions, retrieved context, delimiters, injection boundaries |
| Invocation | Deadline, cancellation, retry only for safe transient errors, circuit breaker |
| Output | JSON/schema validation, enum checks, citations, business invariants |
| Safety | Refusal, content policy, tool permission, human approval |
| Operations | Token/cost, latency, errors, model version, prompt version, trace IDs |

An adapter should translate provider errors into application errors such as `MODEL_TIMEOUT`, `MODEL_RATE_LIMITED`, `MODEL_UNAVAILABLE`, `OUTPUT_INVALID`, and `POLICY_BLOCKED`. Do not expose raw provider messages or secrets to users.

## 6. Structured output and application validation

For business integration, free-form text is usually too fragile. Define a schema:

```json
{
  "intent": "BILLING_DISPUTE",
  "entities": {
    "accountId": "masked-or-authorized-value"
  },
  "answer": "...",
  "citations": ["knowledge-doc-17"],
  "needsHumanReview": true
}
```

Validation must include:

- required fields and allowed enum values;
- maximum lengths and nesting depth;
- valid identifiers and tenant ownership;
- citation existence and authorization;
- no direct execution of model-produced SQL, shell commands, URLs, or code;
- business rules such as “account must belong to the authenticated tenant”;
- explicit abstention when required information is missing.

Schema-valid output can still be factually wrong. Add retrieval, deterministic checks, tests, and human review where the consequence requires it.

## 7. RAG integration flow

For an application knowledge assistant:

1. Ingest approved documents.
2. Normalize, classify, chunk, and attach source/tenant/version metadata.
3. Create embeddings with a versioned embedding model.
4. Store vectors plus authorization metadata.
5. Rewrite or normalize the user query when useful.
6. Retrieve with tenant and permission filters.
7. Optionally rerank the candidate passages.
8. Build a bounded context with source identifiers.
9. Ask the LLM or SLM to answer only from that context.
10. Validate citations and response policy.
11. Log evaluation-safe metadata, not sensitive prompt contents by default.

RAG is not a guarantee against hallucination. Retrieval can be wrong, stale, incomplete, unauthorized, or too noisy. Measure retrieval and answer quality separately.

## 8. Tool and function integration

Use tools when the model needs an authoritative operation or current data. A tool contract should state:

```text
Tool name: getAccountStatus
Input: accountId
Authorization: authenticated user may read only permitted tenant accounts
Side effect: none
Timeout: 2 seconds
Failure: return typed unavailable result; do not fabricate status
Audit: request ID, actor, tenant, tool, outcome; redact sensitive values
```

Tool classes:

- read-only lookup: usually lower risk, still authorization-sensitive;
- calculated result: validate input and calculation independently;
- write operation: require idempotency, authorization, confirmation or approval;
- irreversible action: require explicit human approval and strong auditability.

The model may select a tool, but the application decides whether it is allowed. Never let prompt text override server-side authorization.

## 9. LLM/SLM plus business workflow

For CRM, telecom, billing, onboarding, or support workflows, use a hybrid design:

```text
Event or API request
  -> deterministic validation
  -> workflow state machine
  -> model proposal/classification/extraction
  -> schema and policy validation
  -> human approval if required
  -> deterministic domain service
  -> event/audit/reconciliation
```

Good bounded uses include classifying a case, extracting fields from a document, drafting a response, suggesting a next step, or summarizing an approved record. The model should not silently change billing, activate a service, approve credit, or close a compliance workflow.

## 10. Reliability design

### Timeouts and deadlines

Set a total request deadline and propagate the remaining time to retrieval, tools, and model calls. A retry that outlives the user request is wasted work.

### Retry policy

Retry only safe transient failures, with bounded exponential backoff and jitter. Do not blindly retry invalid prompts, schema failures, policy blocks, or non-idempotent tool operations.

### Fallbacks

Possible fallbacks are a deterministic response, an SLM, a cached answer when freshness permits, a human queue, or an honest “temporarily unavailable” result. A fallback must not pretend that a model answer is authoritative when it is not.

### Streaming and cancellation

For streaming output, handle client disconnects, partial output, moderation, backpressure, and cancellation. Do not commit a side effect merely because a partial token stream was produced.

### Idempotency

Use a request ID or idempotency key for side-effecting operations. Store the operation state and result so a network retry does not duplicate the action.

## 11. Security checklist

- Authenticate every application and internal model call.
- Authorize by user, tenant, resource, and action.
- Treat retrieved documents and user text as untrusted input.
- Defend against direct and indirect prompt injection.
- Keep system instructions separate from untrusted content with clear delimiters.
- Do not place secrets in prompts, logs, embeddings, or model training data.
- Redact or tokenize PII according to the data policy.
- Validate tool names, arguments, URLs, file paths, and query parameters.
- Use allowlists and approvals for side effects.
- Apply quotas, rate limits, token budgets, and maximum tool steps.
- Record model, prompt, embedding, and tool versions for audit.
- Test denial cases, tenant escape attempts, malicious documents, and output-parser failures.

## 12. Evaluation and release gate

Create a small representative dataset before changing the model or prompt. Include normal, ambiguous, adversarial, long, empty, multilingual, permission-sensitive, and failure cases.

Track at least:

| Metric | Meaning |
|---|---|
| Task correctness | Does the answer or extraction satisfy the business label/rubric? |
| Groundedness/faithfulness | Are claims supported by permitted context? |
| Retrieval quality | Did the correct authorized evidence reach the context? |
| Schema validity | Did the output parse and pass constraints? |
| Abstention quality | Did it refuse or escalate when evidence was insufficient? |
| Tool correctness | Was the right authorized tool selected with valid arguments? |
| p50/p95 latency | User experience and capacity planning. |
| Error/fallback rate | Dependency and quality health. |
| Tokens/cost | Per request, tenant, and use case. |

Release only when the candidate meets agreed thresholds without unacceptable regression in safety, latency, cost, or tenant isolation. A high average score can hide dangerous failures in rare cases, so keep critical safety cases as blocking tests.

## 13. Model and artifact governance

Version these independently:

- model identifier and exact weight artifact;
- tokenizer and chat template;
- quantization/runtime configuration;
- prompt/instruction template;
- retrieval and embedding model;
- tool schemas and policy rules;
- evaluation dataset and evaluator version.

For a privately owned model trained from random initialization, record dataset lineage, preprocessing, code revision, seed/configuration, training checkpoints, evaluation evidence, and approved release path. A tokenizer or random-weight decoder is not a trained model release. For an interview portfolio using an external or open model, state the model source, license, and that it is an integration project rather than self-trained ownership.

## 14. Portfolio build: Support Copilot

Build this as a bounded demonstration, not a claim about current employment experience.

### Scope

- Spring Boot API receives a support question and authenticated tenant.
- Rules reject invalid or unauthorized requests.
- SLM classifies intent and routes simple requests.
- RAG retrieves approved knowledge articles with tenant metadata.
- LLM drafts an answer with citations, or abstains.
- Read-only account-status tool is available after authorization.
- Write actions are represented as proposals requiring approval.
- Evaluation dataset, latency/cost metrics, and failure tests are included.

### Suggested components

```text
React or REST client
  -> Spring Boot Copilot API
  -> Auth / tenant policy
  -> Model Gateway
      -> SLM classifier/router
      -> LLM answer generator
  -> Retrieval adapter -> PostgreSQL/pgvector or approved vector store
  -> Tool adapter -> fake account service
  -> audit + metrics + evaluation runner
```

### Acceptance tests

- Unauthenticated request is rejected.
- User cannot retrieve another tenant's document or account.
- Prompt injection in a document cannot authorize a tool.
- Unsupported question produces an honest abstention.
- Invalid model JSON is rejected or safely repaired within a bounded policy.
- Model timeout invokes a documented fallback.
- Repeated approved operation is idempotent.
- Citation points to an authorized source.
- PII is absent from normal logs.
- Evaluation results are reproducible from versioned artifacts.

### Resume-safe wording after completion

`Built a bounded LLM/SLM application-integration project with a Spring Boot model gateway, structured output validation, tenant-filtered retrieval, read-only tools, fallback handling, and evaluation tests.`

Use this only after the project exists and you can demonstrate it. Do not describe it as production experience.

## 15. Interview questions and answer points

1. **When would you choose an SLM over an LLM?** Explain task complexity, latency/privacy/cost, benchmark evidence, and fallback.
2. **How do you integrate a model without coupling the domain to a provider?** Use a gateway, adapter, typed request/result, and contract tests.
3. **How do you guarantee the model does not execute an unauthorized action?** Server-side authorization, tool allowlist, schema validation, approval, and audit.
4. **What happens when the model returns invalid JSON?** Validate, bounded repair if safe, retry only with care, then fallback or escalate.
5. **How do you evaluate an SLM router?** Confusion matrix, routing cost/latency, false escalation, false acceptance, and critical-case tests.
6. **How do you make RAG multi-tenant?** Enforce tenant/resource filters before retrieval and again before citation/tool use.
7. **What is the difference between a model timeout and a model-quality failure?** Operational dependency failure versus incorrect/unsupported content; they need different metrics and responses.
8. **How would you deploy a local model?** Model artifact/runtime, resource isolation, health/readiness, loading, batching, scaling, security, and rollback.
9. **How do you explain your real experience?** Separate AI-assisted development and the academic CNN/LSTM project from current learning/portfolio integration work.
10. **How would you add AI to a Camunda workflow?** Keep workflow state and business rules deterministic; let AI propose bounded data, validate it, and require approval before effects.

## 16. Completion checklist

- [ ] Can explain LLM versus SLM with a task-based example.
- [ ] Can draw the model-gateway request path.
- [ ] Can implement or describe a typed Java integration.
- [ ] Can explain a Python inference-service boundary.
- [ ] Can design RAG, tool, fallback, and workflow integration.
- [ ] Can list security and tenant-isolation controls.
- [ ] Can define evaluation data and release gates.
- [ ] Can explain model/prompt/tokenizer/version lineage.
- [ ] Can demonstrate the Support Copilot lab or label it as planned.
- [ ] Can answer interview questions without claiming unsupported production experience.

