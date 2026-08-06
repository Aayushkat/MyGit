# Feature 11 — Test Everything (pytest)

> **Milestone:** we have 10 features' worth of moving parts. Now we lock them down so future changes don't silently break them. Testing enters because the project has reached the point where "just try it in the browser" is no longer enough.

---

## Step 1 · What are we building today

A **pytest suite** covering our app:

1. **Unit tests** for the pure transforms (language %, years-active, portfolio building).
2. **Integration tests** hitting our endpoints through FastAPI's `TestClient` — with a **fake GitHub client** so no real network calls happen.
3. **Auth tests** (register, login, protected routes).
4. **A taste of TDD**: write a failing test first for a small new behavior, then make it pass.

```bash
pytest -q
# ......................                             22 passed
```

---

## Step 2 · Why do we need this feature

The app now has: GitHub calls, caching, rate limits, DB writes, auth, background tasks, exports. Every future change (a new field, a refactor, a config tweak) can **silently break** any of them. The cost of manual testing grows with every feature — but the *cost of a bug* (a 500 in production, a data leak, a wrong percentage) is much worse.

**Testing is how professionals make change safe.** The rule: *a feature isn't done until its tests pass.* We do it *now* — when the regression risk is real — not as an afterthought.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|-----------|---------------------------|
| **pytest** | the test runner (fixtures, assertions, parametrize) |
| **FastAPI `TestClient`** | hit endpoints in-process (no server, no port) |
| **`dependency_overrides`** | swap real GitHub client / DB session for fakes |
| **Fixtures (`conftest.py`)** | shared setup: app, session, fake client |

**The payoff of all our layering since F2:** because routers get `GitHubClient` via `Depends`, and services get repos via constructors, we can inject a **fake** and test everything without network or a real database. F2's "testable boundaries" comment has come due.

---

## Step 4 · Teach only the required concepts

### 4.1 TestClient — our app, no server

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
resp = client.get("/api/v1/users/torvalds/portfolio")
assert resp.status_code == 200
```

`TestClient` (Starlette) drives the **ASGI app in-process** using `httpx` under the hood — same request lifecycle, no port. Fast, deterministic.

### 4.2 Fixtures — shared setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:      # context manager runs lifespan
        yield c
```

### 4.3 The fake GitHub client (DI pays rent)

Because the router builds its service through `Depends(get_service)`, we can **override** it:

```python
# tests/conftest.py
from app.routers.github import get_service

class FakeGitHub:
    async def get_user(self, username):
        if username == "missing":
            from app.clients.github import GitHubError
            raise GitHubError(404, "User not found")
        return {"login": username, "name": "Test", "avatar_url": "u",
                "followers": 1, "following": 2, "public_repos": 3}

    async def get_repositories(self, username):
        return [{"name": "r", "language": "Python", "stargazers_count": 5, "forks_count": 1, "fork": False}]

@pytest.fixture(autouse=True)
def fake_github(monkeypatch):
    def _make_service(*args, **kwargs):
        return ProfileService(client=FakeGitHub(), session=None)
    app.dependency_overrides[get_service] = _make_service
    yield
    app.dependency_overrides.clear()
```

Now `/users/{username}/portfolio` runs through the **real router + real service logic**, but with **no network** and **no DB**. That's an *integration test* of our app with a *fake boundary* — the professional sweet spot.

> **Why `dependency_overrides` and not a library like `responses`/`respx`?** Overriding our *own* boundary (the `GitHubClient` we built) tests *our* code without mocking httpx internals. Both work; overriding our own seam is more robust and teaches DI.

### 4.4 Unit tests for pure transforms

```python
# tests/test_transform.py
from app.services.profile import compute_portfolio

def test_language_percentages():
    p = compute_portfolio(
        {"login": "x", "avatar_url": "u", "followers": 0},
        [{"name": "a", "language": "Python", "stargazers_count": 1, "forks_count": 0, "fork": False},
         {"name": "b", "language": "Python", "stargazers_count": 1, "forks_count": 0, "fork": False},
         {"name": "c", "language": "Go",     "stargazers_count": 1, "forks_count": 0, "fork": False}],
    )
    langs = {l.name: l.percentage for l in p.top_languages}
    assert langs["Python"] == 67
    assert langs["Go"] == 33
    assert sum(l.percentage for l in p.top_languages) == 100   # rounding fix
```

Pure functions = the cheapest, most reliable tests in the suite. **This is exactly why we extracted the transform in F3.**

### 4.5 Testing error paths

```python
def test_missing_user_404(client):
    r = client.get("/api/v1/users/missing/portfolio")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "GITHUB_ERROR"

def test_bad_username_422(client):
    r = client.get("/api/v1/users/../portfolio")
    assert r.status_code == 422
```

Each error branch is one test — that pins the API contract (F2/F4 error shape) forever.

---

## Step 5 · Implementation plan

```
tests/
├── conftest.py            # client fixture, fake GitHub, DB overrides
├── test_transform.py      # unit: language %, years, rounding
├── test_portfolio.py      # integration: /portfolio 200/404/422
├── test_auth.py           # register/login/protected
└── test_export.py         # PNG headers, streaming
```

| File | Why |
|------|-----|
| `conftest.py` | the shared fixtures (the seams we built pay off) |
| `test_transform.py` | the pure math — fastest, most valuable |
| `test_portfolio.py` | the happy path + error contract end-to-end |

---

## Step 6 · Implement gradually

### Piece 1 — add pytest

```txt
pytest==8.3.4
```
```bash
pytest -q
```

### Piece 2 — `conftest.py` with the fake + overrides

(see 4.3 — write it yourself.)

### Piece 3 — tests for the happy path + errors

(see 4.4 / 4.5 — write them.)

### Piece 4 — auth tests

```python
def test_register_then_protected(client):
    r = client.post("/auth/register", json={"username": "bob", "password": "secret1"})
    assert r.status_code == 201
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    r2 = client.get("/portfolios", headers=headers)
    assert r2.status_code == 200

def test_protected_without_token(client):
    assert client.get("/portfolios").status_code == 401
```

### Piece 5 — a TDD cycle (write the test first)

Pick a small new behavior — e.g. "**exclude forks from total_stars**." Write `test_forks_not_counted`, watch it fail (red), implement the guard in the transform, watch it pass (green). That 5-minute loop *is* TDD.

> **Your turn:** write the whole suite, run `pytest -q`, and fix anything that fails (that's the point — the failures teach you what your code actually does).

---

## Step 7 · Request lifecycle (during a test)

```
pytest → TestClient(app)
  │ calls client.get("/api/v1/users/torvalds/portfolio")
  │  → ASGI app in-process (no socket!)
  │     → FastAPI: dependency_overrides[get_service] = fake_service
  │     → service.get_portfolio → FakeGitHub (no httpx!) → transform → Portfolio
  │     → response_model → JSON
  │ returns Response; pytest asserts status/body
```

The test exercises the **entire** request path except the real GitHub call — which is exactly what you want: *our code* tested, external world stubbed.

---

## Step 8 · Alternatives

- **`respx`/`responses`**: mock httpx at the HTTP level — useful when you want to test the *client itself* against canned GitHub responses. Complementary, not a replacement.
- **Real test DB**: for DB tests (Feature 12/13) use a **separate SQLite in-memory/temp file** via engine override — never the dev `.db`.
- **End-to-end (Playwright)**: browser-level tests for the frontend — slow, brittle, few. Later, if needed.

---

## Step 9 · Refactor as a senior

- **Parametrize** the error contract: `@pytest.mark.parametrize("path,status", [...])` → one test, many cases.
- **Time-inject** for `years_active` (pass `now` in) so the test is deterministic.
- **Fixtures with scopes**: `@pytest.fixture(scope="session")` for the app; function-scoped for DB.
- **Add DB tests**: an in-memory engine fixture, test `save`/`get_cached`/`increment`.

---

## Step 10 · Exercises

1. **Test the cache**: with a fake clock (monkeypatch), verify a second call within TTL is a HIT (log "HIT"), and past-TTL is a MISS (refetches).
2. **Test rate limiting**: hit the endpoint 31 times → 31st is `429` with `Retry-After`.
3. **Test the PNG export**: assert `Content-Type: image/png`, `Content-Disposition`, and that bytes decode as a real image (`PIL.Image.open`).
4. **Test auth**: wrong password → 401; duplicate username → 409; expired token → 401.
5. **TDD a new metric** ("count stars of top 5 repos") — test first, then implement.

### Review yourself
- [ ] Do tests ever hit the real GitHub API or your real `.db`? (They must not.)
- [ ] Are the pure transforms covered? (Highest value.)
- [ ] Are the error branches (404/422/401/429) pinned?
- [ ] Can you run the whole suite with one command and get a green? Then commit.

---

**Next feature:** [Feature 12 — Ship It](12-f12-docker.md). Tests are green; now the app must run anywhere — and it must not die on day one. Docker + docker-compose + CI enter because deployment forces them.