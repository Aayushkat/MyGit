# Feature 5 — Fast + Polite Caching with Redis (and Rate-Limiting Our API)

> **Milestone:** our cache moves from "a DB file" to an in-memory store that's huge fast, shared across processes, and can atomically count. And our own API stops being abusable. Both solve real pain we've now *felt*.

---

## Step 1 · What are we building today

1. **Replace the SQLite profile cache with Redis** (cache-aside, with a TTL that Redis handles for us).
2. **Add rate limiting to our API**: `429 Too Many Requests` with a `Retry-After` header.
3. (Bonus) Use Redis's atomic `INCR` for the **view counter** that the reference app has — that's Feature 7's seed, but the *tool* arrives here.

---

## Step 2 · Why do we need this feature

**Pain 1 — SQLite cache is now a bottleneck.** As profiles accumulate, the cache table grows; reads scan more; every write **locks the DB** (SQLite = single writer), so a user fetching a profile while another saves can stall. Redis lives in RAM, reads/writes in microseconds, and is shared across any number of app processes.

**Pain 2 — our own API is abusable.** Anyone can hammer `/portfolio` a thousand times a minute → they blow up *our* GitHub quota and our DB. We need to say "slow down" (429) like GitHub says to us. The rate limit is the *same concept* we already feel coming FROM GitHub — now we flip roles and add it to OUR side.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|------------|---------------------------|
| **Redis** | shared in-memory cache with TTL + atomic operations; fast reads, no DB locking |
| **redis-py (`redis.asyncio`)** | the async client to talk to Redis |
| (reuse) `Depends`, `config`, httpx | all in place |

**SQLite isn't removed** — it's reused for *durable* data (saved portfolios in Feature 6). The split becomes: **fast/shared/volatile → Redis; durable/relational → SQLite/Postgres.** Learning *where* each lives is a senior intuition.

---

## Step 4 · Teach only the required concepts

### 4.1 Redis: an in-memory key-value server

Redis is a **separate program** (like SQLite/PG) that stores keys→values in **RAM**. Two things it's famously good at:

- **`SET key val EX <ttl>`** — set with expiry; Redis auto-deletes after TTL. This replaces our manual `fetched_at` freshness logic!
- **`INCR key`** — atomically increments a number. Perfect for counters *and* rate limiting (no two processes double-count).

```python
import redis.asyncio as redis
r = redis.from_url(settings.redis_url)

await r.set(f"profile:{username}", json.dumps(profile), ex=900)   # 900s TTL
val = await r.get(f"profile:{username}")   # None if expired/miss
await r.incr("views:torvalds")             # atomic +1
```

**Why is `INCR` atomic when SQLite's UPDATE wasn't?** The design detail most tutorials skip: **Redis is single-threaded.** Every command (`GET`, `SET`, `INCR`, `EXPIRE`) runs on one thread, one after another. Two clients' `INCR` on the same key can never execute *simultaneously* — command 1 finishes fully before command 2 starts. That serialization *is* the atomicity: "an operation that can't be observed mid-way by any other client." `INCR` is "read → add 1 → write," three steps that race on a multi-writer DB but can't on a one-thread server. No locks needed — serialization is built into the architecture.

**TTL expiry isn't magic — it's checked lazily.** Redis doesn't delete the key "at exactly 900s." Keys expire on *access*: the next `GET` checks the stored time and returns nothing if it's past. (There's also a periodic passive cleanup pass to avoid memory leaks — but the *contract to you* is "expired = value missing.") That's why "never stored" and "just expired" are indistinguishable to a reader — which is *exactly right* for a cache: both mean "miss, go refetch."

### 4.2 Why a network cache is better than a file for hot data

Compare:
- **SQLite**: on disk; single writer lock; fast but not "instant"; survives restart.
- **Redis**: in RAM; microsecond; shared across processes; but if it restarts you lose volatile caches.

So the pattern becomes: **hot cache in Redis (cheap, fast, TTL), durable source of truth in the DB.**

### 4.3 Rate limiting with a sliding window

A classic fixed-window limiter using Redis:

```
key = rl:{client_ip}:{endpoint}
count = INCR key                      # atomic
if count == 1: EXPIRE key 60          # start 60s window
if count > ALLOWED: → 429 + Retry-After
```

Simple (but has a "burst boundary" issue — two batches at the exact edge can exceed the limit). A successor algorithm is the token bucket (drip rate). We start with fixed-window for the concept; the exercise upgrades to sliding/token-bucket.

**Why each algorithm exists (pick by the *abuse shape* you fear):**

- **Fixed window** (`INCR` + `EXPIRE 60`): the window resets on the *server clock*, not when the user started. 30 requests at second 59 of window A, then 30 at second 1 of window B = 60 requests in 2 consecutive seconds *around a window edge* — blowing a 30/min limit. That's the burst-boundary hole.
- **Sliding window**: keep a log of recent request *timestamps* (a Redis **sorted set**: `ZADD` a scored member per request, `ZREMRANGEBYSCORE` to drop old ones, `ZCARD` to count). "How many in the last 60s *right now*" — no boundary hole. Cost: more commands, more memory.
- **Token bucket**: a bucket holds up to `capacity` tokens; each request spends one; tokens refill at `rate`/second. An idle user has a full bucket (can burst immediately); the refill rate caps sustained load. Cost: you must store "current tokens + last refill time" and compute refill on read. A small **Lua script** keeps check-and-spend atomic (scripts run on Redis's single thread).

### 4.4 Dependency for rate limiting

A **dependency** `Depends(rate_limit)` or a **middleware**? 
- **Middleware** catches *every* request (simple, broad).
- **Dependency** lets us protect only expensive endpoints (GitHub-touching ones).
We use a **dependency** on the costly endpoints — precise, and reusable.

**Why dependency over middleware?** A dependency only runs for endpoints that *declare* it; a middleware runs for **every** request, before routing. Rate-limiting in middleware would count `GET /` and `/docs` traffic in the same budget you're protecting for `/portfolio` — pointless. "Narrowest blast radius" — the same instinct as Feature 3's service layer and this feature's swap-proof repository.

---

## Step 5 · Implementation plan

```
app/
├── core/redis.py              # redis client setup/one instance
├── clients/cache.py           # CacheStore: get/set/get_or_fetch with TTL (the new implementation)
├── repositories/profile_cache.py  # will be rewritten to use Redis
├── dependencies/rate_limit.py # rate_limit dependency (uses Redis INCR)
├── services/profile.py         # unchanged in logic; CacheStore is now Redis-backed
└── routers/github.py           # add Depends(rate_limit) on the GitHub endpoint
```

| File | Responsibility | Why |
|------|----------------|-----|
| `core/redis.py` | create ONE redis client | singleton, reads config |
| `clients/cache.*` or `repositories/profile_cache.py` | same **shape** as before but Redis backed | no service changes — the layer we built in F4 pays off |
| `rate_limit.py` | check a per-IP, per-endpoint window | protect GitHub budget |

> **Key point:** the service **does not change**. Because Feature 4's refactor introduced a cache interface, we swap "SQLite store" → "Redis store" without touching orchestration. That *is* dependency inversion paying rent.

**The mechanism of that swap:** in Feature 4 you defined the store as a `Protocol` — an *interface* — and the service depends on the *interface*, not the concrete SQLite repository. Now you rewrite the repository body, keeping the same `get_cached`/`save` signatures, and nothing downstream changes. The service holds a *name* of what it needs (`get_cached(username) -> dict | None`); any implementation satisfying the name plugs in. No `if self.using_redis:` branching. The point to *feel*: the seam was invented one feature early (F4), looking forward to F5 — build seams *before* you need the swap, so the swap is cheap when the need arrives.

---

## Step 6 · Implement gradually

### Piece 1 — add deps + config

```txt
redis==5.2.1
```
```python
settings.redis_url: str = "redis://localhost:6379/0"
```

### Piece 2 — core/redis.py

```python
import redis.asyncio as redis
from app.core.config import settings

async def get_redis():
    return redis.from_url(settings.redis_url, decode_responses=True)
```

`decode_responses=True` ⇒ values come back as strings (easier for JSON) rather than bytes.

### Piece 3 — CacheStore now backed by Redis

```python
# app/repositories/profile_cache.py  (rewrite, same interface)
import json
from app.core.redis import get_redis

async def get_cached(username: str) -> dict | None:
    r = await get_redis()
    raw = await r.get(f"profile:{username}")
    return json.loads(raw) if raw else None

async def save(username: str, profile: dict) -> None:
    r = await get_redis()
    await r.set(f"profile:{username}", json.dumps(profile), ex=900)   # TTL 15 min
```

**TTL did the freshness work** — no manual timestamps. Redis expiry *is* the freshness check.

> **Simplest:** get a client per call. Better: one shared client (Step 9 refactor) — measure the difference; note it.

### Piece 4 — the rate limiter

```python
# app/dependencies/rate_limit.py
from fastapi import Depends, HTTPException, Request

LIMIT = 30          # requests / minute (tune later)

async def rate_limit(request: Request):
    r = await get_redis()
    key = f"rl:{request.client.host}:{request.url.path}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    if count > LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests, slow down",
                            headers={"Retry-After": "30"})
```

- `request.client.host` = the caller's IP (the basis of our limit).
- `INCR` + `EXPIRE` on the first hit = the fixed-window limiter from 4.3.
- `Retry-After` header tells callers when to retry.

### Piece 5 — protect the expensive endpoint

```python
# app/routers/github.py
@router.get("/{username}/portfolio", response_model=Portfolio,
            dependencies=[Depends(rate_limit)])
async def portfolio(username: str = ..., service: ProfileService = Depends(get_service)):
    return await service.get_portfolio(username)
```

`dependencies=[...]` runs the rate limiter **before** the endpoint and enforces the 429 without you adding any logic. Clean.

> **Your turn:** implement, start Redis (via Docker later; for now a local/dev Redis, or `docker run -p 6379:6379 redis`). Restart uvicorn, hit `/portfolio` repeatedly and watch request ~31 → `429`. Then verify repeated *cached* hits are instant (Redis) while *non-cached* still call GitHub.

---

## Step 7 · Request lifecycle (Redis + rate limit)

```
Browser → GET /users/torvalds/portfolio
  │ uvicorn → FastAPI
  │ 1. dependencies=[Depends(rate_limit)] runs FIRST   ─┐
  │      │ INCR rl:<ip>:<path>                          │ 429 if > LIMIT
  │ 2. Path validation (username)  ─────────────────────┤
  │ 3. Depends(get_service) → service(client, redis)    ┘
  ▼
service.get_portfolio
  ├─ get_cached:  GET profile:torvalds (Redis)
  │      HIT → json.loads → Portfolio  → 200  (only 2 in-memory ops)
  │      MISS → fetch GitHub (2 httpx) → _compute → SET ex=900
  └─ 200 JSON
```

Count the touching of GitHub in the HIT path: **zero.** And the rate-limiter *never* reached GitHub either. Your stack is now polite to both GitHub and its own users.

---

## Step 8 · Alternatives

| | We use | Alternatives | Pros pick when |
|--|--------|-------------|----------------|
| Cache medium | **Redis** | SQLite/PG cache, in-memory `dict` | Redis/simple when sharing across processes or huge hot data |
| Rate limit placement | **dependency** | middleware | middleware for "every request" (login, API), dependency for costly endpoints |
| Limiter algorithm | fixed window | token bucket (Lua), sliding window | token bucket for bursty-but-smooth (pay wall / video) APIs |
| key base | client IP | + `User-Agent`, + token/account | when you want to hit accounts even behind NAT |

---

## Step 9 · Refactor as a senior

1. **One Redis client per app,** not per call: create it once in a `lifespan`, and inject it (avoids connection churn). This is the "reuse the connection" habit.
2. Extract the limiter as a factory: `rate_limit(limit=30, minutes=1) = Depends(...)` so different endpoints declare different budgets.
3. Move the **cache key builder** (`f"profile:{name}"`) to a `keys.py` helper — a single source for key naming (namespaces with `:`).

---

## Step 10 · Exercises

1. Implement the **token bucket / sliding window** rate limit (instead of fixed) — accept a burst then throttle. Test the boundary case.
2. Add `Retry-After` based on *when the window reset*s (not hard-coded `60`).
3. Switch the limiter to consider **`id` when an account exists** (feature 6) — accounts get a higher, separate quota.
4. **SQLite for durable cache anyway:** keep Redis for the hot profiles, but fall back to the SQLite cache if Redis is down (a resilient cache chain). Add a try/except that degrades gracefully.
5. Cache the **trending/Rankings** (Feature 2 data) server as well, using `TTL_BY_TYPE` (e.g. hourly). Note: this is what the reference app did — different content TTLs.

### Review yourself
- [ ] Nothing about HTTP goes through GitHub for a cache HIT?
- [ ] Is the rate limit applied ONLY to the expensive endpoint (not GET `/`)?
- [ ] Could a Redis outage crash the app (should we degrade gracefully)?

---

### Field notes — silent failures to expect

> **⚠️ `decode_responses=True` or you get `bytes`.** Without it, Redis returns `bytes`, not `str`, and `json.loads(b'{"a": 1}')` fails loudly. One flag fixes a surprising amount of debugging, and it's your first "the client library's defaults are not your product's defaults" lesson.

> **⚠️ `request.client.host` can be a proxy.** Behind a reverse proxy or load balancer (Feature 12/13), every request may appear to come from the *proxy's* IP — all users share one source, so one user's over-limit 429s everyone. The real client IP is typically in `X-Forwarded-For` (set by the proxy). Trusting `client.host` blindly breaks exactly when you deploy.

> **⚠️ Redis counters are RAM — they don't survive a restart.** For a cache/rate-limit that's usually *correct*; the moment you need durability, that's Feature 7's flush-to-DB job, or enabling persistence.

> **📌 `INCR` returns the new value — use it.** `count = await r.incr(key)` gets the incremented count in the same round-trip; no separate `GET`. "Return-value APIs" everywhere, Redis included.

---

**Next feature:** [Feature 6 — Accounts & Saved Portfolios](06-f6-auth.md). Now that we cache well, people will want to keep portfolios. "Keep" implies a user identity. Time for password hashing, JWT, and protected routes — authentication, learned when we actually need it.

---

> *Skipped Feature numbering note — this file is `05-f5-redis.md`; the reference index in [README](README.md) stays authoritative.*