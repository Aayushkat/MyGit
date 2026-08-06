# Chapter 0 — Studying the Reference (CheckMyGit)

> **Step 0 of every project:** understand what you're about to reimagine. We read the reference **only to know *what* it does** — never to copy *how* it's built. Its tech (SvelteKit/Cloudflare) is foreign to us on purpose; we engineer our own from scratch.

---

## 1. What problem does it solve?

> *Turn any public GitHub username into a beautiful, shareable, exportable "portfolio" page — with no sign-up.*

Customers: developers showcasing work, recruiters reviewing candidates, anyone curious about a GitHub profile.

**Core value is the *perception* of work: it makes public GitHub data look great instantly.**

---

## 2. Its features (our feature-inventory → your roadmap)

| Area | What it does |
|------|--------------|
| **Portfolio generation** | Enter a username → rendered profile page |
| **3 templates** | `github`, `bento`, `minimal` layouts over the same data |
| **Shareable URLs** | `/{username}?template=bento` — the whole view lives in the URL |
| **PNG export** | download the rendered page as an image |
| **Contribution heatmap** | year-long calendar (from GraphQL) |
| **Language stats** | donut chart of the user's language mix |
| **Pinned projects** | showcase section |
| **Stats grid** | repos, stars, forks, followers, years active |
| **External contributions** | PRs/commits into repos the user doesn't own |
| **Explore** | `trending`, `rankings`, `globe` pages |
| **View counter** | per-profile + global "portfolios generated" counter |

## 3. User workflow

```
Landing (search) ──► enter username
   └─► /{username}  (skeleton first, data streams in)
        └─► pick template/theme  (URL updates)
             ├─► Download PNG     (client-side html-to-image)
             ├─► Share (URL + QR)
             └─► background: POST /api/view (count it)
```

## 4. UI/UX patterns worth stealing (the *ideas*, not the code)

- **Instant optimism**: skeleton shows before data arrives — perceived speed.
- **URL = app state**: shareable, refreshable, no backend config needed.
- **Graceful degradation**: without a GitHub token they still render (less rich data) rather than erroring.

## 5. Backend workflow & APIs

- **GraphQL** (`api.github.com/graphql`) with `GITHUB_TOKEN`: one query returns user + repos + pinned + contributions. Needs the token.
- **REST** (`api.github.com`) as **fallback** (also fetch `users`, `repos`, `orgs`): works without token but has **no contribution/heatmap** data.
- Server-side **transform functions** compute languages (byte → %), years active, external contributions, aggregate stats — then normalize everything into one profile object the frontend consumes.

## 6. Architecture (high level)

```
Browser ──► [SvelteKit server] ──► [github.ts adapter] ──► GitHub API
              │  transformers (normalize/compute)          ▲
              └─► Cloudflare KV (view counters, cache, SWR)
        [client components] render templates, export via DOM
```

Notable: secrets (token) stay server-side; caching uses edge KV with **stale-while-revalidate**; SEO wiring (sitemap, JSON-LD, 308s) exists.

## 7. Database / auth

- **No user database, no auth.** Stateless app. View counters live in Cloudflare KV, not a relational DB.
- We are adding **auth + a real DB + Redis** — that's our improvement and our learning surface.

## 8. Analytics / search

- Analytics terms: everything is *derived stats* over GitHub data (no first-party event tracking).
- "Search" = GitHub username lookup + explore (trending/rankings).

## 9. Deployment

- Cloudflare Pages (edge), `wrangler` for deploy, `html-to-image` for client export.

---

## 10. Our improved architecture (feature roadmap = the arrows)

We deliberately differ where it teaches you more:

| CheckMyGit does | We do | We learn |
|------------------|-------|----------|
| SvelteKit + GraphQL-first | **FastAPI + REST-first** | HTTP, status codes, adapters |
| no DB | **SQLite → Postgres (SQLModel + Alembic)** | SQL, models, migrations |
| Cloudflare KV | **SQLite then Redis cache** | caching, SWR, rate limits |
| no auth | **JWT + hashed passwords** | authentication end-to-end |
| client export | **server PNG/PDF + streaming** | file responses, background tasks |
| single server | **layered architecture** | clean/architectural structure |

**Now flip to [Feature 1 — Hello, Portfolio API](01-f1-hello-api.md). You'll write your first file in minutes.**