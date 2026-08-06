# The GitHub Portfolio Project — Mentor-Led Handbook

A **project-driven** apprenticeship handbook. We build a real GitHub-analytics web app (inspired by *CheckMyGit*) feature by feature, and every technology is introduced **only when a feature makes it necessary** — never as isolated theory.

> **The single rule of this handbook:**
> We don't say *"today we learn FastAPI routing."*
> We say *"we need a search box that returns a GitHub profile — that needs an HTTP endpoint — which means we now need to understand routing."*
> Then we build it.

---

## How each feature-chapter is structured

Every chapter follows the same 10-step rhythm (your rules, locked in):

| Step | What happens |
|------|--------------|
| 1 | **What are we building today** — one concrete feature. |
| 2 | **Why do we need this feature** — the real-world purpose. |
| 3 | **What new technologies are required** — only what this feature needs. |
| 4 | **Teach only the required concepts** — concise, tied straight back to the project. |
| 5 | **Implementation plan** — files, why each exists, responsibilities. |
| 6 | **Implement gradually** — piece by piece, each piece explained. |
| 7 | **Request lifecycle** — trace browser → HTTP → router → DI → service → GitHub/DB → JSON → UI. |
| 8 | **Alternatives** — other approaches, and when professionals choose them. |
| 9 | **Refactoring** — how a senior would improve it (SOLID, DI, layers). |
| 10 | **Exercises** — implementation tasks, never theory questions. |

You write every file. I explain every line's *why*, review your code, and point at mistakes.

---

## The Roadmap (each milestone introduces tech only when needed)

```
FEATURE-DRIVEN ROADMAP
─────────────────────────────────────────────────────────────────────────────
FEATURE 1  · Hello, Portfolio API          → Python, FastAPI, uvicorn,
│                                              routing, first GET, JSON
FEATURE 2  · GitHub profile search          → httpx, async/await, GitHub REST,
│                                              Pydantic responses, env config
FEATURE 3  · Repos + language stats         → data transforms, aggregation,
│                                              sorting, response models
FEATURE 4  · Stop hitting rate limits       → SQLite, SQLModel, sessions,
│            (persist what we fetch)            Alembic migrations
FEATURE 5  · Fast + polite caching          → Redis, cache-aside, SWR,
│            (rate limiting our API)            sliding window, 429
FEATURE 6  · Accounts & saved portfolios    → password hashing, JWT, OAuth2,
│                                              protected routes
FEATURE 7  · Share links + view counters    → URL state, background tasks,
│                                              counter flush pattern
FEATURE 8  · Export as PNG / PDF            → file + streaming responses,
│                                              Pillow, CPU→thread pool
FEATURE 9  · The real frontend              → HTML, CSS, DOM, fetch,
│            (HTML/CSS/JS)                      localStorage, XSS safety
FEATURE 10 · Rebuild frontend in React      → why frameworks exist,
│                                              components, state
FEATURE 11 · Test everything                → pytest, TestClient, fakes, DI
│                                              overrides, TDD
FEATURE 12 · Ship it                        → Docker, docker-compose,
│                                              CI (GitHub Actions), deploy
FEATURE 13 · Make it production              → logging, security hardening,
└──────────────────────────────────────────────  observability, health checks
```

**Why this order?** Each feature creates the *pain* that justifies the next technology:
- We fetch GitHub 100×/day → we *need* persistence (SQLite).
- SQLite cache is slow & not shared → we *need* Redis.
- The API is open to abuse → we *need* rate limiting.
- Users want to save portfolios → we *need* auth.
- Slow exports block responses → we *need* background tasks.

Tech is never "assigned" — it *grows out of* the project.

---

## Your tools for each chapter

- **A terminal** (PowerShell on Windows here).
- **Python 3.11+** and a virtual environment (`uv` or `venv`).
- **Git** (we'll commit after each feature — that's how you learn it).
- **A browser** with DevTools open (Network tab will become your best friend).

---

## The End-Goal Checklist

By the last feature, from memory and understanding:

- [ ] Trace a request from browser to JSON and back, naming each layer.
- [ ] Explain why we have routers, services, repositories, clients — and what breaks without them.
- [ ] Read/design a REST API: verbs, status codes, pagination, versioning.
- [ ] Write and migrate a schema (SQLite → Postgres).
- [ ] Cache correctly (Redis, SWR) and rate-limit safely.
- [ ] Authenticate with JWT and hash passwords.
- [ ] Run background jobs without blocking the event loop.
- [ ] Build a JS frontend, then migrate it to React and explain why.
- [ ] Test with pytest + TestClient + fakes.
- [ ] Containerize, CI, deploy.
- [ ] Harden and monitor it like a production app.

---

**Start here:** [Chapter 0 — Studying the Reference](00-reference-analysis.md), then [Feature 1](01-f1-hello-api.md).

*You are the engineer. I am the senior sitting next to you. Let's build.*
