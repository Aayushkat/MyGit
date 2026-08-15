# Relay — A Production-Grade Webhook Delivery Platform, Mentor-Led Handbook

A **project-driven** apprenticeship handbook. We build **Relay** — a real webhook delivery platform in the spirit of Svix or Stripe's webhook infrastructure — piece by piece, and every technology is introduced **only when the project makes it necessary**, never as isolated theory.

> **The single rule of this handbook:**
> We don't say *"today we learn SQS."*
> We say *"our API can't wait for a subscriber's slow server before answering — that means ingest and delivery must be decoupled — which means we now need a queue."*
> Then we build it.

You write every file. I explain every line's *why*, review your code, and point at the mistakes production would punish.

---

## 1. What we are building — and why *this* project teaches *this* stack

**Relay** does one job that almost every SaaS company must eventually do well: when something happens (an order ships, a payment clears), deliver that event to customer-registered HTTPS endpoints — **reliably**.

Concretely, Relay:

- **Accepts events** over an authenticated HTTP API (`POST /events`).
- **Queues them** so ingest stays fast even when subscriber endpoints are slow or down.
- **Delivers them** to every subscribed endpoint with an **HMAC-SHA256 signature** (header `X-Relay-Signature`, timestamped to block replay attacks).
- **Retries with backoff** when delivery fails, and parks poison messages in a **dead-letter queue** instead of retrying forever.
- **Exposes its health**: structured logs, metrics, and traces, because "did the webhook arrive?" is the first support ticket every webhook provider gets.

### Why this project drives this curriculum

Webhook delivery is the smallest project that *genuinely needs* the modern backend/AWS toolbox. Nothing here is decoration:

```
The pain                                  →  The tool it forces on us
──────────────────────────────────────────────────────────────────────────
Consumers need a stable API contract      →  OpenAPI, contract-first design
Ingest must survive slow subscribers     →  SQS (queueing, decoupling)
Failures are normal, not exceptional      →  retries, backoff, DLQ
Events + subscriptions + attempts to store →  DynamoDB single-table design
Subscribers must trust the payload        →  HMAC signatures, replay defense
"It's slow" / "it's lost" tickets         →  logs, metrics, traces
TLS, routing, abuse at the front door     →  Envoy edge proxy
A distributed system you can't eyeball    →  unit + integration + contract tests
Clicking consoles doesn't reproduce       →  CloudFormation (IaC)
"Works on my machine" servers             →  Packer images + SaltStack states
```

If you can build, test, and operate Relay, you can walk into a backend team and recognize 90% of what is on the whiteboard. That is the promise: **the project drives the curriculum** — we never install a tool the project has not yet made us need.

---

## 2. Single-student scope guardrails

Relay is scoped for **one student, one laptop**. These guardrails keep it that way:

- **One service, two processes.** The FastAPI app (ingest + management API) and the delivery worker. No microservice zoo.
- **One table, one queue.** DynamoDB table `relay-main`, SQS queue `relay-deliveries` with DLQ `relay-deliveries-dlq`. We learn single-table design *because* we refuse to sprawl.
- **Local first, always.** Everything runs against LocalStack in Docker. Real AWS is one optional chapter (12), fenced with billing alarms and teardown commands.
- **No Kubernetes, no Terraform-vs-CDK detours, no multi-region.** Chapter 13 *explains* the scaling story so you can talk about it; we do not build it.
- **No frontend.** Relay's consumers are machines. `curl`, PowerShell's `Invoke-RestMethod`, and the auto-generated OpenAPI docs page are our UI.
- **You implement everything yourself.** The handbook shows snippets and explains them; there is no repo to clone the answers from.

When a chapter tempts us to grow beyond this list, the chapter will say so — and then decline.

---

## 3. The tech stack — each tool earns its place

| Technology | The project need that justifies it |
|---|---|
| **Python 3.13 + uv** | One fast, reproducible toolchain: interpreter, venv, lockfile — no pip/venv/poetry juggling on an 8 GB machine. |
| **FastAPI** (`app/` layout: `api/`, `services/`, `clients/`, `models/`, `core/`) | Async HTTP API with Pydantic validation and a live OpenAPI document we can diff against our hand-written contract. |
| **OpenAPI (contract-first)** | Subscribers integrate against our API; the contract must be designed, versioned, and verified — not reverse-engineered from code. |
| **DynamoDB** (single table `relay-main`) | Events, subscriptions, and delivery attempts with predictable key-based access patterns — the canonical single-table use case. |
| **SQS** (`relay-deliveries` + `relay-deliveries-dlq`) | Ingest must return in milliseconds while delivery takes seconds and fails often; the queue is the shock absorber, the DLQ the safety net. |
| **aioboto3** | Async AWS SDK so DynamoDB and SQS calls don't block the FastAPI event loop. |
| **LocalStack + Docker Compose** | The entire AWS surface (DynamoDB, SQS, CloudFormation) on localhost, for $0. |
| **Envoy** (Docker, port 8080 → API on 8000) | TLS termination, routing, and local rate limiting belong at the edge, not inside application code. |
| **HMAC-SHA256 signatures** (`X-Relay-Signature`) | Subscribers must verify payloads came from us and are not replays — the industry-standard webhook auth scheme. |
| **structlog + Prometheus + OpenTelemetry** | JSON logs with request IDs, delivery metrics, and cross-process traces — the only way to debug "where did my event go?". |
| **pytest + moto + LocalStack + schemathesis** | Unit tests (moto fakes AWS in-process), integration tests (real wire calls to LocalStack), and contract tests generated from our OpenAPI document. |
| **ruff** | One fast tool for lint + format; zero configuration debates. |
| **CloudFormation** | The table, queues, and alarms as reviewable, deletable code — the same template runs on LocalStack and real AWS. |
| **Packer** (docker builder locally; `amazon-ebs` documented) | Immutable machine images: the server is built once, never hand-edited. |
| **SaltStack** (masterless, `salt-call --local`) | Declarative configuration applied to the image — repeatable instead of SSH-and-pray. |

---

## 4. The roadmap

Each chapter exists because the previous one created the pain that justifies it.

| Chapter | Title | Introduces |
|---|---|---|
| [00-terrain-and-design.md](00-terrain-and-design.md) | The terrain: webhooks, delivery guarantees, and the Relay design | What webhooks are, at-least-once delivery, idempotency, and Relay's architecture on paper before any code. |
| [01-fastapi-skeleton-openapi.md](01-fastapi-skeleton-openapi.md) | FastAPI skeleton, uv toolchain, and the OpenAPI contract | uv project setup, the `app/` package layout, contract-first OpenAPI design, and diffing spec vs. live docs. |
| [02-ingest-api.md](02-ingest-api.md) | The ingest API: events, validation, API keys, and signatures | `POST /events` with Pydantic validation, API-key auth, and HMAC-SHA256 signing with timestamps. |
| [03-dynamodb-foundations.md](03-dynamodb-foundations.md) | DynamoDB: single-table design and the persistence layer | PK/SK modeling for `relay-main`, access patterns, and an aioboto3 repository layer against LocalStack. |
| [04-sqs-queueing.md](04-sqs-queueing.md) | SQS: decoupling ingest from delivery | Producer/consumer decoupling, message contracts, visibility timeout, and why the queue makes ingest fast. |
| [05-delivery-worker.md](05-delivery-worker.md) | The delivery worker: retries, backoff, and the DLQ | The consumer loop, exponential backoff with jitter, attempt tracking, and dead-lettering poison messages. |
| [06-envoy-edge.md](06-envoy-edge.md) | Envoy at the edge | An edge proxy in Docker: TLS termination, routing to the API, and local rate limiting on port 8080. |
| [07-observability.md](07-observability.md) | Observability: logs, metrics, traces | structlog JSON logs with request IDs, Prometheus metrics, and OpenTelemetry traces across API and worker. |
| [08-testing.md](08-testing.md) | Testing a distributed service | The test pyramid for Relay: moto unit tests, LocalStack integration tests, schemathesis contract tests. |
| [09-cloudformation-iac.md](09-cloudformation-iac.md) | CloudFormation: infrastructure as code | The table, queues, and DLQ as a template deployed to LocalStack — infrastructure you can review and delete. |
| [10-packer-images.md](10-packer-images.md) | Packer: immutable machine images | Image building with the docker builder locally; the `amazon-ebs` AMI path documented for the real thing. |
| [11-saltstack-config.md](11-saltstack-config.md) | SaltStack: configuration management | Masterless states (`salt-call --local`) that turn a blank image into a configured Relay host. |
| [12-ec2-deploy.md](12-ec2-deploy.md) | EC2: the optional real deployment | The one optional real-AWS chapter: free tier, billing alarms first, exact teardown, and a skip-if-unsure path. |
| [13-production-hardening.md](13-production-hardening.md) | Production hardening and the scaling story | Security hardening, operational runbooks, and how Relay would scale — explained, not built. |

**Why this order?** Follow the pain:

```
Contract designed (01) → ingest endpoint exists (02)
  → events vanish on restart            → we NEED persistence        (03)
  → ingest blocks on slow subscribers   → we NEED a queue            (04)
  → deliveries fail and must not loop   → we NEED retries + DLQ      (05)
  → plaintext HTTP, no abuse control    → we NEED an edge proxy      (06)
  → "where did my event go?"            → we NEED observability      (07)
  → too many moving parts to eyeball    → we NEED real tests         (08)
  → hand-made infra can't be reproduced → we NEED IaC                (09)
  → hand-made servers can't either      → we NEED images + config    (10, 11)
  → it only lives on localhost          → OPTIONAL real deploy       (12)
  → what would production demand?       → hardening + scaling story  (13)
```

---

## 5. Decisions locked in

Every chapter follows these pinned decisions. They are settled here so no chapter relitigates them.

| Decision | Locked value |
|---|---|
| Product | **Relay**: events in via API → queued → delivered to subscriber endpoints with signatures, retries, and a DLQ. Single-student scope. |
| Language & toolchain | **Python 3.13**, managed with **uv** (interpreter, venv, lockfile). |
| Web framework & layout | **FastAPI**, package layout `app/` with `api/`, `services/`, `clients/`, `models/`, `core/`. |
| API design | **Contract-first**: the OpenAPI document is written before code; FastAPI's generated document is diffed against it. |
| AWS SDK | **aioboto3** (async) everywhere we touch AWS. |
| Persistence | **DynamoDB single table `relay-main`** with PK/SK single-table design. |
| Queueing | **SQS `relay-deliveries`** with DLQ **`relay-deliveries-dlq`**. |
| Infrastructure | All AWS resources provisioned by **CloudFormation** — no console clicking. |
| Cost | **Never-pay**: all development against **LocalStack** (Docker Compose, `localstack/localstack`). Only chapter 12 optionally touches real AWS free tier — with billing alarms, exact teardown commands, and a skip path. |
| Edge | **Envoy** in Docker on **port 8080** in front of the API on **8000**: TLS termination, routing, local rate limiting. |
| Webhook auth | **HMAC-SHA256** in header **`X-Relay-Signature`**, with a timestamp to prevent replay. |
| Images & config | **Packer** docker builder locally (amazon-ebs documented for the real AMI); **SaltStack masterless** (`salt-call --local`) applies states. |
| Observability | **structlog** JSON logs with request IDs, **Prometheus** metrics, **OpenTelemetry** tracing. |
| Testing | **pytest** + **moto** (unit) + **LocalStack** (integration) + **schemathesis** (contract tests against OpenAPI). |
| Lint/format | **ruff** for both. |

If a chapter appears to contradict this table, the table wins — file it as an erratum.

---

## 6. How each chapter is structured

Every chapter follows the same 10-step rhythm:

| Step | What happens |
|------|--------------|
| 1 | **What we are building** — one concrete slice of Relay. |
| 2 | **Why the project needs it** — the pain that forces the new tool. |
| 3 | **New technologies required** — a table: tech → why *now*. |
| 4 | **Concepts** — the theory, taught properly but only what this chapter needs; ends with official-docs pointers. |
| 5 | **Implementation plan** — the files we'll create, one responsibility each. |
| 6 | **Build it piece by piece** — snippets with what/why explanations; never one giant final dump. |
| 7 | **Run and verify** — exact PowerShell commands, expected output, proof it works. |
| 8 | **How it flows** — an ascii trace of the request/data path we just built. |
| 9 | **A senior's review** — what production would demand; tradeoffs: chosen vs. alternative vs. when the alternative wins. |
| 10 | **Exercises** — 3–5 implementation tasks. No solutions. |

Step 4 is calibrated deliberately: enough theory that you never need to open a second tab to finish the chapter — and not one history lesson more.

---

## 7. Hardware and the never-pay strategy

The reference machine is modest on purpose: **Windows 11, PowerShell, Ryzen 3 7320U, 8 GB RAM, no dedicated GPU.** If it runs here, it runs anywhere.

**The core promise: you will not spend a cent to finish this handbook.**

- **LocalStack is our AWS.** DynamoDB, SQS, and CloudFormation all run in one Docker container. Same APIs, same SDK calls, zero dollars.
- **Every heavy tool ships with a lightweight path.** Packer practices with its docker builder (no AMI, no EC2). SaltStack runs masterless (no master server). Envoy is one small container. Observability backends are optional viewers — the instrumentation itself is nearly free.
- **8 GB discipline.** We run only the containers a chapter needs and stop them after (`docker compose down`). No chapter requires more than LocalStack + Envoy + the app at once. Close the browser tab farm first.
- **Chapter 12 is the only exception, and it is optional.** It uses the real AWS free tier, creates the billing alarm *before* any resource, ends with exact teardown commands, and opens with a "skip this if unsure" path. Skipping it costs you nothing but one checkbox in section 8.

Verify your machine is ready:

```powershell
# Docker Desktop must be running (WSL 2 backend)
docker --version
docker compose version

# uv manages Python 3.13 for us — no separate Python install needed
uv --version
uv python install 3.13

# Git, because we commit after every chapter
git --version
```

> **Industry lens:** Real engineering orgs run this exact split. Developers build and test webhook pipelines against LocalStack or moto in CI — nobody develops against a live AWS account, because shared mutable cloud state makes tests flaky and mistakes expensive. Real AWS is reached only through reviewed infrastructure-as-code in a pipeline, with billing alerts and least-privilege roles. Our LocalStack-first, CloudFormation-always, alarms-before-resources workflow is not a student compromise — it is the production workflow, shrunk to one laptop.

---

## 8. The end-goal checklist

By the last chapter, from memory and understanding, you can:

- [ ] Explain webhooks, at-least-once delivery, and idempotency — and why "exactly-once" is a lie vendors tell.
- [ ] Design an API contract-first in OpenAPI and verify the implementation never drifts from it.
- [ ] Build an async FastAPI service with a clean `api/ services/ clients/ models/ core/` layering, and say what breaks without each layer.
- [ ] Model events, subscriptions, and delivery attempts in a DynamoDB single table, and defend the PK/SK design.
- [ ] Decouple ingest from delivery with SQS and explain visibility timeout, redrive, and the DLQ from experience.
- [ ] Implement retries with exponential backoff and jitter, and know when to stop retrying.
- [ ] Sign webhooks with HMAC-SHA256 and defend against replay — and verify a signature as a subscriber would.
- [ ] Put Envoy in front of a service: TLS termination, routing, rate limiting.
- [ ] Trace one event through logs, metrics, and traces across two processes, using a request ID.
- [ ] Test a distributed service at three levels: moto units, LocalStack integration, schemathesis contract tests.
- [ ] Express all infrastructure as CloudFormation and deploy the same template locally and (optionally) for real.
- [ ] Build an immutable machine image with Packer and configure it with masterless SaltStack.
- [ ] (Optional) Deploy to a real EC2 free-tier instance — with billing alarms up first and a clean teardown after.
- [ ] Walk a whiteboard through how Relay would scale: sharding, fan-out, multi-tenancy, backpressure.

---

**Start here:** [Chapter 0 — The terrain: webhooks, delivery guarantees, and the Relay design](00-terrain-and-design.md).

*You are the engineer. I am the senior sitting next to you. Let's build Relay.*
