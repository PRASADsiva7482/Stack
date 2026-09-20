# 30. Behavioral, Resume Deep Dive, and Mock Interviews

**Status:** Learning target.  
**Goal:** Sound like a credible senior engineer: specific, calm, technically honest, and able to connect decisions to outcomes.

## 1. Story bank

Prepare six real stories from 6D and one academic story. Do not write fictional success stories.

| Story | Evidence to collect |
|---|---|
| Difficult production defect/RCA | symptom, timeline, your actions, verification |
| Performance improvement | before/after measurement, scope, trade-off |
| Design disagreement | options, decision process, result |
| Tight deadline | prioritization, risk, communication |
| Collaboration with QA/DevOps/business | handoffs, conflict, resolution |
| Mistake or failure | what you owned, correction, prevention |
| Learning quickly | unfamiliar technology, experiment, outcome |

Use STAR plus engineering detail:

```text
Situation -> Task/constraint -> Action/decision -> Result/evidence -> Reflection
```

If you cannot disclose numbers, use relative facts only when true: “reduced repeated database calls,” “improved restartability,” or “shortened investigation.” Never manufacture a percentage.

## 2. Tell-me-about-yourself answer

> “I am a Senior Software Engineer with 5+ years of experience in enterprise and consulting-driven application development. In my current CRM Core Platform work at 6D Technologies, I develop Java 17 and Spring Boot microservices and REST APIs, use JPA/Hibernate and SQL/MySQL, build Camunda workflows and Spring Batch jobs, integrate React components, write JUnit tests, and support GitLab CI/CD and production troubleshooting. I am now strengthening distributed systems, cloud, and AI application engineering so I can move into a product team where I can own backend reliability and customer-facing platform outcomes.”

This is strong because it is specific without claiming Kafka, Redis, cloud, or AI production ownership.

## 3. Resume bullet map

| Original resume claim | Primary question | Follow-ups to prepare |
|---|---|---|
| Designed Spring Boot microservices/REST APIs | Walk through one service | boundary, validation, errors, versioning, testing, failure |
| Built modular components/SOLID/layers | Why this structure? | coupling, transactions, testability, when not to abstract |
| JPA/Hibernate persistence | Explain one entity flow | persistence context, lazy load, N+1, locking, query plan |
| Camunda workflows | Walk through one process | state, retries, timers, worker failure, compensation, versioning |
| Spring Batch jobs | How was bulk processing controlled? | chunk transaction, restart, skip/retry, idempotency, memory |
| React integration | What did you own? | API states, validation, auth, browser error, performance |
| SQL/API performance optimization | Prove the improvement | baseline, plan, index, load, regression protection |
| GitLab CI/CD support | Which pipeline stage? | build failure, artifact, deployment, rollback, honest scope |
| Production support/RCA | Tell me about an incident | impact, evidence, mitigation, root cause, prevention |
| Agile/stakeholder collaboration | How did disagreement resolve? | trade-off, communication, customer impact |
| AI-assisted development | How do you use assistants safely? | review, tests, security, hallucinated code, data policy |
| CNN/LSTM academic project | Explain the pipeline | CNN features, sequence model, training/evaluation, limitations |

For each row, prepare one real example, one code/design follow-up, and one “I have not done that directly, but I would…” answer.

## 4. Handling experience gaps

Use this pattern:

> “I have not operated that in production. My current understanding is ____. I built/studied ____ to validate it. In production I would first check ____, then implement ____, and measure ____.”

Examples:

- Kafka: do not say “I designed Kafka architecture” if it is not on the resume.
- Kubernetes: say “I understand deployment, service, probes, and troubleshooting concepts; I am building hands-on evidence.”
- AI: say “My resume exposure is AI-assisted development and an academic CNN/LSTM project; RAG and tool calling are portfolio learning targets.”

## 5. Behavioral questions

Prepare answers for:

1. Tell me about yourself.
2. Why are you changing roles?
3. Why a product company?
4. Explain your current project.
5. What was your hardest production issue?
6. Tell me about a failure.
7. Tell me about a technical disagreement.
8. How do you handle an urgent deadline?
9. How do you prioritize bugs versus features?
10. How do you review another engineer’s code?
11. How do you work with QA, DevOps, and product owners?
12. What did you learn recently?
13. When did you push back on a requirement?
14. What would you redesign in your current system?
15. Why should we hire you?

Avoid blaming, vague “we” answers, confidential customer details, and unsupported numbers. Say “I” for your contribution and “the team” for shared work.

## 6. Mock interview protocol

Run these rounds one question at a time:

1. Java plus coding.
2. Spring, JPA, and SQL.
3. Microservices, Kafka, and Redis.
4. System design.
5. Current-project deep dive.
6. Production troubleshooting.
7. AI application engineering.
8. Behavioral/senior judgment.

Score each answer from 0-4:

| Score | Meaning |
|---:|---|
| 0 | Incorrect or no answer |
| 1 | Definition only; major gaps |
| 2 | Correct basic answer; weak internals/trade-offs |
| 3 | Correct, structured, production-aware |
| 4 | Clear senior answer with evidence, alternatives, failure, and measurement |

For coding, also score correctness, complexity, edge cases, tests, and communication. For design, score requirements, data model, APIs, scale, failure, security, observability, and trade-offs.

## 7. Strong senior signals

- Clarifies requirements before designing.
- Names a failure mode before choosing a pattern.
- Measures instead of guessing.
- Distinguishes at-most-once, at-least-once, and exactly-once claims.
- Separates current experience from planned learning.
- Explains what they would not build yet.
- Mentions migration, rollback, security, and operations.
- Takes responsibility without pretending to own other teams’ work.

## 8. Final self-check

You are ready to interview when you can explain your project in five minutes, answer a follow-up without memorized text, solve a medium coding problem in 35 minutes, design a service with failure handling, and state “I do not know” followed by a credible investigation plan.

