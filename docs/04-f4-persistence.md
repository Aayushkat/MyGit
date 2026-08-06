# Feature 4 — Stop Hitting Rate Limits (Persistence with SQLite)

> **Milestone:** remember what we've already fetched. This is the feature where the **database** becomes necessary — and where you feel *why* the reference app needed caching.

---

## Step 1 · What are we building today

A **profile cache table**: every portfolio we build gets stored (as JSON) with a timestamp. On the next request for the same username:

- if the cached copy is **fresh** (< 15 min old), return it — **zero GitHub calls**;
- if it's **stale or missing**, fetch from GitHub, store it, and return.

```json
{ "username": "torvalds", "profile": { ... }, "fetched_at": "2026-08-06T12:00:00Z" }
```

We'll store it in **SQLite** via **SQLModel**, and manage schema changes with **Alembic** so we can later move to PostgreSQL without tears.

---

## Step 2 · Why do we need this feature

Do the math from the last feature: every `/portfolio` request = **2 GitHub HTTP calls**, and GitHub allows **~60 requests/hour** per IP without a token (5,000/hr with). 

- One person refreshing the page 5 times = up to 10 GitHub calls = ~10 minutes of your hourly budget *gone*.
- Two people in a demo = your app is rate-limited, **with a real 403 from GitHub**, and every portfolio breaks.

**This is the real-world reason caches exist.** We're not learning "SQL" in the abstract; the project just *forced* us to persist data. This is Feature-Driven Learning working as intended.

---

## Step 3 · What new technologies are required

| Technology | Why THIS feature needs it |
|-----------|---------------------------|
| **SQLite** | a file-based relational DB — zero setup, perfect for dev; later swap for Postgres |
| **SQLModel** | SQLAlchemy + Pydantic in one: our schemas become tables (or table rows) |
| **Sessions / Engine** | the DB connection pattern FastAPI expects (one session per request) |
| **Alembic** | schema migrations — so changing our table later doesn't destroy data |
| (reuse) `httpx`, `config`, `Depends` | all already in place |

**Redis is NOT here.** A database solves "cache on disk across restarts." Redis (Feature 5) solves "fast shared in-memory cache + counters." We add it when we outgrow SQLite — which we will, because SQLite writes are slower and single-writer.

---

## Step 4 · Teach only the required concepts

### 4.1 Tables, rows, primary keys

A database = **tables** (like spreadsheets). A **row** = one record. A **primary key** = the unique column identifying a row.

```
PROFILE_CACHE
─────────────
username (PK)     profile_json    fetched_at
torvalds          {...}           2026-08-06T12:00:00Z
```

`username` as primary key is natural here: one cache row per user, and "get by username" is our only lookup.

### 4.2 SQLModel: table = a class

SQLModel lets one class be **both** a Pydantic schema and a DB table:

```python
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class ProfileCache(SQLModel, table=True):
    username: str = Field(primary_key=True)
    profile_json: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- `table=True` says "this is a real table, not just a schema."
- `Field(primary_key=True)` makes `username` the unique key (upsert target).
- Store the whole portfolio as **one JSON column** — simplest, and it's what a cache needs. (Normalizing every repo into its own table is over-engineering *for a cache*; we'd normalize if repos were the source of truth.)

### 4.3 Engine + Session (the connection pattern)

- **Engine** = one connection pool for the app (create once).
- **Session** = a single "unit of work" for one request (create per request, close in `finally`).

```python
# app/core/db.py
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=settings.debug, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
```

- `check_same_thread=False` is a SQLite quirk: FastAPI may use threads; SQLite by default forbids cross-thread use.
- `get_session` with `yield` = **FastAPI dependency**: enter → open session, exit → auto-closes. That's the "one session per request, always cleaned up" pattern.

### 4.4 Upsert ("insert or update")

```python
from sqlmodel import select

def save(session: Session, username: str, profile_json: str):
    row = session.get(ProfileCache, username)
    if row is None:
        row = ProfileCache(username=username, profile_json=profile_json)
        session.add(row)
    else:
        row.profile_json = profile_json
        row.fetched_at = now()
    session.commit()
```

"Upsert" = update the row if it exists, else insert. Two-line logic, huge win for cache semantics.

### 4.5 Migrations (Alembic) in one breath

`create_all` builds tables from scratch but **can't evolve them**. Alembic writes migration files:

```bash
alembic init migrations            # once
alembic revision --autogenerate -m "create profile_cache"
alembic upgrade head
```

Now when we add a column (Feature 7 adds `views`), we generate a *new* migration that preserves existing rows. Migrations are how real teams ship schema changes safely. Postgres later = just `DATABASE_URL` change.

---

## Step 5 · Implementation plan

```
app/
├── core/
│   └── db.py                 # engine + get_session
├── models/
│   └── profile_cache.py      # ProfileCache table
├── repositories/
│   └── profile_cache.py      # save / get / is_fresh (the ONLY file that runs SQL)
├── services/
│   └── profile.py            # now: check cache → fetch → save (orchestrates)
└── routers/github.py         # unchanged: still just calls the service
```

| File | Responsibility | Why now |
|------|----------------|---------|
| `core/db.py` | engine + session dependency | the DB connection layer every DB user needs |
| `models/profile_cache.py` | the table definition | the schema |
| `repositories/profile_cache.py` | SQL access (get/save) | keeps SQL out of services & routers (one place to swap DB later) |
| `services/profile.py` | cache-or-fetch orchestration | business flow lives here |

**Why a `repositories/` layer?** The service now does two things: talk to GitHub (client) *and* talk to DB (repository). If we put raw SQL in the service, swapping SQLite→Postgres (Feature 12) would mean touching business logic. The repository owns the SQL; the service owns the *policy* ("if fresh, serve; else fetch").

---

## Step 6 · Implement gradually

### Piece 1 — add deps

```txt
sqlmodel==0.0.22
alembic==1.14.0
```

### Piece 2 — config gets a DB URL

```python
# app/config.py (add)
class Settings(BaseSettings):
    ...
    database_url: str = "sqlite:///./github_portfolio.db"
```

SQLite URL syntax: `sqlite:///<path>`. Postgres later: `postgresql+psycopg://user:pass@host/db`.

### Piece 3 — the model

```python
# app/models/profile_cache.py
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class ProfileCache(SQLModel, table=True):
    username: str = Field(primary_key=True)
    profile_json: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Piece 4 — repository

```python
# app/repositories/profile_cache.py
import json
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from app.models.profile_cache import ProfileCache

FRESHNESS = timedelta(minutes=15)

def get_cached(session: Session, username: str):
    row = session.get(ProfileCache, username)
    if row is None:
        return None
    if datetime.now(timezone.utc) - row.fetched_at > FRESHNESS:
        return None                 # stale → treat as miss
    return json.loads(row.profile_json)

def save(session: Session, username: str, profile: dict):
    row = session.get(ProfileCache, username)
    if row is None:
        session.add(ProfileCache(username=username, profile_json=json.dumps(profile)))
    else:
        row.profile_json = json.dumps(profile)
        row.fetched_at = datetime.now(timezone.utc)
    session.commit()
```

**Why `json.loads`/`json.dumps`:** SQLite has no "dict" type; we store the portfolio as a JSON **string** and parse when reading. Simple, and matches "cache the whole answer" semantics.

### Piece 5 — service orchestrates cache-or-fetch

```python
# app/services/profile.py
from app.repositories.profile_cache import get_cached, save

class ProfileService:
    def __init__(self, client, session):      # now needs a DB session too
        self.client = client
        self.session = session

    async def get_portfolio(self, username: str) -> Portfolio:
        cached = get_cached(self.session, username)
        if cached is not None:
            return Portfolio.model_validate(cached)   # cache HIT
        user_raw = await self.client.get_user(username)          # cache MISS:
        repos_raw = await self.client.get_repositories(username) # fetch...
        portfolio = _compute_portfolio(user_raw, repos_raw)
        save(self.session, username, portfolio.model_dump())     # ...and store
        return portfolio
```

- `Portfolio.model_dump()` → dict; `Portfolio.model_validate(cached)` → back to model. Pydantic round-trips for free.
- `save(...)` happens **only on a miss** (avoid pointless writes).
- Notice the *policy* lives here: "if fresh → hit; else fetch+save." That's exactly what a cache is.

### Piece 6 — wire the session dependency

```python
# app/routers/github.py
from app.core.db import get_session
from sqlmodel import Session

def get_service(
    client: GitHubClient = Depends(get_client),
    session: Session = Depends(get_session),
) -> ProfileService:
    return ProfileService(client=client, session=session)
```

Run `alembic upgrade head` (or a dev `create_db_and_tables()` for now — migrations come in Step 9). Restart uvicorn, hit `/users/torvalds/portfolio` twice, and **watch the log**: request 1 does the GitHub calls; request 2 answers in ~5ms from SQLite.

> **Your turn:** implement pieces 1–6. Add a temporary `print("HIT"/"MISS")` in the service; verify a HIT on the second request. Then commit.

---

## Step 7 · Request lifecycle (two requests, two paths)

```
Request 1 (MISS)                       Request 2 (HIT)
Browser → GET /users/torvalds          Browser → GET /users/torvalds
  │ uvicorn → FastAPI                    │ uvicorn → FastAPI
  │ Depends: ProfileService(gh, db)      │ Depends: same service
  ▼                                      ▼
service.get_portfolio                    service.get_portfolio
  ├─ cache: get_cached → None            ├─ cache: get_cached → dict ✔
  ├─ client.get_user → GitHub            └─ Portfolio.model_validate(...)
  ├─ client.get_repositories → GitHub    └─ 200 JSON  (no GitHub calls!)
  ├─ _compute_portfolio(...)
  ├─ repository.save(...)   (SQLite)
  └─ 200 JSON
```

The second path never touches GitHub — that's the entire point.

---

## Step 8 · Alternatives

| Choice | We use | Alternatives | When pros pick them |
|--------|--------|--------------|---------------------|
| Store whole portfolio as JSON column | single row per user | one row per repo (normalized) | when repos are queried independently (analytics), you'd normalize |
| SQLite now | simplest | Postgres from day one | when you know you'll need concurrent writes/locking/many rows early |
| Cache freshness 15 min | constant | configurable TTL per data type | trending data needs shorter TTL; profiles longer |
| Repository layer | yes | SQL inline in service | inline is fine for tiny apps; layer pays off the moment you switch engines or test |

**The big one — "cache as a DB table" vs "Redis":** a DB cache survives restarts and is free to run; Redis is *much* faster and shared across processes. Feature 5 will show the pain that pushes us to Redis (SQLite writes lock the DB; cache reads slow down as the table grows; and we need counters that Redis does atomically).

---

## Step 9 · Refactor as a senior

1. **Create `create_db_and_tables()` + lifespan** (run on startup for dev), then wire **Alembic** for real migrations (the "how to change schema without data loss" lesson).
2. **Separate `CacheStore` protocol/interface** so the repository is swappable for a Redis one in Feature 5 with *zero* service changes:

```python
# app/repositories/base.py
class ProfileCacheStore(Protocol):
    def get_cached(self, username: str) -> dict | None: ...
    def save(self, username: str, profile: dict) -> None: ...
```

The service only depends on the *interface*. Feature 5 swaps implementations — that's **Dependency Inversion** in action, learned by doing.

---

## Step 10 · Exercises

1. Add a **stale-but-serve** mode: if the cache is old but < 6h, return it anyway and log "STALE" (this prefigures stale-while-revalidate in Feature 5).
2. Make `FRESHNESS` come from **config** (`settings.profile_cache_minutes`), not a hard-coded constant.
3. **Simulate the rate-limit pain**: comment out the cache, hit `/portfolio` 61 times, watch the first `429`. Uncomment, hit 100 times — count how many reach GitHub (should be ~1).
4. Run an **Alembic** migration: `alembic revision --autogenerate -m "create profile_cache"`, `upgrade head`, and confirm the table exists (`sqlite3 github_portfolio.db ".tables"`).

### Review yourself
- [ ] Does a second request for the same user skip GitHub entirely (check log)?
- [ ] Is all SQL confined to `repositories/`?
- [ ] Could you switch to Postgres by changing only `DATABASE_URL` + deps? (That's the goal of the layering.)
- [ ] Are times UTC, and freshness comparisons timezone-aware?

---

**Next feature:** [Feature 5 — Fast + Polite Caching with Redis](05-f5-redis.md). SQLite works but writes lock and reads slow as data grows — and we still have no way to rate-limit *our own* API. Time for an in-memory, shared cache: Redis.
