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
| Q05 | Data: keep your data safe | Shipped · 2.9 | none (wireframe skipped by Ivan) | Light to medium. From the stress test, A2 |
| Q06 | Tidy-ups: amounts, backup values, rate timeout, long totals | Shipped · 2.10 | none (wireframe skipped by Ivan) | Light. From the stress test, A3 |
| Q07 | Onboarding: welcome card, tips and Help | Shipped · 2.11 | [Onboarding prototype](https://claude.ai/artifact/FHaHJmMntjWM9eeDrrDkN9) | Medium. Builds after Q06, as 2.11 |
| Q08 | Navigation: missing doors | Approved — awaiting Build | [Q08–Q11 prototype](https://claude.ai/artifact/FeN6KP83zyBJrWmh2465Dt) | Light to medium. From the navigation audit (A) and visual audit finding 8 |
| Q09 | Search: your records in results | Approved — awaiting Build | same | Medium. Navigation audit (B). After Q08 |
| Q10 | Spending: calendar and bar doors | Approved — awaiting Build | same | Light. Navigation audit (C). After Q09 |
| Q11 | Motion: sheets and rows | Approved — awaiting Build | same | Medium. Visual audit (A). After Q10 |
| Q16 | Logging: location | Approved — awaiting Build | same (item 12) | Light to medium. Prototyped as "Q14"; Q12–Q15 are suggested by other Recon. After Q11 |

**Render:** 31 Oct 2026, 22:56 · Ivan: "render all, then build" · scope: Q01–Q06 exactly as written in HANDOFF.md, built in the order listed above (2.5 to 2.10).

**Render:** 31 Oct 2026, 23:20 · Ivan: "render" · scope: Q07 exactly as written in HANDOFF.md, built after Q06 (2.11). **Build:** 1 Nov 2026, Ivan: "build q07 - onboarding" · shipped as 2.11.

**Render:** 1 Nov 2026, 08:26 · Ivan: "render" · scope: Q08, Q09, Q10, Q11 and Q16 exactly as written in HANDOFF.md and as prototyped, built in that order (each takes the next version when it lands). Q12–Q15 are not rendered.

Handoffs: [HANDOFF.md](HANDOFF.md). Recon behind these: the Suki project docs `suki_audit_2026-10-31.md`, `suki_stress_test_2026-10-31.md`, `suki_navigation_audit_2026-11-01.md` and `suki_visual_motion_audit_2026-11-01.md`.

## Decided

- 31 Oct 2026: the tab bar stays full size (it doesn't collapse to a pill). The app is small enough that shrinking makes no difference.
- 31 Oct 2026: onboarding is one welcome card plus tips next to what they explain (Apple's onboarding guidance), not a multi-page tour. Ivan only sees it from Settings › Help.
- 1 Nov 2026: Suki asks for location only when the arrow is tapped, never at launch, and finds the town offline (Q16).
- 1 Nov 2026: left out of the navigation audit as extra choices, not doors: links on every detail row, a Settings tab, a Notes tab.

## Ideas, not yet queued

- Quick Till: show the change as notes and coins to expect (₱200 + ₱10 + 50¢); fit the amount chips on one row.
- iPhone SE: Save purchase and Log this bill sit under the tab bar on first view.
- A search circle beside the tab bar (four tabs plus Search), as in iOS 26.
- Nueva Ecija prices: no local tricycle fare or post-rise bus fare is published online yet; add them from price notes during the trip.
- Home week strip, a price range strip on items, and calendar tints by amount (visual audit, Milestone B; suggested Q12).
- Search rows: make the peso price the only bold figure (visual audit finding 10; default keeps the pounds).
- Prices by region, using the town from Q16.
