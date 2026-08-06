# Feature 8 — Export as PNG / PDF

> **Milestone:** give the user a downloadable file. This forces **file/streaming responses** and — because image rendering is CPU-heavy — the first real use of **offloading work off the event loop**.

---

## Step 1 · What are we building today

1. `GET /export/{username}/png` — returns a PNG file (a simple "portfolio card" we draw with Pillow).
2. `GET /export/{username}/json` — returns the same portfolio as a downloadable JSON (bonus, teaches `Content-Disposition`).
3. **Result headers** done right: `Content-Type: image/png`, `Content-Disposition: attachment; filename="...png"`.

```http
GET /export/octocat/png
→ 200
  Content-Type: image/png
  Content-Disposition: attachment; filename="octocat-portfolio.png"
  <binary PNG bytes>
```

---

## Step 2 · Why do we need this feature

"Share a link" (F7) is good, but recruiting/CV contexts need a **portable file** — a PNG to drop in a doc, or a PDF. This feature is also the "real" answer to the reference app's Download/PDF export buttons.

Underneath, it teaches two production essentials:
- **Responses that aren't JSON** (image bytes, big files) — `FileResponse`/`StreamingResponse` and the right headers.
- **CPU work vs the event loop** — drawing an image is actual CPU work; if we do it inside an `async def` we'd freeze the loop, exactly the sin from Feature 2. This is the first time we *must* deliberately offload CPU work.

---

## Step 3 · What new technologies are required

| Technology | Why THIS feature needs it |
|-----------|---------------------------|
| **Pillow (PIL)** | draw the PNG server-side (we control output, no browser needed) |
| **`FileResponse` / `BytesIO`** | return binary file content with proper headers |
| **`asyncio.to_thread`** | run the CPU-heavy Pillow work off the event loop |
| (reuse) caching, schemas | already in place |

**Why server-side rendering instead of "client-side html-to-image"?** The reference uses client-side `html-to-image` (render the user's own browser DOM). Both are valid. We choose server-side because (a) it works even for a plain <share-link> opened by a crawler, (b) it teaches `StreamingResponse` + CPU offload after download/caching, and (c) it tests conversions. Note the trade-off (Step 8) for later when we may add a "render the live template" option.

---

## Step 4 · Teach only the required concepts

### 4.1 Pillow: draw in code

```python
from PIL import Image, ImageDraw

img  = Image.new("RGB", (1200, 630), "#0d1117")
draw = ImageDraw.Draw(img)
draw.text((60, 60), "Portfolio", fill="#f0f6fc")          # name
draw.text((60, 120), f"{username} · {stars}★", fill="#8b949e")
# ... more boxes/bars ...
buf = BytesIO()
img.save(buf, format="PNG")
return buf.getvalue()
```

Fast and dependency-light; reads like drawing coordinates by hand. (Fiddly for fancy layouts — that's the trade-off in 4.3 / Step 8.)

### 4.2 File/streaming responses

- **`FileResponse("./file.png", media_type="image/png")`** — serves a file from disk; FastAPI sets content-type and handles range requests.
- **`StreamingResponse(iterable, ...)`** — streams bytes (great for big/on-the-fly content, avoids buffering the whole body in memory).
- **`Content-Disposition: attachment`** forces a *download* (vs `inline`). Headers `Content-Type` (what the data *is*) vs `Content-Disposition` (how the browser treats it) — both matter.

### 4.3 CPU work off the loop (`asyncio.to_thread`)

A Pillow render is pure CPU. In an `async def` endpoint, calling it directly blocks the whole event loop (all other users during the render). Fix: hand it to a **thread executor** so the loop stays free:

```python
png = await asyncio.to_thread(render, username, data)   # off the loop
```

**When to `to_thread`: CPU-bound, short-medium work (image/text transforms).** For heavy/long jobs → a worker queue (Step 9). This is the first concrete instance of "respect the event loop."

### 4.4 Trade-off honesty

Hand-drawn Pillow text/cards are *brittle*: re-layout means editing coordinates. Production "OG image" generators instead render an **HTML template → SVG → PNG** (Satori/Resvg, as the reference's TODO shows). We learn Pillow (raw mechanics + thread issue) and discuss the HTML template as the "real-world upgrade."

---

## Step 5 · Implementation plan

```
app/
├── services/export.py          # render_png(data) → bytes ; render_json
└── routers/export.py           # GET /export/{username}/png, /json
```

| File | Why |
|------|-----|
| `services/export.py` | the CPU work, separate & testable; the router stays HTTP-only |
| `routers/export.py` | headers, route, call the service off-loop |

---

## Step 6 · Implement gradually

### Piece 1 — deps

```txt
pillow==11.0.0   # (or whatever's current)
```

### Piece 2 — the service (pure-ish + CPU)

```python
# app/services/export.py
from io import BytesIO
from PIL import Image, ImageDraw

def render_png(username: str, repos: int, stars: int) -> bytes:
    img = Image.new("RGB", (1200, 630), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.text((60, 90),  username,               fill="#ffffff")
    draw.text((60, 160), f"{repos} repos",       fill="#8b949e")
    draw.text((60, 210), f"{stars} stars",        fill="#8b949e")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```

### Piece 3 — how to be robust

Wrap with **filename sanitize** (injectable headers!) + a note that username is alphanum already (we validated it, but sanitize anyway in `Content-Disposition`).

### Piece 4 — the router

```python
# app/routers/export.py
import asyncio
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from app.services.export import render_png

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/{username}/png")
async def export_png(username: str = Path(...)):
    data = await profile_service.get_portfolio(username)   # cached
    png = await asyncio.to_thread(render_png, username, data.total_repos, data.total_stars)
    return StreamingResponse(BytesIO(png), media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{username}-portfolio.png"',
                 "Cache-Control": "public, max-age=900"})
```

- `await asyncio.to_thread(...)` → Pillow runs off-loop → returns bytes.
- `StreamingResponse(BytesIO(png))` streams bytes to the client.
- **`Cache-Control`**: the PNG for a username is deterministic → cache it (the cache pattern again). This is a good place to *store the generated PNG in Redis* (Exercise 2) so we don't re-render + re-fetch each time.

> **Your turn:** implement, restart, `curl -i http://127.0.0.1:8000/export/octocat/png`, open the file; then open it in a browser to trigger the download. Check the response headers.

---

## Step 7 · Request lifecycle (export with CPU offload)

```
GET /export/octocat/png
  │ uvicorn → FastAPI → validate → get_portfolio (cache hit)
  │ await asyncio.to_thread(render_png, ...)      ──► thread pool off loop
  │     (the only 'slow' CPU step)
  │ StreamingResponse(  PNG bytes, image/png,
  │                     Content-Disposition: attachment, Cache-Control: public  )
  ▼
BROWSER  downloads octocat-portfolio.png
```

---

## Step 8 · Alternatives

- **FileResponse (disk) vs StreamingResponse (bytes)**: disk rewards disk cache; bytes both if you already hold the bytes from Redis. Pick the simpler one that fits.
- **Server-side (Pillow/SSG) vs client-side (html-to-image)**: server = robust & shareable (linkable), client = exactly WYSIWYG. The reference chose client for its live template; we picked server for the export-to-file + streaming lesson. Later we may do both.
- **PDF**: Pillow draws PNG; a "PDF" is just another target (render SVG→PDF, or html→pdf in a headless browser). Implementation in Exercise 4.

---

## Step 9 · Refactor as a senior

- **Cache the generated PNG** (Redis, key `png:{username}`, TTL hours) — a real "expensive artifact caching" pattern.
- **Jobs for slow/big**: if renders were heavy and slow, move them to a **background queue** (F9's worker) and return `202 + {job_id}` with a polling URL. This is the "long-running block" route.
- **HTTP headers**: keep header strings in one helper (no injection).
- **Add a `Accept`-driven `format` (png/json)** instead of two endpoints — Exercise 5.

---

## Step 10 · Exercises

1. Add `GET /export/{username}/json` that downloads the same data with `Content-Disposition` — verify download.
2. **Cache the produced PNG in Redis**; on the second call, serve from Redis without re-render (and log "cached-png").
3. Add **sanitization** of `username` before it touches `Content-Disposition` (defense-in-depth, even though we validate).
4. **PDF export**: reuse the same `<card>` and create a one-page PDF (allow Pillow→PDF by saving as `PDF` format). Note the difference in content-type.
5. **Accept-header content negotiation**: `GET /export/{username}` returns PNG if `Accept: image/png`, else JSON — the "one endpoint, many formats" design.

### Review yourself
- [ ] Is no CPU work done directly in an `async def` endpoint (always `asyncio.to_thread` for Pillow)?
- [ ] Is the PNG both `image/png` AND an attachment (two different headers)?
- [ ] Facing a slow-but-fine render: is it cached (Redis)?
- [ ] Could a crafted `username` break the `Content-Disposition` header? (Is our validation enough + defense-in-depth?)

---

**Next feature:** [Feature 9 — The Real Frontend (HTML/CSS/JS)](09-f9-frontend.md). We've been returning JSON to an empty page. Now we build the pages that display and consume it. Raw JS at first — we'll understand it before React (F10).