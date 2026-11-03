# Suki · Render queue

The one live list of planned work. Nothing here is built until Ivan says **render** for the named item, and then **build**.
States: `Awaiting Render` · `Approved — awaiting Build` · `Building` · `Shipped` · `Blocked`.
Items are `Q## · Subsystem: Feature`. IDs are never reused. Each item takes the next minor version when it's built.
**Release order** (below the table) is the order to build in. Render places the item in it (at the end unless Ivan says where), with "needs Q##" in its reason for anything that must ship first; the Build that ships an item removes it in the same push. The [Render queues](https://imperialfox.github.io/render-queue/) dashboard reads it for Up next and Next build.

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
| Q17 | Home: exchange rate card | Shipped · 2.19 | [Smart add prototype](https://claude.ai/artifact/KmqSWPKWGBSEWDjMQEgCkF) ("Rate above") | Light. After Q16 |
| Q14 | Logging: Smart add | Shipped · 2.20 | same | Medium to heavy. Folds in the quick add Recon's suggested Q14. After Q17 |
| Q15 | Logging: the Siri inbox | Shipped · 2.21 | none (slim follow-on to Q14) | Light. Quick add Recon (B), cut down. After Q14 |
| Q12 | Look: calendar tints and price range strip | Shipped · 2.16 | [Q12 prototype](https://claude.ai/artifact/NFwAtWyj5ERxgyGifutbeS) | Light to medium. Visual audit (B), without the week strip. Built before Q13 at Ivan's word |
| Q18 | Quick Till: note press | Approved — awaiting Build | [Note press prototype](https://claude.ai/artifact/EsJMmBNf71Sm48FDttcpLS) ("iOS way" feel) | Light to medium. Phase 1 of 4 of the till drawer idea; spec in the project doc `idea_till_note-press_notes.md`, plan in the project doc `q18_till_drawer-and-note-press_blueprint.md`. Finger tilt, Fly and Slot with a setting, and the new note and coin materials. After Q13 |
| Q19 | Quick Till: till drawer | Approved — awaiting Build | same | Heavy. Phase 2 of 4: the hidden drawer, opening and shutting the iOS way, the scroll chain and the knock. Empty inside. After Q18 |
| Q20 | Quick Till: drawer contents and fullness | Approved — awaiting Build | same | Medium. Phase 3 of 4: notes land in their compartments, the fullness gauge and the overloaded state. After Q19 |
| Q21 | Quick Till: the haul and maker's mark | Approved — awaiting Build | same | Light. Phase 4 of 4: the ten-swipe hand-over-hand pull and "Designed by Ivan". After Q20 |
| Q22 | Spending: pounds at the rate you paid | Shipped · 2.22 | none (skipped by Ivan, like Q05 and Q06) | Light. Rate history Recon's Milestone A, in the project doc `idea_rate_history_notes.md`: totals in pounds add each purchase at its own rate, and a back-dated purchase gets that day's ECB rate. Built before Q23 |
| Q23 | Convert: rate history | Shipped · 2.23 | [Rate history prototype](https://claude.ai/artifact/PMTmqDCE7i2cXavLkqYekA) (version 1793642745-fdc9, on prototype kit 1.0.0) | Medium. Milestone B in the same doc: the page from Convert's rate row, why it moved, sourced news notes, and history that never depends on one service. After Q22 |

## Release order

Build top to bottom; each still needs its own **build**. One line per item: `N. Q## — reason`, with "needs Q##" for anything that must ship first. Names live in the table above.

1. Q18 — phase 1 of the till drawer; fine after the trip
2. Q19 — needs Q18
3. Q20 — needs Q19
4. Q21 — needs Q20

**Render:** 31 Oct 2026, 22:56 · Ivan: "render all, then build" · scope: Q01–Q06 exactly as written in HANDOFF.md, built in the order listed above (2.5 to 2.10).

**Render:** 31 Oct 2026, 23:20 · Ivan: "render" · scope: Q07 exactly as written in HANDOFF.md, built after Q06 (2.11). **Build:** 1 Nov 2026, Ivan: "build q07 - onboarding" · shipped as 2.11.

**Render:** 1 Nov 2026, 08:26 · Ivan: "render" · scope: Q08, Q09, Q10, Q11 and Q16 exactly as written in HANDOFF.md and as prototyped, built in that order (each takes the next version when it lands). Q12–Q15 are not rendered. **Build (Q08):** 1 Nov 2026, 10:04, Ivan: "Build Q08" · shipped as 2.12. **Build (Q09):** 1 Nov 2026, 10:48, Ivan: "Q09 (Search shows your own purchases and notes) build" · shipped as 2.13. **Build (Q10):** 1 Nov 2026, 11:43, Ivan: "Q10 (calendar and bar doors on Spending) build" · shipped as 2.14. **Build (Q11):** 1 Nov 2026, 12:17, Ivan: "Q11 build" · shipped as 2.15. **Build (Q16):** 1 Nov 2026, 14:43, Ivan: "Q16 Build" · shipped as 2.18.

**Render:** 1 Nov 2026, 09:33 · Ivan: "im happy to render but queue the[m] as two seperate items" · scope: Q17 and Q14 exactly as written in HANDOFF.md and as prototyped, built after Q16, Q17 first (*default*: the light one first, so it can land before the 7 Nov trip). Q12, Q13 and Q15 are not rendered. **Build (Q17):** 1 Nov 2026, 20:01, Ivan: "Suki Q17 Build" · shipped as 2.19. **Build (Q14):** 2 Nov 2026, 00:04, Ivan: "Suki Q14 Build" · shipped as 2.20.

**Render:** 1 Nov 2026, 09:45 · Ivan, answering which suggested items to approve: Q13 "Right after Q11", Q15 "Render the slim version now" · scope: Q13 exactly as the locked prototype and its spec (built after Q11, before Q16); Q15 exactly as written in HANDOFF.md (built after Q14). Q12 is not rendered: Ivan wants to go through it as a wireframe and prototype first. **Build (Q13):** 1 Nov 2026, 13:07, Ivan: "Q13 build" · shipped as 2.17. **Build (Q15):** 2 Nov 2026, 07:14, Ivan: "Suki Q15 Build" · shipped as 2.21.

**Render:** 1 Nov 2026, 09:56 · Ivan: "render" · scope: Q12 exactly as written in HANDOFF.md and as prototyped (calendar tints and the price range strip), built after Q15. **Build:** 1 Nov 2026, 12:46, Ivan: "Q12 Build" (ahead of Q13–Q15, which keep their order) · shipped as 2.16.

**Render:** 1 Nov 2026, 13:09 · Ivan: "render", then chose "All four, Q18–Q21" · scope: Q18, Q19, Q20 and Q21 exactly as written in HANDOFF.md and as prototyped ("iOS way" feel), built one at a time in that order, after the items already approved; each starts only when Ivan says build for it.

**Render:** 2 Nov 2026, 18:22 · Ivan: "render" (after "bring up the prototype again just to see now where we are at") · scope: Q22 and Q23 exactly as written in HANDOFF.md, Q23 as prototyped, with the defaults written there; Q22 is built first, then Q23. Each starts only when Ivan says build for it. Neither depends on Q18–Q21. Q22–Q25 were suggested as placeholders in the till game Recon; those numbers weren't claimed, so these take them. **Build (Q22):** 3 Nov 2026, 17:28, Ivan: "Suki Q22 Build" · shipped as 2.22, with 2.22.1 for the day's format. **Build (Q23):** 3 Nov 2026, 18:10, Ivan: "Suki Q23 Build" · shipped as 2.23.

Handoffs: [HANDOFF.md](HANDOFF.md). Recon behind these: the Suki project docs `suki_audit_2026-10-31.md`, `suki_stress_test_2026-10-31.md`, `suki_navigation_audit_2026-11-01.md` and `suki_visual_motion_audit_2026-11-01.md` and `suki_quick_add_recon_2026-11-01.md`; the till drawer's spec and phases: `idea_till_note-press_notes.md` and `q18_till_drawer-and-note-press_blueprint.md`; rate history (Q22, Q23): `idea_rate_history_notes.md`.

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

- 3 Nov 2026: Rate history refuses a reply with a day jumping more than 10%, not the handoff's "about 5%": the real ECB series has a 6.8% day (24 Jun 2016), which 5% would throw away (Q23's build).
- 3 Nov 2026: Rate history's news notes link only to the BSP, the Bank of England or the PSA. The prototype's 16 Oct note ("Peso passes ₱63", put down to US inflation) was left out, as no such record says it; the 2008, 2016 and 2022 notes went in with Bank of England statements (Q23's default).

## Ideas, not yet queued

Sorted by priority, highest first: what's broken or helps on the trip (7 Nov – 2 Dec), then groundwork, then polish. Nothing here has an ID or an approval yet; each goes through wireframe, prototype and Render before it joins the table.

1. iPhone SE: Save purchase and Log this bill sit under the tab bar on first view.
2. Nueva Ecija prices: no local tricycle fare or post-rise bus fare is published online yet; add them from price notes during the trip.
3. Prices by region, using the town from Q16.
4. Back-dated purchases use Rate history first (added 3 Nov 2026, Q23's build): Q22's one-day lookup could read the saved history and snapshot before asking Frankfurter, so a purchase logged for an earlier day offline gets its real rate at once instead of "estimated". Light.
5. Screen and element IDs (added 3 Nov 2026): every screen, section and element gets its own clear name (like `quickadd-sheet`), and anything that shows up in more than one place also gets a group name, so every copy can be viewed together. First step: an ID map (screens, then their parts, then the group names) to check before any code changes. Medium.
6. Assets kit (added 3 Nov 2026): switch every element over to the tuning and assets of Ivan's assets kit (coming soon). Waits for the kit, and easier after idea 4: each group swaps once instead of copy by copy. The two can't run at the same time; both touch every screen.
7. A search circle beside the tab bar (four tabs plus Search), as in iOS 26.
8. Smart add: a receipt already works through iPhone's Live Text (copy the text from a photo, paste it in). Help could say so.
9. Search rows: make the peso price the only bold figure (visual audit finding 10; default keeps the pounds).
10. Rows glide when editing moves a purchase (Q11 covers saving, deleting and Undo only).
11. Chart bars: switch their entrance from the borrowed ripple to Suki's settle (visual audit finding 9).
12. Smart add: the prototype's "Try" example chips were left out of Q14 (they'd put made-up purchases a tap from his real log). They could come back as examples that only fill the box with a clearly made-up line, or as a Help section.
13. Smart add: the flip (the card turning over on its middle) was prototyped beside the fade; the fade was kept. Kept here for the record.
14. Rate history, later (from its Recon, 2 Nov 2026): compare two dates with two fingers, as in Stocks (medium); your real rate against the reference, noted when changing money (medium); copy a summary for family (light).
