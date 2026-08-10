# Feature 3 — Repositories & Language Stats

> **Milestone:** our API now returns not just who a user is, but what they've *built* — repos, stars, forks, and a language breakdown. This is the feature where "data transformation" and "computation" become first-class citizens.

---

## Step 1 · What are we building today

Extend the user endpoint so the response includes:

```json
{
  "username": "torvalds",
  "name": "Linus Torvalds",
  "total_repos": 10,
  "total_stars": 4000,
  "top_languages": [
    { "name": "C", "percentage": 70 },
    { "name": "Python", "percentage": 30 }
  ],
  "repositories": [
    { "name": "linux", "stars": 150000, "language": "C", "fork": false }
  ]
}
```

The `top_languages` list is **computed** from the repos — the first time we do "derived data" rather than just pass-through.

---

## Step 2 · Why do we need this feature

Two reasons:

1. **It's the heart of a GitHub analytics app.** "Language stats + repos + stars" is *the* value proposition (the reference app's donut chart is exactly this). Without it we're just a proxy.
2. **It forces the *transform* pattern.** Real apps rarely return raw API data. They **compute** something: aggregates, percentages, rankings. Learning to write a clean, pure, testable `transform` function now pays off forever.

---

## Step 3 · What NEW technologies are required

Almost none! That's the lesson: **computation is Python, not a new tool.**

We reuse:
- `httpx` (already have it) → to fetch the user's repos.
- `response_model` / `BaseModel` → to model `Repo`, `LanguageStat`.

The genuinely new skills are **not** technology but *technique*:
- **Aggregation** with Python's `list`, `dict`, `defaultdict`.
- **Percentage math** (with rounding — small, sneaky bug source).
- **Sorting** (sort by stars desc, by language bytes desc).

> That's a feature with no new dependency — the rarity you should recognize and savor. When the *next* feature needs SQLite/Redis, you'll see a dependency actually become necessary.

---

## Step 4 · Teach only the required concepts

### 4.1 Raw GitHub data (what we get)

`GET /users/{username}/repos` returns a JSON **list**, each item having (among many): `name`, `stargazers_count`, `forks_count`, `language`, `fork` (bool), `archived`.

We don't want to return all of that; we **project** to the fields the portfolio needs.

### 4.2 Aggregation with a dict (counting by language)

Emoji counting "how many repos per language" is a classic aggregation:

```python
counts = {}                    # language -> count
for repo in repos:
    lang = repo.get("language")
    if not lang:               # some repos have no language
        continue
    counts[lang] = counts.get(lang, 0) + 1
```

`dict.get(lang, 0)` — if the key exists use its count, else start at 0. This is the idiomatic "increment-or-initialize" trick. (`collections.Counter` also solves this — we'll meet it below.)

**Why three ways to count — and why you should care which you pick.** `dict.get`, `defaultdict(int)`, and `Counter` are *not* interchangeable sugar; each one encodes *who owns the default behavior*:

- `dict.get(lang, 0)` — *you* write the "initialize on first sight" logic, inside your loop, every loop.
- `defaultdict(int)` — the default is bound to the *container*. Cleaner, but beware: `counts[missing_key]` **creates** the key with value 0. Iterate `counts.items()` afterwards and you'll include phantom zero-languages that never appeared.
- `Counter` — a dict subclass with two extras that matter *here*: `.most_common()` returns (item, count) pairs **already sorted descending** — that's your "sort for free" — and `Counter` supports arithmetic (`+`, `-`), so you can combine counts from multiple pages the day pagination gives you several repo lists.

The cargo-cult trap is reaching for `Counter` "because it's fancy" without knowing it auto-sorts (and that `.most_common()` ties break by insertion order). Know *which* behavior each container owns and you'll pick by intention, not fashion.

### 4.3 Percentage, then round — and the gotcha

```python
total = sum(counts.values())
langs = [{"name": k, "percentage": round(v / total * 100)} for k, v in counts.items()]
```

**The rounding bug:** `round(1/3*100) + round(1/3*100) + round(1/3*100)` = 33+33+33 = 99, not 100. Charts will show a 1% gap. A real product needs to be **capped/normalized** — e.g., force the largest to absorb the remainder. (This exact bug exists in the reference app; they fixed it with an adjustment step. You'll reproduce/fix it in the exercise.)

**Why does this happen at all — two separate mechanisms are at work:**

1. **Binary floating point.** `1/3` can't be represented exactly in binary (just like `1/3` in decimal), so `1/3 * 100` is `33.333333333333336`-ish, and `round()` snaps it to `33`. That's friction, not the real bug.
2. **Independent rounding doesn't guarantee constraints.** Each percentage is rounded **in isolation**. Rounding is a many-to-one map — lots of exact values land on the same integer — so nothing forces `sum(rounded) == 100`. This is a *math* error, not a floating-point quirk: even with perfect rational arithmetic, `34 + 33 + 33 = 100` is only guaranteed if you *coordinate* the rounding.

The fix ("largest absorbs remainder") coordinates them: compute exact values, floor each, then give the leftover `100 - sum` one point at a time to the largest fractions. That's a real, named algorithm — the **largest remainder method**, used for allocating seats in proportional-representation elections. Knowing it has a name (not just "some trick") is the difference between reproducing it and understanding it.

### 4.4 Sorting descending

```python
langs.sort(key=lambda l: l["percentage"], reverse=True)
repos_by_stars = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
top_languages = langs[:5]
```

`sorted(..., reverse=True)` = high-to-low. We then **slice** (`[:5]`) to cap the list — don't send 50 languages.

### 4.5 Why "pure function" is the single most valuable idea in this feature

The doc keeps saying "make it pure." Here's the mechanism, not the slogan. A **pure function**:

- returns the same output for the same input, *always*, and
- has **no side effects** — no network, no filesystem, no global variable, no reading the clock, no mutating its inputs.

Why is it so cheap to test and so expensive to get wrong? Because *everything it depends on is passed in as an argument, and everything it produces comes back as a return value.* There is no hidden state for a bug to sneak through or for a test to set up. `compute_portfolio(user_raw, repos_raw)` — feed it two plain Python structures, get a `Portfolio` back. A test can call it a thousand times in a second with no database, no mocking, no server running.

Contrast: a function that reads `datetime.now()` internally is **impure** — it hides one of its inputs (the clock). Every impurity you push out to the caller's boundary is a piece of implicit state you've made *explicit*. That's literally *why* the `not r.get("fork")` guard (Exercise 3) and the rounding fix are testable: they're pure. Nothing about this is FastAPI-specific — **impure functions are hard to test because their behavior depends on the outside world; pure functions are trivial to test because the outside world is their inputs.**

---

## Step 5 · Implementation plan

Add/modify:

```
app/
├── schemas/github.py        # add Repository, Language, ProfileSchema
├── clients/github.py         # add get_repositories()
├── services/
│   └── profile.py            # NEW: orchestrates fetch + transform into PortfolioOut
└── routers/github.py         # now uses the service instead of calling the client directly
```

| File | Responsibility | Why it now exists |
|------|----------------|-------------------|
| `clients/github.py` | fetch raw user + raw repos from GitHub | the only file that knows GitHub URLs |
| `schemas/github.py` | define `Repository`, `LanguageStat`, `Portfolio` | the typed contract |
| `services/profile.py` | **orchestrate**: call client, run transform, return `Portfolio` | business logic has its own home now |
| `routers/github.py` | HTTP only: get username, delegate to service | stays thin |

**Why did a `service` layer "appear" now and not before?** Because before, the router → client mapping was one-to-one. Now we have *two* calls (user + repos) plus *computation*. Multi-step logic belongs in a **service** — not the router (which should stay HTTP-only) and not the client (which should stay GitHub-only). This is *when* a layer becomes defensible: when its absence makes a file do too many jobs.

**The mechanism to internalize is not "services are good" — it's single-responsibility applied at the seam of a dependency.** A layer is justified exactly when its *absence* would give one file two unrelated jobs. The rule you can apply anywhere: if a route function is doing more than (a) read the request, (b) delegate, (c) return, it's doing too much.

Also worth noting: `ProfileService.__init__(self, client)` — the service takes its dependency as a **constructor argument**. That's dependency injection through *composition*, not through FastAPI. It means the service is testable *without FastAPI at all*: `ProfileService(client=FakeGitHub())`. The DI system (`Depends`) wires up the *routers*; the service wires itself. This is the same pattern reused when `session` gets added in Feature 4 — worth recognizing now so it isn't mysterious then.

---

## Step 6 · Implement gradually

### Piece 1 — schemas

```python
# app/schemas/github.py
from pydantic import BaseModel

class GitHubUser(BaseModel):
    username: str
    name: str | None = None
    avatar_url: str
    followers: int = 0

class Repo(BaseModel):
    name: str
    stars: int = 0
    forks: int = 0
    language: str | None = None
    is_fork: bool = False

class LanguageStat(BaseModel):
    name: str
    percentage: int = 0

class Portfolio(BaseModel):
    user: GitHubUser
    total_repos: int
    total_stars: int
    top_languages: list[LanguageStat]
    repositories: list[Repo]
```

Nested models (`list[Repo]`, `list[LanguageStat]`) are the normal way to compose shapes.

### Piece 2 — add repo fetch to the client

```python
# app/clients/github.py (add the method)
async def get_repositories(self, username: str, per_page: int = 100) -> list[dict]:
    async with httpx.AsyncClient(headers=self._headers, timeout=15.0) as client:
        r = await client.get(
            f"{self.BASE}/users/{username}/repos",
            params={"sort": "stars", "direction": "desc", "per_page": per_page},
        )
    if r.status_code == 404:
        raise GitHubError(404, "User not found")
    if r.status_code == 403 or r.status_code == 429:
        raise GitHubError(429, "GitHub rate limited")
    r.raise_for_status()
    return r.json()
```

- `params={...}` sends **query parameters** (`?sort=stars&per_page=100`), the clean httpx way (not string concat).
- `per_page=100` is the max GitHub allows; we'll handle pagination properly in Exercise 1 / Feature 5.

**Why pagination lives in headers, not the body.** GitHub caps `per_page=100`, and the mechanism for "give me the next page" is the **`Link` header**:

```
Link: <https://api.github.com/users/x/repos?page=2>; rel="next", <...page=4>; rel="last"
```

`rel` is the relationship — "next", "last", "first", "prev". A polite client reads the `next` URL from the header and keeps requesting until there is no `next`. That's the *definition* of walking a paginated API — not guessing page numbers (`?page=N` works, but the header is the source of truth; the server may split differently than you assume). Two practical details: never loop forever (cap total pages, in case an upstream gives you an unbounded `next` chain), and in httpx the header is just `r.headers.get("link")` (parsing each `rel` is a one-line regex).

### Piece 3 — the pure transform (in the service)

```python
# app/services/profile.py
from collections import Counter
from app.schemas.github import Portfolio, Repo, LanguageStat, GitHubUser

def compute_portfolio(user_raw: dict, repos_raw: list[dict]) -> Portfolio:
    langs_count = Counter(r["language"] for r in repos_raw if r.get("language"))
    total = sum(langs_count.values()) or 1

    stats = [{"name": l, "percentage": round(c / total * 100.0)} for l, c in langs_count.most_common()]
    _fix_rounding(stats)                     # makes them sum to 100 (see 4.3)

    repos = [Repo(name=r["name"],
                  stars=r.get("stargazers_count", 0),
                  forks=r.get("forks_count", 0),
                  language=r.get("language"),
                  is_fork=r.get("fork", False))
             for r in repos_raw]
    repos.sort(key=lambda r: r.stars, reverse=True)

    return Portfolio(
        user=GitHubUser(username=user_raw["login"],
                        name=user_raw.get("name"),
                        avatar_url=user_raw["avatar_url"],
                        followers=user_raw.get("followers", 0)),
        total_repos=len(repos_raw),
        total_stars=sum(r.stars for r in repos),
        top_languages=[LanguageStat(**s) for s in stats[:5]],
        repositories=repos[:20],             # cap for a readable portfolio
    )
```

**Why is this function pure (no network)?** Because it takes normal data and returns a model. Pure functions are the *easiest thing in the world to unit test* (Feature 11) and require no mocking.

`Counter` is the stdlib's tiny but perfect aggregation: `.most_common()` gives us counts *already sorted descending* — that handles our sorting for free. (We still sort `repos` by stars explicitly.)

`_fix_rounding(stats)` — write it yourself (Exercise 2) so `percentages` always total 100. (A senior keeps that subtlety isolated in its own tiny function.)

### Piece 4 — the service method (orchestration)

```python
# app/services/profile.py (add)
class ProfileService:
    def __init__(self, client):
        self.client = client

    async def get_portfolio(self, username: str) -> Portfolio:
        user_raw = await self.client.get_user(username)
        repos_raw = await self.client.get_repositories(username)
        return _count_portfolio(user_raw, repos_raw)
```

Two `await`s run **sequentially** (repos after user). We could run them *in parallel* with `asyncio.gather` (see Step 8) — a professional performance tweak.

**Why sequential is slower, mechanically:** `await client.get_user(...)` suspends the coroutine until user data returns. While it waits, the *second* call hasn't even been started — the event loop is idle for the whole first round-trip (~200-400ms), *then* repos start. Total ≈ 2 × round-trip. With `asyncio.gather(*[get_user(u), get_repositories(u)])`, both httpx calls are *scheduled* before either is awaited — both sockets are in flight at the same time — total ≈ 1 × round-trip. `gather` isn't magic: it means "start all these coroutines now (each is a task), then combine." (Bare `gather` also stops at the *first* exception while leaving the other task running — handle partial failure with `return_exceptions=True` when one call can independently 404.)

### Piece 5 — wire the router to the service

```python
# app/routers/github.py
from app.services.portfolio import ProfileService
from app.schemas.github import Portfolio

def get_service() -> ProfileService:          # DI: swap this in tests
    return ProfileService(client=GitHubClient())

@router.get("/{username}/portfolio", response_model=Portfolio)
async def portfolio(
    username: str = Path(..., min_length=1, max_length=39, pattern=USERNAME_RE),
    service: ProfileService = Depends(get_service),
):
    return await service.get_portfolio(username)
```

**Result:** the router is 5 lines and knows nothing about GitHub. It maps a path param to a request and returns a typed model. All logic lives in the service; all HTTP to GitHub lives in the client.

> **Your turn:** implement each piece, run it, hit `/users/torvalds/portfolio`, and verify the JSON. Then make a small error deliberately (typo a schema field) and watch FastAPI's validation reject it — that's useful feedback, not a failure.

---

## Step 7 · Request lifecycle (now with a service & two HTTP conversations)

```
Browser → GET /users/torvalds/portfolio
  │  uvicorn → FastAPI → validate username (or 422)
  │  Depends(get_service) → ProfileService(GitHubClient())
  ▼
  router.portfolio()
    └─ await service.get_portfolio("torvalds")
         ├─ await client.get_user("torvalds")        # httpx → GitHub (1st HTTP call)
         ├─ await client.get_repositories("torvalds") # httpx → GitHub (2nd HTTP call)
         └─ _count_portfolio(...)   → Portfolio (pure math, no I/O)
  ▼
  response_model serializes Portfolio → JSON  200
  ▼
  Browser gets JSON
```

**Observation:** there are now two outbound HTTP round-trips per request (user + repos). That doubling is exactly what Feature 4/5 (persistence + caching) will fix. Noted now, solved later — that's planning.

---

## Step 8 · Alternatives

- **`Counter` vs manual dict** vs `defaultdict(int)`: all fine; `Counter` is stdlib, clear, and pre-sorted. Manual dict is more flexible for non-count logic.
- **Parallel vs sequential calls**: `asyncio.gather(...)` runs both httpx calls at once (halves latency) — but adds error-handling complexity. Professional choice for latency-sensitive apps: `gather`. Your call; implement it in Exercise 5 for the *feel*.
- **Transform in service vs router**: keeping it in the service means it's testable + reusable; in the router it's buried. Another "adaptability vs brevity" trade-off.

---

## Step 9 · Refactor as a senior

- **Split `_fix_rounding`, `_count_languages` etc. into a separate module** `app/services/transform.py` if they grow — keep the service file readable.
- **Make aggregation pay attention to forks** — the reference deliberately *excludes forks* from language stats (forks are not YOUR code). Add a `not r.get("fork")` guard to the language counter (Exercise 3).
- **Typed return** — good. Add `TYPE_CHECKING` hints / annotate helpers (`list[dict]` → keep). Readability wins.

---

## Step 10 · Exercises

1. Add `archived: bool` and `pushed_at` to `Repo`; surface `pushed_at` in the JSON.
2. Implement `_fix_rounding` so the top_languages percentages always = 100. Test with `[1/3, 1/3, 1/3]` (expect 34/33/33 — the largest+remainder trick).
3. Exclude **forks** from language stats (repos where `fork: true` shouldn't inflate your language bar). Verify with a fixture.
4. Implement **pagination**: GitHub caps `per_page` at 100; make `get_repositories` follow the `Link` header (next page) until "done" or a max (e.g., 200). This *is* the pagination lesson from earlier — now it's real.
5. Change the two calls to run in **parallel** with `asyncio.gather(...)` and measure speed difference (add a quick `time.perf_counter` log).

### Review yourself
- [ ] Is the transform a `pure function` (no network/DB) — and therefore beginner-friendly to test?
- [ ] Did you cap `top_languages` and `repositories` (you're not shipping 10,000 repos)?
- [ ] Could a colleague swap the GitHub client for a mock without touching the router or service (DI works)?

### Field notes — silent failures to expect

> **⚠️ `round()` isn't "round to nearest 0" — it's banker's rounding.** Python's `round(2.5)` is **2**, not 3 (round-half-to-even). Invisible for percentages most of the time, but the moment you port this logic (JS `Math.round(2.5)` → 3; SQL `ROUND` varies by engine), identical inputs give off-by-one outputs. A silent cross-language difference, not a bug in your math.

> **⚠️ Slicing `[:5]` with fewer than 5 items is fine** — `[1][:5]` → `[1]`, no error. That forgiveness is why the code *feels* safe. But 0 items vs ties behave differently between `lst[:5]` and `Counter.most_common(5)` — know both exist.

> **📌 You can test the transform *right now*, before the router exists.** Since `compute_portfolio` is pure, `python -c "from app.services.profile import compute_portfolio; ..."` runs it with zero infrastructure. Getting in the habit of running pure functions from a one-liner is "testing" before Feature 11 arrives.

> **📌 The `is_fork` guard is a product decision, not a math decision.** Excluding forks from language stats means "language mix represents your *own* code." Keep that reasoning visible — a future teammate might "helpfully" remove the guard and silently change what the product means.

---

**Next feature:** [Feature 4 — Stop Hitting Rate Limits](04-f4-persistence.md). Your two HTTP calls per request + no caching means GitHub's 60-request/hour cap will bite. Time to persist what we fetch — enter SQLite, SQLModel, and migrations.

> *(Roadmap note: filename will be `04-f4-persistence.md` once we finalize numbering; follow the index in [README](README.md).)*