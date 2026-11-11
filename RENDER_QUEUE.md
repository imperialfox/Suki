# Suki · Render queue

The one live list of planned work. Nothing here is built until Ivan says **render** for the named item, and then **build**.
States: `Awaiting Render` · `Approved — awaiting Build` · `Building` · `Shipped` · `Blocked`.
Items are `Q## · Subsystem: Feature`. IDs are never reused. Each item takes the next minor version when it's built.
**Release order** (below the table) is the order to build in. Render places the item in it (at the end unless Ivan says where), with "needs Q##" in its reason for anything that must ship first; the Build that ships an item removes it in the same push. Render also fills the item's **Size** in the table (Light, Light to medium, Medium, Medium to heavy or Heavy, the effort guessed in its handoff) and ends its Release order line with the approval stamp `(Ivan, 1 Nov 2026)`. The [Render queues](https://imperialfox.github.io/render-queue/) dashboard reads it for Up next and Next build, and the Size column for each item's size ring.

| ID | Item | State | Size | Prototype | Notes |
|---|---|---|---|---|---|
| Q01 | Fixes: confirm labels, search, swap, rate line | Shipped · 2.5 | | [Suki prototype](https://claude.ai/artifact/GYRLsBqjns8tCFveFhAhE8) | Light. Blank red confirm buttons are the urgent one |
| Q03 | Spending: over time, calendar, Undo, Show more, new day | Shipped · 2.6 | | same | Medium. Show more and new-day refresh added from the stress test |
| Q02 | Prices: a sourced price database and browsing by category | Shipped · 2.7 | | same | Medium. 100 prices with sources, checked 31 Oct 2026 |
| Q04 | Look: soft-edge bar, dock position, tokens, Accessibility, item glyphs | Shipped · 2.8 | | same | Medium |
| Q05 | Data: keep your data safe | Shipped · 2.9 | | none (wireframe skipped by Ivan) | Light to medium. From the stress test, A2 |
| Q06 | Tidy-ups: amounts, backup values, rate timeout, long totals | Shipped · 2.10 | | none (wireframe skipped by Ivan) | Light. From the stress test, A3 |
| Q07 | Onboarding: welcome card, tips and Help | Shipped · 2.11 | | [Onboarding prototype](https://claude.ai/artifact/FHaHJmMntjWM9eeDrrDkN9) | Medium. Builds after Q06, as 2.11 |
| Q08 | Navigation: missing doors | Shipped · 2.12 | | [Q08–Q11 prototype](https://claude.ai/artifact/FeN6KP83zyBJrWmh2465Dt) | Light to medium. From the navigation audit (A) and visual audit finding 8 |
| Q09 | Search: your records in results | Shipped · 2.13 | | same | Medium. Navigation audit (B). After Q08 |
| Q10 | Spending: calendar and bar doors | Shipped · 2.14 | | same | Light. Navigation audit (C). After Q09 |
| Q11 | Motion: sheets and rows | Shipped · 2.15 | | same | Medium. Visual audit (A). After Q10 |
| Q13 | Quick Till: bigger buttons and change as cash | Shipped · 2.17 | | [Quick Till prototype](https://claude.ai/artifact/1HLP63FZ3DXfqo7vTdEg8g) | Light to medium. Visual audit (C); spec in the project doc `q13_till_change-as-cash_spec.md`. After Q11 |
| Q16 | Logging: location | Shipped · 2.18 | | same as Q08 (item 12) | Light to medium. Prototyped as "Q14"; Q12–Q15 are suggested by other Recon. After Q13 |
| Q17 | Home: exchange rate card | Shipped · 2.19 | | [Smart add prototype](https://claude.ai/artifact/KmqSWPKWGBSEWDjMQEgCkF) ("Rate above") | Light. After Q16 |
| Q14 | Logging: Smart add | Shipped · 2.20 | | same | Medium to heavy. Folds in the quick add Recon's suggested Q14. After Q17 |
| Q15 | Logging: the Siri inbox | Shipped · 2.21 | | none (slim follow-on to Q14) | Light. Quick add Recon (B), cut down. After Q14 |
| Q12 | Look: calendar tints and price range strip | Shipped · 2.16 | | [Q12 prototype](https://claude.ai/artifact/NFwAtWyj5ERxgyGifutbeS) | Light to medium. Visual audit (B), without the week strip. Built before Q13 at Ivan's word |
| Q18 | Quick Till: note press | Shipped · 2.24; fix (only the two boxes can be selected) shipped · 2.24.1 | | [Note press prototype](https://claude.ai/artifact/EsJMmBNf71Sm48FDttcpLS) ("iOS way" feel) | Light to medium. Phase 1 of 4 of the till drawer idea; spec in the project doc `idea_till_note-press_notes.md`, plan in the project doc `q18_till_drawer-and-note-press_blueprint.md`. Finger tilt, Fly and Slot with a setting, and the new note and coin materials. After Q13 |
| Q19 | Quick Till: till drawer | Shipped · 2.25 | | same | Heavy. Phase 2 of 4: the hidden drawer, opening and shutting the iOS way, the scroll chain and the knock. Empty inside. After Q18 |
| Q20 | Quick Till: drawer contents and fullness | Shipped · 2.26 | Medium | same | Medium. Phase 3 of 4: notes land in their compartments, the fullness gauge and the overloaded state. After Q19 |
| Q21 | Quick Till: the haul and maker's mark | Shipped · 2.27 | Light | same | Light. Phase 4 of 4: the ten-swipe hand-over-hand pull and "Designed by Ivan". After Q20 |
| Q22 | Spending: pounds at the rate you paid | Shipped · 2.22 | | none (skipped by Ivan, like Q05 and Q06) | Light. Rate history Recon's Milestone A, in the project doc `idea_rate_history_notes.md`: totals in pounds add each purchase at its own rate, and a back-dated purchase gets that day's ECB rate. Built before Q23 |
| Q23 | Convert: rate history | Shipped · 2.23 | | [Rate history prototype](https://claude.ai/artifact/PMTmqDCE7i2cXavLkqYekA) (version 1793642745-fdc9, on prototype kit 1.0.0) | Medium. Milestone B in the same doc: the page from Convert's rate row, why it moved, sourced news notes, and history that never depends on one service. After Q22 |
| Q24 | Navigation: Door Rules | Shipped · 2.28 | Light to medium | none (UI consistency audit strips) | UI consistency audit of 2.27, findings 1, 2, 4, 5, 7, 8 and the delete wording in 6. After Q21 |
| Q25 | Interface: Screen IDs | Shipped · 2.29 | Light to medium | none | The same audit, finding 20 (was idea 5). After Q24 |
| Q26 | Interface: Value Set and Test | Shipped · 2.30 | Light to medium | none | The same audit, findings 18, 19, 22, part of 21. After Q25 |
| Q27 | Interface: Parts Kit Pop-ups | Shipped · 2.31 (2.31.1) | Medium | the Parts gallery | The same audit, findings 3, 6, 10 to 12, 14, 21; sheets, alerts, toasts, the kit runs the motion. Trip guard. After Q26 |
| Q28 | Interface: Parts Kit Controls and Presses | Shipped · 2.32 | Medium | the Parts gallery | The same audit, findings 9, 13, 15; glass and solid presses, rows and card doors, chips, segmented controls, switches, the tab bar and top bar. Trip guard. After Q27 |
| Q29 | Interface: Presses and Tap Areas | Shipped · 2.33 | Light | none | The same audit, findings 16, 17. After Q28 |
| Q30 | Interface: Element Sheet | Approved — awaiting Build | Medium | none | The same audit, finding 20 (element sheet). After Q28 |
| Q31 | Data: Never Save Before Loading | Shipped · 2.34 | Light | none (wireframe skipped by Ivan) | Cross-audit M01 (F1). Phase 0: on 6 Nov only if phone-checked that evening, else first on the trip |
| Q32 | Tests: Safari Engine and a Steady Suite | Approved — awaiting Build | Light to medium | none | Cross-audit M08, M17 (ideas list 5). Tests and GitHub only, no app version |
| Q33 | Data: Other Windows and an Error Notice | Shipped · 2.35 | Light to medium | none (wireframe skipped by Ivan) | Cross-audit M02, M16, M15. After Q31 |
| Q34 | Rate: Sanity Check | Shipped · 2.36 | Light | none (wireframe skipped by Ivan) | Cross-audit M03 (F6) |
| Q35 | Prices: Data Checks, Age, Rail Fare and Units | Shipped · 2.37 | Light | none (wireframe skipped by Ivan) | Cross-audit M12, M04, M06 data half |
| Q36 | Search: Stricter Matching | Shipped · 2.38 | Light to medium | none (wireframe skipped by Ivan) | Cross-audit M05 (F3). After Q35 |
| Q37 | Prices: Expansion, Stage 1 | Shipped · 2.39 | Medium | none (wireframe skipped by Ivan) | Cross-audit M07 stage 1. After Q36 |
| Q38 | Prices: Expansion, Stage 2 and Clean-up | Approved — awaiting Build | Medium | none (wireframe skipped by Ivan) | Cross-audit M07 stage 2, M13. After Q37 |
| Q39 | Interface: Spacing and Type Names | Approved — awaiting Build | Medium | none | Cross-audit M18. No visual change. After Q30, from 3 Dec |
| Q40 | Interface: Kit 1.3.0, Zoom and Contrast | Approved — awaiting Build | Light to medium | the Parts gallery | Cross-audit M09, M10, M11, Erase gap (ideas list 15). Needs Q39 and parts kit 1.3.0 (its own Render). From 3 Dec |

## Release order

Build top to bottom; each still needs its own **build**. One line per item: `N. Q## — reason`, with "needs Q##" for anything that must ship first. Names live in the table above.

1. Q38 — prices, stage 2 and clean-up; needs Q37 (shipped as 2.39) (Ivan, 6 Nov 2026)
2. Q30 — the element sheet; needs Q28 (shipped as 2.32); moved behind Q31 to Q38 by the 6 Nov Render, from 3 Dec (Ivan, 5 Nov 2026)
3. Q39 — spacing and type names; needs Q30; from 3 Dec (Ivan, 6 Nov 2026)
4. Q40 — kit 1.3.0, zoom and contrast; needs Q39 and parts kit 1.3.0 (its own Render, not yet given); from 3 Dec (Ivan, 6 Nov 2026)

### Any time

- Q32 — tests in Safari's engine and a steady suite; no app version; best before Q33 (Ivan, 6 Nov 2026)

**Render:** 6 Nov 2026, 10:46 · Ivan: "Render", then chose "Phases 0 to 5" and, for wireframes, "Yes, skip them" · scope: Q31 to Q40, the Phases 0 to 5 pieces of the cross-audit Blueprint (6 Nov 2026, project note `suki_cross_audit_blueprint_2026-11-06.md`), exactly as written in HANDOFF.md, with every default in its shared block (the trip rule, Q31 on 6 Nov only if phone-checked that evening, wireframes skipped for Q31 to Q38, other windows reload, contrast S07, main button rule S08), built one at a time in Release order; each starts only when Ivan says build for it. Q30 (already approved) moves behind Q38. Not rendered: the plan's Phase 6 (screens), which needs its wireframe first, and Phase 7; parts kit 1.3.0, which has its own Render in `imperialfox/parts-kit`, so Q40 waits for it.

**Render:** 5 Nov 2026, 09:17 · Ivan: "Render for 1-7" · scope: Q24 to Q30, the seven items of the UI consistency Blueprint (draft 1, 5 Nov 2026), exactly as written in HANDOFF.md, with every default in its shared block (the kit move split in two, the kit version, S03 to S06, the tab bar under a sheet, the trip guard), built one at a time in Release order; each starts only when Ivan says build for it. They replace the parts kit move blueprint of 4 Nov (its A, B and C are Q25, Q26, Q27 and Q28). Q27 and Q28 ship before the 7 Nov trip only if live and checked on the phone by the evening of 6 Nov; otherwise from 3 Dec. **Build (Q24):** 5 Nov 2026, 09:33, Ivan: "Suki Q24 Build" · shipped as 2.28. **Build (Q25):** 5 Nov 2026, 10:42, Ivan: "Suki Q25 Build" · shipped as 2.29. **Build (Q26):** 5 Nov 2026, 14:24, Ivan: "Suki Q26 Build" · shipped as 2.30. **Build (Q27):** 5 Nov 2026, 15:07, Ivan: "Suki Q27 Build" · shipped as 2.31 on kit 1.2.0, with 2.31.1 for the welcome card scrolling on a small iPhone (the version before it is commit `9246418`; the tag `suki-2.30` couldn't be pushed from Claude's workspace). **Build (Q28):** 5 Nov 2026, 18:40, Ivan: "Suki Q28 Build" · shipped as 2.32 (the version before it is commit `e060624`, 2.31.1). **Build (Q29):** 5 Nov 2026, 19:42, Ivan: "Suki Q29 Build" · shipped as 2.33 (the version before it is commit `05f8132`, 2.32).

**Render:** 31 Oct 2026, 22:56 · Ivan: "render all, then build" · scope: Q01–Q06 exactly as written in HANDOFF.md, built in the order listed above (2.5 to 2.10).

**Render:** 31 Oct 2026, 23:20 · Ivan: "render" · scope: Q07 exactly as written in HANDOFF.md, built after Q06 (2.11). **Build:** 1 Nov 2026, Ivan: "build q07 - onboarding" · shipped as 2.11.

**Render:** 1 Nov 2026, 08:26 · Ivan: "render" · scope: Q08, Q09, Q10, Q11 and Q16 exactly as written in HANDOFF.md and as prototyped, built in that order (each takes the next version when it lands). Q12–Q15 are not rendered. **Build (Q08):** 1 Nov 2026, 10:04, Ivan: "Build Q08" · shipped as 2.12. **Build (Q09):** 1 Nov 2026, 10:48, Ivan: "Q09 (Search shows your own purchases and notes) build" · shipped as 2.13. **Build (Q10):** 1 Nov 2026, 11:43, Ivan: "Q10 (calendar and bar doors on Spending) build" · shipped as 2.14. **Build (Q11):** 1 Nov 2026, 12:17, Ivan: "Q11 build" · shipped as 2.15. **Build (Q16):** 1 Nov 2026, 14:43, Ivan: "Q16 Build" · shipped as 2.18.

**Render:** 1 Nov 2026, 09:33 · Ivan: "im happy to render but queue the[m] as two seperate items" · scope: Q17 and Q14 exactly as written in HANDOFF.md and as prototyped, built after Q16, Q17 first (*default*: the light one first, so it can land before the 7 Nov trip). Q12, Q13 and Q15 are not rendered. **Build (Q17):** 1 Nov 2026, 20:01, Ivan: "Suki Q17 Build" · shipped as 2.19. **Build (Q14):** 2 Nov 2026, 00:04, Ivan: "Suki Q14 Build" · shipped as 2.20.

**Render:** 1 Nov 2026, 09:45 · Ivan, answering which suggested items to approve: Q13 "Right after Q11", Q15 "Render the slim version now" · scope: Q13 exactly as the locked prototype and its spec (built after Q11, before Q16); Q15 exactly as written in HANDOFF.md (built after Q14). Q12 is not rendered: Ivan wants to go through it as a wireframe and prototype first. **Build (Q13):** 1 Nov 2026, 13:07, Ivan: "Q13 build" · shipped as 2.17. **Build (Q15):** 2 Nov 2026, 07:14, Ivan: "Suki Q15 Build" · shipped as 2.21.

**Render:** 1 Nov 2026, 09:56 · Ivan: "render" · scope: Q12 exactly as written in HANDOFF.md and as prototyped (calendar tints and the price range strip), built after Q15. **Build:** 1 Nov 2026, 12:46, Ivan: "Q12 Build" (ahead of Q13–Q15, which keep their order) · shipped as 2.16.

**Render:** 1 Nov 2026, 13:09 · Ivan: "render", then chose "All four, Q18–Q21" · scope: Q18, Q19, Q20 and Q21 exactly as written in HANDOFF.md and as prototyped ("iOS way" feel), built one at a time in that order, after the items already approved; each starts only when Ivan says build for it. **Build (Q18):** 4 Nov 2026, 08:31, Ivan: "Suki Q18 Build" · shipped as 2.24. **Build (Q19):** 4 Nov 2026, 12:38, Ivan: "Suki Q19 Build" · shipped as 2.25. **Build (Q20):** 4 Nov 2026, 19:25, Ivan: "Suki Q20 Build" · shipped as 2.26. **Build (Q21):** 4 Nov 2026, 20:20, Ivan: "Suki Q21 Build" · shipped as 2.27.

**Render:** 4 Nov 2026, 10:27 · Ivan: "render and build" · scope: the Q18 fix (only the two boxes can be selected on the Till, 2.24.1) exactly as written in HANDOFF.md, folded into Q18 at his word (10:25). **Build:** same message · shipped as 2.24.1.

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
- 6 Nov 2026: hotel nights and flights won't go in the price data, as their prices change daily; Search says so instead (Q37). No more rough guides from blogs.
- 6 Nov 2026: a second window reloads when another saves; no merging records by id (Q33).
- 6 Nov 2026: wireframes skipped for Q31 to Q38 at Ivan's word, as nothing moves on screen.
- 11 Nov 2026: Q37 counts the audit's 85 searches strictly (the top result has a price): 50 on 2.38, 59 on 2.39, not the 65 its Done when asked. The Blueprint's "59 today" counted any result, including the wrong ones Q36 removed. Ivan: build as agreed; Q38 carries on toward 70 (Q37's build).
- 11 Nov 2026: the DA bulletin comes from Ivan's download when Claude's web tools can't open da.gov.ph (Q37's build).
- 11 Nov 2026: medicines are priced from PhilHealth's GAMOT fees (Circular 2026-0018), with a note that a pharmacy's own shelf price may be higher; the DOH price index couldn't be opened. Ivan chose this over leaving them unpriced (Q37's build).

## Ideas, not yet queued

Sorted by priority, highest first: what's broken or helps on the trip (7 Nov – 2 Dec), then groundwork, then polish. Nothing here has an ID or an approval yet; each goes through wireframe, prototype and Render before it joins the table.

1. iPhone SE: Save purchase and Log this bill sit under the tab bar on first view.
2. Nueva Ecija prices: no local tricycle fare or post-rise bus fare is published online yet; add them from price notes during the trip.
3. Prices by region, using the town from Q16.
4. Back-dated purchases use Rate history first (added 3 Nov 2026, Q23's build): Q22's one-day lookup could read the saved history and snapshot before asking Frankfurter, so a purchase logged for an earlier day offline gets its real rate at once instead of "estimated". Light.
5. Moved to Q32 (6 Nov 2026): the flaky fold check in `test_smart.py`.
6. Assets kit (added 3 Nov 2026): switch every element over to the tuning and assets of Ivan's assets kit (coming soon). Waits for the kit, and easier after Q25 (screen IDs): each group swaps once instead of copy by copy. The two can't run at the same time; both touch every screen.
7. A search circle beside the tab bar (four tabs plus Search), as in iOS 26.
8. Smart add: a receipt already works through iPhone's Live Text (copy the text from a photo, paste it in). Help could say so.
9. Search rows: make the peso price the only bold figure (visual audit finding 10; default keeps the pounds).
10. Rows glide when editing moves a purchase (Q11 covers saving, deleting and Undo only).
11. Chart bars: switch their entrance from the borrowed ripple to Suki's settle (visual audit finding 9).
12. Smart add: the prototype's "Try" example chips were left out of Q14 (they'd put made-up purchases a tap from his real log). They could come back as examples that only fill the box with a clearly made-up line, or as a Help section.
13. Smart add: the flip (the card turning over on its middle) was prototyped beside the fade; the fade was kept. Kept here for the record.
14. Rate history, later (from its Recon, 2 Nov 2026): compare two dates with two fingers, as in Stocks (medium); your real rate against the reference, noted when changing money (medium); copy a summary for family (light).
15. Moved to Q40 (6 Nov 2026): pin the kit version whose sheets that fit their content rise from below, then drop `HOST.rise()`. The kit fix itself is part of parts kit 1.3.0, its own Render.
16. Chips: take the kit's accent for a picked chip (part 18) instead of Suki's ink (added 5 Nov 2026, Q28's build). Q28 kept the ink so chips look the same at rest; the kit's way would make Search's and Spending's picked chip blue. Polish only.
17. Prices: each row's unit should match its item's (added 11 Nov 2026, Q35's build). Q35's check makes one item's rows agree with each other, not with the item: Bear Brand powdered milk (a 135 g pack) shows as ₱50 "per litre/carton", and the 13 dishes' rows say "per plate" under "per serving". The data test could check each row against the item's unit too. Fits with Q37 or Q38.
18. Prices: a cooked rice item ("kanin", per cup or plate) so "kanin" finds a price again (added 11 Nov 2026, Q36's build, its default 3). Fits with Q37 or Q38.
19. Search: an item and a place in one search ("jeepney to Cubao", "tricycle Alona Beach") shows no price since Q36, because every word must fit. Showing the item for its word, only when the other words are places Suki knows (its towns list), would bring it back without "coconut oil" finding cooking oil (added 11 Nov 2026, Q36's build). Helps; light.
20. Medicines: a pharmacy's own shelf price (Mercury Drug, Watsons) beside PhilHealth's fee, and a price for loperamide, which PhilHealth's list doesn't have (added 11 Nov 2026, Q37's build). Helps.
21. Tests: the random taps, seed 13, failed on GitHub twice (Q34 and Q37's first runs): "sheet state confirm but nothing shown" and "page behind a sheet left scaled", after opening a purchase, closing a tip and resizing to 1440×900. Both re-runs passed. Fits with Q32 (a steady suite) (added 11 Nov 2026, Q37's build). Core for the tests.
