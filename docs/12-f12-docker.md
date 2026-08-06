# Feature 12 — Ship It (Docker, Compose, CI)

> **Milestone:** the app runs anywhere and the pipeline guards it. Containers, orchestration, and CI enter because deployment *forces* them — not for fashion.

---

## Step 1 · What are we building today

1. A `Dockerfile` that packages our API.
2. a `docker-compose.yml` wiring **api + db (Postgres) + redis** so the whole stack runs with one command.
3. A **GitHub Actions** CI that runs lint + tests on every push.
4. (Optional deploy hook.) The "it works on my machine" days end today.

```bash
docker compose up --build
```

---

## Step 2 · Why do we need this feature

Two facts force us here:

- **Reproducibility**: our environment is Python 3.12 + specific libs + Redis + Postgres. A machine that lacks any of it breaks. An **image** is that environment, frozen. "Works on my machine" becomes "works in the container."
- **You can't keep running SQLite in prod forever** — Postgres handles concurrent writes, and our layering (F4) was built exactly so `DATABASE_URL` is just a config change.

**CI**: Tests exist (F11) but nobody runs them — until a pipeline does it on every push. That's enforcement, and it's what "the team's confidence" means.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|-----------|---------------------------|
| **Docker** | package the app + its exact environment |
| **docker-compose** | run all our services together (api, db, redis) |
| **PostgreSQL** | the prod DB (SQLite → Postgres, per F4's plan) |
| **GitHub Actions** | CI: lint + test on every push |
| (reuse) Alembic | real migrations instead of `create_all` |

**Alembic finally becomes *required*** — in a container, `create_all` at startup is the wrong way; migrations are the safe one.

---

## Step 4 · Teach only the required concepts

### 4.1 image vs container vs compose

- **Image** = frozen template (code + OS + deps). Built from a `Dockerfile`.
- **Container** = a running copy of an image (isolated process).
- **Compose** = a YAML describing *several* containers + their network + volumes.

```
Dockerfile ─build→ Image ─run→ Container(s)
docker-compose.yml ─up→ [api] + [db] + [redis] wired together
```

### 4.2 A small, safe Dockerfile

Key traits: multi-stage (debs don't leak), non-root user, pinned Python, no secrets baked in.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build-deps /wheels /wheels   # (see Step 6)
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt
RUN useradd -m appuser && USER appuser    # drop root
COPY app/ ./app/
COPY static/ ./static/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`USER appuser` = never run as root (a security + practice warning). Pinning Python = reproducible.

### 4.3 Compose: the stack

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db, redis]
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: portfolio
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: portfolio
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

**Crucial lesson:** inside compose, containers reach each other by **service name** (`db`, `redis`), *not* `localhost`. So `DATABASE_URL=postgresql+psycopg://...@db:5432/portfolio` — our F4 config change makes this a one-line diff. That layering, again, is paying rent.

### 4.4 The one config change that costs nothing

```python
# .env (prod)
DATABASE_URL=postgresql+psycopg://portfolio:${POSTGRES_PASSWORD}@db:5432/portfolio
REDIS_URL=redis://redis:6379/0
```
Because we coded against `settings.database_url` (F4), swapping SQLite→Postgres is literally this. That's the whole point of the repository/config layering.

---

## Step 5 · Implementation plan

```
├── Dockerfile
├── .dockerignore         # don't copy .venv, .git, .env-in-the-image
├── docker-compose.yml      # api + db + redis
├── alembic/ ...           # migrations (run in compose as migrate service)
└── .github/
    └── workflows/ci.yml   # lint + pytest (+ redis/postgres services)
```

| File | Why |
|------|-----|
| `Dockerfile` | produce the runnable image |
| `.dockerignore` | keep secrets/junk out of the build |
| `docker-compose.yml` | local "prod-like" stack + networking |
| `ci.yml` | gate merges on green |
| `alembic/` | schema version-control now that nothing is `create_all` |

---

## Step 6 · Implement gradually

### Piece 1 — `.dockerignore`

```
.venv
__pycache__
.git
.env
tests
```

### Piece 2 — lint (ruff) + docs

Add a `pyproject.toml` with a `[tool.ruff]` config + run `ruff check .`. Lint is your first line of CI.

### Piece 3 — the Dockerfile

(use 4.2; build it — Piece 4 needs it — actually `docker build -t portfolio .`.)

### Piece 4 — migrations as a service

In compose, add a `migrate` service that runs `alembic upgrade head && exit`, `depends_on: db` — so the DB is up *and migrated* before the API serves traffic, safely.

```yaml
  migrate:
    build: .
    env_file: .env
    depends_on: [db]
    command: alembic upgrade head
```

### Piece 5 — CI

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:17-alpine, env: { POSTGRES_PASSWORD: test }, ports: ["5432:5432"] }
      redis:    { image: redis:7-alpine, ports: ["6379:6379"] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
      - run: ruff check app
      - run: pytest -q
```

Now every push runs against Postgres + Redis in CI. A red pipeline stops a bad merge — that's the enforcement.

> **Your turn:** build the image, `docker compose up --build`, hit `localhost:8000/health`, run a search, watch it use Postgres + Redis. Then push to GitHub and watch CI run.

---

## Step 7 · Request lifecycle (in a container)

```
curl localhost:8000/portfolios
  │ host port 8000 → compose map → api container (uvicorn, port 8000 inside)
  │ api → depends_on db/redis → Postgres + Redis containers (by name)
  │ (rate limit on Redis, cache on Redis, portfolio in Postgres & Redis)
  ▼  200 JSON → browser
```
Same code as ever — but now the *whole environment* is the same everywhere.

---

## Step 8 · Alternatives

- **Hosting**: Railway/Render/Fly.io — they build from a Dockerfile and give managed Postgres/Redis; we keep compose for local parity. `docker compose up` ≈ prod-ish env.
- **Two-stage Dockerfile** (build wheels in stage 1, slim runtime in stage 2) vs single stage: single is simpler, multi is smaller/safer. Use multi when image size matters (F13 optional).
- **Alembic in compose vs at deploy-time**: we do a `migrate` compose service; some run it in `entrypoint` (careful shape `depends_on` race).

---

## Step 9 · Refactor as a senior

- **Multi-stage build** for a smaller, safer image.
- **Healthcheck** on the `api` (reuse our `/healthz` if added → F13) so orchestration restarts it correctly.
- **`.env.example` committed**, real `.env` git-ignored — (protect the token + keys).
- **CI matrix** (multiple Python versions) once you want the "works on 3.11+ guarantee."

---

## Step 10 — Exercises

1. Add `/healthz` returning `{"status":"ok"}` and wire a Docker `HEALTHCHECK` to it (`docker inspect` shows healthy).
2. Change `database_url` to Postgres in `.env`, run `migrate` service, and confirm data in Postgres (psql). This is the payoff of F4.
3. Add a CI job that **builds the image** (not just tests).
4. Push a branch with a deliberately failing test — see CI turn red and block the merge. That's the enforcement, felt.
5. Add `pip-audit` (or `dependabot`) to CI to surface vulnerable deps.

### Review yourself
- [ ] Is the container non-root and without `.env`/secrets baked in?
- [ ] Does the app talk to `db`/`redis` by compose **service name**, not localhost?
- [ ] Is there a `migrate` step before the API serves?
- [ ] Does CI run lint + tests + build on every push?

---

**Next feature:** [Feature 13 — Make It Production](13-f13-production.md). It's deployed; now it must not kill its own users. Logging, security headers, secrets, observability, and hardening enter because *running in production* demands them.