# Feature 10 — Move the Frontend to React

> **Milestone:** the manual "state → re-render" choreography from F9 has become a burden. Time to meet the tool that exists precisely because of that pain.

---

## Step 1 · What are we building today

We **rewrite** the portfolio frontend (F9) as a small **React + TypeScript** app:

- One `App` component with `useState` for the search + theme (**UI state**).
- A `Portfolio` component that fetches and renders via **TanStack Query** (**server state**).
- Same features (search, stats, languages, theme) — but now declarative and typed.

```tsx
function App() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  return (
    <div data-theme={theme}>
      <Search onSearch={setUsername} />
      {username && <Portfolio username={username} />}
    </div>
  );
}
```

---

## Step 2 · Why do we need this feature

**The pain F9 left us:** every user action meant "call the right `renderX` by hand" — search, theme, loading, error states — and keeping them all in sync gets messy fast. The bug class "the UI is showing stale data because I forgot to call render after X" is a rite of passage.

**React's core idea:** *UI = f(state)*. You describe what should render **given the current state**, and React figures out the smallest DOM change for you. Update state → React re-renders. No manual choreography.

That's why frameworks exist — not to look cool, but because manual DOM sync is a serious maintainability trap.

**A second pain hides inside the first:** half of what F9 juggled wasn't really *UI* state at all — it was a hand-rolled cache of *server* data (the fetched portfolio) plus its loading/error bookkeeping. Treating those as the same kind of state is what made the choreography explode. React fixes the rendering half; a **server-state library** (TanStack Query) fixes the fetching half. This chapter installs both ideas.

---

## Step 3 · What new technologies are required

| Technology | Why this feature needs it |
|-----------|---------------------------|
| **React** (`react`, `react-dom`) | the "UI = f(state)" engine |
| **Vite** | dev server + build tool + TS/JSX compile (replaces "no build step") |
| **TypeScript** | typed props + a compile-time copy of the API contract |
| **JSX / TSX** | the HTML-in-JS syntax React uses |
| **`useState` / `useEffect`** | component UI state + side-effects |
| **TanStack Query** (`@tanstack/react-query`) | server state: caching, dedup, client-side SWR |
| (reuse) the SAME REST API | the backend doesn't change at all |

**The big realization:** **nothing on the backend changes.** React is purely a *presentation* concern. The API contract (F2's `response_model`) is the interface both frontends consumed. This is why "frontend and backend talk JSON" is the load-bearing wall of the whole architecture.

---

## Step 4 · Teach only the required concepts

### 4.1 Components = functions that return UI

```tsx
type RepoListProps = { repos: { name: string }[] };

function RepoList({ repos }: RepoListProps) {   // props in, JSX out
  return <ul>{repos.map(r => <li key={r.name}>{r.name}</li>)}</ul>;
}
```

Components take **props** (read-only data) and return **JSX** (HTML-ish). Reuse via composition. The props type is the component's contract — pass the wrong shape and the compiler refuses, the exact service Pydantic performs for your endpoints.

A note on `key`: when React re-renders a list it matches old children to new ones **by key**, not by position. A stable identity (`r.name`) lets it move items instead of recreating them; an array index as key silently mis-associates state when the list reorders. Same idea as a primary key in F4.

### 4.2 State and effects

- **`useState(initial)`** — a state slot + a setter. Changing state **triggers re-render**.
- **`useEffect(fn, deps)`** — runs side effects (like `fetch`) after render. `deps` tells React *when* to re-run (e.g. when `username` changes).

```jsx
function Portfolio({ username }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let alive = true;
    fetch(`/api/v1/users/${encodeURIComponent(username)}/portfolio`)
      .then(r => r.json())
      .then(d => alive && setData(d))     // guard against race after unmount
      .catch(e => alive && setError(e.message));
    return () => { alive = false; };      // cleanup = "ignore late responses"
  }, [username]);                          // re-run when username changes

  if (error) return <ErrorBox message={error} />;
  if (!data) return <Spinner />;
  return <div>{data.user.name}</div>;
}
```

The `alive` flag + cleanup is the professional pattern for **"ignore a fetch that's no longer relevant."**

### 4.3 Why the virtual DOM / diffing matters

React keeps a virtual representation; on state change it **diffs** against the previous one and applies only what changed. You almost never touch the DOM manually — you describe state, React handles updates. (Contrast with F9's manual `renderPortfolio`.)

---

## Step 5 · Implementation plan

```
frontend/                    # a NEW package (separate from the Python app)
├── index.html
├── vite.config.js           # dev server + build output
├── package.json
└── src/
    ├── main.jsx             # mount <App/> into #root
    ├── App.jsx              # theme + search state
    ├── Portfolio.jsx        # fetch + render (uses fetchPortfolio)
    ├── components/
    │   ├── Search.jsx
    │   ├── Stats.jsx
    │   └── LanguageBars.jsx
    └── api.js               # fetchPortfolio(username) — shared, one place
```

| File | Why |
|------|-----|
| `api.js` | the ONLY file that knows our REST endpoints (mirror of `clients/`!) |
| `App.jsx` | top-level state (theme, username) + layout |
| `Portfolio.jsx` | the fetch/effect + renders subcomponents |

**Why a separate `frontend/` folder (not inside `static/`)?** React needs a build step (Vite → static files). We'll build it and **serve the output from FastAPI** (`/static` or a mount). Dev uses Vite's hot server against the same API.

---

## Step 6 · Implement gradually

### Piece 1 — scaffold Vite + React

```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install
npm run dev          # dev server at localhost:5173 (hot reload)
```

### Piece 2 — `api.js` (keep HTTP in one place)

```js
// frontend/src/api.js
export async function fetchPortfolio(username) {
  const res = await fetch(`/api/v1/users/${encodeURIComponent(username)}/portfolio`);
  if (!res.ok) { const b = await res.json().catch(() => null); throw new Error(b?.error?.message ?? `HTTP ${res.status}`); }
  return res.json();
}
```

The browser is another HTTP client — same rules as F9.

### Piece 3 — App + Search + Portfolio

```jsx
// App.jsx
import { useState } from "react";
import Search from "./components/Search.jsx";
import Portfolio from "./Portfolio.jsx";

export default function App() {
  const [theme, setTheme] = useState("dark");
  const [username, setUsername] = useState("");
  return (
    <div data-theme={theme}>
      <button onClick={() => setTheme(t => (t === "dark" ? "light" : "dark"))}>theme</button>
      <Search onSearch={setUsername} />
      {username && <Portfolio username={username} />}
    </div>
  );
}
```

**Notice what React gives you for free:** no `render()` calls, no `getElementById`. Setting `username` makes `<Portfolio>` re-run its effect — that's the whole app state, explicitly.

### Piece 4 — build & serve from FastAPI

```bash
npm run build        # outputs frontend/dist/*
```

```python
# mount the built SPA on FastAPI
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
def index():
    return open("frontend/dist/index.html").read()
```

> **Your turn:** implement the pieces, build, and hit `/`. Then delete a piece of the manual F9 `render.js` and re-express it as React components — that's how you *feel* the difference.

---

## Step 7 · Request lifecycle (React edition)

```
User types + submits
  │ App setUsername(u) → state changes
  │ React re-renders App → renders <Portfolio username={u}/>
  │ Portfolio's useEffect runs (username dep) → fetch() → GET /api/v1/users/u/portfolio
  │     (same FastAPI stack: rate-limit, cache, GitHub, DB → JSON)
  │ .then setData(data) → re-render <Stats data />, <LanguageBars data />
  ▼
browser shows the portfolio. Same API, same JSON — new presentation layer.
```

The server is completely indifferent to React vs vanilla — that's the point of a clean API boundary.

---

## Step 8 · Alternatives

- **Next.js / Remix** = React + server-side rendering + routing — for SEO-heavy, large apps. We chose a client-rendered SPA (simplest).
- **Svelte / Vue** = other reactive frameworks, same idea. (The reference used Svelte.)
- **Staying vanilla (no framework)** = fine for small pages; we felt the choreography pain in F9 precisely to make this trade-off *real*.

---

## Step 9 · Refactor as a senior

- **Custom hook `usePortfolio(username)`** wrapping fetch+state+cleanup — reusable, testable.
- **Theme via `useTheme` hook** reading `localStorage` on init.
- **ErrorBoundary** component for render-time errors (a React-specific practice).
- **Keep `api.js` as the only HTTP-touching module** (a.k.a. "the frontend's `clients/` layer").

---

## Step 10 · Exercises

1. Add **caching in the frontend**: if you search the same username twice, don't re-fetch (a simple in-memory Map or `localStorage`). (This is the client-side echo of F4/F5.)
2. Add **template switcher** (`github`/`bento`/`minimal`) that changes the rendered layout via state — a pure "f(state)" demo.
3. **Persist `username`** in `localStorage` too, so reload keeps your last portfolio.
4. Add a **`usePortfolio` hook** (refactor Step 9) and use it in two components.

### Review yourself
- [ ] Does the backend code change in this feature? (It should NOT.)
- [ ] Do we keep `api.js` as the single HTTP module (no `fetch` scattered in components)?
- [ ] Are effects cleaning up late responses (`alive` flag)?
- [ ] Can you name the exact pain React removed (vs F9's manual re-render choreography)?

---

**Next feature:** [Feature 11 — Test Everything](11-f11-testing.md). We have features; now we make sure they don't break. pytest enters because the project *needs* regression safety.
