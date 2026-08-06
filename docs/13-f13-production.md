# Feature 13 — Make It Production (Logging, Security, Observability)

> **Milestone:** the app is deployed; now it must not hurt its own users or silently break. This final feature is about the discipline that separates "it runs" from "it won't burn down."

---

## Step 1 · What are we building today

1. **Structured logging** with a `request_id` and per-request duration (so every log line traces to one request).
2. **Security headers** + a security checklist pass (secrets, CORS, rate limits on auth).
3. **A `/healthz`** endpoint and a **`/metrics`** counter (Prometheus-style) — the observability hooks.
4. **A review of the whole project** against a security checklist.

```json
{"ts":"2026-08-06T12:00:00Z","level":"info","event":"request",
 "method":"GET","path":"/users/torvalds/portfolio","status":200,
 "duration_ms":4,"request_id":"c9f...d21"}
```

---

## Step 2 · Why do we need this feature

Once it's live, three realities hit:

- **When it fails (and it will), you need to know *why*** — without good logs you're blind. `print()` doesn't scale.
- **The internet is hostile** — CORS `*`, default JWT secret, `DEBUG=True`, un-limited auth endpoints are one leak/misconfig away from a real breach.
- **It must be *measured*** — "is it working?" needs a heartbeat (health) and basic traffic (metrics).

These aren't luxuries; they're the difference between a demo and a deployment. This feature exists precisely *because the project is now in production*.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|-----------|---------------------------|
| Python **`logging`** + a FastAPI **middleware** | structured, per-request logs |
| **Middleware** (headers) | security headers on every response |
| `Prometheus`-compatible `/metrics` (a manual counter) | at-a-glance traffic/status counts |
| (reuse) config, rate-limit, health route | the checklist pass |

**No new frameworks** — the senior move is to use the stdlib + two small middlewares well, not to bolt on a heavy observability stack (that's a later upgrade). Keep it learnable.

---

## Step 4 · Teach only the required concepts

### 4.1 Structured logging + request_id

A **request_id** lets you chase one user's request through every log line (like how a shopping order number ties a package's journey). Middleware is the right home because it runs for *every* request:

```python
# app/middleware.py
import logging, time, uuid
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger("app")

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        log.info("request complete",
                 extra={"request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration_ms": round((time.perf_counter()-start)*1000, 1)})
        return response
```

**The rule:** log *events* with *fields*, at the right level (`INFO` for requests, `ERROR`/`CRITICAL` for failures). **Never log passwords/tokens**.

### 4.2 Security headers middleware

```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

CIS/OWASP basics. Two of them are free wins against common classes of attacks/clickjacking/mime-sniffing.

### 4.3 CORS done right

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=settings.allowed_origins,   # NEVER "*"
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```
`allow_origins` = your real frontend origin (in production). `*` means "any site may read your API" — a real security footgun.

### 4.4 Health + metrics

```python
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

metrics = {"http_requests_total": 0, "http_errors_total": 0}
@app.get("/metrics")
def metrics():
    return Response(
        f"http_requests_total {metrics['http_requests_total']}\n"
        f"http_errors_total {metrics['http_errors_total']}\n",
        media_type="text/plain",
    )
```
(Feed the counters from the request middleware — a tiny, real Prometheus-format endpoint. Orchestrators probe it; you read it.)

---

## Step 5 · Implementation plan

```
app/
├── middleware.py           # request_id logging + security headers
├── core/logging.py        # logging setup (JSON formatter optional)
├── routers/meta.py        # /healthz, /metrics
└── main.py                # wire middlewares
```

| File | Why |
|------|-----|
| `middleware.py` | cross-cutting concerns that touch every request |
| `routers/meta.py` | the operator-facing endpoints |
| `core/logging.py` | one logging config |

---

## Step 6 · Implement gradually

### Piece 1 — set up logging + wire middlewares

(4.1/4.2 into `main.py` via `add_middleware`.)

### Piece 2 — the ops endpoints

(4.4.)

### Piece 3 — the **security checklist pass** (run it against the whole project)

| Check | Where | Fix if violated |
|-------|-------|-----------------|
| No secrets in code/logs | all | config only, `.env`/env vars |
| `jwt_secret` overridden in prod | config | fail-fast if default & `debug=False` |
| `DEBUG=False` in prod | config | env gate |
| Passwords hashed | auth repo | bcrypt (F6) |
| rate-limit on auth + costly endpoints | F5 | keep |
| `User-Agent`+timeout on GitHub calls | F2 | keep |
| CORS list = our origin | middleware | fix |
| non-root container | Docker | fix |
| headers / X-XSS | middleware | add |
| `/docs` disabled in prod? | FastAPI | `docs_url=None` when `debug=False` |

This list is the *grading rubric* reviewers apply. Walking it end-to-end is the real lesson.

---

## Step 7 · Request lifecycle (with middlewares)

```
curl /portfolios
  │ → HTTP → uvicorn → FastAPI
  │ → RequestLogMiddleware (assigns request_id, starts timer)
  │     → security headers set on response
  │     → Rate limit dep (validate) → cache → service → DB → JSON
  │ → response returns; middleware logs the line (id, path, status, ms)
  ▼ 200 + headers; one structured log line appeared
```

Now debugging = `grep request_id=<id> app.log`.

---

## Step 8 · Alternatives

- **JSON vs plaintext logs**: plaintext is fine to start; JSON (`python-json-logger`) is the prod-standard for tools (Loki/Datadog). Our `extra={...}` is already structured — easy to serialize later.
- **Prometheus pip `client` vs our manual counter**: manual teaches; the client is the real tool. Upgrade when metrics grow.
- **Sentry vs our logging**: Sentry catches *exceptions live far better*; it's the next tool you'd add (deep automatically). We do "logs now, Sentry later."

---

## Step 9 · Refactor as a senior

- **`python-json-logger`** — emit JSON from day one in prod.
- **`Sentry`/`Prometheus`-client** — replace the hand-rolled counter.
- **Health that checks DB + Redis**: `/healthz` returns 503 if Redis/Postgres are down — orchestration drains it. (Our most valuable health upgrade.)
- **Log correlation** already there via `request_id`; propagate the ID into the GitHub/DB layers too if tracing ever matters.

---

## Step 10 — Exercises

1. Wire the `/metrics` counters into the request middleware (requests + status_group). Read them with `curl /metrics`.
2. Make `/healthz` return `503` if Redis or Postgres is unreachable (it *checks* them).
3. Add `docs_url=None` when `debug=False` (hide `/docs` in prod) and verify it's off.
4. Add a **JSON logging** formatter (stdlib `logging` with a custom formatter) — ship JSON lines.
5. **Audit pass**: run the Step 6 checklist against your repo and fix at least 2 real findings.

### Review yourself
- [ ] Does every request produce one structured log line with a `request_id`?
- [ ] Are secrets, tokens, and full bodies absent from all logs?
- [ ] Are security headers set and is CORS restricted to our real origin?
- [ ] Is `/healthz` live AND does it check the DB/Redis in prod?

---

## End of the apprenticeship

You now have a **feature-complete, layered, tested, containerized, hardened** GitHub-analytics API — and (more importantly) you built an *understanding* of every line of it:

1. What the request lifecycle is (browser → HTTP → ASGI → FastAPI → router → DI → service → client/DB → JSON → browser).
2. Why routers/services/repositories/clients exist — and what breaks without them.
3. How to design REST, persist data (SQLite→Postgres), cache (Redis, SWR), rate limit, and redesigns.
4. How to authenticate (JWT + hashing), defer work (background tasks), export (streaming, CPU-offload).
5. How a JS frontend + a React migration consume the same JSON API.
6. How to test, containerize, CI, deploy, and harden it — because the features, one by one, made every one of those tools *necessary*.

Go back to [Feature 1](01-f1-hello-api.md) and build it again — now from memory, explaining it to a friend. That repetition is where you become able to design and build future backends on your own.

---

*This is the last feature in the handbook. The project is now in your hands — go ship it.*