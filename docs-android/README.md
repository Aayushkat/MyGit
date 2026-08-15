# Gitfolio — The Android Mentor Handbook

A **project-driven** apprenticeship handbook for Android. We build **Gitfolio** — a GitHub portfolio companion app — feature by feature, and every technology is introduced **only when a feature makes it necessary**, never as isolated theory.

> **The single rule of this handbook:**
> We don't say *"today we learn Jetpack Compose state hoisting."*
> We say *"we need a search box whose text survives rotation — that means state has to live somewhere above the UI — which means we now need to understand state hoisting and ViewModel."*
> Then we build it.

---

## 1. What we are building — and why THIS project teaches THIS stack

**Gitfolio** does four things, and each one drags a slice of the modern Android stack into the project at exactly the moment we can't avoid it:

| Feature | What it forces us to learn |
|---------|---------------------------|
| Search any GitHub user | Compose UI, text input state, ViewModel, networking (Retrofit + OkHttp + kotlinx.serialization) |
| View a rich portfolio (repos, languages, followers, avatars) | Navigation Compose, list performance, Coil image loading, data mapping |
| Star/save favorite profiles locally | Room (offline cache), DataStore (preferences), repository pattern, Hilt DI |
| Background-refresh saved profiles | WorkManager, coroutines + Flow done properly, app lifecycle |

It talks to the **public GitHub REST API** (`api.github.com`) — the same API your MyGit backend consumes. That synergy is deliberate: you already know what the data looks like from the server side. Now you'll learn what it takes to consume it well from a phone — flaky networks, process death, rate limits, offline users.

**The project drives the curriculum.** No chapter opens with "Android has four application components, let's enumerate them." Every chapter opens with a feature Gitfolio needs *now*, and the tech list is whatever that feature demands — nothing more. If a technology never becomes necessary, it never appears.

---

## 2. Scope guardrails (read these before you dream bigger)

This handbook is calibrated for **one student, one app, one physical phone, one 8 GB laptop**. The guardrails that keep it finishable:

- **One app module.** No multi-module architecture, no Kotlin Multiplatform, no design-system library. Those are team-scale solutions to team-scale pain; we don't have the pain.
- **No backend to build.** GitHub's public API *is* our backend. No accounts, no OAuth dance — unauthenticated requests (60/hour) are enough for development, and we handle the rate limit as a first-class app state, not an afterthought.
- **No emulator.** Your Ryzen 3 + 8 GB machine cannot run Android Studio *and* an emulator comfortably. A physical phone over USB is faster, more honest, and free. This is non-negotiable (see §7).
- **Refactors are earned, not preloaded.** We start chapter 04 with the ViewModel calling Retrofit *directly* — deliberately "wrong" — and only in chapter 05, when the pain is visible on screen, do we extract a repository and bring in Hilt. You will feel *why* architecture exists before you type it.
- **Every line is yours.** The handbook explains, shows snippets, and reviews. You type, run, break, and fix everything on your own machine.

---

## 3. The tech stack — each piece justified by a project need

2026 industry-standard only. Nothing deprecated, nothing legacy, nothing "because a tutorial from 2021 used it."

| Technology | The Gitfolio need that justifies it |
|------------|-------------------------------------|
| **Kotlin 2.x** | The language of Android. Null safety and coroutines are load-bearing for an app that lives on a flaky network. |
| **Jetpack Compose + Material 3** | Our entire UI: search screen, portfolio detail, saved list. Declarative UI is the 2026 default; XML layouts are legacy. |
| **Gradle + version catalog** (`libs.versions.toml`) | One file that pins every dependency version. On 8 GB of RAM, a disciplined build is a survivable build. |
| **ViewModel + StateFlow** | Search results must survive rotation and process recreation. Unidirectional data flow keeps UI state debuggable. |
| **Retrofit + OkHttp + kotlinx.serialization** | Typed calls to `api.github.com` with JSON parsed into Kotlin data classes — no hand-rolled `HttpURLConnection`, no reflection-based Gson. |
| **Coil** | Every profile has an avatar; every repo list scrolls. Coil loads, caches, and recycles images without us reinventing that wheel. |
| **Hilt** | Once a repository sits between ViewModel and network (ch 05), somebody has to construct and share it. Hilt is that somebody. |
| **Room** | Saved profiles must open instantly and offline. Room is the SQLite cache that makes "starred" mean something on the subway. |
| **DataStore** | Small preferences (theme choice, last sync time) — the modern replacement for SharedPreferences. |
| **WorkManager** | Saved profiles should refresh even when the app is closed. WorkManager is how Android lets you do that without burning the battery. |
| **Navigation Compose** | Search → portfolio detail → saved list is a navigation graph, with back-stack behavior users expect for free. |

---

## 4. The Roadmap

Thirteen chapters. Each introduces tech **only when Gitfolio needs it**:

| Chapter | Title | Introduces |
|---------|-------|------------|
| [00-platform-and-toolchain.md](00-platform-and-toolchain.md) | The Android platform and a survivable toolchain | What Android actually is, Android Studio tuned for 8 GB RAM, physical-device debugging, first run of the empty app. |
| [01-kotlin-for-the-project.md](01-kotlin-for-the-project.md) | Kotlin, exactly as much as Gitfolio needs | Data classes, null safety, lambdas, collections — practiced on real GitHub JSON shapes, nothing academic. |
| [02-first-compose-screen.md](02-first-compose-screen.md) | The search screen in Jetpack Compose | Composables, modifiers, layout, Material 3 components, previews — the search UI, static for now. |
| [03-state-and-viewmodel.md](03-state-and-viewmodel.md) | State, ViewModel, and unidirectional data flow | `remember`, state hoisting, ViewModel, StateFlow, UI state as a single immutable class. |
| [04-networking-github-api.md](04-networking-github-api.md) | Networking: the GitHub API from the app | Retrofit, OkHttp, kotlinx.serialization, suspend calls, loading/error/success states, rate limits. |
| [05-architecture-repository-hilt.md](05-architecture-repository-hilt.md) | Architecture: repository layer and Hilt DI | The refactor the last chapter's pain demands: repository pattern, Hilt modules, constructor injection. |
| [06-navigation.md](06-navigation.md) | Navigation: from search to portfolio detail | Navigation Compose, type-safe routes, arguments, back stack, the portfolio detail screen. |
| [07-room-offline-cache.md](07-room-offline-cache.md) | Room: offline-first saved profiles | Entities, DAOs, the database as source of truth, starring profiles, reading them offline. |
| [08-coroutines-and-flow.md](08-coroutines-and-flow.md) | Coroutines and Flow, properly | Structured concurrency, dispatchers, cancellation, cold flows, `stateIn` — the machinery we've been using, finally understood. |
| [09-background-work.md](09-background-work.md) | WorkManager: refreshing saved profiles in the background | Periodic work, constraints, Hilt worker injection, verifying background sync actually ran. |
| [10-testing.md](10-testing.md) | Testing Gitfolio | JUnit, ViewModel tests with fake repositories, coroutine test dispatchers, a first Compose UI test. |
| [11-theming-material3.md](11-theming-material3.md) | Material 3 theming and polish | Color schemes, dynamic color, dark theme, typography, the pass that makes it feel shippable. |
| [12-release.md](12-release.md) | Release: signing, shrinking, shipping | Keystores, R8 shrinking, release builds, what it takes to hand someone an APK/AAB. |

**Why this order?** Each chapter creates the *pain* that justifies the next:

```
PAIN-DRIVEN ARC
──────────────────────────────────────────────────────────────────────
Static search screen         → useless without state       → ch 03
State without data           → we need the real API        → ch 04
ViewModel doing networking   → untestable, unshareable     → ch 05
One screen only              → tapping a result goes where? → ch 06
Every open re-fetches        → offline cache               → ch 07
Flows everywhere, half-magic → understand them properly    → ch 08
Saved profiles go stale      → background refresh          → ch 09
"It works on my phone"       → prove it with tests         → ch 10
It works but looks default   → theme it                    → ch 11
It lives only on your phone  → sign and ship it            → ch 12
──────────────────────────────────────────────────────────────────────
```

Tech is never "assigned" — it *grows out of* the app.

---

## 5. Decisions locked in

Every chapter assumes these. They are pinned so the handbook never contradicts itself:

| Decision | Value |
|----------|-------|
| Product | **Gitfolio**: search GitHub users, view rich portfolios (repos, languages, followers), star/save profiles locally, background-refresh saved profiles. |
| API | Public GitHub REST API (`api.github.com`) — the same API the MyGit backend consumes. |
| Language / UI | Kotlin 2.x, Jetpack Compose + Material 3. |
| Build | Gradle with version catalog (`libs.versions.toml`). |
| Architecture | ViewModel + StateFlow, unidirectional data flow. **Starts simple** — ViewModel calls Retrofit directly in ch 04 — **refactored** to repository + Hilt in ch 05 when the pain justifies it. |
| Networking | Retrofit + OkHttp + kotlinx.serialization. |
| Images | Coil. |
| Persistence | Room (offline cache), DataStore (preferences). |
| Background | WorkManager. |
| Navigation | Navigation Compose. |
| Package | `dev.gitfolio.app` |
| SDK | Min SDK 26, target latest stable. |
| Hardware doctrine | Physical phone, no emulator, capped Studio heap, Gradle configuration cache (see §7). |

If a chapter ever appears to conflict with this table, the table wins.

---

## 6. How each chapter is structured

Every chapter follows the same 10-step rhythm:

| Step | What happens |
|------|--------------|
| 1 | **What we are building** — one concrete feature. |
| 2 | **Why the project needs it** — the pain that makes it necessary now. |
| 3 | **New technologies required** — a table: tech → why now. |
| 4 | **Concepts** — the theory, taught properly but only what this chapter needs. |
| 5 | **Implementation plan** — every file, and the single responsibility of each. |
| 6 | **Build it piece by piece** — snippets with what/why explanations, never one giant dump. |
| 7 | **Run and verify** — exact PowerShell commands, expected output, proof it works on your phone. |
| 8 | **How it flows** — an ascii trace: tap → state → repository → network/DB → UI. |
| 9 | **A senior's review** — what production would demand; tradeoffs table (chosen vs alternative vs when the alternative wins). |
| 10 | **Exercises** — 3–5 implementation tasks. No solutions. |

Step 4 is calibrated: enough theory that you never need to open a second tab to finish the chapter, never so much that it becomes a textbook. Each chapter ends with 2–4 deep-dive pointers to official docs for when you *want* the second tab.

> **Industry lens:** Real Android teams work exactly like this handbook's arc, just at larger scale: a feature lands "too simply" first, and the refactor to repositories, DI, and modules happens when a second engineer or a second screen makes the simple version hurt. Google's own architecture guidance is framed as recommendations that teams adopt *when the pain arrives*, and app teams at scale (banking apps, ride-share apps) run the same pipeline you'll finish with — version catalogs, unidirectional data flow, WorkManager for sync, R8-shrunk signed builds through CI. Nothing in this handbook is a teaching-only toy pattern you'd unlearn on the job.

---

## 7. Hardware & cost strategy (the 8 GB survival rules)

Your machine: Windows 11, Ryzen 3 7320U, 8 GB RAM, no dedicated GPU. Android development is famously heavy; here is how we make it comfortable — total cost: **$0** plus a USB cable.

1. **Develop on your physical Android phone** via USB (or wireless) debugging. The emulator is itself a second operating system; on 8 GB it will fight Android Studio for memory and both will lose. A real phone deploys faster and shows you real behavior.
2. **Cap the Android Studio heap** (~2 GB) so the IDE cannot slowly eat the machine.
3. **Close everything else during Gradle sync** — browsers with 30 tabs are Gradle's natural predator.
4. **Enable the Gradle configuration cache** so repeat builds skip work they've already done.

Chapter 00 walks through each of these with exact settings. The two you'll meet on day one:

```powershell
# Verify your phone is connected and authorized for debugging
adb devices
```

```properties
# gradle.properties — the survival lines (explained fully in ch 00)
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx2048m
```

Every heavy tool in this handbook comes with its lightweight path, and no chapter requires paid services, cloud accounts, or hardware you don't already own.

---

## 8. The End-Goal Checklist

By the last chapter, from memory and understanding, you can:

- [ ] Trace a tap from Compose UI → ViewModel → repository → Retrofit/Room → StateFlow → recomposition, naming each layer and what breaks without it.
- [ ] Build a Compose screen from scratch: layout, state hoisting, Material 3 components, previews.
- [ ] Model UI state as a single immutable class and explain why unidirectional data flow beats scattered mutable state.
- [ ] Call a REST API from Android with Retrofit + kotlinx.serialization and handle loading, error, empty, and rate-limited states.
- [ ] Justify the repository pattern and Hilt DI by describing the pain of their absence — because you lived it in ch 04.
- [ ] Navigate between screens with type-safe routes and predictable back-stack behavior.
- [ ] Make a feature offline-first with Room as the source of truth.
- [ ] Explain structured concurrency, dispatchers, cancellation, and cold vs hot flows — and spot a leaked coroutine in review.
- [ ] Schedule constrained background work with WorkManager and prove it ran.
- [ ] Test a ViewModel with fakes and a test dispatcher; write a basic Compose UI test.
- [ ] Theme an app with Material 3 including dark and dynamic color.
- [ ] Produce a signed, R8-shrunk release build and explain every step of the signing chain.

---

**Start here:** [Chapter 00 — The Android platform and a survivable toolchain](00-platform-and-toolchain.md).

*You are the engineer. I am the senior sitting next to you. Let's build.*
