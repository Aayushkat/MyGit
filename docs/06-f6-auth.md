# Feature 6 — Accounts & Saved Portfolios (Authentication)

> **Milestone:** users can register, log in, and save "their" portfolios — the feature that *requires* authentication, taught because the app needs it.

---

## Step 1 · What are we building today

1. `POST /auth/register` — create an account (username + password).
2. `POST /auth/token` — log in, get a **JWT**.
3. `GET /me` — protected endpoint, returns the logged-in user.
4. `POST /portfolios` + `GET /portfolios` — save & list *my* portfolios (this is the reason auth exists).

```json
POST /auth/register  {"username":"bob","password":"hunter2"}
→ 201 { "user": {"username":"bob"}, "token": "eyJhbGciOi..." }

GET /me  (Authorization: Bearer eyJhbGciOi...)
→ 200 { "username": "bob" }
```

---

## Step 2 · Why do we need this feature

People want to **save** a portfolio (theme, template, username) so it survives navigation — "saved" means it belongs to *someone*, and "belongs to someone" means **identity**. Without auth, anyone could read or delete anyone's saved data. So this feature's real purpose is: *allow personal data to exist safely*.

Two things we *must* learn while doing it:
- **How to store secrets safely** (passwords: hashed, never plaintext).
- **How a server proves who you are on every request** (tokens: JWT).

---

## Step 3 · What new technologies are required

| Technology | Why THIS feature needs it |
|-----------|---------------------------|
| **Password hashing (bcrypt via `passlib`)** | never store a plaintext password |
| **JWT (`pyjwt`)** | a signed token the server verifies without a DB lookup |
| **`OAuth2PasswordBearer`** | FastAPI's standard hook to read `Authorization: Bearer` |
| (reuse) SQLModel tables (User, Portfolio), sessions, Depends | all in place |

**Why not full OAuth2 "Login with GitHub" yet?** That needs a registered GitHub OAuth app (client ID/secret) and adds a redirect dance. The *core* concept — "prove you are who you say" — is exactly the same; we'll add GitHub OAuth later as a stretch (Step 8 notes how). Password+JWT teaches the mechanism with zero external sign-up.

---

## Step 4 · Teach only the required concepts

### 4.1 Hashing passwords (the non-negotiable)

A password must never be stored as-is. We store a **one-way hash**: you can compute hash(password) easily, but you can't invert hash→password. **bcrypt** is slow-by-design (good against brute-force) and **salts** every hash (identical passwords → different hashes).

```python
from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

hash_password = lambda p: pwd.hash(p)          # to store
verify_password = lambda p, h: pwd.verify(p, h)  # to check login
```

**Never** use MD5/SHA for passwords — they're fast enough to brute-force. This is a security rule, not a preference.

### 4.2 JWT: a signed claim

A **JWT** is three base64 parts: `header.payload.signature`. The signature is a keyed hash (HMAC with our secret) of the first two parts — so if anyone tampers with the payload, the signature won't verify.

```python
import jwt
payload = {"sub": "bob", "exp": now + 1h}
token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
decoded = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
```

**Why JWT instead of a "session row" in the DB?** Because verifying a JWT is *pure math* — any server in our fleet can trust it without asking the database. Trade-off: tokens can't be "revoked" server-side (until we add a denylist). For saved-portfolio auth, short-lived tokens are perfect.

### 4.3 Reading the token: `OAuth2PasswordBearer`

```python
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
```

A dependency that reads `Authorization: Bearer <token>` from the request header and hands you the token string. If it's missing → FastAPI auto-401s. Perfect for wiring into `get_current_user`.

### 4.4 The protected-route pattern

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    creds_error = HTTPException(401, "Invalid token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise creds_error
    user = db.get(User, payload["sub"])     # actually load the user
    if not user:
        raise creds_error
    return user
```

Endpoints declare `user: User = Depends(get_current_user)` → FastAPI resolves the whole chain (header → decode → DB row) before your code runs. **401 = no/invalid creds; 403 = valid creds but not allowed** (we don't have 403 cases yet — Feature 7's ownership check introduces it).

---

## Step 5 · Implementation plan

```
app/
├── core/security.py            # hashing + JWT helpers
├── models/
│   ├── user.py                 # User table (id, username, hashed_password, created_at)
│   └── portfolio.py            # Portfolio table (id, owner, username, template, options, created_at)
├── schemas/
│   └── auth.py                 # RegisterIn, Token, UserOut
├── repositories/
│   └── users.py                # get_by_username, create_user
├── dependencies/
│   └── auth.py                 # get_current_user
└── routers/
    ├── auth.py                 # register, token
    └── portfolios.py           # create, list, get, delete (all require login)
```

| File | Why |
|------|-----|
| `core/security.py` | single home for hash/verify/JWT (used by router + dependency) |
| `models/*` | the persisted tables |
| `repositories/users.py` | SQL for users — keeps SQL out of routers |
| `dependencies/auth.py` | the reusable "who am I?" dependency every protected route imports |
| `routers/auth.py` + `routers/portfolios.py` | HTTP-facing, thin |

---

## Step 6 · Implement gradually

### Piece 1 — deps + config

```txt
passlib[bcrypt]==1.7.4
pyjwt==2.10.1
```
```python
# config.py add
jwt_secret: str = "change-me-in-prod"        # NEVER ship this default
jwt_algorithm: str = "HS256"
access_token_expire_minutes: int = 60
```

### Piece 2 — security helpers

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str: return pwd.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd.verify(p, h)

def create_access_token(subject: str) -> str:
    payload = {"sub": subject,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
               "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
```

### Piece 3 — models

```python
# app/models/user.py
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

```python
# app/models/portfolio.py
from sqlmodel import SQLModel, Field

class Portfolio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    github_username: str
    template: str = "github"
    options: str = "{}"          # JSON string of options
    created_at: datetime = ...
```

**Unique index** on `username` = "you can't register the same name twice" enforced at the DB level (not just app-level). **Foreign key** = a Portfolio points at a real User; the DB won't let you point nowhere.

### Piece 4 — register + login routes

```python
# app/routers/auth.py
@router.post("/auth/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_session)):
    if db.exec(select(User).where(User.username == body.username)).first():
        raise HTTPException(409, "Username already taken")
    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"user": UserOut(username=user.username), "token": create_access_token(str(user.id))}

@router.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect username or password")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}
```

- **409** on duplicate username (not 400 — that's the "state conflict" code).
- `OAuth2PasswordRequestForm` = the standard login form (`username`+`password`) that `/docs`' "Authorize" button uses. It *is* the OAuth2 password flow.
- 401 for bad creds — never reveal *which* of username/password was wrong.

### Piece 5 — the protected endpoint

```python
# app/routers/portfolios.py
@router.post("/portfolios", status_code=201)
def create_portfolio(body: PortfolioIn, user: User = Depends(get_current_user),
                     db: Session = Depends(get_session)):
    p = Portfolio(owner_id=user.id, github_username=body.github_username,
                  template=body.template, options=body.options.model_dump_json())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("/portfolios")
def list_mine(user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    return db.exec(select(Portfolio).where(Portfolio.owner_id == user.id)).all()
```

**Notice:** `get_current_user` runs, and if the token is bad, FastAPI returns 401 **before** `create_portfolio` ever executes. That's the "guard at the door" pattern — the endpoint can assume a valid user.

> **Your turn:** implement it, run Alembic (or `create_all`) for the new tables, and test the whole flow in `/docs`:
> register → login (Authorize) → create a portfolio → list portfolios → call `/portfolios` *without* a token (expect 401).

---

## Step 7 · Request lifecycle (auth version)

```
POST /auth/token  {"username":"bob","password":"..."}
  │ uvicorn → FastAPI
  │ 1. OAuth2PasswordRequestForm validates the form body
  │ 2. login(): query User by username (SQLite)
  │ 3. verify_password(...) — bcrypt compare
  │ 4. create_access_token → JWT (signed with secret)
  ▼  201/200 {access_token, token_type}

GET /portfolios   (Authorization: Bearer <jwt>)
  │ 1. OAuth2PasswordBearer reads header → token string (401 if absent)
  │ 2. get_current_user: jwt.decode (verify signature+exp)
  │ 3. db.get(User, sub) → row (401 if not found)
  │ 4. endpoint runs with user injected
  ▼  200 [ ... my portfolios ... ]
```

The JWT round-trip is the entire story: **sign at login, verify per request.** Nothing stored server-side for the token.

---

## Step 8 · Alternatives

- **JWT vs server sessions (cookie)**: sessions = store an ID in DB/Redis, revocable, but every request needs a lookup + a cookie/CSRF dance. JWT = stateless, but not revocable without extra machinery. For our scale: JWT is right; note the cookie+CSRF variant as the "production web-app session" evolution.
- **bcrypt vs argon2**: argon2 is newer/stronger; bcrypt is battle-tested and everywhere. Either is fine; pick bcrypt for ecosystem comfort.
- **Password flow vs GitHub OAuth**: OAuth "Login with GitHub" removes password storage but needs a registered app; identical token philosophy. We'll add it as a stretch feature.

---

## Step 9 · Refactor as a senior

- **Never load `hashed_password` in API responses**: `UserOut` (schema) must exclude it — and use `response_model` everywhere so it can't leak. (Also confirms our F2 habit.)
- **Move hash/verify calls into the `repository`** (`users.py`): `create_user`, `get_by_username`, `authenticate(username, password)` — the router becomes 3 lines.
- **Ownership check (403):** add `GET /portfolios/{id}` where a user can only see their own (403 otherwise). That introduces the 403 concept naturally.
- **Password strength:** validate min length in `RegisterIn` (Pydantic `min_length=8`).

---

## Step 10 · Exercises

1. Add `GET /portfolios/{id}` with an **ownership check**: 403 if `owner_id != current_user.id`, 404 if the portfolio doesn't exist. (Think: which code wins when both apply? What would a hacker probe see?)
2. Add password `min_length=8` + confirm that `/docs` documents it (422 on weak).
3. **Token denylist on logout** (Redis): `POST /auth/logout` adds the JWT's `jti`/`exp` to a Redis key; `get_current_user` checks it → 401. Test: logout then reuse token.
4. **Refresh tokens**: return a longer-lived `refresh_token`; add `POST /auth/refresh`. (Optional, but it's the "what real apps do" answer to "JWT can't be revoked".)

### Review yourself
- [ ] Passwords hashed with bcrypt and **never** in responses/logs?
- [ ] `jwt_secret` not the default value in production (config, .env)?
- [ ] 401 (no/bad token) vs 403 (forbidden owner) used correctly?
- [ ] Token verification pure, DB fetch separate — testable in Feature 11?

---

**Next feature:** [Feature 7 — Share Links & View Counters](07-f7-share-counters.md). Saved portfolios are only useful if you can *share* them — and "views" are only useful if you can *count* them. Enter URL state, background tasks, and Redis counters.
