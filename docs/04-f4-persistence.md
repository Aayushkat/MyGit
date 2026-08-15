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

We'll store it in **SQLite** via **SQLAlchemy 2.0's async ORM**, and manage schema changes with **Alembic** so we can later move to PostgreSQL without tears.

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
| **SQLite** (via **aiosqlite**) | a file-based relational DB — zero setup, perfect for dev; the async driver keeps the event loop free; later swap for Postgres |
| **SQLAlchemy 2.0 (async ORM)** | the industry-standard Python ORM: typed `Mapped[]` models, `async_sessionmaker` sessions |
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

**What a database actually is, physically.** When you write `table=True`, a real file on disk gets structures that let the engine find rows fast. Three behaviors fall out of the mechanics:

- **Rows live in pages inside a B-tree index.** "The table" and "the index on the primary key" are the *same* structure in SQLite — that's why primary-key lookups (`session.get`) are fast, and why adding an index on `username` in Feature 6 means "making another B-tree." A `WHERE username = ?` does a tree walk (O(log n)), not a scan.
- **SQLite is a single file with a single writer.** One process writes at a time, under an exclusive lock (unless you enable WAL mode) — that's where "SQLite writes lock the DB" comes from. Many readers, one writer.
- **Postgres (Feature 12) is a server, not a file** — it has many writers via MVCC (readers see a snapshot; writers don't block each other). This is *precisely* why the roadmap migrates: at production scale, the single-writer file model stops scaling.

So you're not just "learning SQL" — you're learning "what a file-based single-writer B-tree does," then "what a server-based multi-writer database does." Both are databases; the difference is the concurrency model.

### 4.2 SQLAlchemy 2.0: table = a class

SQLAlchemy's **declarative** style maps a Python class to a table. In 2.0, the mapping is *typed*: `Mapped[str]` declares both the Python type and the column type, and `mapped_column(...)` carries the DB details (primary key, defaults, constraints):

```python
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ProfileCache(Base):
    __tablename__ = "profile_cache"

    username: Mapped[str] = mapped_column(primary_key=True)
    profile_json: Mapped[str]
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
```

- Inheriting from `Base` (a `DeclarativeBase` subclass we define once) registers the class in SQLAlchemy's **metadata** — the in-memory catalog of every table the app knows about. Alembic diffs against this metadata later.
- `mapped_column(primary_key=True)` makes `username` the unique key (upsert target).
- Store the whole portfolio as **one JSON column** — simplest, and it's what a cache needs. (Normalizing every repo into its own table is over-engineering *for a cache*; we'd normalize if repos were the source of truth.)

**Two models, two jobs.** Notice we now have *two* kinds of model class in the app, and they are deliberately different libraries:

- `ProfileCache` (SQLAlchemy) describes **how data lives on disk** — a row.
- `Portfolio` (Pydantic v2) describes **how data crosses the API boundary** — a validated schema.

The bridge between them is Pydantic's round-trip: `model_dump()` walks the Pydantic fields and serializes to a plain dict; `model_validate(data)` re-runs *validation* (defaults, type checks, coercion) and rebuilds a model. So a cached dict (from `json.loads`) becomes a `Portfolio` again in one call — validation, not just re-casting. Two consequences worth naming:

- **`model_validate` raises if the dict has fields the model doesn't know** (unless `model_config = ConfigDict(extra="ignore")`). Cache a snapshot under an *older* schema, deploy a model with *fewer* fields, and the cached row throws on read. That's `schema evolution` meeting `cache invalidation` — the "version-skew" problem. Worth naming now so it's not a mystery later.
- Because the DB row and the API schema are separate classes, they can **evolve independently** — you can add a DB column without leaking it into your JSON responses, and vice versa. That separation *is* the design; it's not an accident.

**Why SQLAlchemy rather than SQLModel?** You may see tutorials use **SQLModel** — a wrapper (by FastAPI's author) that merges a SQLAlchemy table and a Pydantic schema into one class. It's genuinely convenient for small apps. Industry codebases still overwhelmingly use plain SQLAlchemy, for three reasons: (1) the "one class = both things" convenience becomes *coupling* the moment your API shape and your table shape need to diverge — which they always eventually do; (2) SQLAlchemy 2.0's typed `Mapped[]` style closed most of the ergonomic gap SQLModel existed to fill; (3) SQLAlchemy is the deeper, better-maintained dependency — every advanced feature (async, relationship loading strategies, compiled query caching) lands there first. Learning SQLAlchemy transfers to nearly every Python job; the design of this feature — repository, freshness window, JSON column — is identical either way.

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

**Engine vs Session — the actual relationship.** These two get cargo-culted the hardest:
- **Engine** ≈ a *pool of database connections*, created once per app. It doesn't talk to your code per request; it hands out connections.
- **Session** ≈ a *transaction scope* — "one unit of work." It borrows a connection from the pool, tracks changes, commits, and returns the connection.

The `yield` in `get_session` is the mechanism worth slowing down on: **code before the `yield` runs when the dependency is entered (once per request), the yielded session is injected into the endpoint, and code after the `yield` runs when the request ends — including on exceptions.** That's how "always close the session" is guaranteed both when everything works *and* when the route raises. (Teardown you can't forget by calling the wrong function.)

One real gotcha hiding here: **don't hold a session across an `await` if you can avoid it.** While a DB call blocks, a *thread* holds the connection. Await something slow mid-session and you're pinning a connection open and possibly blocking another request's writer. This constraint is why the caching repositories keep the session out of the hot path.

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

Why is this more than a convenience? It's the **non-idempotent-write problem**: if you're not careful, the same cache row gets INSERTed twice (a duplicate-PK error, or two rows), or you burn a write for no change. The two-step form encodes the actual semantics — "refresh this cache entry or create it" — and internally SQLAlchemy tracks which objects it has seen to decide `INSERT` vs `UPDATE` at `commit()`. (Databases also have a native `INSERT ... ON CONFLICT ... DO UPDATE` — same family — but the two-step version reads better at this scale.)

### 4.5 Migrations (Alembic) in one breath

`create_all` builds tables from scratch but **can't evolve them**. Alembic writes migration files:

```bash
alembic init migrations            # once
alembic revision --autogenerate -m "create profile_cache"
alembic upgrade head
```

Now when we add a column (Feature 7 adds `views`), we generate a *new* migration that preserves existing rows. Migrations are how real teams ship schema changes safely. Postgres later = just `DATABASE_URL` change.

**Why `create_all` can't evolve the schema:** it reads the model classes and creates *missing* tables — and that's all. It **never alters existing tables**; it was designed for "first time you stand up a DB." Alembic's mechanism is a *version ledger*: it keeps a special `alembic_version` table recording which revision the DB is at. `revision --autogenerate` **diffs** your model metadata against the live DB and generates code for the delta; `upgrade head` applies pending migrations in order. Adding the `views` column later is a **new migration running `ALTER TABLE ADD COLUMN` that preserves existing rows** — whereas `create_all` against an existing DB would do *nothing at all*. That's "the schema is versioned, not just declared."

> **Field note:** autogenerate is a *suggestion engine*, not a diff oracle. It misses column *renames* (usually sees a drop+add instead), and it must be *imported into `env.py`* or it "finds nothing" — the classic silent failure.

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

**The cache is a three-state machine, and only two are visible.** The state is: **MISS** (no row), **HIT** (row fresh), **STALE** (row old). This repo deliberately collapses STALE → MISS (treat old as missing). Feature 5 collapses *all* of it into a Redis TTL. The underlying, feature-spanning idea is **cache-read policy**: freshness is decided in the *policy layer* (service), while storage lives in the *repository* — that's *why* the service changes nothing when you swap storage in Feature 5. One extension to file away: **stale-but-serve** (Exercise 1) — sometimes it's better to serve a slightly old answer than gamble on a slow/hanging upstream. That "stale-while-revalidate" idea is exactly what Feature 5's Redis TTL and the reference app's KV cache are doing in another costume.

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

### Field notes — silent failures to expect

> **⚠️ Naive vs aware datetimes.** Mixing `datetime.now()` (naive) and `datetime.now(timezone.utc)` (aware) raises `TypeError: can't compare offset-naive and offset-aware datetimes`. Your `fetched_at` must be consistently aware (UTC) all the way down: at write, at the freshness comparison, and at serialization. The single most common datetime bug in this codebase.

> **⚠️ `check_same_thread=False` is a pragmatic lie, not a virtue.** It relaxes a SQLite-internal safety check (a connection created in one thread may not be used in another). FastAPI may serve requests from multiple threads, hence the flag — but it's exactly why production needs Postgres (proper per-connection thread safety), not "SQLite with the warning off."

> **⚠️ A session that's committed but not refreshed.** After `session.add(row); session.commit()`, the object can hold a stale `id`/defaults until `session.refresh(row)` re-reads them. Feature 6 routers that return an object right after commit rely on refresh. Forget it and the response shows `"id": null` while the DB row exists.

> **⚠️ `.env` location, again (same as Feature 2).** `Settings()` reads `.env` relative to the *current working directory*. Run uvicorn from a different folder and the DB URL silently defaults. If a stray `github_portfolio.db` appears somewhere unexpected, that's the sign.

> **📌 JSON-as-a-column is a *cache* decision, not a data-modeling decision.** Storing a whole portfolio as one JSON string is right when you read it all back whole. The moment you need to query *inside* the profile ("all repos from 2024 with >10 stars"), that storage is wrong — you'd normalize. "Cache = one blob, truth = normalized" is the intuition.

> **📌 Feel a cache hit in the logs.** Request 1 (MISS): hundreds of milliseconds with GitHub calls. Request 2 (HIT): single-digit milliseconds, no GitHub. If you can't distinguish them by timing, you don't have a cache — you have a slower network layer.

---

**Next feature:** [Feature 5 — Fast + Polite Caching with Redis](05-f5-redis.md). SQLite works but writes lock and reads slow as data grows — and we still have no way to rate-limit *our own* API. Time for an in-memory, shared cache: Redis.
