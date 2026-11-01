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
| Q08 | Navigation: missing doors | Shipped · 2.12 | [Q08–Q11 prototype](https://claude.ai/artifact/FeN6KP83zyBJrWmh2465Dt) | Light to medium. From the navigation audit (A) and visual audit finding 8 |
| Q09 | Search: your records in results | Shipped · 2.13 | same | Medium. Navigation audit (B). After Q08 |
| Q10 | Spending: calendar and bar doors | Shipped · 2.14 | same | Light. Navigation audit (C). After Q09 |
| Q11 | Motion: sheets and rows | Shipped · 2.15 | same | Medium. Visual audit (A). After Q10 |
| Q13 | Quick Till: bigger buttons and change as cash | Shipped · 2.17 | [Quick Till prototype](https://claude.ai/artifact/1HLP63FZ3DXfqo7vTdEg8g) | Light to medium. Visual audit (C); spec in the project doc `q13_till_change-as-cash_spec.md`. After Q11 |
| Q16 | Logging: location | Shipped · 2.18 | same as Q08 (item 12) | Light to medium. Prototyped as "Q14"; Q12–Q15 are suggested by other Recon. After Q13 |
| Q17 | Home: exchange rate card | Approved — awaiting Build | [Smart add prototype](https://claude.ai/artifact/KmqSWPKWGBSEWDjMQEgCkF) ("Rate above") | Light. After Q16 |
| Q14 | Logging: Smart add | Approved — awaiting Build | same | Medium to heavy. Folds in the quick add Recon's suggested Q14. After Q17 |
| Q15 | Logging: the Siri inbox | Approved — awaiting Build | none (slim follow-on to Q14) | Light. Quick add Recon (B), cut down. After Q14 |
| Q12 | Look: calendar tints and price range strip | Shipped · 2.16 | [Q12 prototype](https://claude.ai/artifact/NFwAtWyj5ERxgyGifutbeS) | Light to medium. Visual audit (B), without the week strip. Built before Q13 at Ivan's word |
| Q18 | Quick Till: note press | Approved — awaiting Build | [Note press prototype](https://claude.ai/artifact/EsJMmBNf71Sm48FDttcpLS) ("iOS way" feel) | Light to medium. Phase 1 of 4 of the till drawer idea; spec in the project doc `idea_till_note-press_notes.md`, plan in the project doc `q18_till_drawer-and-note-press_blueprint.md`. Finger tilt, Fly and Slot with a setting, and the new note and coin materials. After Q13 |
| Q19 | Quick Till: till drawer | Approved — awaiting Build | same | Heavy. Phase 2 of 4: the hidden drawer, opening and shutting the iOS way, the scroll chain and the knock. Empty inside. After Q18 |
| Q20 | Quick Till: drawer contents and fullness | Approved — awaiting Build | same | Medium. Phase 3 of 4: notes land in their compartments, the fullness gauge and the overloaded state. After Q19 |
| Q21 | Quick Till: the haul and maker's mark | Approved — awaiting Build | same | Light. Phase 4 of 4: the ten-swipe hand-over-hand pull and "Designed by Ivan". After Q20 |

**Render:** 31 Oct 2026, 22:56 · Ivan: "render all, then build" · scope: Q01–Q06 exactly as written in HANDOFF.md, built in the order listed above (2.5 to 2.10).

**Render:** 31 Oct 2026, 23:20 · Ivan: "render" · scope: Q07 exactly as written in HANDOFF.md, built after Q06 (2.11). **Build:** 1 Nov 2026, Ivan: "build q07 - onboarding" · shipped as 2.11.

**Render:** 1 Nov 2026, 08:26 · Ivan: "render" · scope: Q08, Q09, Q10, Q11 and Q16 exactly as written in HANDOFF.md and as prototyped, built in that order (each takes the next version when it lands). Q12–Q15 are not rendered. **Build (Q08):** 1 Nov 2026, 10:04, Ivan: "Build Q08" · shipped as 2.12. **Build (Q09):** 1 Nov 2026, 10:48, Ivan: "Q09 (Search shows your own purchases and notes) build" · shipped as 2.13. **Build (Q10):** 1 Nov 2026, 11:43, Ivan: "Q10 (calendar and bar doors on Spending) build" · shipped as 2.14. **Build (Q11):** 1 Nov 2026, 12:17, Ivan: "Q11 build" · shipped as 2.15. **Build (Q16):** 1 Nov 2026, 14:43, Ivan: "Q16 Build" · shipped as 2.18.

**Render:** 1 Nov 2026, 09:33 · Ivan: "im happy to render but queue the[m] as two seperate items" · scope: Q17 and Q14 exactly as written in HANDOFF.md and as prototyped, built after Q16, Q17 first (*default*: the light one first, so it can land before the 7 Nov trip). Q12, Q13 and Q15 are not rendered.

**Render:** 1 Nov 2026, 09:45 · Ivan, answering which suggested items to approve: Q13 "Right after Q11", Q15 "Render the slim version now" · scope: Q13 exactly as the locked prototype and its spec (built after Q11, before Q16); Q15 exactly as written in HANDOFF.md (built after Q14). Q12 is not rendered: Ivan wants to go through it as a wireframe and prototype first. **Build (Q13):** 1 Nov 2026, 13:07, Ivan: "Q13 build" · shipped as 2.17.

**Render:** 1 Nov 2026, 09:56 · Ivan: "render" · scope: Q12 exactly as written in HANDOFF.md and as prototyped (calendar tints and the price range strip), built after Q15. **Build:** 1 Nov 2026, 12:46, Ivan: "Q12 Build" (ahead of Q13–Q15, which keep their order) · shipped as 2.16.

**Render:** 1 Nov 2026, 13:09 · Ivan: "render", then chose "All four, Q18–Q21" · scope: Q18, Q19, Q20 and Q21 exactly as written in HANDOFF.md and as prototyped ("iOS way" feel), built one at a time in that order, after the items already approved; each starts only when Ivan says build for it.

Handoffs: [HANDOFF.md](HANDOFF.md). Recon behind these: the Suki project docs `suki_audit_2026-10-31.md`, `suki_stress_test_2026-10-31.md`, `suki_navigation_audit_2026-11-01.md` and `suki_visual_motion_audit_2026-11-01.md` and `suki_quick_add_recon_2026-11-01.md`; the till drawer's spec and phases: `idea_till_note-press_notes.md` and `q18_till_drawer-and-note-press_blueprint.md`.

## Decided

- 31 Oct 2026: the tab bar stays full size (it doesn't collapse to a pill). The app is small enough that shrinking makes no difference.
- 31 Oct 2026: onboarding is one welcome card plus tips next to what they explain (Apple's onboarding guidance), not a multi-page tour. Ivan only sees it from Settings › Help.
- 1 Nov 2026: Suki asks for location only when the arrow is tapped, never at launch, and finds the town offline (Q16).
- 1 Nov 2026: Location's towns come from PSA's outlines (NAMRIA and PSA, through OCHA, CC BY-IGO), not GeoNames, the handoff's default: GeoNames was blocked from the build, and its GitHub copy has no San Jose City and only 1,190 of 1,642 towns (Q16's build).
- 1 Nov 2026: left out of the navigation audit as extra choices, not doors: links on every detail row, a Settings tab, a Notes tab.
- 1 Nov 2026: Smart add sits beside the form; it doesn't replace it. Home's Log card switches sides in place.
- 1 Nov 2026: turned down: Smart add as a sheet rising from the bottom. Ivan: "not a fan of it popping up from the bottom".
- 1 Nov 2026: it's called Smart add now, to build on later (usual price, suggestions and the typical note are in from the start).
- 1 Nov 2026: left out of Q12: the Home week strip. Spending's week chart already shows the same bars, and Home now has the rate card.
- 1 Nov 2026: Spending's filter matches every word in any order, like Search (asked during Q09's build). Then "Show all N in Spending" always opens the same N.
- 1 Nov 2026: the calendar tints are stronger than the Q12 prototype's, because the prototype's failed the palette check (the lightest step was too close to white, and the top two looked alike). Light goes darker, dark goes brighter.
- 1 Nov 2026: the rate card uses Suki's own icon colours as a one-off. The app style rules (no branding in the app) stay as they are; no other screen uses these colours.
- 1 Nov 2026: the till drawer and note press is its own item (Q18), not folded into Q13. Ivan: "i can imagine that its a heavy build". Number claimed only; nothing approved.
- 1 Nov 2026: the till drawer idea is split into four items built in order, Q18 to Q21 (note press, drawer, contents, haul and mark), each with its own Render, Build and version. Ivan chose the recommended split. Rendered together at 13:09; each still waits for its own build.
- 1 Nov 2026: Quick Till's buttons are Exact, 20, 50, 100, 500 and 1000 (Q13). No ₱200 (no longer made) and no coin row; buttons that change with the bill were turned down because they'd move under his thumb.

## Ideas, not yet queued

- iPhone SE: Save purchase and Log this bill sit under the tab bar on first view.
- A search circle beside the tab bar (four tabs plus Search), as in iOS 26.
- Nueva Ecija prices: no local tricycle fare or post-rise bus fare is published online yet; add them from price notes during the trip.
- Search rows: make the peso price the only bold figure (visual audit finding 10; default keeps the pounds).
- Prices by region, using the town from Q16.
- Smart add: a receipt already works through iPhone's Live Text (copy the text from a photo, paste it in). Help could say so.
- Smart add: the flip (the card turning over on its middle) was prototyped beside the fade; the fade was kept.
- Rows glide when editing moves a purchase (Q11 covers saving, deleting and Undo only).
- Chart bars: switch their entrance from the borrowed ripple to Suki's settle (visual audit finding 9).
