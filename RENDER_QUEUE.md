# Suki · Render queue

The one live list of planned work. Nothing here is built until Ivan says **render** for the named item, and then **build**.
States: `Awaiting Render` · `Approved — awaiting Build` · `Building` · `Shipped` · `Blocked`.
Items are `Q## · Subsystem: Feature`. IDs are never reused. Each item takes the next minor version when it's built.

| ID | Item | State | Prototype | Notes |
|---|---|---|---|---|
| Q01 | Fixes: confirm labels, search, swap, rate line | Shipped · 2.5 | [Suki prototype](https://claude.ai/artifact/GYRLsBqjns8tCFveFhAhE8) | Light. Blank red confirm buttons are the urgent one |
| Q03 | Spending: over time, calendar, Undo, Show more, new day | Shipped · 2.6 | same | Medium. Show more and new-day refresh added from the stress test |
| Q02 | Prices: a sourced price database and browsing by category | Shipped · 2.7 | same | Medium. 100 prices with sources, checked 31 Oct 2026 |
| Q04 | Look: soft-edge bar, dock position, tokens, Accessibility, item glyphs | Shipped · 2.8 | same | Medium |
| Q05 | Data: keep your data safe | Approved — awaiting Build | none (wireframe skipped by Ivan) | Light to medium. From the stress test, A2 |
| Q06 | Tidy-ups: amounts, backup values, rate timeout, long totals | Approved — awaiting Build | none (wireframe skipped by Ivan) | Light. From the stress test, A3 |
| Q07 | Onboarding: welcome card, tips and Help | Approved — awaiting Build | [Onboarding prototype](https://claude.ai/artifact/FHaHJmMntjWM9eeDrrDkN9) | Medium. Builds after Q06, as 2.11 |

**Render:** 31 Oct 2026, 22:56 · Ivan: "render all, then build" · scope: Q01–Q06 exactly as written in HANDOFF.md, built in the order listed above (2.5 to 2.10).

**Render:** 31 Oct 2026, 23:20 · Ivan: "render" · scope: Q07 exactly as written in HANDOFF.md, built after Q06 (2.11). **Build:** awaiting. The "then build" above covered Q01–Q06 only, so Q07 needs its own "build".

Handoffs: [HANDOFF.md](HANDOFF.md). Recon behind these: the Suki project docs `suki_audit_2026-10-31.md` and `suki_stress_test_2026-10-31.md`.

## Decided

- 31 Oct 2026: the tab bar stays full size (it doesn't collapse to a pill). The app is small enough that shrinking makes no difference.
- 31 Oct 2026: onboarding is one welcome card plus tips next to what they explain (Apple's onboarding guidance), not a multi-page tour. Ivan only sees it from Settings › Help.

## Ideas, not yet queued

- Quick Till: show the change as notes and coins to expect (₱200 + ₱10 + 50¢); fit the amount chips on one row.
- iPhone SE: Save purchase and Log this bill sit under the tab bar on first view.
- A search circle beside the tab bar (four tabs plus Search), as in iOS 26.
- Nueva Ecija prices: no local tricycle fare or post-rise bus fare is published online yet; add them from price notes during the trip.
