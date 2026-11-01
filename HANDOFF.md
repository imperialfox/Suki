# Suki · Build handoffs

One block per queue item. Each fits on one screen; long notes are linked, not pasted. Handoffs carry no personal data.

---

## Q01 · Fixes: confirm labels, search, swap, rate line
**Render:** 31 Oct 2026, 22:56, scope as below · **Build:** 31 Oct 2026 · shipped as 2.5
For: Ivan · Builder: Claude · Repo: imperialfox/Suki, from 2.4 · Needs: 2.4 live on `main`.

**Goal:** fix what's broken or misleading before the trip.
**Agreed:**
1. Red confirm buttons show their white label (`.red` no longer overrides `.cta.red`).
2. Search is stricter: short words must be nearly exact, and results far below the best match are dropped. "water" no longer shows Kwek-kwek.
3. The swap arrow is a button: it puts the other currency on top, focuses it, and the handy amounts follow (₱20 to ₱5,000 when pesos are on top).
4. The rate line says "Updated today / yesterday / 3 days ago / 22 Oct", with no clock time or second date.
5. Settings shows the rate with ₱; the example search is spelt "sinigang baboy".
**Out of scope:** new prices, layout changes.
**Done when:** all tests pass, including the new ones in `test_flows.py`. **Checks:** full suite.
**Debrief:** Built from the prototype commit unchanged. The swap trades the two boxes' places with a small slide (it fades with Reduce Motion). Tests: new checks for the button label colour, search not showing unrelated items, the swap and peso handy amounts, the plain rate line and ₱ in Settings.

## Q02 · Prices: a sourced price database and browsing by category
**Render:** 31 Oct 2026, 22:56, scope as below · **Build:** 31 Oct 2026 · shipped as 2.7 · Needs: Q01 (stricter search).

**Goal:** Search gives a real price, with its source, for what he'll actually buy and ride.
**Agreed:**
1. `js/typical.js`: 100 prices for 64 items (LTFRB fares after the 28 Sep 2026 rise, DTI suggested retail prices of 11 May 2026, supermarket and menu prices, telco promos, rough guides for street food and services), each with source, link and date. Never a guessed number.
2. 32 new catalogue items (transport, services, fast food, beer, pantry). No existing id changes.
3. Search: category chips (All, Transport, Food, Market, Drinks, Services, Essentials); All shows four per category with "Show all N", which selects that chip. Chips narrow a search too. The example chips go.
4. Item page: typical prices, then the DA card where there is one, then **You paid** (your logged purchases of it), **Log what you paid**, and price notes. The sheet is titled with the category.
**Out of scope:** Nueva Ecija-specific prices (none published).
**Done when:** tests pass; MAINTAINING.md says how to update `typical.js`.
**Debrief:** Built from the prototype unchanged, apart from merging the test lists with Q03's. Prices come from three research passes with sources (LTFRB via GMA, Philstar, Top Gear and SunStar; the DTI bulletin of 11 May 2026; Metro Supermarket; Jollibee and Mang Inasal menus; Globe; travel writers for rough guides). Nothing for San Jose City is published, so it isn't guessed. The jeepney fare rise was checked again against SunStar and GMA. Tests: browsing, Show all, chips narrowing a search, an item's typical prices and sources, You paid, and Log what you paid.

## Q03 · Spending: over time, calendar, Undo, Show more, new day
**Render:** 31 Oct 2026, 22:56, scope as below · **Build:** 31 Oct 2026 · shipped as 2.6.

**Goal:** see where the money went, day by day.
**Agreed:**
1. Range switch D · W · M · All (no 6M or Y: it's a trip) with a sliding glass knob; arrows step back through periods; the list follows the period.
2. A bar a day (a week each when All spans over two months), stacked by category, axis on the right, dotted gridlines. Tap or slide to read a day. Bars arrive in a small staggered ripple; nothing else new moves.
3. Breakdown by category with dots, share bars and percentages; tapping filters the list. Category colours checked with the palette validator, light and dark (Shopping is now purple).
4. Home's date and title open a month calendar; tap a day to see its purchases. Months step with motion that follows the direction of time.
5. Undo on deleting a purchase or price note. Rows show one detail (the place). Sideways chip rows fade at the edge with more.
6. *From the stress test (#10):* the list draws the newest 60 purchases, then a "Show 60 more" row; the total, chart and breakdown still count everything in the period.
7. *From the stress test (#7):* when the date changes (coming back to the app, or a check each minute), the screen redraws in place so "Today", the bars and the calendar move on. *Default if unanswered:* it waits while a sheet is open or a box has the cursor.
**Done when:** tests pass, including the new Spending, calendar, Show more and new-day ones.
**Debrief:** Built from the prototype, plus the two stress-test additions. Show more draws 60 at a time; with 3,000 purchases and the processor slowed 4×, Spending opens in 0.23 s (was about 2 s) and the filter keeps up at 70–140 ms a key. The new-day check runs every minute and on returning to the app, and waits while a sheet is open or a box has the cursor (the default). Tests: range switch, stepping, bar picking, breakdown filtering, calendar, Undo, Show more and the new-day redraw.

## Q04 · Look: soft-edge bar, dock position, tokens, Accessibility, item glyphs
**Render:** 31 Oct 2026, 22:56, scope as below · **Build:** 31 Oct 2026 · shipped as 2.8.

**Goal:** match the updated `ivan-app-look`.
**Agreed:**
1. Top bar has no card: a soft blurred edge from the top of the screen appears once you scroll, with the compact title.
2. Tab bar on iPhone upright sits 21pt from the bottom with 21pt sides (`--dockb`), still full size. Safe areas are `--sat/--sab/--sal/--sar`.
3. Apple's system colours as `--sys-*` tokens, light and dark; no hex in rules (a test checks). Font sizes on Apple's scale (a test checks).
4. Settings › This device › Accessibility: Reduce motion (Match iPhone, On, Off) and Slow motion. Device-only, never in backups. Reduce Motion is the `html.motion-reduced` class.
5. A glyph per catalogue item (34 glyphs). Shortcuts use Cmd on Apple devices, Ctrl elsewhere.
**Out of scope:** the tab bar collapsing (decided against, 31 Oct).
**Done when:** tests pass at every size, light and dark.
**Debrief:** Built from the prototype unchanged. Tests: font sizes on Apple's scale and no hex colours in rules (test_release), the tab bar 21pt from the bottom with 21pt sides, the soft edge appearing only after scrolling, distinct item glyphs, and Accessibility (on, back to Match iPhone, slow motion, and neither setting in backups).

## Q05 · Data: keep your data safe
**Render:** 31 Oct 2026, 22:56, scope as below (wireframe skipped by Ivan) · **Build:** 31 Oct 2026 · shipped as 2.9.

**Goal:** nothing he logged can vanish quietly. From the stress test, A2 (#1–4).
**Agreed:**
1. A backup with nothing usable in it (every record damaged) is refused, and nothing changes.
2. Before a restore or Erase, Suki keeps a safety copy of what's on the phone. Afterwards a message offers **Undo**, which puts it all back. *Default if unanswered:* the copy is kept until the next restore or erase.
3. Saved data Suki can't read, or records it has to drop, are copied somewhere safe **before** anything saves over them. Home shows a notice, and Settings › Your data gets a **Recovered data** row that saves the copy as a file. *Default if unanswered:* the copy is kept until he saves it, then he can clear it.
4. If the storage database won't open, Home says so. Purchases saved to the fallback spot are merged back in by id the next time the database opens, so none are hidden.
5. "Couldn't save" stays on screen until tapped, and an Undo message never hides it.
**Out of scope:** cloud backup, automatic backups.
**Done when:** tests reproduce each of the stress test's A2 cases and show them handled; full suite passes.
**Debrief:** Built as agreed, with the defaults: the safety copy is kept until the next restore or erase, and recovered data stays until it's saved and then cleared. Decided within scope: putting back swaps (what's there becomes the new safety copy), and money() reads ₱ and PHP so those records are kept instead of rescued. Tests reproduce each stress-test case: an all-damaged backup, an empty backup, restore and Erase with Undo and put-back, a string where purchases should be, an unreadable price note, storage that won't open then recovers (records merged, fallback cleared), and a failed save after a delete (the warning stays after Undo has gone).

## Q06 · Tidy-ups: amounts, backup values, rate timeout, long totals
**Render:** 31 Oct 2026, 22:56, scope as below (wireframe skipped by Ivan) · **Build:** 31 Oct 2026 · shipped as 2.10.

**Goal:** the small rough edges from the stress test, A3 (#5, #6, #8, #9).
**Agreed:**
1. Amounts: "12.50.5" asks you to check the amount; a pasted "1 000" reads as ₱1,000; anything that rounds to ₱0.00 is refused, on the form and in Quick Till.
2. Backups and saved data: a price above ₱10,000,000 or below ₱0.01 is treated as damaged; an impossible date like 30 Feb becomes today, like other bad dates.
3. With no signal, a rate refresh stops after two sources time out (about 12 seconds instead of 24), and doesn't try at all when the phone says it's offline. The saved rate keeps working.
4. Very long totals on Home's summary card step down a size instead of breaking across lines.
**Done when:** tests cover each case; full suite passes.

### For your iPhone (after the build)
1. Delete a purchase: the red button has words, and Undo brings it back.
2. Spending: slide your finger across the bars.
3. Scroll Search: the top edge blurs softly and the tab bar sits low like Music's.
4. Open a jeepney or beer price and tap a source link.
5. Settings › Accessibility › Reduce motion On: sheets fade instead of rising.

---
**Debrief:** Built as agreed. Decided within scope: a long total also moves Today under it, because shrinking the font alone wasn't enough on a 320-point screen. Also made one test steadier: it now reads the sheet's animation name rather than catching the fade mid-play. Tests: two dots, ₱0.00 on the form and in Quick Till, "1 000", out-of-range prices and 30 Feb in saved data, two timeouts stopping the refresh, and a ₱30,000,000 total on one line at 320 points.

## Q07 · Onboarding: welcome card, tips and Help
**Render:** 31 Oct 2026, 23:20, scope as below · **Build:** 1 Nov 2026 · shipped as 2.11.
For: Ivan, and anyone he shares Suki with on the trip · Builder: Claude · Repo: imperialfox/Suki · Needs: 2.10 (Q06) live on `main`. Prototype: [Onboarding prototype](https://claude.ai/artifact/FHaHJmMntjWM9eeDrrDkN9). Recon: Apple's [Onboarding guidance](https://developer.apple.com/design/human-interface-guidelines/onboarding).

**Goal:** someone new gets going without a tour; Ivan never sees it unless he asks.
**Agreed:**
1. **Safari sheet.** Opened in a browser tab (not from the Home Screen), Suki shows "Add Suki to your Home Screen" with three steps, **Got it** and **Not now**. It shows on each Safari open, never in the Home Screen app. *Default if unanswered:* the steps read "Tap ⋯ then Share · Choose Add to Home Screen · Open Suki from there" (check against iOS 26 Safari during Build).
2. **Welcome card.** On the first Home Screen launch with no saved data, after the launch screen: a tall sheet with the icon, "Welcome to Suki", three rows (Convert and count change, Look up fair prices, Track your spending), "Works with no signal once it's been opened" and **Continue**. It can't be dragged away. Shown once.
3. **Tips**, one at a time, next to what they explain: the Quick Till amount chips; pull to refresh on Home; swipe a purchase left on Spending; drag down on the first detail sheet. Each goes when you do it or tap ✕, and doesn't come back.
4. **Settings › Help**, its own row above About: **Show welcome** (plays it again), a **Show tips** switch (on for a fresh install, off when Suki already has data; turning it on shows every tip again), a Hidden gestures list, and the Add to Home Screen steps.
5. Seen-states and the switch are device-only, never in backups.
6. Motion as in the prototype: the welcome sheet rises after the launch fade, its rows 45 ms apart; tips fade and scale in on the gentle spring and leave quicker; Reduce motion gives fades only. Help is a push.
**Out of scope:** a multi-page tour, tips for buttons that already explain themselves, rating or permission prompts.
**Risks:** a tip must never cover a primary button or the tab bar; tips wait while a sheet is open.
**Done when:** tests cover each item, including an existing install never seeing the welcome card and a backup round trip leaving seen-states alone; full suite passes.
**Checks:** full suite; screenshots at 375 and 402 px, light and dark.
**Debrief:** Built from the prototype and the handoff. Checked within scope against iOS 26: Add to Home Screen sits under ⋯ → Share, and the new Open as Web App switch has to stay on for Suki to open on its own, so step 2 says so. The sheet's title is shortened to Add to Home Screen so it fits a 375-point screen. Help is pushed from Settings with a slide (a fade with Reduce Motion); it has no swipe-back, like Settings. A tip whose target is below the fold waits until it's scrolled into view. Tests: test_onboard.py (37 checks) covers the Safari sheet, the welcome card (fresh, locked, shown once, never on an existing install), each tip, tips waiting for sheets and staying clear of buttons and the tab bar, Help, and a backup round trip leaving onboarding alone. Every other fuzz run has tips on, and the layout check includes Help, the welcome and the Home Screen steps.


## Q08 · Navigation: missing doors
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting
For: Ivan · Builder: Claude · Repo: imperialfox/Suki · Needs: 2.11 live on `main`. Prototype: [Suki prototype · Q08–Q11](https://claude.ai/artifact/FeN6KP83zyBJrWmh2465Dt) (its last script before `boot.js` is the prototype layer). Recon: project doc `suki_navigation_audit_2026-11-01.md` (findings 1–4, 9) and `suki_visual_motion_audit_2026-11-01.md` (finding 8).

**Goal:** no dead ends. Every word that names a place is a door to it.
**Agreed:**
1. **Home's summary card is two doors.** Total spent opens Spending on All; Today opens Spending on D (today). Each caption ends in a small ›. With nothing logged, the card reads "Nothing spent yet" with one line under it.
2. **Spending's top bar gets a + circle** (only when there are purchases). It opens the same Log sheet as Quick Till's "Log this bill" and an item's "Log what you paid".
3. **Calendar:** a picked day (today or earlier) gets a row "Log a purchase on 28 Oct" ("on today" for today). It opens the Log sheet over the calendar with that date, and saving returns to the calendar.
4. **A purchase leads to its prices:** a row "Jeepney prices · Usually ₱14–17 · first 4 km ›" in its details, opening the item sheet over the purchase. *Default if unanswered:* the row shows only on a whole-word match (the item's name or English name, plurals allowed), so a loose match (quick-add Recon finding 5: Spaghetti → Massage) never offers the wrong prices.
5. **Words become doors:** Search's old-rate note "Refresh it on Convert" goes to Convert and refreshes; the empty Price notes sheet and its footer link to Search; Search with no match offers "Log "…" as a purchase", which opens the Log sheet with the name filled in and the cursor in the amount.
6. **Settings rows open things:** Last backed up → Export a backup; Saved exchange rate → Convert; About's Add to your Home Screen → the same steps sheet as Help (subtitle "The steps, for a new phone").
7. **Empty Spending:** no chart or range switch. One card: "No spending yet", one line, and a Log a purchase button.
**Out of scope:** links on every detail row, a Settings tab, a Notes tab, category names.
**Where to look:** `screens.js` (scrHome, scrSpending, purchaseDetail, staleRate, searchResults, scrSettings), `ui.js` (renderBar, sheetHTML calendar and notes), `events.js` (ACT).
**Risks:** each new sheet opened from a sheet must return to it (push). Q07's tips still find their targets.
**Done when:** a test per door, including the whole-word rule; full suite passes. **Checks:** full suite; screenshots at 375 and 402 px, light and dark.

## Q09 · Search: your records in results
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting · Needs: Q08 (built first). Prototype and Recon as Q08 (navigation audit findings 5 and 7).

**Goal:** Search finds anything he's logged, not only the price list.
**Agreed:**
1. **With text:** Prices (catalogue matches, as now), then **In your purchases** (every word must appear in the item, place, where bought, category or notes; newest first; three rows, then "Show all N in Spending", which opens Spending on All filtered by the same words), then **In your price notes** (rows open the item).
2. **Nothing matches:** "No clear match…" and Q08's "Log "…" as a purchase". If only his own records match, the no-match message doesn't show; the Log row still does.
3. **Search's All view** starts with a "Your price notes · 2 notes from the trip ›" row opening the Price notes sheet. The Settings row stays as a second door.
4. The placeholder reads "Prices, your purchases, your notes".
**Out of scope:** the search circle beside the tab bar (still an idea), changes to Spending's filter.
**Done when:** tests for each group, Show all, and the notes row; full suite passes. **Checks:** full suite; screenshots at 375 px, light and dark.

## Q10 · Spending: calendar and bar doors
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting · Needs: Q09 (built first). Prototype and Recon as Q08 (navigation audit findings 6 and 8).

**Goal:** time is easy to move through, and the screen says one thing at a time.
**Agreed:**
1. **Spending's period label** ("Today", "This week", "October", "Since 23 Oct") becomes an accent button with a small calendar glyph. It opens the calendar on that period's month (All opens this month; D opens with that day picked).
2. **A picked bar narrows the list** to that day (or week), under a line "Showing Yesterday only · Show this week". Tapping a purchase in that list keeps the pick; tapping anywhere else clears it, as now.
3. **Help › Hidden gestures** adds "Tap Home's title · To open the calendar (Spending's date does too)".
**Out of scope:** a calendar tab, changing what the chart shows.
**Done when:** tests for the label door per range, the narrowed list, the kept pick and the Help row; full suite passes. **Checks:** full suite.

## Q11 · Motion: sheets and rows
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting · Needs: Q10 (built first). Prototype as Q08. Recon: visual audit findings 1–3 and 9.

**Goal:** things arrive and leave, so he never has to re-read a screen to see what changed.
**Agreed:**
1. **Closing a sheet** slides it down off the screen while the page behind grows back, as one movement, quicker than the arrival (about 330 ms, `cubic-bezier(.3,0,.25,1)`); the dim fades. Going back to a sheet underneath: that sheet is simply there (no second rise) and the closing one slides off over it. iPad and Mac: shrink to .94 and fade (220 ms). Reduce Motion: a 200 ms fade. Every close path: ✕, Cancel, the dim, Escape, dragging down, and after a save or delete.
2. **"Settle"** is defined once in `motion.js`: a 12 px drop to place with opacity 0 → 1 on the `ripple` spring, rows 45 ms apart. Q13 (Quick Till) reuses it if it builds later.
3. **Rows:** a saved purchase settles into whatever list it lands in (Home's Recent, Spending, a calendar day); rows and headers below glide to their new place on `gentle`; a row that goes (deleted, or pushed out of Recent) fades and shrinks to .94 where it was (220 ms); Undo plays the arrival again.
4. **Saving on Home:** the button shows "✓ Saved" for about 1.4 s, then returns. "Purchase saved" gets **Undo**, which removes it again.
5. Slow motion also slows the page-behind scale (today it's a fixed 0.45 s in CSS).
6. **Kept still:** tabs switch instantly; figures never animate; Settings, Help and Convert don't move.
**Out of scope:** the Home week strip, the price range strip and calendar tints (visual audit Milestone B, not rendered).
**Risks:** redraws use innerHTML, so measure before and after the redraw (FLIP); the prototype wraps `render()`, but the build should do it where the change happens. Never block taps mid-animation, and a second close mid-way must still work.
**Done when:** motion-on tests: a closing sheet is still on screen mid-way and gone after, no stray copies left, a new row has a running animation, rows below move, Reduce Motion only fades; full suite passes. **Checks:** full suite; frames at 4× slow motion, light and dark.

## Q16 · Logging: location
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting · Needs: Q11 (built first). Prototyped as "Q14" in the Q08–Q11 prototype (item 12); renumbered because the quick add Recon (`suki_quick_add_recon_2026-11-01.md`) suggests Q14 and Q15.

**Goal:** the place fills itself in, privately and offline.
**Agreed:**
1. **Default town:** a new purchase's Location starts as the place of the newest purchase that day that has one (today from Home or Spending's +; that day from the calendar). The label says "Location · from earlier today" or "· from that day". On Home it also shows beside "More details · Quezon City".
2. **An arrow inside Location** fills the nearest town, labelled "· near you", and the box tints briefly. iPhone's permission prompt comes on the first tap only, never at launch. Denied: "Location is off for Suki. Type the town, or allow it in Settings." No town within 40 km: "No town found near you. Type it in instead."
3. **The town list lives inside the app:** offline, and the position never leaves the phone. *Default if unanswered:* Philippine cities and municipalities with positions from GeoNames (CC BY 4.0), credited in Settings › About.
4. Typing in or clearing Location stops the filling for that purchase; the next purchase starts again. Editing an old purchase never changes its place.
5. Location gets the full width; Where bought goes underneath.
**Out of scope:** shop names, tracking in the background, prices by region (an idea).
**Risks:** the purchase log and quick add work (other chats) may replace Home's three fields with one box. *Default if unanswered:* if that lands first, the town default goes wherever that form shows the place, and the arrow stays in the Log sheet's Location. GeoNames may be blocked from the workspace: use a GitHub copy, or ask Ivan to attach the file.
**Done when:** tests for the defaults (today, that day, none), the arrow with a mocked position (allowed, denied, nothing near), typing stopping the fill, and no prompt at launch; full suite passes. **Checks:** full suite; screenshots at 375 px, light and dark.
**For your iPhone (after the build):** whether iPhone remembers Allow between launches.
