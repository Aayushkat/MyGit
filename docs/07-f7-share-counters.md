# Feature 7 — Share Links & View Counters

> **Milestone:** a portfolio becomes *addressable* (shareable by URL) and *measurable* (who/how many times it's viewed). This is the feature that needs **background tasks** and puts **Redis counters** to real work.

---

## Step 1 · What are we building today

1. **Shareable links for saved portfolios**: `GET /p/{username}?template=bento` renders/refers to a portfolio the same way the reference app does — the whole view <config> lives in the URL.
2. **A public, non-login profile page**: anyone with the link can see the portfolio (no auth). That's "shareability."
3. **View counter**: each time a portfolio page loads, we count one view. The landing page shows the **global total** ("X portfolios generated").

```json
GET /p/octocat
→ 200 { "profile": {...}, "template": "github", "views": 1234 }
```

---

## Step 2 · Why do we need this feature

- **Shareability** is *the* core feature of the whole app (remember the reference: `/{username}?template=bento`). A portfolio that can't be linked is worthless.
- **Counters** answer "is this useful?" and make the landing page feel alive ("X portfolios generated").
- **Background tasks**: bumping a counter *must not* slow the page response. So this feature is where "do it later, in the background" becomes a *necessity* — we learn background tasks because the page would otherwise be slower for no benefit.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|-----------|---------------------------|
| **Query params / URL state** (HTTP) | encode template/theme in the URL — no config store |
| **Redis `INCR` (again)** | a fast, shared view counter (the tool from F5) |
| **FastAPI `BackgroundTasks`** | bump the counter *after* the response is sent |
| (reuse) `Depends`, `get_session`, client, Redis | no new core-tech |

**A whole feature with almost no new dependency** again — proof that "technology" is 20% and "design" is 80%. The genuinely new *capability* is running work after the response, via `BackgroundTasks`.

---

## Step 4 · Teach only the required concepts

### 4.1 URL as state

A URL can **carry the entire view**: `format`, `template`, `theme`, username (in path). On load, the frontend reads `location.search`, sets its state, and renders. This gives:

- **share** — paste the URL,
- **refresh** — reload keeps the view,
- **linkable** — no "session" needed.

That's the entire "share" UX — no login required to *view*.

### 4.2 FastAPI `BackgroundTasks`

```python
from fastapi import BackgroundTasks

def bump_counter(username: str):        # runs LATER, off the response path
    ...
@app.get("/p/{username}")
async def portfolio(username: str, bg_tasks: BackgroundTasks):
    # ... build the view ...
    bg_tasks.add_task(bump_counter, username)    # queue it, don't await
    return view
```

**Under the hood:** FastAPI collects tasks, sends the **response to the client first**, then awaits the background tasks. The client isn't blocked by `bump_counter`. This is "make fast things fast, defer slow things" made literal.

> Rule of thumb: `BackgroundTasks` for *light, best-effort* work (a counter increment, a log, an email). For *heavy/critical/retryable* work you'd graduate to a task queue (Feature 8's export touches this). For *now*, an INCR is perfect.

### 4.3 An atomic counter with Redis + a durable drain

A counter needs to be **fast to write** (every view) but we also want **durability** (SQLite). Pattern:

```
view → Redis INCR profile_views:{username}   (fast, atomic)
       └(background, batched) flush to Portfolio.views in DB periodically
```

For this feature we'll read the live count from Redis and provide a "reset" endpoint; the DB-persist flush is Exercise 4. The important concept: **fast writes, batched persistence** — serverless/edge apps do exactly this.

---

## Step 5 · Implementation plan

```
app/
├── services/
│   └── portfolio.py          # add get_public(username, template) → includes views
├── dependencies/counters.py  # get_views / increment_views (Redis)
├── routers/
│   ├── portfolio.py          # REDIRECT /p/{username} requires → render (no auth)
│   └── stats.py              # GET /stats/global → total generated
└── static/                   # (starting point for the HTML page, Feature 9)
```

| File | Why |
|------|-----|
| `dependencies/counters.py` | isolates "load the counter" logic (testable) |
| `routers/portfolio.py` | public page route + uses BackgroundTasks to increment |
| `routers/stats.py` | the global counter for the landing page |

**Note:** we purposely do NOT put the counter logic inline in the route — "how we count views" is its own concern, reused by (a) the page render and (b) the stats endpoint.

---

## Step 6 · Implement gradually

### Piece 1 — counters module

```python
# app/dependencies/counters.py
import redis.asyncio as redis
from app.core.redis import get_redis

# Redis key for the total number of "generations" (landing hero number)
TOTAL_KEY = "stats:portfolio_total"

async def get_view_count(username: str) -> int:
    r = await get_redis()
    n = await r.get(f"views:{username.lower()}")
    return int(n) if n else 0

async def increment_view(username: str) -> None:
    r = await get_redis()
    await r.incr(f"views:{username.lower()}")
    await r.incr(TOTAL_KEY)

async def get_global_total() -> int:
    r = await get_redis(); n = await r.get(TOTAL_KEY)
    return int(n) if n else 0
```

Because `INCR` is atomic, **two simultaneous requests can never both see "0 then set 1"** — no lost updates. That's the textbook reason to use Redis for counters.

### Piece 2 — the public page route with a background bump

```python
# app/routers/portfolio.py
from fastapi import APIRouter, BackgroundTasks
from app.dependencies import counters
from app.services.portfolio import ProfileService

router = APIRouter(prefix="/p", tags=["portfolio"])

@router.get("/{username}")
async def public_portfolio(
    username: str,
    template: str = Query("github"),      # URL state
    background: BackgroundTasks = BackgroundTasks(),
    service: ProfileService = Depends(get_service),
):
    profile = await service.get_portfolio(username)          # served+cached
    views = await counters.get_view_count(username)
    background.add_task(counters.increment_view, username)   # AFTER response
    return {"profile": profile, "template": template, "views": views}
```

- `Query("github")` = the `?template=github` in the URL is our "shareable state."
- `background.add_task(...)` — the count bumps only after we've handed back the JSON, so the number we *show* in this response is the count from before this view (standard "you came from a share; count starts reflecting next time").

### Piece 3 — the global counter endpoint

```python
# app/routers/stats.py
@router.get("/stats/global")
async def global_stats():
    return {"total": await counters.get_global_total()}
```

> **Your turn:** implement, restart, and confirm:
> 1. `GET /p/octocat?template=github` returns the profile with `views`.
> 2. Hit it 5 times, `views` goes up (the increment happens after the response — don't  be confused that the value lags one request).
> 3. `GET /stats/global` shows the total.

---

## Step 7 · Request lifecycle (background task)

```
Browser → GET /p/octocat
  │ uvicorn → FastAPI
  │ rate_limit (if applied) + validation
  │ service.get_portfolio → cache/HIT or fetch+MISS (GitHub)
  │ get_view_count (Redis)
  │ background.add_task(increment_view)   ← queued, NOT awaited
  ▼
  return JSON {profile, views}  ──────►  BROWSER GETS RESPONSE NOW
          ◄────── 200 sent ─────────┘
  background: increment_view(octocat)   ← runs after; INCR views + total
```

The client is back at 30ms while the increment happens quietly after. That's `BackgroundTasks` in a nutshell.

---

## Step 8 · Alternatives

| | We use | Alternatives | Pros pick when |
|--|--------|-------------|----------------|
| Counter medium | **Redis INCR** | SQLite UPDATE, Postgres, an app-global int | need shared+atomic across processes → Redis; |
| Deferred work | **FastAPI BackgroundTasks** | queue (RQ/Dramatiq/Celery) | when the work is heavy, critical, or must retry (exports, emails) |
| View count accuracy | Redis (may reset) | persistent DB record | when "views" is a hard, auditable number → DB; for display-only "nice," Redis is fine |

**Trade-off to note:** Redis counts can be lost on restart (not persisted by default). For "it went from 1200→1204," perfect. If "views" must be durable, flush to a DB column periodically (Exercise 3). Track the split: **Redis = hot, DB = truth.**

---

## Step 9 · Refactor as a senior

- **Durability**: add a `views` column on a `PortfolioView` table, and flush Redis counters→DB via a small **cron/scheduled task** (Feature 8-9 notes). Redis stays for hot reads; the DB is the truth.
- **Robust key naming**: keep `views:`/`total:` prefixes in `counters.py` only (single source of key names).
- **Cap the fire-hose**: background tasks that pile up can exhaust memory — cap/one-at-a-time if load grows (or move to a queue).

---

## Step 10 · Exercises

1. Add `theme` to the URL state (`?theme=dark`) and echo it back in the response. (Frontend later uses it.)
2. Add a **bounded** counter per user (Redis memory safety): set a TTL on the `views:` key so no single user's counter lives forever, and read `TTL` to know when it expires.
3. **Global counter durability**: persist `total:portfolio_total` to a Startup / periodic in one SQLite row, restoring Redis on restart.
4. Add a deliberate slow background task (e.g. `sleep(2)` then bump) and observe that the GET **returns instantly** while the task completes after. *(This is the "feel it" exercise for BackgroundTasks.)*

### Review yourself
- [ ] Does an unauthenticated visitor get the portfolio page (share work, no token needed)?
- [ ] Is the counter bump never in the response fast path using `await`?
- [ ] Are counter keys namespaced (`views:` / `total:`)?
- [ ] Can `GET /p/{}` be spammed to blow up GitHub's rate limit? (Think — is caching enough? Where would a rate limit help?)

---

**Next feature:** [Feature 8 — Export as PNG/PDF](08-f8-export.md). Share links exist; now people want a *file* to put in a CV. Time for file/streaming responses, and CPU-heavy image rendering off the event loop.