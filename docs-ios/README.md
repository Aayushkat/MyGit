# Gitfolio for iOS — Mentor-Led Handbook (Future Track)

A **project-driven** apprenticeship handbook for the Apple platform. We build **Gitfolio** — the same app as the Android handbook: search GitHub users, view rich profiles, save favorites offline, refresh them in the background — and every technology is introduced **only when the app makes it necessary**, never as isolated theory.

> **The single rule of this handbook:**
> We don't say *"today we learn SwiftUI state management."*
> We say *"our search screen forgets its results when the view redraws — we need state that survives the redraw — which means we now need `@State` and the Observation framework."*
> Then we build it.

---

## This is a FUTURE track — you don't have a Mac yet, and that's fine

Read that again, because it shapes everything:

- **Every chapter is complete learning material you will execute later**, with exact macOS and Xcode commands ready for the day the Mac arrives. Nothing is hand-waved with "we'll cover this when you have hardware."
- **The primary goal *right now* is terminology fluency.** When you finish this track, you speak the Apple ecosystem's language: you know what a *target*, a *scheme*, a *bundle identifier*, an *entitlement*, a *provisioning profile*, and a *simulator runtime* are — before you've ever clicked Build. That vocabulary is exactly what separates "I watched a SwiftUI video" from "I can hold a conversation with an iOS team."
- **Every chapter opens with a one-line note:** *"No Mac yet? What you can still absorb from this chapter."* That note tells you what to internalize on your Windows machine today — concepts, architecture, API shapes, Swift syntax — versus what waits for hardware.
- **Concepts map 1:1 to the Android handbook.** You already built Gitfolio's shape once. Each chapter explicitly bridges: *"Android's ViewModel ≈ an `@Observable` class held by the view."* Learning iOS as a translation of what you know is dramatically faster than learning it cold.

You can read Swift, sketch view hierarchies, design the data layer, and even write Swift in an online playground from Windows. What you cannot do without a Mac is compile an iOS app. So we front-load everything the brain can do, and leave the compiler for later.

---

## What we are building — and why THIS project teaches THIS stack

Gitfolio is small enough to finish and real enough to hurt in all the instructive places:

| The app needs… | …which forces us to learn |
|---|---|
| A search screen that feels native | SwiftUI's declarative view system |
| Results that update as you type | State, `@Observable`, data flow |
| Live data from GitHub's REST API | `URLSession` async/await, `Codable`, error handling |
| A codebase that survives growth | MVVM, dependency injection, protocol-driven design |
| Profile pages you can drill into | `NavigationStack`, value-based routing |
| Favorites that work on airplane mode | SwiftData models, queries, persistence |
| Background refresh without jank | Swift 6 strict concurrency, actors, `Task` |
| Confidence it actually works | Swift Testing, XCTest UI tests |
| An app humans can install | Code signing, TestFlight, App Store review |

That is the whole 2026 iOS interview syllabus, and not one item was chosen from a syllabus — each one is pulled in by a feature the app needs **now**. The project drives the curriculum. Tech is never "assigned"; it *grows out of* Gitfolio.

---

## Scope guardrails (single student, one app)

To keep this finishable by one person on evenings and weekends:

- **One app, one platform.** iPhone, current iOS major. No iPad-optimized layouts, no watchOS, no widgets, no visionOS detours.
- **No backend of our own.** GitHub's public REST API is the server. We consume; we don't deploy servers.
- **No third-party dependencies unless a chapter explicitly justifies one.** The 2026 first-party stack (SwiftUI, SwiftData, URLSession, Swift Testing) covers everything Gitfolio needs. Learning to *not* reach for a package is a senior skill.
- **No pixel-perfect design work.** We use system components, SF Symbols, and semantic colors. The goal is engineering, not visual design.
- **Every line is yours.** The handbook explains and reviews; you implement. Snippets come piece by piece with the *why* attached — never one giant final dump to paste.

---

## Decisions locked in

Every chapter obeys these. They never change mid-track, so you never re-decide:

| Decision | Locked value |
|---|---|
| Track type | **Future track** — no Mac yet; chapters are executable later, absorbable now |
| Product | **Gitfolio** — search GitHub users, rich profile view, offline favorites, background refresh (same product as the Android handbook; concepts bridge explicitly) |
| Language | **Swift 6** with strict concurrency enabled — no `@unchecked Sendable` escape hatches |
| UI | **SwiftUI** only — no UIKit screens, no storyboards |
| State | **Observation framework** (`@Observable`) — not the legacy `ObservableObject`/`@Published` pair |
| Networking | **URLSession async/await + Codable** — no Alamofire |
| Persistence | **SwiftData** — not Core Data, not SQLite wrappers |
| Dependencies | **Swift Package Manager** — no CocoaPods, no Carthage |
| Testing | **Swift Testing** (`@Test`, `#expect`) for unit tests; **XCTest** for UI tests only |
| IDE | **Xcode, latest stable** — commands given for the current release |
| Bundle identifier | `dev.gitfolio.app` |
| Deployment target | Current iOS major version |

If you ever see a tutorial online using `ObservableObject`, storyboards, or CocoaPods — that's the pre-2026 world. This handbook does not use deprecated APIs, period.

---

## The tech stack, justified by the project

| Technology | The Gitfolio need that justifies it — *why now* |
|---|---|
| **Swift 6 (strict concurrency)** | Every file we write. Strict concurrency because background refresh + UI updates *will* race without compiler-checked isolation — Swift 6 makes the data race a compile error, not a Tuesday-night crash. |
| **SwiftUI** | The search screen, profile view, favorites list. Declarative UI means the screen is a function of state — the same mental model as Compose on Android. |
| **Observation (`@Observable`)** | Typed search text must re-render results instantly. `@Observable` gives fine-grained, low-boilerplate view updates. Android's `ViewModel` + `StateFlow` ≈ an `@Observable` class the view owns. |
| **URLSession + async/await** | Fetching `https://api.github.com/users/...`. Built in, async-native, free. Android's Retrofit + OkHttp ≈ `URLSession` with a thin typed client we write ourselves. |
| **Codable** | GitHub's JSON → Swift structs, compiler-generated. Android's Moshi/kotlinx.serialization ≈ `Codable`. |
| **SwiftData** | Favorites must survive airplane mode and app relaunch. Android's Room ≈ SwiftData: annotated model classes, queries, an on-disk store. |
| **Swift concurrency (actors, `Task`)** | Background refresh must never block the main thread or corrupt shared state. Android's coroutines + `Dispatchers` ≈ Swift's `Task` + actor isolation. |
| **Swift Package Manager** | The one dependency manager Apple ships and Xcode understands natively. Android's Gradle dependencies ≈ SPM packages. |
| **Swift Testing + XCTest** | Refactoring the networking layer without tests is gambling. Swift Testing is the 2026 unit-test standard; XCTest remains the UI-automation layer. |
| **Xcode + TestFlight** | The only road to a real iPhone and the App Store. Android Studio ≈ Xcode; Play Internal Testing ≈ TestFlight. |

---

## The Roadmap

Eleven chapters. Each one exists because the previous chapter created the pain that justifies it.

| File | Chapter | Introduces |
|---|---|---|
| [00-platform-and-toolchain.md](00-platform-and-toolchain.md) | The Apple platform and toolchain | The vocabulary of the ecosystem: Xcode, targets, schemes, bundle IDs, simulators, signing — the map you need before writing any code. |
| [01-swift-for-the-project.md](01-swift-for-the-project.md) | Swift, exactly as much as Gitfolio needs | Structs vs classes, optionals, protocols, closures, value semantics — the working subset, not the whole language. |
| [02-first-swiftui-screen.md](02-first-swiftui-screen.md) | The search screen in SwiftUI | Views as functions of state, view composition, modifiers, previews — Gitfolio's first visible screen. |
| [03-state-and-observation.md](03-state-and-observation.md) | State and the Observation framework | `@State`, `@Observable`, `@Bindable`, data flow rules — why typing in the search field updates the list. |
| [04-networking-github-api.md](04-networking-github-api.md) | Networking: URLSession and Codable | Async requests, JSON decoding, typed errors, a real GitHub API client — live data on screen. |
| [05-architecture-mvvm.md](05-architecture-mvvm.md) | Architecture: MVVM and dependency injection | View models, protocol-backed services, injection for testability — the structure that survives chapters 6-10. |
| [06-navigation.md](06-navigation.md) | Navigation | `NavigationStack`, value-based destinations, programmatic navigation — search results that drill into profiles. |
| [07-swiftdata-persistence.md](07-swiftdata-persistence.md) | SwiftData: offline saved profiles | `@Model`, `ModelContainer`, queries, offline-first favorites — Gitfolio works on airplane mode. |
| [08-concurrency.md](08-concurrency.md) | Swift concurrency, properly | Actors, `Sendable`, structured tasks, `@MainActor`, background refresh — Swift 6 strictness paying rent. |
| [09-testing.md](09-testing.md) | Testing Gitfolio on iOS | Swift Testing suites, fake services via DI, XCTest UI tests — proof the app works before every change. |
| [10-release.md](10-release.md) | Release: TestFlight and the App Store | Signing, provisioning, archives, TestFlight distribution, App Store review — Gitfolio on a real phone. |

**Why this order?** Each chapter creates the *pain* that justifies the next:
- A screen with no data is a mockup → we *need* networking (04).
- A view model doing networking inline is untestable → we *need* architecture (05).
- One screen isn't an app → we *need* navigation (06).
- Favorites vanish on relaunch → we *need* persistence (07).
- Refresh races the UI → we *need* real concurrency (08).
- Refactors without proof are gambling → we *need* tests (09).
- An app only you can run isn't shipped → we *need* release (10).

---

## How each chapter is structured

Every chapter follows the same 10-step rhythm, locked in:

| Step | What happens |
|------|--------------|
| 1 | **What we are building** — one concrete slice of Gitfolio. |
| 2 | **Why the project needs it** — the pain that makes it necessary now. |
| 3 | **New technologies required** — a table: tech → why now. |
| 4 | **Concepts** — the theory, taught properly but only what this chapter needs; enough to finish the chapter without opening anything external. |
| 5 | **Implementation plan** — every file, and the single responsibility of each. |
| 6 | **Build it piece by piece** — each snippet followed by what it does and why; never one giant dump. |
| 7 | **Run and verify** — exact commands, expected output, how to *prove* it works. |
| 8 | **How it flows** — an ascii trace of the request/data path. |
| 9 | **A senior's review** — what production would demand; tradeoffs table (chosen vs alternative vs when the alternative wins). |
| 10 | **Exercises** — 3-5 implementation tasks. No solutions. |

Plus the future-track addition: every chapter opens with *"No Mac yet? What you can still absorb from this chapter."*

You write every file. The handbook explains every line's *why*.

---

## Hardware & cost strategy (read before buying anything)

You need a Mac eventually. Here is the honest 2026 buying advice:

### The budget champion: a used M1 Mac mini

- **What to buy:** used/refurbished **M1 Mac mini, 16 GB RAM, 256 GB SSD**. Apple Silicon changed the math — a 2020 M1 still compiles Swift faster than most Intel Macs ever did, still runs the latest stable Xcode, and the used market has made it the cheapest legitimate entry into iOS development.
- **Minimum specs, non-negotiable:** Apple Silicon (M1 or newer), **16 GB RAM** (8 GB chokes when Xcode + Simulator + a browser run together — you know this pain from your 8 GB Windows machine), 256 GB SSD (Xcode plus simulator runtimes eat ~50 GB alone; keep headroom).
- **What you don't need:** a display upgrade (any monitor/TV with HDMI works), a MacBook (portability costs double), the newest chip (Gitfolio compiles in seconds on an M1).
- **Check before buying used:** it boots to a signed-out macOS (no Activation Lock), and it can run the **current macOS major** — the latest stable Xcode requires it.

### Cloud Macs: a stopgap, not a home

Renting a cloud Mac (MacStadium, AWS EC2 Mac, and similar) gets you a real Xcode over remote desktop today. Use it, if at all, only to *taste* the toolchain — because:

- **Rent outruns ownership fast.** A few months of hourly or dedicated-instance pricing exceeds a used M1 mini that you then own forever.
- **Latency poisons the feedback loop.** SwiftUI's superpower is instant previews; a remote desktop round-trip turns "instant" into "annoying," and you'll practice less.
- **Device testing is crippled.** You cannot plug your iPhone into a data center. Chapter 10 (signing, TestFlight, real-device debugging) genuinely wants local hardware.

**The plan:** absorb chapters 00-09 on Windows now, save toward the used M1 mini, and treat a cloud Mac only as an optional bridge if the wait gets long.

> **Industry lens:** real iOS teams treat local Macs as developer workstations and put *cloud* Macs where they actually belong — CI. Every pull request triggers a build-and-test run on rented Mac runners (GitHub Actions macOS runners, Xcode Cloud, MacStadium fleets), while humans develop on local Apple Silicon. The pattern you'll live in a job is exactly the one this handbook recommends: own the machine you type on, rent the machines that run your pipelines.

---

## The Android ↔ iOS Rosetta Stone

You built Gitfolio once. This is the translation table the chapters keep expanding:

| You knew it as (Android) | You'll know it as (iOS) |
|---|---|
| Kotlin | Swift 6 |
| Jetpack Compose | SwiftUI |
| ViewModel + StateFlow | `@Observable` class |
| Retrofit + OkHttp | URLSession async/await |
| Moshi / kotlinx.serialization | Codable |
| Room | SwiftData |
| Coroutines + Dispatchers | Tasks + actors |
| Gradle dependencies | Swift Package Manager |
| JUnit + Compose testing | Swift Testing + XCTest |
| Android Studio | Xcode |
| applicationId | Bundle identifier (`dev.gitfolio.app`) |
| Play Internal Testing | TestFlight |

Same app, same architecture, different vocabulary. That's the whole trick.

---

## The End-Goal Checklist

By the last chapter — from memory and understanding, not from copy-paste:

- [ ] Speak the Apple ecosystem's language: target, scheme, bundle ID, entitlement, provisioning profile, simulator runtime, archive — and explain each to someone else.
- [ ] Read and write idiomatic Swift 6: structs by default, optionals handled honestly, protocols for seams, strict concurrency satisfied without escape hatches.
- [ ] Build a SwiftUI screen as a function of state and explain exactly what triggers a re-render.
- [ ] Wire `@Observable` state through views and say precisely why it replaced `ObservableObject`.
- [ ] Call a REST API with URLSession async/await, decode it with Codable, and model failures as typed errors.
- [ ] Structure an app as MVVM with injected, protocol-backed services — and explain what breaks without the seams.
- [ ] Navigate with `NavigationStack` and value-based routing, including programmatic navigation.
- [ ] Persist offline data with SwiftData and explain how it mirrors Room.
- [ ] Explain actor isolation, `Sendable`, and `@MainActor` — and why Swift 6 makes data races compile errors.
- [ ] Test with Swift Testing (fakes via DI) and drive the UI with XCTest.
- [ ] Describe the full release path: signing → provisioning → archive → TestFlight → App Store review.
- [ ] Translate any Gitfolio concept between Android and iOS on demand.

---

**Start here:** [Chapter 00 — The Apple platform and toolchain](00-platform-and-toolchain.md). No Mac required to start absorbing.

*You are the engineer. I am the senior sitting next to you. The Mac can wait — the fluency can't. Let's build.*
