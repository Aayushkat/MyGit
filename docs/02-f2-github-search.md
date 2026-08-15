# Feature 2 — GitHub Profile Search

> **Milestone:** our endpoint returns *real* GitHub data. This is where the project stops being an empty shell.

---

## Step 1 · What are we building today

Upgrade `GET /users/{username}` so it actually fetches a real GitHub profile and returns real fields:

```json
{
  "login": "torvalds",
  "name": "Linus Torvalds",
  "bio": "...",
  "avatar_url": "https://avatars.githubusercontent.com/...",
  "followers": 12345,
  "following": 3,
  "blog": "https://...",
  "company": "Linux Foundation"
}
```

Plus a simple HTML **search page** at `/` that lets you type a username and see the result.

---

## Step 2 · Why do we need this feature

This is the *core* of the whole app: look up any GitHub user and show their info. It also forces us to learn the three things every real backend does constantly:

1. **Talk to another API** (GitHub) — in our case the request *leaves* our server. (Notice: our server becomes a **client** of GitHub's server — same HTTP, roles swapped.)
2. **Send a typed, validated response** — we must not just dump GitHub's raw JSON; we return *our* clean shape (a Pydantic `response_model`).
3. **Handle an external failure** — "user doesn't exist" (404), "GitHub rate-limited us" (403/429), etc.

Once this works, Feature 3 (repos + language stats) is just *more of the same* with a bigger payload.

---

## Step 3 · What new technologies are required

Only what this feature needs:

| Technology | Why now |
|-----------|---------|
| **httpx** | the Python HTTP client we use to call GitHub (async-compatible) |
| **async/await** | so our server can *wait* on GitHub's network call without freezing other users |
| **GitHub REST API** | the data source |
| **Pydantic `response_model`** | define + validate the exact JSON we return |
| **configuration (env / `.env`)** | store the GitHub token so we can turn it up or off |
| **uv** *(toolchain upgrade)* | our dependency list just grew — time to manage it the way industry does (Piece 0) |
| **ruff** *(toolchain upgrade)* | one fast linter + formatter, configured in `pyproject.toml` |

Not yet: database, Redis, auth, frontend framework. We'll have good reason for each of those when they arrive.

> Stop and notice: "database" is *not* here, even though you can picture one. We add it in Feature 4, *only when rate limits force us to.* That's the discipline.

---

## Step 4 · Teach only the required concepts

### 4.1 httpx — our backend's HTTP client

We already *served* HTTP (uvicorn). With httpx we now *make* HTTP requests. They look just like what the browser did to us:

```python
import httpx
async with httpx.AsyncClient() as client:
    r = await client.get("https://api.github.com/users/torvalds")
    data = r.json()
```

- `client.get(url)` performs a `GET` (same verb as our route).
- `r.json()` parses the response body into Python.
- `r.status_code` is the HTTP status (Chapter 0).

**Why `async`?** The call to GitHub can take ~300ms of pure waiting. In an async server, while *that* call waits, the single event loop can answer other users. If we made it blocking, **every user would freeze** whenever one GitHub call was slow. (We'll feel this concretely in Feature 4 without caching.)

### 4.2 async / await (the two-second version)

- `async def` declares a coroutine — a function that can pause.
- `await` says *"pause here until this other coroutine finishes, and let the loop do other work meanwhile."*

```python
async def fetch_user(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.github.com/users/{username}")
        return r.json()
```

The function **suspends** at `await`, the event loop runs other pending work, and when GitHub answers, `fetch_user` **resumes** where it paused. To you it looks sequential; under the hood it's concurrent.

> Don't overstudy async yet. For now the rule is: *any network/DB call in FastAPI should be `async` + `await`ed; never let it block.* We refine the how/why in later features (esp. background tasks).

### 4.3 Pydantic `response_model` — the API contract

A **response model** is a Pydantic class that defines the *exact shape* of our JSON. FastAPI validates our returned value against it before sending:

```python
from pydantic import BaseModel

class GitHubUser(BaseModel):
    login: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str
    followers: int = 0

@app.get("/users/{username}", response_model=GitHubUser)
def read_user(username: str):
    ...
```

**Why define a model instead of passing GitHub's dict straight through?**
1. **Contract** — consumers know exactly what to expect; we don't leak GitHub's whole bigger payload.
2. **Safety** — a `response_model` filters fields; we can never accidentally leak a field we didn't intend (e.g., a token).
3. **Docs** — `/docs` shows exactly this structure.

### 4.4 Configuration via environment variables

The GitHub token (and later DB URL, Redis URL, JWT secret) must be **configuration**, never hard-coded. Read them from the environment / a `.env` file:

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    github_token: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

- `github_token: str | None = None` — a token is optional. With one we get 5,000 req/hr; without, 60. This mirrors the reference app's "graceful degradation."
- The `.env` file holds real values (git-ignored); `.env.example` is committed with placeholders.

---

## Step 5 · Implementation plan

```
github_portfolio/
├── app/
│   ├── __init__.py
│   ├── main.py                 # assembles app, mounts routers
│   ├── config.py               # Settings (env)
│   ├── clients/
│   │   └── github.py           # httpx adapter: fetch_user (our HTTP to GitHub)
│   ├── schemas/
│   │   └── github.py           # Pydantic models: GitHubUserOut
│   └── routers/
│       ├── hello.py            # (from Feature 1)
│       └── github.py           # GET /users/{username}
├── requirements.txt
├── .env.example
├── .gitignore
```

| File | Responsibility |
|------|----------------|
| `clients/github.py` | **only** knows how to talk to GitHub (URLs, headers, errors). Knows nothing about HTTP routes. |
| `schemas/github.py` | the data shapes we send/receive (Pydantic). |
| `routers/github.py` | HTTP layer: takes a path param, asks a client, returns a model. |
| `config.py` | where the token and everything configurable live. |
| `main.py` | assembles app + routers (unchanged pattern). |

**Why a `clients/` layer?** The router should not know GitHub's URL or error formats. If we put `httpx` calls inside the router, later (Feature 11, tests) we can't easily fake GitHub. Keeping the GitHub call in a separate **client** lets tests swap in a fake — that's your first taste of *separation of concerns* + *dependency injection*.

---

## Step 6 · Implement gradually

### Piece 0 — requirements (add to Feature 1's list)

```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
httpx==0.28.1
pydantic-settings==2.7.1
```

### Piece 1 — config (`.env.example` + `config.py`)

```bash
# .env.example
GITHUB_TOKEN=
```

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    github_token: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

Create a real `.env` too (any value). **Commit `.env.example`, never `.env`.**

### Piece 2 — the schema

```python
# app/schemas/github.py
from pydantic import BaseModel

class GitHubUser(BaseModel):
    login: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str
    followers: int = 0
    public_repos: int = 0
```

### Piece 3 — the GitHub client

```python
# app/clients/github.py
import httpx
from fastapi import HTTPException
from app.config import settings

class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self):
        self._headers = {"Accept": "application/vnd.github.v3+json",
                         "User-Agent": "github-portfolio-app"}
        if settings.github_token:
            self._headers["Authorization"] = f"token {settings.github_token}"

    async def get_user(self, username: str) -> dict:
        async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
            r = await client.get(f"{self.BASE}/users/{username}")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if r.status_code == 403 or r.status_code == 429:
            raise HTTPException(status_code=429, detail="GitHub rate limit hit, try later")
        r.raise_for_status()
        return r.json()
```

**Why each piece matters:**
- `User-Agent` header — GitHub requires it (responses without it can be rejected).
- `timeout=15.0` — never let a slow GitHub hang our request forever (Feature chapters revisit timeouts).
- `404` → our `404`; `403/429` → `429` (GitHub rate limit); everything else → `raise_for_status()` becomes a `500`-family error.
- We return a **dict**, not a model yet — the router turns it into a model (keeps client = raw, router = typed).

### Piece 4 — the router

```python
# app/routers/github.py
from fastapi import APIRouter, Depends, Path
from app.clients.github import GitHubClient
from app.schemas.github import GitHubUser

router = APIRouter(prefix="/users", tags=["users"])

def get_client() -> GitHubClient:
    return GitHubClient()

@router.get("/{username}", response_model=GitHubUser)
async def get_user(
    username: str = Path(..., min_length=1, max_length=39, pattern=r"^[a-zA-Z0-9-]+$"),
    client: GitHubClient = Depends(get_client),
):
    data = await client.get_user(username)
    return GitHubUser(username=data["login"], name=data.get("name"),
                      bio=data.get("bio"), avatar_url=data["avatar_url"],
                      followers=data.get("followers", 0),
                      public_repos=data.get("public_repos", 0))
```

**Why:**
- `Path(...)` validates the username (1–39 chars, alphanumeric + hyphen) → invalid gives `422`. That's the *username validation* discussed in the reference.
- `Depends(get_client)` is **dependency injection**: the router *declares* it needs a `GitHubClient`, FastAPI builds it. (In Feature 11 you'll replace this with a fake in tests — that's the payoff.)
- `async def` everywhere we await — this whole endpoint *yields* to the loop while GitHub responds.

### Piece 5 — mount the router + a search page

```python
# app/main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import github  # and hello

app = FastAPI(title="GitHub Portfolio")
app.include_router(github.router)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Search a GitHub profile</h1>
    <form action="/users/" method="get">
      <label>Username <input name="q"></label>
      <button>Go</button>
    </form>
    """
```

Wait — `/users/q/{username}` is not a search yet. We'll convert this form to use the frontend in Feature 9 (HTML/CSS/JS). For THIS feature, just verify with `curl`/browser that `/users/torvalds` returns real JSON.

> **You write it.** Create the files, reload uvicorn, hit:
> - `http://127.0.0.1:8000/users/torvalds` → real JSON
> - `http://127.0.0.1:8000/users/definitely-not-a-real-user-123` → `404` with our JSON error
> - an invalid string (`/users/a..b`) → `422`
> Check `/docs` — your endpoint with its input/response models is auto-documented.

---

## Step 7 · The request lifecycle (recite it)

```
Browser  ──►  GET /users/torvalds
                │ uvicorn parses HTTP
                ▼
           FastAPI matches route /users/{username}
                ├─ Path validation (Pattern, max_length …)  (or 422)
                ├─ Depends(get_client) → builds a GitHubClient
                ▼
           router.get_user(username)
                └─ await client.get_user("torvalds")       ← now *we* are a CLIENT
                     └─ httpx GET https://api.github.com/users/torvalds
                          ▲  (outbound call; our server waits asynchronously)
                          │ GitHub returns 200 JSON
                          └─ we map into GitHubUser
                ▼
           response_model validates & serializes → JSON
                ▼
           HTTP/1.1 200 OK  Content-Type: application/json  body:{...}
                ▼
           Browser renders the parsed JSON / shows it
```

Two full HTTP conversations happen: **you↔us** and **us↔GitHub**. Walk that fact out loud — the "recursion" that trips up every junior is exactly this.

---

## Step 8 · Alternatives

| Decision | Our choice | Alternatives | When pros pick alternatives |
|----------|-----------|--------------|------------------------------|
| HTTP client | `httpx` | `requests`, `aiohttp` | `requests` (sync-only) for simple scripts; `aiohttp` for websockets |
| Validation | Pydantic `response_model` | none/`dict` | returning raw dicts is fine for internal endpoints, but weak as a public contract |
| Calling GitHub path | a `clients/` adapter | inline `httpx` in router | inlining = faster to write, but unmockable & tangled (we refactor toward adapters) |
| Token optional vs required | optional (degrade) | required | required token is simpler but forces every user to configure |

**The recurring trade-off:** convenience-now vs. adaptability-later. A `clients/` layer is slightly more files now, but it's what lets us test (F11) and cache (F4) cleanly.

---

## Step 9 · Refactor as a senior

**Add a small custom exception for GitHub errors** instead of scattering `HTTPException` in the client. This lets the app's error shape stay consistent:

```python
# app/clients/github.py (improved)
class GitHubError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

...

if r.status_code == 404:
    raise GitHubError(404, "User not found")
if r.status_code in (403, 429):
    raise GitHubError(429, "GitHub rate limited")
r.raise_for_status()
return r.json()
```

```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse
from app.clients.github import GitHubError

@app.exception_handler(GitHubError)
async def github_error_handler(request: Request, exc: GitHubError):
    body = {"error": {"code": "GITHUB_ERROR", "message": exc.message}}
    return JSONResponse(status_code=exc.status, content=body)
```

**Why:** now *every* GitHub failure produces the SAME JSON error shape. That sets up Feature 9's frontend to handle one uniform error format. A senior standardizes error shapes before the frontend is built.

Also: **put all the schemas + client together** is already done. Keep them one-responsibility.

---

## Step 10 · Exercises (implementation)

1. Add `GET /users/{username}/repos` that returns a typed list (start with 1 field: `name`). You'll hit GitHub's `/users/{u}/repos`.
2. Make the client handle **timeouts cleanly**: set `timeout=10`, and on `httpx.TimeoutException` raise a `GitHubError(504-ish)`.
3. In the router, currently you copy fields by hand into `GitHubUser(...)`. Refactor by adding a **classmethod** `GitHubUser.from_raw(data)` on the schema — cleaner mapping.

### Review yourself
- [ ] Is the token only ever read from config (never hard-coded)?
- [ ] Do 404/429/422 each return a *different, correct* status code with a JSON body?
- [ ] Could you swap GitHub for another API without touching the router? (The `clients/` file limits the blast radius.)

---

**Next feature:** [Feature 3 — Repositories & Language Stats](03-f3-repos-languages.md). Now we want the full portfolio — repos, languages, counts — and we hit the "transformation" and "sorting" problems.