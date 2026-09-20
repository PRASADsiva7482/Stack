# 28. Product Engineering, SaaS, and Telecom/BSS

**Status:** Learning target with strong domain relevance.  
**Resume boundary:** The original resume proves work on a CRM Core Platform, but not ownership of product strategy or every telecom subsystem.

## 1. Product engineering mindset

A product engineer connects a technical decision to a customer problem, measurable behavior, and an operational cost. A good answer covers:

```text
customer problem -> constraints -> options -> decision -> verification -> feedback -> iteration
```

Ask:

- Who is the user and what failure hurts them?
- What must be correct, available, fast, secure, and auditable?
- What is the smallest reversible release?
- What compatibility and migration promises already exist?
- What telemetry tells us whether the feature helps?

Technical quality includes maintainability, backward compatibility, supportability, security, and cost—not only throughput.

## 2. Product decisions interview format

When asked “why did you choose this design?” answer:

1. State the requirement and the constraint.
2. Name two realistic alternatives.
3. Explain the decision criteria: correctness, latency, scale, team skill, cost, and operability.
4. Explain the failure and migration plan.
5. State what you measured and what you would revisit.

Example:

> “For a bulk data process, the requirement was bounded memory and restartability. Loading all rows was simple but unsafe; offset pagination was easy but becomes slower at large offsets. I would prefer chunked processing with a stable key and a transaction per chunk, then verify memory, duration, retry behavior, and duplicate handling. The exact choice depends on the existing schema and ordering guarantees.”

## 3. SaaS architecture

Common tenancy models:

| Model | Isolation | Cost/operations | Use when |
|---|---|---|---|
| Shared DB/shared schema | Lowest | Simple, efficient | Strong row-level authorization and moderate isolation are acceptable |
| Shared DB/separate schema | Medium | More migrations/operations | Tenants need logical separation |
| Separate DB | Highest | Costly provisioning and migrations | Regulatory, noisy-neighbor, or contractual isolation requires it |

Tenant identity must be derived from trusted authentication, not a caller-controlled header. Enforce tenant scope in service authorization, queries, cache keys, events, files, logs, and background jobs. Add negative tests proving tenant A cannot access tenant B.

Multi-tenant features also need usage metering, quotas, plan limits, rate limiting, audit history, configuration, billing concepts, and noisy-neighbor controls.

## 4. Telecom/BSS mental model

```text
customer/account -> product catalog -> order management -> provisioning
       |                  |                  |
       v                  v                  v
 billing/invoice <- rating/charging <- usage/mediation/network events
       |
       v
 payments -> collections -> dispute/revenue assurance
```

- **CRM:** customer, account, contact, interaction, case, and service relationship.
- **BSS:** commercial and customer-facing processes: product, order, billing, charging, payment, care, and revenue.
- **OSS:** network/service operations: inventory, provisioning, assurance, fault, and configuration.
- **Product catalog:** products, offers, bundles, eligibility, prices, rules, and lifecycle.
- **Order management:** decomposes a commercial order into fulfillment actions and tracks state.
- **Provisioning:** activates or changes the technical service in network systems.
- **Mediation:** collects, normalizes, correlates, enriches, and routes usage records.
- **Rating:** applies tariff and pricing rules to usage.
- **Charging:** reserves or deducts balance, often in real time.
- **Billing/invoicing:** aggregates rated events and produces invoices, adjustments, taxes, and statements.
- **Revenue assurance:** reconciles expected and observed events across network, usage, billing, and finance.

Do not confuse prepaid real-time charging with postpaid invoice generation. They have different latency, consistency, and recovery requirements.

## 5. Workflow and Camunda connection

Use a deterministic workflow engine for state, timers, retries, approvals, audit, and compensating actions. Keep external side effects idempotent. Store correlation IDs and business keys. A model may classify or extract information, but a deterministic rule or human approval should authorize financial, provisioning, or account-changing actions.

Typical onboarding flow:

```text
validate order -> check eligibility -> reserve resources -> provision service
       -> confirm billing -> notify customer
       -> compensate or manual review on failure
```

## 6. Product metrics and reliability

Choose metrics that reflect the feature: activation completion time, failed orders, duplicate charges, invoice correctness, support resolution time, p95/p99 latency, availability, and cost per transaction. Avoid vanity metrics such as raw request count without outcome.

Feature flags enable gradual release, but flags need owners, expiry dates, audit, and tests for both states. A migration should be observable and reversible.

## 7. Domain interview questions

1. CRM versus BSS versus OSS?
2. Product catalog versus order management?
3. Rating versus charging versus billing?
4. Why is charging latency-sensitive?
5. What is mediation and why can duplicate usage records matter?
6. How do you model a subscriber lifecycle?
7. How do you prevent duplicate provisioning?
8. How do you handle a billing event that arrives late?
9. How do you design a multi-tenant CRM?
10. Where should a workflow engine stop and application code begin?
11. How do you compensate when provisioning succeeds but billing fails?
12. What is a good product metric for a subscriber onboarding feature?

## 8. Honest experience positioning

> “My verified experience is Java/Spring engineering on a CRM Core Platform, with Camunda workflows, Spring Batch, JPA/Hibernate, REST, SQL, React integration, testing, CI/CD support, and production troubleshooting. I understand the BSS relationships and am deepening distributed systems, cloud, and AI through labs and portfolio projects. I distinguish platform concepts I studied from subsystems I personally implemented.”

## 9. Practice projects

1. Model a subscriber onboarding state machine with idempotent commands and compensation.
2. Design shared-schema multi-tenancy with tenant-scoped queries and negative authorization tests.
3. Create a small rating-to-invoice batch flow with late events and reconciliation.
4. Write an architecture decision record comparing synchronous REST with events for provisioning notifications.

