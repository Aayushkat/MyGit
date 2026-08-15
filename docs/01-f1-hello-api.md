# Feature 1 — Hello, Portfolio API

> **Milestone:** a server that answers requests. Nothing more. The whole project grows from this one small thing.

---

## Step 1 · What are we building today

A tiny FastAPI application with **one endpoint**: `GET /hello` that returns JSON like:

```json
{ "message": "Hello, portfolio!" }
```

And a **root page** `GET /` that returns a plain HTML page with a heading.

That's it. That's the entire feature. It looks trivial — and it is — but it is the *first HTTP request that your code answers*, and from here every feature is "more routes, more layers."

---

## Step 2 · Why do we need this feature

Before you can search a GitHub username, render a portfolio, or authenticate anyone, you need:

1. A **running server** that listens for requests.
2. A way to define **what URL does what** (routing).
3. Proof that **your code** — not a tutorial — can receive a request and send back a response.

Everything else in the project is built *on top of* this skeleton. If this feels too easy, good — it should. The point of Feature 1 is to walk the **request lifecycle** once, slowly, so every later feature is just "add a route + add logic."

---

## Step 3 · What new technologies are required

Exactly three runtime pieces, because that's all this feature needs:

| Technology | Why this feature needs it |
|-----------|---------------------------|
| **Python** | the language we chose for the backend |
| **FastAPI** | the framework that turns "a URL" into "a Python function" |
| **uvicorn** | the server that actually listens on a port and speaks HTTP |

Plus two **workshop tools**. They never ship to users, but a professional repo has them from day one:

| Tool | Why it exists |
|------|---------------|
| **uv** | package + environment manager — the industry default in 2026: one fast tool that replaces `venv` + `pip`, with a lockfile for reproducibility |
| **ruff** | linter **and** formatter — catches real mistakes and ends style debates, configured in `pyproject.toml` |

That's it. No database, no Redis, no Docker, no frontend. When a future feature needs those, *that* feature will introduce them.

> This is the core discipline: **resist adding technology the current feature doesn't need.** Senior engineers add tools when a problem appears, not preemptively.

---

## Step 4 · Teach only the required concepts

### 4.1 The three moving parts

```
uvicorn ── listens on a TCP port, speaks HTTP ──►  FastAPI ──► your Python function
 (server)                                          (framework)   (your code)
```

Think of it as a restaurant:
- **uvicorn** is the building with the door. It accepts customers (requests) and has waiters who take orders.
- **FastAPI** is the menu + the kitchen rules: it reads the order (the URL), checks it against the menu (your routes), and calls the right chef (your function).
- **Your function** is the chef: it makes the dish (the response) and hands it back.

### 4.2 What "a route" is

A route = a **URL pattern + an HTTP method** that maps to a function:

```python
@app.get("/hello")
def hello():
    return {"message": "Hello, portfolio!"}
```

- `@app.get("/hello")` says: *"when a `GET` request arrives at path `/hello`, run `hello()`."*
- The function returns a Python dict. FastAPI **automatically turns it into JSON** and wraps it in an HTTP response with status `200`.

### 4.3 What "GET" is

HTTP has verbs (Chapter 0 already set the stage). `GET` means *"retrieve something, change nothing."* It's the right verb for a page that just shows data. Feature 2's profile search stays `GET` too (fetching is still retrieval); we'll meet `POST` when accounts and saved portfolios arrive in Feature 6 — `POST` is for requests that *create or change* something on the server.

That distinction has a name: `GET` is **safe** (no side effects) and **idempotent** (calling it twice is the same as once). Browsers, proxies, and caches *rely* on this — they will happily prefetch or replay a `GET`. Put a side effect behind a `GET` and something in the chain will eventually trigger it when you didn't ask. This is the first API-design rule you'll carry through all thirteen features.

### 4.4 Why `main.py`?

When you run `uvicorn app.main:app`, uvicorn needs to find the application object. The path `app.main:app` means:
- `app` = the package/folder named `app`
- `main` = the module `app/main.py`
- `app` = the `FastAPI()` instance inside that module

So `main.py` is a **convention** — "the entry point that assembles the application." Name it `main.py` and uvicorn's `:app` syntax stays obvious.

---

## Step 5 · Implementation plan

We need this structure:

```
github_portfolio/
├── app/
│   ├── __init__.py      # makes the folder a Python package
│   ├── main.py          # creates the FastAPI app, holds routes
├── requirements.txt     # the dependencies this feature needs
├── .gitignore           # don't commit __pycache__, .env, etc.
```

| File | Responsibility |
|------|----------------|
| `app/__init__.py` | empty file; marks `app` as a package so `app.main` imports work |
| `app/main.py` | the app object + this feature's two routes |
| `requirements.txt` | `fastapi` and `uvicorn` (pinned-ish) |

> **Why not put every future route in main.py?** You will — for exactly one feature. When routes grow (Feature 2+), we'll refactor them into `routers/`. That's Step 9's job: *refactoring*, done when it's needed.

---

## Step 6 · Implement gradually

### Piece 1 — the dependency list

```txt
# requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
```

Pin versions so your project is reproducible. `uvicorn[standard]` adds the fast `uvloop` event loop and useful extras.

### Piece 2 — the package marker

Create `app/__init__.py` — **empty**. Its only job is to make `app` a Python package.

### Piece 3 — the app and the first route

Create `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="GitHub Portfolio")

@app.get("/hello")
def hello():
    return {"message": "Hello, portfolio!"}
```

**Why each line:**
- `from fastapi import FastAPI` — bring in the framework.
- `app = FastAPI(...)` — this **is** the ASGI application object. When uvicorn runs `app.main:app`, this object is what it finds and calls for every request. The `title` shows up in the auto-generated docs at `/docs`.
- The decorator + function = one route.

### Piece 4 — install and run

```bash
# Windows (PowerShell), from the project folder
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- `python -m venv .venv` creates an isolated environment (never install project deps into your global Python).
- `pip install -r requirements.txt` installs exactly our two deps.
- `uvicorn app.main:app --reload` starts the server on port 8000. `--reload` restarts it whenever you save a `.py` file (dev convenience; **never** use it in production).

Now open:
- `http://127.0.0.1:8000/hello` → JSON
- `http://127.0.0.1:8000/docs` → interactive API docs FastAPI generated **for free** from our route.

### Piece 5 — add the root page

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GitHub Portfolio")

@app.get("/hello")
def hello():
    return {"message": "Hello, portfolio!"}

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>GitHub Portfolio</h1><p>This will become the landing page.</p>"
```

- `HTMLResponse` tells FastAPI "this returns HTML, not JSON." Return value is a plain string of HTML.
- The landing page will grow into the real search page in Feature 2.

> **Your turn (per the rules, you write it):** create the files, run the server, hit `/hello` and `/`. Then **commit** this to git (`git init`, add, commit). Git becomes second nature only by using it this early.

---

## Step 7 · The request lifecycle (say it out loud)

When you type `http://127.0.0.1:8000/hello`:

```
Browser                      Server
   │                            │
   │  GET /hello  HTTP/1.1 ────► │  uvicorn listens on TCP port 8000
   │  Host: 127.0.0.1:8000      │  parses the HTTP request
   │                            │  passes it to FastAPI
   │                            │  FastAPI matches route GET /hello
   │                            │  calls hello()
   │                            │  turns {"message": ...} into JSON
   │  ◄─ HTTP/1.1 200 OK ─────── │  Content-Type: application/json
   │  Content-Type: application/json
   │  {"message":"Hello, portfolio!"}
   ▼
 browser renders/prints the JSON
```

The **status line** `HTTP/1.1 200 OK` and the **header** `Content-Type: application/json` and the **body** `{...}` — that's the whole HTTP conversation. FastAPI handled the details; you must be able to *describe* them.

---

## Step 8 · Alternatives (and when professionals pick them)

| Alternative | What it is | When a professional picks it |
|-------------|-----------|------------------------------|
| **Django** | a batteries-included framework (ORM + admin + more) | when the app is mostly CRUD/forms and they want everything built-in |
| **Flask** | a micro-framework, minimal | tiny services, or when they want to wire everything by hand |
| **FastAPI** (ours) | modern, async, auto-validating | API-first apps with async I/O — exactly ours |
| **Node/Express, Go, Rust** | other ecosystems | different performance/team requirements |

We chose **FastAPI** because: Python (your learning target), async-native (our GitHub calls later will need it), and it auto-validates + auto-documents (perfect for learning correct API design).

> There's no "right" answer in architecture — there are **trade-offs**. Noting the alternatives is the habit that makes you senior.

---

## Step 9 · Refactoring (how a professional improves it)

Right now, routes live in `main.py`. That's correct **for one feature**. Before adding Feature 2, split routes into a router:

```python
# app/routers/hello.py   (new)
from fastapi import APIRouter

router = APIRouter()

@router.get("/hello")
def hello():
    return {"message": "Hello, portfolio!"}
```

```python
# app/main.py (refactored)
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import hello

app = FastAPI(title="GitHub Portfolio")
app.include_router(hello.router)

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>GitHub Portfolio</h1>"
```

**Why refactor now:**
- `main.py` should be a thin **assembler** — it wires routers together.
- Each feature's routes live in its own file → readable, reviewable, mergeable.
- FastAPI "discovers" the routes via `include_router` — no magic.

**This is the layered-structure habit** you'll deepen with services/repositories in Feature 2+.

---

## Step 10 · Exercises (implementation, not theory)

1. Add a route `GET /health` returning `{"status": "ok"}` (you'll reuse it for Docker health checks later).
2. Add `GET /users/{username}` returning `{"username": username, "followers": 0}` — with the username coming from the URL path. (This is *exactly* the shape Feature 2 will make real.) If it returns `422` for an empty username, you've correctly hit FastAPI's validation — read the error body.
3. **Refactor** the `/hello` route into `app/routers/hello.py` (Step 9), confirm the app still runs, and commit.

### Review yourself like a senior
- Did you pin versions? ✅/❌
- Is the venv active and `.venv` in `.gitignore`? ✅/❌
- Can you explain (out loud) what `uvicorn app.main:app --reload` does, word by word? ✅/❌

---

**Next feature:** [Feature 2 — GitHub Profile Search](02-f2-github-search.md). We need real data — enter httpx and the GitHub API.
