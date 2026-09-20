# Resume Evidence and Application Workbook

This workbook keeps applications persuasive and truthful. It is especially important when moving from a telecom/CRM delivery background toward product engineering or applied AI roles.

## 1. Evidence rule

Every resume claim must fit one of these levels:

| Label | Meaning | How to say it |
|---|---|---|
| `RESUME-VERIFIED` | Supported by the supplied resume or a work artifact you can discuss. | “I built/maintained …” |
| `EXPOSURE` | You used or saw it in a limited way, but do not own a deep production story. | “I have exposure to …” |
| `LEARNING TARGET` | Studied, lab-built, or planned; not professional production experience. | “I built a lab for …” |
| `ILLUSTRATIVE` | A design exercise used to demonstrate understanding. | “I would design it as …” |
| `NEEDS EVIDENCE` | A metric, tool, scale, or ownership claim still needs proof. | Do not put it on the resume yet. |

Do not convert a learning note into a production claim just because the technology appears in the notes.

## 2. Current evidence inventory

The supplied resume supports these core claims:

- Senior Software Engineer with 5+ years of enterprise/application development experience.
- Java 17, Spring Boot, Spring MVC, Spring Data JPA, Hibernate, REST APIs, microservices, SQL/MySQL.
- React integration, Camunda BPM, Spring Batch, Git/GitLab, Maven, JUnit, Agile/Scrum.
- Production support, RCA, secure coding, performance tuning, OOP/design patterns, collections, streams, exceptions, and multithreading.
- AI-assisted development exposure through GitHub Copilot, Cascade, and LLM coding assistants.
- Academic CNN + LSTM image-captioning project involving computer vision and NLP.

The resume does not by itself prove deep production ownership of Kafka, Redis, AWS, Kubernetes, OpenTelemetry, Prometheus, Grafana, Spring AI, RAG, vector databases, autonomous agents, or MCP. Keep those as learning targets or add them only after you have a demonstrable project and can explain the implementation.

## 3. Claim ledger

Copy this table into a personal document and fill it with evidence. Never include confidential code, customer names, credentials, private URLs, or proprietary data.

| Claim | Label | Evidence location | What I personally did | Metric or observable result | Interview follow-up ready? |
|---|---|---|---|---|---|
| Java/Spring backend work | RESUME-VERIFIED | Resume / sanitized module notes |  |  |  |
| REST API integration | RESUME-VERIFIED |  |  |  |  |
| JPA/Hibernate persistence | RESUME-VERIFIED |  |  |  |  |
| Camunda/workflow | RESUME-VERIFIED |  |  |  |  |
| Spring Batch | RESUME-VERIFIED |  |  |  |  |
| Production support/RCA | RESUME-VERIFIED |  |  |  |  |
| Performance tuning | RESUME-VERIFIED |  |  |  |  |
| Git/Maven/JUnit | RESUME-VERIFIED |  |  |  |  |
| Kafka/Redis | LEARNING TARGET unless separately evidenced |  |  |  |  |
| AWS/Kubernetes | LEARNING TARGET unless separately evidenced |  |  |  |  |
| RAG/agents/MCP | LEARNING TARGET unless separately evidenced |  |  |  |  |

For every row, prepare a 60-second explanation, a five-minute deep dive, one failure mode, and one test or measurement.

## 4. The project story template

Write one page per important project using this format:

```text
Project / domain:
Users or business capability:
Starting problem:
System boundary and dependencies:
My exact responsibility:
Important data or workflow:
Hardest technical decision:
Alternative considered:
Failure or incident:
Evidence used to diagnose it:
Fix and why it worked:
How we tested it:
Operational result (only if measured):
What I would improve now:
Confidentiality-safe wording:
Likely interviewer follow-ups:
```

Use the engineering sequence: context -> constraint -> decision -> implementation -> verification -> result -> lesson.

## 5. STAR plus engineering detail

For behavioral questions, use:

- Situation: one sentence of business and technical context.
- Task: your responsibility and success condition.
- Action: two or three specific actions, including communication.
- Result: measured result if available; otherwise a verifiable outcome.
- Engineering detail: failure mode, trade-off, test, or operational safeguard.
- Reflection: what you would repeat or change.

Avoid vague results such as “improved performance significantly” unless you know the before/after measurement. Say “I profiled the slow path, changed the query shape, and validated the result with repeatable timing” when that is what you can defend.

## 6. Minimum story bank

Prepare one true story for each row:

| Story | Evidence to collect |
|---|---|
| Complex feature or API delivered | Requirement, design, ownership, test, result |
| Production defect or incident | Timeline, symptoms, evidence, containment, root cause, prevention |
| Performance issue | Baseline, measurement tool, change, comparison |
| Data or transaction problem | Invariant, transaction boundary, concurrency behavior |
| Workflow or batch failure | State, retry/restart behavior, reconciliation |
| Security or validation concern | Threat, control, negative test, audit trail |
| Disagreement or difficult stakeholder | Options, decision criteria, communication, result |
| Mentoring or code review | Person/team need, guidance, outcome |
| Missed estimate or mistake | Signal, correction, learning, process change |
| New technology learning | Why needed, spike, test, limitation, next step |

For each story, create a short version under 90 seconds and a deep version under five minutes.

## 7. Safe resume positioning

### Headline

`Senior Software Engineer | Java 17 | Spring Boot | REST/microservices | JPA/Hibernate | SQL | Production support and RCA`

Add “Applied AI learning” or “AI-assisted development” only where the job and evidence support it. Do not use “AI engineer” as the primary title solely because you use coding assistants.

### Summary structure

```text
Senior Software Engineer with 5+ years of experience building and supporting Java/Spring backend capabilities for enterprise CRM and telecom workflows. Strong in REST APIs, JPA/Hibernate, SQL, workflow/batch processing, testing, and production troubleshooting. Interested in product engineering roles where long-term ownership, reliability, and measurable customer outcomes matter. Building applied-AI capability through structured labs in retrieval, tool integration, security, and evaluation.
```

Adjust the final sentence to the actual target role. Remove it for a pure backend role if it distracts from the job requirements.

### Bullet formula

`Action + capability + technical context + business/quality outcome + evidence`

Example template:

`Implemented [capability] using [verified technology], handling [important edge case]; validated with [test/diagnostic], improving [measured or verifiable outcome].`

Do not insert invented percentages, request volumes, uptime, latency, team size, cost savings, or customer counts.

## 8. Application customization worksheet

Complete this for each job description:

| Job requirement | My evidence | Gap | Proof I will build or explain | Resume change |
|---|---|---|---|---|
| Java/Spring |  |  |  |  |
| Distributed systems |  |  |  |  |
| Data/SQL |  |  |  |  |
| Cloud/platform |  |  |  |  |
| Product/domain |  |  |  |  |
| AI capability |  |  |  |  |
| Communication/ownership |  |  |  |  |

Use a three-column gap decision:

1. Can defend now: include and prepare follow-ups.
2. Can demonstrate in a public/sanitized project: build it before claiming depth.
3. Cannot defend yet: leave out or label as learning.

## 9. Gap answers

### Kafka, Redis, cloud, or Kubernetes gap

“My production background is strongest in Java/Spring, APIs, JPA/Hibernate, SQL, workflows, batch processing, and production support. I have been building hands-on knowledge of [technology] through a focused lab covering [specific features]. I understand the main trade-offs and failure modes, but I would not claim long-term production ownership yet. I can show the design, tests, and operational checks.”

### Applied AI gap

“My professional experience includes AI-assisted software development, and my academic project used CNN and LSTM techniques for image captioning. My current applied-AI work is a learning/portfolio track covering embeddings, RAG, tool calling, security, and evaluation. I distinguish that from production ownership and focus on measurable, bounded behavior.”

### Product-company transition

“I bring experience supporting enterprise CRM and telecom workflows where correctness, integrations, and incident response matter. I am strengthening product habits around customer outcomes, discovery, backward compatibility, observability, and iterative delivery so I can own a capability through its full lifecycle.”

## 10. Evidence pack before an interview

Keep a private, sanitized pack containing:

- One-page resume and a job-specific version.
- Project story pages for two or three real projects.
- Incident/RCA story with no customer secrets.
- Architecture sketch with fictionalized names and values.
- Test examples and a short list of diagnostics used.
- Coding, LLD, and system-design score history.
- List of technologies you can claim, have exposure to, or are learning.
- Five questions for the interviewer about ownership, quality, on-call, architecture, and product outcomes.

## 11. Final truth check

Before submitting an application, ask:

- Can I explain every noun on the resume?
- Can I state what I personally did?
- Can I describe one failure or trade-off for each major technology?
- Are all metrics measured and defensible?
- Are learning projects labelled as projects rather than employment experience?
- Does the resume match the job without keyword stuffing?
- Have I removed confidential information?

