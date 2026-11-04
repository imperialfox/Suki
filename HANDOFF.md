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
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** 1 Nov 2026, 10:04 · shipped as 2.12.
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
**Debrief:** Built from the prototype and the handoff, with the whole-word default (item 4). Decided within scope:
- The whole-word rule is its own search over item names (`strictItemFor`): Suki's loose match didn't recognise "Jeepney to Cubao" or "Chickenjoy bucket" at all, so gating it would have hidden the row for the trip's most common purchases. The longest whole name wins. Aliases don't count, so "Water", "Coke" and "San Miguel" get no row yet.
- The Home Screen row in About opens the steps sheet with ✕ (not the locked Safari version).
- The empty Spending card is capped at phone width, so its button doesn't stretch across a Mac window.
Tests: `test_doors.py` (42 checks) covers each door, the whole-word rule (Spaghetti, Mangoes and Banana have loose matches but no row; plurals and longer names still match) and the iPad pane. The empty-Spending check in `test_flows.py` now expects the new card and checks the chart, range switch and + appear after the first purchase. Full suite: 341 checks, all passing (offline timed out once side by side on a 2-processor machine and passed alone, a known issue). Screenshots at 375 and 402 px, light and dark, plus iPad, Mac and landscape.
**For your iPhone:** (1) Tap the total and then Today on Home: each opens the right Spending. (2) The + beside Spending's large title feels natural. (3) Log on a past day from the calendar and land back on the calendar. (4) A jeepney purchase shows "Jeepney prices", the way you actually type it.
**Left for later:** "You paid" still uses the loose match (quick add Recon finding 5, fixed with Q14). Safe aliases (water, beer brand names) could join the whole-word rule.

## Q09 · Search: your records in results
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** 1 Nov 2026, 10:48 · shipped as 2.13 · Needs: Q08 (built first). Prototype and Recon as Q08 (navigation audit findings 5 and 7).

**Goal:** Search finds anything he's logged, not only the price list.
**Agreed:**
1. **With text:** Prices (catalogue matches, as now), then **In your purchases** (every word must appear in the item, place, where bought, category or notes; newest first; three rows, then "Show all N in Spending", which opens Spending on All filtered by the same words), then **In your price notes** (rows open the item).
2. **Nothing matches:** "No clear match…" and Q08's "Log "…" as a purchase". If only his own records match, the no-match message doesn't show; the Log row still does.
3. **Search's All view** starts with a "Your price notes · 2 notes from the trip ›" row opening the Price notes sheet. The Settings row stays as a second door.
4. The placeholder reads "Prices, your purchases, your notes".
**Out of scope:** the search circle beside the tab bar (still an idea), changes to Spending's filter.
**Done when:** tests for each group, Show all, and the notes row; full suite passes. **Checks:** full suite; screenshots at 375 px, light and dark.
**Debrief:** Built from the handoff and the prototype's Q09 layer. One question came up during the build:
- **Spending's filter now matches each word too** (Ivan, 1 Nov 2026, asked during the build, so it widens "Out of scope: changes to Spending's filter" by that one change). Before, it only found the words side by side, so "Show all" for "cubao jeepney" would have opened Spending showing nothing. Both now use one matcher (`matcher()`), with Spending's fields (how paid included), so the count always agrees. One-word filtering works as before.
Decided within scope: the category chips narrow the prices only, not his records (as the prototype). Each group's header shows its count. Price notes are newest first.
Tests: `test_search.py` (35 checks): each group, Show all landing on the same six in Spending, words in any order in both places, the no-match rules, the notes row (and not on a single category), hostile text, an empty app, and no sideways scroll. Full suite: 383 checks, all passing. Screenshots at 375 px, light and dark.
**For your iPhone:** (1) Search "jeepney" after a few rides: your rides show under the prices. (2) "Show all … in Spending" lands on the same purchases. (3) Search's All view starts with Your price notes.
**Left for later:** the search circle beside the tab bar (still an idea).

## Q10 · Spending: calendar and bar doors
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** 1 Nov 2026, 11:43 · shipped as 2.14 · Needs: Q09 (built first). Prototype and Recon as Q08 (navigation audit findings 6 and 8).

**Goal:** time is easy to move through, and the screen says one thing at a time.
**Agreed:**
1. **Spending's period label** ("Today", "This week", "October", "Since 23 Oct") becomes an accent button with a small calendar glyph. It opens the calendar on that period's month (All opens this month; D opens with that day picked).
2. **A picked bar narrows the list** to that day (or week), under a line "Showing Yesterday only · Show this week". Tapping a purchase in that list keeps the pick; tapping anywhere else clears it, as now.
3. **Help › Hidden gestures** adds "Tap Home's title · To open the calendar (Spending's date does too)".
**Out of scope:** a calendar tab, changing what the chart shows.
**Done when:** tests for the label door per range, the narrowed list, the kept pick and the Help row; full suite passes. **Checks:** full suite.
**Debrief:** Built from the handoff and the prototype's Q10 layer. Decided within scope:
- **With a day's bar picked,** the label reads that day, so its door opens the calendar with that day picked (as D does). A picked week opens on its Monday's month. The pick stays, so closing the calendar comes back to the same view.
- **The way back names the period properly:** "Show this week", "Show last week", "Show all of November", "Show all since 23 Oct". The prototype lowercased the whole label ("show october").
- **What keeps the pick:** a purchase row or Show more in the list, any sheet including tapping outside it to close, and the details pane on iPad and Mac (otherwise tapping Edit beside the list would have widened it).
- **Fixed on the way:** with a day picked, the list widened the moment a finger touched anything else, so the filter's ✕ (near the bottom of the page) and Export as CSV (under the list) jumped away and the tap was lost. Now the headline goes back at once and the list widens just after the tap lands.
- An empty picked day says "Nothing spent on this day." under the line.
Tests: `test_timedoors.py` (37 checks): the label door for All, W, an earlier week, M, D and yesterday, a picked day and a picked week; the narrowed list, its line and both ways back; the pick kept through ✕, tapping outside and the iPad pane; the filter and CSV working first time with a day picked; the Help row; no sideways scroll; screenshots at 375 px, light and dark. Full suite: 420 checks, all passing (run locally with the pinned Playwright 1.56 pointed at a newer Chromium, as before).
**For your iPhone:** (1) On Spending, tap "This week" under the total: the calendar opens on this month. (2) Tap yesterday's bar: the list shows only yesterday, and "Show this week" brings it all back. (3) Open a purchase from that list and close it: yesterday is still picked. (4) The blue date with its little calendar reads as tappable in sunlight.
**Left for later:** nothing new.

## Q11 · Motion: sheets and rows
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** 1 Nov 2026, 12:17 · shipped as 2.15 · Needs: Q10 (built first). Prototype as Q08. Recon: visual audit findings 1–3 and 9.

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
**Debrief:** Built from the handoff and the prototype's Q11 layer, but where the change happens rather than by wrapping `render()`. Decided within scope:
- **Sheets:** `renderSheet()` spots a close (fewer sheets than before) and moves the old sheet into a new `#leaving` layer that can't be tapped, so every close path gets the exit with nothing extra, and the app has already moved on (tab bar back, the next tap works) while it slides. Ids are stripped from the copy.
- **Dragging down** now closes at once and the exit carries on from the finger's position (it used to slide to 110% and close 0.2 s later).
- **Back to the sheet underneath:** it also comes back scrolled where it was (the stack keeps its scroll), so "simply there" is literal.
- **Rows** use `rowsBefore()` / `rowsAfter()` around each change (save, delete, both Undos). Only a purchase that's new to the list settles, so a calendar coming back into view after logging on a day keeps its other rows still. Rows off screen don't move.
- **The tick** shows with motion off and with Reduce Motion too (it's feedback, not movement); only the tick's small pop is motion. Undo after a save says "Purchase removed".
- **Out of the agreed list:** editing a purchase ("Save changes") doesn't glide rows yet, and the chart bars keep their ripple (the audit's idea to switch them to settle wasn't in the handoff).
Tests: `test_motion.py` (63 checks): the exit mid-way and gone after for ✕, Escape, the dim, Cancel and dragging down (a short drag still springs back); the page behind on the quicker curve and slowed by Slow motion (1.8 s and 1.32 s at 4×, 0 s with motion off); back to the sheet underneath with no rise and its scroll kept; two quick closes and a tap mid-exit; settle on Spending, Recent and a calendar day, rows below moving, the row pushed out of Recent and a deleted row shrinking away, Undo settling it back; Saved and Undo on Home (and gone from storage); iPad's .94 shrink in 220 ms; Reduce Motion fades only (200 ms); tabs, Settings and Convert still; frames at 4× in light and dark. Full suite: 483 checks, all passing (pinned Playwright 1.56 pointed at a newer Chromium, as before).
**For your iPhone:** (1) Open a purchase and close it with ✕, then by dragging it down: it should slide away with the page growing back as one movement. (2) Log a purchase on Home: the button says "✓ Saved" and the row drops into Recent. (3) Delete a purchase on Spending, then Undo: it shrinks away, then drops back in. (4) Settings › Accessibility › Slow motion on, and watch a sheet close: does the drop feel like a coin landing? (5) Edit a purchase and close Edit: the purchase is just there, not rising again.
**Left for later:** rows gliding when an edit moves a purchase to another day; the chart bars switching from ripple to settle (visual audit finding 9).

## Q13 · Quick Till: bigger buttons and change as cash
**Render:** 1 Nov 2026, 09:45, scope as below · **Build:** 1 Nov 2026, 13:07, Ivan: "Q13 build" · shipped as 2.17 · Needs: Q11 (built first: reuse its "settle" from `motion.js`).
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Suki Quick Till prototype](https://claude.ai/artifact/1HLP63FZ3DXfqo7vTdEg8g) (locked in by Ivan, 1 Nov, 08:23). Full spec, tokens and the left-out list: project doc `q13_till_change-as-cash_spec.md`. Recon: visual audit findings 6 and 7.

**Goal:** at a counter, big targets, and change shown the way it will look in his hand.
**Agreed** (each as in the spec):
1. **Buttons:** Exact, 20, 50, 100, 500, 1000, all 44 pt on one row; ₱20 looks like the coin (nickel with a bronze ring). Labels match the notes ("1000"); VoiceOver says "Add a ₱1,000 note" / "Add a ₱20 coin". Clear becomes a ✕ inside the cash box.
2. **The change as cash** under the figure: notes largest first, fanned, number up the left edge; then coins in small piles (8 px overlap); the ₱20 coin two-tone and the ₱5 nine-sided.
3. **Bundles:** up to four of a note fan out; five or more become one bundle with "×34" on the front; fan, bundle and coins wrap, never cut off; the count changes without animating.
4. **Breakdown:** notes 1000, 500, 100, 50; coins ₱20, ₱10, ₱5, ₱1, 25¢, 5¢, 1¢ (no ₱200, no 50¢: 50¢ shows as two 25¢).
5. **Colours as tokens,** the same in light and dark (`--note-50` … `--coin-ring`, values in the spec).
6. **Motion:** new pieces settle 45 ms apart, removed ones shrink away in 160 ms, staying ones glide on `gentle`; the figure never animates; Reduce Motion fades only.
**Out of scope:** banknote artwork of any kind (BSP rules; see the spec), a coin row, buttons that change with the bill.
**Where to look:** `screens.js` (scrTill, the change block), `events.js` (till keys), `css/app.css`, `motion.js`. Keep the `.denoms` class (Q07's tip points at it); `.tillout` keeps a minimum height.
**Done when:** tests: the six buttons fit at 375 px, random amounts break down exactly, bundles at ₱34,750 and ₱999,999 stay inside the card, rapid taps leave no stray pieces, VoiceOver labels; full suite passes. **Checks:** full suite; screenshots at 375 and 402 px, light and dark.
**For your iPhone:** the settle at full speed; note colours against real notes in daylight; the edge numbers at a glance.
**Debrief:** Built from the locked prototype and the spec. Decided within scope:
- **Settle and leave are Q11's,** given an optional size: `MOTION.settle(el, i, 10)` for the 10 px drop and `MOTION.leave(g, 160, .6)` for the 160 ms shrink. Purchases still use 12 px and .94.
- **Only the cash row redraws.** Typing or a button changes the words in place and keeps each piece that stays (by its key), as the prototype did; a full redraw (switching tabs) draws it still. Removed pieces shrink away as copies, so switching tabs mid-way leaves nothing behind.
- **The buttons keep their actions** (`cashAdd`, `cashExact`, `cashClear`), so the tip and older tests still work. Labels are centred: the app's buttons inherit text alignment, which the prototype's didn't.
- **The ✕** doesn't take the cursor, so the keyboard stays up if it was (as in the prototype).
Tests: `test_till.py` (73 checks). Full suite: 597 of 600 side by side; the 3 were Q11 checks in `test_motion.py` timing out on this 2-processor machine (the known issue), and that file passed 63 of 63 on its own, before and after this change (pinned Playwright 1.56 pointed at a newer Chromium, as before). Also checked by eye: screenshots at 375 and 402 px, light and dark.
**For your iPhone:** (1) On Till, tap 500 then 1000 for a ₱789.50 bill: do the notes and coins drop in like coins on a counter? (2) Hold a real ₱100, ₱500 and ₱1,000 next to the screen in daylight: do the colours match? (3) Can you read the edge numbers on the fanned notes at a glance? (4) In a pile of 25¢ coins, the coins behind are partly covered: is that still clear? (5) Tap the ✕ while typing: the keyboard should stay up.
**Left for later:** nothing new. Q18 restyles these notes and coins.

## Q16 · Logging: location
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** 1 Nov 2026, 14:43, Ivan: "Q16 Build" · shipped as 2.18 · Needs: Q13 (built first; Q13 was slotted in after Q11 on 1 Nov, 09:45). Prototyped as "Q14" in the Q08–Q11 prototype (item 12); renumbered because the quick add Recon (`suki_quick_add_recon_2026-11-01.md`) suggests Q14 and Q15.

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
**Debrief:** Built as prototyped, in `js/locate.js` (new), with the outlines in `js/towns.js` (made by `tools/towns.py`). Decisions within scope:
- **Town data:** not GeoNames (agreed 3's default). Its site is blocked from the workspace, and the GitHub copy of its city list misses San Jose City and a quarter of all towns. Used the outlines of all 1,642 cities and municipalities from PSA (NAMRIA and PSA, through OCHA's COD-AB, CC BY-IGO; PSGC Q3 2026, via faeldon/philippines-json-maps), credited in Settings › About. 133 KB, loaded with the app, read on the first tap.
- **Finding the town:** the outline the point is in; else the nearest outline within 40 km (beaches, boats). Better than the nearest centre point near borders: Cubao is Quezon City, Cebu IT Park is Cebu City. Names as people say them ("Makati", "Cebu City").
- **An auto-filled place is worked out again on every draw,** so it follows the data (a deleted purchase, a draft reloaded the next day). Where it came from is kept in the form state only (`locFrom`), never saved with the purchase.
- **One message the handoff didn't word:** when the phone gives no answer, "Couldn't find where you are. Type the town in instead."
- **The arrow is on every purchase form,** editing included: tapping it is his choice. Only the automatic fill is limited to new purchases.
- The risk didn't arise: Smart add (Q14) hasn't landed, so the town default sits in Home's form and the Log sheet.
Tests: `test_location.py` (46 checks, listed in `MAINTAINING.md`). Full suite: 645 of 646 side by side; the one was `test_data.py`'s "Export shows Preparing first", which passed 67 of 67 on its own, with and without this change (the known small-machine timing). Pinned Playwright 1.56 pointed at a newer Chromium, as before. Screenshots at 375 px, light and dark, checked by eye.
**For your iPhone:** (1) On the trip, tap the arrow: does iPhone ask once, and does it fill the right town? (2) Close and reopen Suki, tap again: does it remember Allow? (3) Try it with no signal. (4) After logging one purchase with a place, does the next one start there, with "from earlier today"? (5) On a beach or a boat, does it still find the nearest town?
**Left for later:** nothing new. Prices by region (already an idea) can use `townAt`.

## Q17 · Home: exchange rate card
**Render:** 1 Nov 2026, 09:33, scope as below · **Build:** 1 Nov 2026, 20:01, Ivan: "Suki Q17 Build" · shipped as 2.19 · Needs: Q16 (built first; Q08 changes the summary card under it).
For: Ivan, and family he shows Suki to · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Smart add prototype](https://claude.ai/artifact/KmqSWPKWGBSEWDjMQEgCkF), switch "Rate above".

**Goal:** anyone glancing at Home sees today's rate first.
**Agreed:**
1. **A card above the total spent card:** "Exchange rate" (Footnote), **£1 = ₱76.12** (Title 2, bold, two decimals), then "Updated 2h ago" (relative times, then the date). The whole card is one button.
2. **Suki's icon colours, as a one-off:** the icon's navy gradient (`#173874` → `#06102b`) with its blue glow (`#4b84ff`, soft, top left), white text, radius 20, springy press. They go in as named tokens (`--suki-top`, `--suki-bottom`, `--suki-glow`), used here only. The style rules don't change.
3. **Tapping opens Convert.** *Default if unanswered:* no refresh on the tap; Convert's own refresh stays as it is.
4. **No saved rate yet:** the card reads "Exchange rate · Get today's rate on Convert". An old rate keeps its white text ("Updated 3 days ago"), never red.
5. iPhone on its side and iPad: the card heads the dashboard's left column, above the summary card.
**Out of scope:** the rate the other way round (₱100 = £…), a rate chart, alerts.
**Where to look:** `screens.js` (scrHome), `css/app.css` (tokens), `rate.js` (the saved rate and its time).
**Done when:** tests for the rate and its age, the door to Convert, and the no-rate card; white on both navy ends passes 4.5:1; full suite passes. **Checks:** full suite; screenshots at 375 and 402 px, light and dark.
**For your iPhone:** white on navy in bright sun.
**Debrief:** Built from the prototype's "Rate above" card. The default applied: tapping opens Convert with no refresh.
- **Decisions within scope:** the age reads "Updated just now", "5 min ago", "2h ago", then "yesterday", "3 days ago" and the date, and moves on in place every 30 s (no redraw). The label and age are white at 80%, not full white, as in the prototype; they still pass 4.5:1 (lowest 5.4:1 under the glow). The shadow, rim and softer white went in as tokens beside the three named ones, all used by this card only. With no rate the line is Headline weight. Convert's own rate line is unchanged.
- **Contrast:** white is 11.3:1 on the top navy, 18.8:1 on the bottom and 7.3:1 at the brightest spot of the glow.
Tests: `test_ratecard.py` (47 checks, listed in `MAINTAINING.md`). Full suite: 693 of 693 side by side, pinned Playwright 1.56 pointed at a newer Chromium, as before. Screenshots at 375 and 402 px, light and dark, plus on its side and iPad, checked by eye.
**For your iPhone:** (1) Pull down on Home to update: is the rate card at the top? (2) Is the white readable in bright sun? (3) Tap it: does Convert open? (4) Leave Home open a few minutes: does "Updated … ago" move on?
**Left for later:** nothing new.

## Q14 · Logging: Smart add
**Render:** 1 Nov 2026, 09:33, scope as below · **Build:** 2 Nov 2026, 00:04, Ivan: "Suki Q14 Build" · shipped as 2.20 · Needs: Q17 (built first; Q11's "Saved" button and settle, and Q16's town, are reused).
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Smart add prototype](https://claude.ai/artifact/KmqSWPKWGBSEWDjMQEgCkF) (the reader is inlined; its sample purchases are made up). Recon: project doc `suki_quick_add_recon_2026-11-01.md` (findings 1, 4, 5).

**Goal:** type, say or paste a purchase in one line, see what Suki understood, save in one tap. The form stays.
**Agreed:**
1. **Two sides of Home's Log card:** the form, as now, and Smart add. A pill on the "Log a purchase" heading switches them ("Smart add" ↔ "Full form"). Suki remembers the last side on this device (not in backups).
2. **Switching is a fade after iPhone Duo's fold:** the card stays put; the typing box is the hinge and slides between its two spots; everything else dissolves through a blur that grows with distance from it (cubic), rows 28 ms apart, and the new side resolves from blur and slight dimness, rows 45 ms apart. Reduce Motion: a plain crossfade. Interruptible.
3. **The reader** (new `js/reader.js`), word rules only, offline: amounts (₱, P, PHP, pesos, k; English and Tagalog number words; "one twenty"; "1:20 pesos"; £ at the saved rate, flagged), days (today, *kahapon*, *kanina*, weekdays, dates, nearest year), places (from X to Y, in, at, to), where bought, paid with, category (learned words → price list → clue words → shop → a tinted guess). Several at once: a new line, "also", or between two amounts; a day, place or "both by card" said once applies to the whole line.
4. **The preview** asks only what's missing (How much? · What was it?), an either/or for a tie, flags a future date and pounds. Save purchase / Save N purchases (with Undo). "Edit in the form" fills the form side. Batch rows open the usual Log sheet to check.
5. **It learns:** changing a category remembers the word. Settings › Your data › Words Suki has learned lists them, each removable. Kept in backups.
6. **Smart from the start:** *your usual* price (the middle of the last three of the same thing, same place first), editable; suggestions from his own purchases while typing words, before any number (three, tapping fills the line); a plain note "Within / More than / Less than the typical ₱x–y" on whole-word price-list matches only.
7. **His words are kept** with each purchase (`said`, shown as "You typed: …" in its details). A new field; older data and backups are unaffected.
8. **From the Recon:** P50, "50 pesos" and 2k also work in the form's amount box; logged purchases use the whole-word matcher Q08 adds (Search keeps its looser one). Q16's town fills Location when the line names no place.
**Out of scope:** the Siri inbox and multi-line paste detection (suggested Q15), any AI, a bottom sheet (turned down), the flip.
**Where to look:** `screens.js` (scrHome, purchaseForm, purchaseDetail), `events.js`, `catalog.js` (matching), `storage.js` and `backup.js` (`said`, learned words), `motion.js` (the fade), new `js/reader.js`.
**Risks:** the Recon's 136 test phrases weren't kept: write a synthetic phrase file (about 120, including every case named in the Recon) before the reader. Blur on a moving card can stutter on iPhone: blur only the card's rows, and fall back to the crossfade if frames drop at 4× slow motion.
**Done when:** the phrase tests pass; tests for the sides and the remembered side, each ask, the either/or and learning, batch save with Undo, Edit in the form, usual price, suggestions, the typical note, "You typed", and learned words through a backup round trip; a motion-on test that rapid switching leaves no stray copy; full suite passes. **Checks:** full suite; screenshots at 375 and 402 px, light and dark; frames at 4×.
**For your iPhone:** whether the keyboard hides the preview; whether Siri dictation reads well; whether the fade stays smooth.
**Debrief:** Built from the prototype, with the reader ported into `js/reader.js` and the side, preview and learning in `js/smart.js` (new); the fade is `MOTION.fold`. Decisions within scope:
- **Phrases:** the Recon's were lost, as warned. Wrote 123 made-up ones (135 purchases) in `tests/fixtures/smart_phrases.json`, covering every case the Recon names. Writing them found and fixed six reader slips the prototype had: "PHP 1,250" split at the comma, "sim card" read as paying by card, "jeep 14 november 21st" read as 14 Nov, "at the airport" kept "The", "limang daan hotel" ran into the next word, and an opening "On Tuesday at SM Megamall," didn't share the place.
- **Whole-word matching** (agreed 8): `wordMatch()` in `catalog.js` (the prototype's rule: names and other spellings as whole words, plurals, one-letter slips in long words). The reader, Your usual and **"You paid"** use it, since "You paid" was the one place logged purchases used the loose match (Recon finding 5). The prices row keeps Q08's `strictItemFor`, and Search its own.
- **Learned words** live in `D.learned` (IndexedDB key `learned`), in backups, the safety copy, Erase and the restore sheet. A backup or safety copy from before 2.20 leaves the phone's words as they are, rather than emptying them.
- **His words:** a line holding several purchases gives each its own part where the split is clear (`jeepney 14`, `water 25`), else the whole line. Editing a purchase, or saving it through Edit in the form, keeps them.
- **Usual price, town, check sheet:** as prototyped. A batch row opens the usual Log sheet titled "Check purchase" with Done, which puts the changes back in the list unsaved; a category changed there is learned too.
- **Left out:** the prototype's "Try" example chips (they'd put made-up purchases a tap from his real log; noted as an idea). The Shortcut time stamp is read for the day (`[2026-11-21 13:05] yesterday` is the 20th), but `saidAt` and "Already saved" are Q15's.
- **Blur:** only the rows blur, never the card. If two frames take over 120 ms in a fold, later folds that session are a crossfade.
Tests: `test_smart.py` (100 checks, listed in `MAINTAINING.md`). Full suite: 796 of 796 side by side, pinned Playwright 1.56 pointed at a newer Chromium, as before. Screenshots at 375 and 402 px, light and dark, and fade frames at 4×, checked by eye.
**For your iPhone:** (1) Tap "Smart add" on Home and type "jeep to cubao 14": does the keyboard leave the preview and Save in view? (2) Use the keyboard's mic and say a purchase the way you would at a counter: does it read right? (3) Switch sides a few times: is the fade smooth, or does it stutter? (4) Say "jeep" with no amount after logging one: does Your usual fill it? (5) Paste two or three lines from Notes: does it find each purchase?
**Left for later:** Q15 (the Siri inbox) is next and builds on the time stamps the reader already reads. The "Try" chips idea is in the queue's ideas.

## Q15 · Logging: the Siri inbox
**Render:** 1 Nov 2026, 09:45, scope as below · **Build:** 2 Nov 2026, 07:14, Ivan: "Suki Q15 Build" · shipped as 2.21 · Needs: Q14 (built first; live as 2.20, checked). Recon: project doc `suki_quick_add_recon_2026-11-01.md` (findings 2 and 3, the Shortcut steps), cut down because Smart add's box already keeps line breaks and reads the Shortcut's time stamps.

**Goal:** say a purchase to Siri anywhere, paste the whole inbox into Smart add later, and nothing is saved twice.
**Agreed:**
1. **Already saved:** a pasted line that starts with a Shortcut stamp (`[2026-11-21 13:05]`) and matches a saved purchase's words and stamp shows as "Already saved", greyed, and is left out of Save. The header reads "3 new · 2 already saved". Purchases keep the stamp as `saidAt` beside Q14's `said` (a new field; older data and backups are unaffected).
2. *Default if unanswered:* lines without a stamp are never skipped, so typing "jeep 14" twice in a day still saves twice.
3. **Help › Log by voice with Siri:** the six Shortcut steps from the Recon (Dictate Text, Format Date as `yyyy-MM-dd HH:mm`, Text, Append to Note "Suki inbox", Copy to Clipboard, Show Notification), how to run it (Hey Siri, the Action Button, a Lock Screen control), and that clearing the note is optional.
**Out of scope:** opening Suki from the Shortcut (`webapp://`), a Paste button, any server or AI tidying ("Use Model"), building the Shortcut itself (Ivan does that on his phone).
**Where to look:** `js/reader.js` (from Q14), the Smart add preview, `storage.js` and `backup.js` (`saidAt`), the Help screen from Q07.
**Done when:** tests: a stamped inbox saves once, pasting it again marks every line "Already saved", a mix saves only the new lines, unstamped duplicates still save, `saidAt` survives a backup round trip, the Help section lists the steps; full suite passes. **Checks:** full suite; screenshots at 375 px.
**For your iPhone:** the Shortcut runs from Siri and the Action Button; dictation works with no signal; pasting the note keeps its line breaks.
**Debrief:** Built as agreed. The default applied: lines without a stamp are never skipped. Decisions within scope:
- **The match** is the stamp plus his words for that purchase (`saidAt|said`, case and spacing aside), so a line holding two purchases matches each on its own part. The same words at another time are new; two identical stamped lines in one paste both save.
- **The preview:** already-saved rows are greyed `div`s, not buttons, with a plain grey "Already saved" badge (never the warning colour). The header reads "3 new · 2 already saved", "All 5 already saved" or "Already saved", and one already-saved line shows in the list style, with no Edit in the form.
- **Nothing new to save:** no Save button; a line says so, with "Clear the box" (added so the box isn't left full with nothing to do).
- **The stamp is checked:** an impossible one (30 Feb, 25:61) is ignored by the reader and dropped from saved data and backups; the rest of the purchase is kept.
- **Help:** a "Logging" group with "Log by voice with Siri", opening its own sheet (like the Home Screen steps). "Smart add" in it is a door to Home's Smart add, with the cursor in the box.
- **One gap:** a stamped line saved by 2.20 (before `saidAt` existed) has no stamp, so it can save once more. Noted in `MAINTAINING.md`.
Tests: `test_inbox.py` (56 checks, listed in `MAINTAINING.md`). Full suite: 852 of 852 side by side, pinned Playwright 1.56 pointed at a newer Chromium, as before. Screenshots at 375 px, light and dark, checked by eye.
**For your iPhone:** (1) Build the Shortcut from Settings › Help › Log by voice with Siri, then say "Hey Siri, Log to Suki": does the note get a line starting with the time? (2) Try it from the Action Button, and once with no signal. (3) Paste the note into Smart add: are the line breaks kept, and does it find each purchase? (4) Save, then paste the same note again: does every line show "Already saved"? (5) Check that Siri writes the time as `[2026-11-21 13:05]`, with the square brackets.
**Left for later:** nothing new.

## Q12 · Look: calendar tints and price range strip
**Render:** 1 Nov 2026, 09:56, scope as below · **Build:** 1 Nov 2026, 12:46, Ivan: "Q12 Build" · shipped as 2.16 · Needs: Q08's prices row and Q10's calendar door (both live). Queued after Q15, but built first at Ivan's word: it doesn't touch the parts Q13–Q17 change (the Till, the form, Home), and they keep their order.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Q12 prototype](https://claude.ai/artifact/NFwAtWyj5ERxgyGifutbeS) (sample spending; typical prices from Suki's list). Recon: visual audit findings 4 and 5 (Milestone B), without the week strip.

**Goal:** a number next to something to compare it with, at a glance.
**Agreed:**
1. **Calendar tints:** a day with spending is tinted in three steps (`--tint-1`, `--tint-2`, `--tint-3` from the accent), by thirds of that month's spending days; fewer than three days get the middle step. A "Less ● ● ● More" key sits under the grid. Today keeps its outline; a picked day is solid ink (black, white in dark) so it never reads as a big day. Day labels for VoiceOver keep the amount. Tapping is unchanged.
2. **Price range strip** on the item sheet, at the foot of the typical-prices card: one band per typical price (two ranges never merge into one), a solid dot for each time he paid, a ring for each price note; same prices stack upwards; the axis shows a rounded low and high; a key (Typical · You paid · Price notes). Shown when the item has a typical price and at least one paid price or note.
3. **Dots and rows are linked:** tapping a dot lights its row in You paid or Your price notes, and tapping a row lights its dot, with a label ("₱50 · Yesterday · Bulakan to Barrio") kept inside the strip's edges. Tapping elsewhere clears it.
4. **No grading:** no good or bad words or colours. Nothing animates on the strip or the tints (kept still); the tints change with the month as the days do.
**Out of scope:** the Home week strip (left out), a strip on Search rows, budgets.
**Where to look:** `ui.js` (the calendar sheet), `screens.js` (itemDetail, typicalCard, paidFor), `css/app.css` (tint tokens, run through the dataviz palette check in light and dark).
**Done when:** tests for the three steps (and the under-three-days case), the key, the picked-day look, separate bands, stacked dots, the dot–row link both ways, the label staying inside at both ends; full suite passes. **Checks:** full suite; screenshots at 375 and 402 px, light and dark.
**For your iPhone:** whether the three tints are easy to tell apart in bright light; whether the strip reads without the key.
**Debrief:** Built from the handoff and the prototype. Decided within scope:
- **Tint colours changed from the prototype.** The handoff's palette check (dataviz validator, ordinal) failed the prototype's .12 / .32 / full tints: the lightest step was too close to the white card (1.14:1, floor 2:1), and on screen the top two steps looked alike. The shipped steps pass in light and dark: light goes light blue → the accent → a deeper blue; dark goes deep blue → the accent → a bright blue (dark grows brighter). The day number uses whichever ink reads best on each step. Tokens: `--tint-1/2/3`, `--tint-1-ink`, `--tint-3-ink`.
- **Thirds** are by rank, and days with the same amount share a step (a month of equal days sits in the middle). The key and the new footnote show only in a month with spending.
- **The strip** sits under the price rows, before the sources (the comparison next to the prices, the fine print last). Dots within about a dot's width stack (up to five levels); each dot's tap area is one level tall so stacked dots don't steal taps. Every time you paid gets a dot, though You paid lists five rows; a dot without a row still shows its label.
- **A You paid row still opens the purchase** (it's one of Q08's four doors to it), and lights its dot, which is still lit when you come back. Tapping elsewhere clears it, except on a sheet opened over the item. A price note row lights its ring; its bin is its own tap.
- **The label** is kept inside the strip by CSS alone (`left: x%` with `translateX(-x%)`), so nothing is measured.
Tests: `test_compare.py` (44 checks). Full suite: 527 checks, all passing (pinned Playwright 1.56 pointed at a newer Chromium, as before). Also checked by eye: the iPad pane.
**For your iPhone:** (1) Open the calendar on a busy month: can you tell the three blues apart in daylight, and in dark mode at night? (2) Pick a big day: it turns black (white in dark), not blue. (3) Open Jeepney or Tricycle after logging one: does the strip make sense without reading the key? (4) Tap a dot, then its row, then somewhere else: the light follows and clears. (5) Tap a You paid row, close the purchase: its dot is lit.
**Left for later:** nothing new.

## Q18 · Quick Till: note press
**Render:** 1 Nov 2026, 13:09, scope as below (with Q19–Q21) · **Build:** 4 Nov 2026, 08:31, Ivan: "Suki Q18 Build" · shipped as 2.24 · Needs: Q13 live (its buttons, change row and breakdown); checked: 2.17.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Suki note press prototype](https://claude.ai/artifact/EsJMmBNf71Sm48FDttcpLS). Spec: project doc `idea_till_note-press_notes.md`; phases: `q18_till_drawer-and-note-press_blueprint.md`. Phase 1 of 4.

**Goal:** tapping a note feels like handing over cash.
**Agreed:**
1. **Finger tilt:** the six buttons tip towards the thumb while held and spring back on release.
2. **Fly** (the starting setting): the note arcs into the cash box; the ₱20 spins like a tossed coin.
3. **Slot:** the note slides up into a slot line under the cash box; the line fades in for the slot, out about a second later, and is hidden at rest.
4. **Setting:** Settings › Accessibility › "Note animation: Fly · Slot". Device-only, not in backups (like `suki:motion`).
5. **The amount updates when the note lands;** the change row settles in straight after. No counting up.
6. **New materials** for Q13's notes and coins (flying and in the change row): notes a block of paper, coins a hint of metal. Tokens only (`--dr-*`, `--coin-*`, `--ring-edge`), mixed from Suki's own; no hex in rules.
7. **Reduce Motion:** no tilt, no flight; the amount updates at once.
**Out of scope:** the drawer and the slot line as a handle (Q19); sounds; haptics (parked).
**Where to look:** `screens.js` (scrTill, the change block, Accessibility), `events.js` (till keys), `motion.js` (`settle`), `css/app.css`, `storage.js` (list the new device-only key). Keep `.denoms` and `.tillout`'s minimum height.
**Done when:** tests: each tap adds the right amount once, also when tapped fast; no stray flying notes after rapid taps or a redraw; the setting switches and survives a reload, and isn't in backups; Reduce Motion gives no flight; Q13's tests still pass; full suite passes. **Checks:** screenshots at 375 and 402 px, light and dark.
**For your iPhone:** the tilt under your thumb; Fly and Slot at full speed; the notes' new look in daylight.
**Debrief:** Built from the prototype (version 1793537229-9b73) and the spec, with the prototype's timings. Decided within scope:
- **What you did last wins.** Typing in the cash box, ✕ or Exact drop a note still in the air (nothing added); any redraw (another sheet, switching tabs) lands it at once, so each tap adds once and nothing is left on screen. The spec didn't say; this keeps the amount honest.
- **The slot line sits in the gap above the buttons,** absolutely placed, so Q18 moves nothing on the Till. It isn't a button yet; Q19 makes it the handle and gives it its VoiceOver label.
- **The drawer's `--dr-*` tokens wait for Q19,** the first phase that uses them. Q18 adds `--coin-hi`, `--coin-lo`, `--coin-edge` and `--ring-edge`.
- **The tilt covers all six buttons,** Exact included. Exact doesn't fly; it sets the amount at once, as before.
- **Q13's motion-on checks** in `test_till.py` now wait for the note to land before reading the change row; what they check is unchanged.
Tests: `test_notepress.py` (81 checks), `test_till.py` still 73 of 73. Full suite: 1,063 of 1,065 side by side; the 2 were fold checks in `test_smart.py`, which passed 100 of 100 on its own (Known test issues). Pinned Playwright 1.56 pointed at a newer Chromium, as before. Screenshots at 375 and 402 px, light and dark, and mid-flight, checked by eye.
**For your iPhone:** (1) Press and hold 500 near a corner: does it tip towards your thumb, and spring back when you let go? (2) Tap 1000 for a ₱789.50 bill: does the note arc into the box, and the change settle in as it lands? (3) Tap 20 a few times fast: does the coin spin, and does the amount end right? (4) Switch to Slot in Settings › Accessibility and tap a note: does the line show for it, then fade? (5) In daylight, do the notes read as paper and the coins as metal?
**Left for later:** nothing new. Q19 (the drawer) is next.
**Receipt:** Q18 · Light to medium → Light to medium · 63 steps · 47k written · 16.6M re-read · 1 full test run

### Q18 fix · only the two boxes can be selected (2.24.1)
**Render:** 4 Nov 2026, 10:27, Ivan: "render and build" · scope: as below, with its default · **Build:** 4 Nov 2026, 10:27, same message · Raised by Ivan, 4 Nov 2026, 10:23: "i keep having the trouble on the till page of highlighting the buttons". Folded into Q18 at his word (10:25) rather than a new item, so it ships as a patch, 2.24.1.
**Goal:** pressing anywhere on the Till never highlights text, except inside the two boxes.
**Why:** none of the Till's buttons are set as unselectable, so a long press (which the tilt invites) selects the button's number and can bring up the copy menu. Labels, the change figure and the cash row can be selected the same way.
**Agreed:**
1. On the Till page (`#app.tab-till`), no text selection and no long-press menu (`user-select: none`, `-webkit-touch-callout: none`) on everything: the six buttons, labels, the eyebrow and figure, the cash row, the foot lines and Log this bill.
2. Total bill and Cash handed over stay fully selectable (`-webkit-user-select: text` set back on the two inputs), so holding to move the cursor, selecting and pasting still work.
3. Taps, the tilt and the flights work as now.
**Out of scope:** other pages. Copying the change figure goes away; *default if unanswered:* that's fine.
**Where to look:** `css/app.css` (one rule near the Quick Till block). Add checks to `test_notepress.py`.
**Done when:** tests: after a long press on a button, a label and the figure, nothing is selected (`getSelection()` empty, computed `user-select` is `none`, `-webkit-touch-callout` is `none`); both boxes still select their text and take typing; Q13 and Q18 tests still pass; full suite passes. A patch version, 2.24.1, with its changelog section.
**Effort:** light.
**For your iPhone:** hold a note button for a second: no highlight and no copy menu; hold inside each box: the cursor and Select still work.
**Debrief:** shipped as 2.24.1. Built in the Q18 chat, at Ivan's word. One rule in `css/app.css` (`#app.tab-till` unselectable, its inputs selectable again), so anything added to the Till later is unselectable too unless it opts in; noted in `MAINTAINING.md`. The default applied: the change figure no longer copies. Tests: `test_notepress.py` section 7 (12 new checks: holding or triple-tapping a button, Exact, a label, the figure, the cash row and the title selects nothing; Log this bill is unselectable; both boxes select and take typing; other pages left alone; the long-press menu off), 93 of 93. Full suite: 1,076 of 1,077 side by side; the 1 was the known `test_smart.py` fold timing, 100 of 100 on its own.
**Receipt:** Q18 fix · Light → Light · 27 steps · 16k written · 9.5M re-read · 1 full test run · same chat as Q18, counted from where its receipt ended

## Q19 · Quick Till: till drawer
**Render:** 1 Nov 2026, 13:09, scope as below (with Q18, Q20, Q21) · **Build:** 4 Nov 2026, 12:38, Ivan: "Suki Q19 Build" · shipped as 2.25 · Needs: Q18 live (the slot line and materials); checked: 2.24.1.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype and spec as Q18 ("iOS way" feel; the Now/iOS toggle and slow-motion controls are prototype only). Phase 2 of 4.

**Goal:** a hidden drawer under the cash box that opens and shuts like a real one.
**Agreed:**
1. **The drawer:** a rigid tray 300 pt deep, tilted 26° in 3D, concentric corners (12 and 5 pt); opens from under the still cash box; the six buttons ride on its front; the cash box's shadow (`::after`, opacity follows `--open`) deepens as it opens; layout 3 + 8 compact (four note slots, five coin cups), empty here; open height 106 pt.
2. **Opening the iOS way:** follows the finger; on release it settles at whichever end it would coast to (`project(v)` with deceleration 0.99, past halfway); speed read over the last ~100 ms up to release; springs as length and bounce (open 0.45 s, a tap opens with no bounce, a flick gets up to 0.15; shut 0.35 s, no bounce, cut off at 0); past open it stretches with iOS's rubber band.
3. **Shutting as a chain:** a swipe up shuts it, then the rest of the same swipe scrolls the page; let go mid-flick and the page glides on (rAF, any new touch stops it). **The knock:** a hard shut nudges only the cash box up 1–2.2 pt at the instant it hits.
4. **Easter egg:** the line is hidden at rest (shows on touch, while open, and on keyboard or VoiceOver focus); no tip, not in Help. The line is a real button: "Open till drawer" / "Close till drawer".
5. **Starts closed every time;** closes on a new bill or when typing starts. A tap still types; only a drag past 6 pt is the drawer's.
6. **Devices:** iPhone upright only (on its side, only Q20's overload peek shows). iPad and Mac: the card's width; click, Space or Enter, or a mouse drag.
7. **Reduce Motion:** a 0.2 s fade; no spring, jiggle or knock.
**Out of scope:** contents and fullness (Q20); the haul and mark (Q21); haptics.
**Where to look:** `screens.js` (scrTill), the drawer's gesture code (in `gestures.js`, beside the other drags), `motion.js` (`spring(duration, bounce)`, `project`), `css/app.css`.
**Risks:** `render()` redraws must leave it shut with no stray listeners or frames; must not fight sheets, swipe to delete or Q11's motion; 3D smoothness on the phone.
**Done when:** motion-on tests: a 45 pt held pull shuts, 55 pt opens; a tiny flick shuts, a flick with a stalled last frame opens; a swipe up shuts then scrolls; the knock only on a hard shut; caught mid-movement; typing and a redraw leave it shut; Reduce Motion fades only; the button's labels; no sideways overflow; the fuzzer passes; full suite passes. **Checks:** screenshots open and shut, 375 and 402 px, light and dark, iPad and Mac.
**For your iPhone:** finding it with no hint; the open and shut feel; the scroll hand-off; the knock's timing; smoothness.
**Debrief:** shipped as 2.25, built in a fresh chat from this handoff. All seven agreed points as written, with the prototype's numbers (iOS way only; its Now code and toggle not built).
- **How:** markup `tillDrawer()` in `screens.js`; the gesture block at the end of `gestures.js` (all numbers in `DRAWER`); `MOTION.iosSpring`, `project` and `rubber` added to `motion.js`; `render()` calls `drawerReset()`. Details in `MAINTAINING.md` › The drawer (Q19).
- **Decided within scope:** (1) the handle is the old 14 px gap and `.denoms` lost its margin, so shut, the Till is pixel for pixel as before. (2) A drag that starts sideways, or after holding still 500 ms inside the box, is left to the text, so 2.24.1's cursor and Select keep working. (3) A tap in the cash box shuts the drawer (it types, and typing shuts it). (4) The compartments' labels wait for Q20, whose handoff lists them. (5) Not in the README either, so the Easter egg stays hidden. (6) Turning an iPhone on its side shuts it at once.
- **Tests:** new `test_drawer.py`, 82 checks (Done when, all covered). Touched files: till 73, notepress 93, flows 125, onboard 37, all passing. Full suite: 1,157 of 1,159 side by side; the 2 were the known timing checks in `test_smart.py` and `test_motion.py`, 100 of 100 and 63 of 63 on their own.
- **Left for later:** Q20 (contents, labels, the overload peek), Q21 (the haul).
**Receipt:** Q19 · Heavy → Light to medium · 57 steps · 69k written · 14.8M re-read · 1 full test run

## Q20 · Quick Till: drawer contents and fullness
**Render:** 1 Nov 2026, 13:09, scope as below (with Q18, Q19, Q21) · **Build:** 4 Nov 2026, 19:25, Ivan: "Suki Q20 Build" · shipped as 2.26 · Needs: Q19 live; checked: 2.25.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype and spec as Q18. Phase 3 of 4.

**Goal:** the open drawer shows roughly how much cash is in it.
**Agreed:**
1. **Notes land in their compartment** when the drawer is open; the ₱20 goes into its cup.
2. **A fullness gauge, not a count:** only the cash handed over decides how full it looks; full at ₱20,000.
3. **Contents:** notes stand on edge in each slot as a paper block, labels on each slot's front lip; coins lie in loose heaps in scooped cups that slope into a basin.
4. **Physics:** on open and close, coin heaps lag a frame and settle; notes sway about 1.6° and right themselves.
5. **Overloaded from ₱50,000:** notes tip out, coins spill; with the drawer shut, notes peek out from under the cash box; VoiceOver: "Till overloaded. Check the amount."
6. **Calm changes:** pieces fade over about 0.2 s; ✕ clears with a calm fade.
**Out of scope:** the haul and mark (Q21); the spec's "Apple-detail ideas not yet built".
**Where to look:** `screens.js` (tray contents, the fill), `css/app.css`, the landing target from Q18.
**Done when:** tests: fullness follows the amount; the peek at ₱50,000 and not below; the VoiceOver text; ✕ empties it; notes land in the right compartment; nothing overflows at ₱999,999; full suite passes. **Checks:** screenshots empty, half, full and overloaded, light and dark.
**For your iPhone:** whether fullness reads at a glance; the overload peek; smoothness with 40-odd notes.
**Debrief:** shipped as 2.26, built in a fresh chat from this handoff. All six agreed points as written, with the prototype's numbers (its fill curve, counts, heap and spill places, and timings).
- **How:** counts and places in `screens.js` (`drawerLevels`, `drawerCounts`, `sheetStyle`, `coinStyle`, all numbers in `TILL_FULL`), drawn still by `drawerFill()`; the fades in `fillDrawer()` in `events.js`, called from `updateTill`; the landing target in `noteFly`; `drawerJiggle` and the peek in `gestures.js`. Details in `MAINTAINING.md` › The drawer's contents (Q20).
- **Decided within scope:** (1) a note heads for its compartment only once the drawer is fully open (as the prototype); part-open, it goes to the cash box. (2) The compartment gives the nod instead of the cash box. (3) In Slot mode, landing in the drawer skips the slot line. (4) A hard shut also makes the coins jump with the knock (the spec's knock line). (5) Reduce Motion keeps the 0.2 s fades but has no jiggle. (6) The cash box got a wrapper (`.cwell`) so the peek can sit under it; nothing depended on its parent. (7) Q19's "empty" check now checks the nine labels.
- **Tests:** new `test_drawerfill.py`, 72 checks (Done when, all covered). Touched files: drawer 82, till 73, notepress 93, all passing. Full suite: 1,231 of 1,231 locally. On GitHub the first run failed the known fold check in `test_smart.py`; re-run once, 1,231 of 1,231.
- **Left for later:** Q21 (the haul and the mark). The spec's "Apple-detail ideas" stay unbuilt.
**Receipt:** Q20 · Medium → Light to medium · 62 steps · 45k written · 15.1M re-read · 1 full test run

## Q21 · Quick Till: the haul and maker's mark
**Render:** 1 Nov 2026, 13:09, scope as below (with Q18–Q20) · **Build:** 4 Nov 2026, 20:20, Ivan: "Suki Q21 Build" · shipped as 2.27 · Needs: Q20 live; checked: 2.26.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype and spec as Q18. Phase 4 of 4.

**Goal:** the Easter egg inside the Easter egg.
**Agreed:**
1. **Hand over hand:** with the drawer fully open, hold it with one finger and swipe down with another, swapping fingers while one stays down. One finger never starts it.
2. **Heavy and steady:** 0.035 pt per pt of finger travel, linear, hard stop at 120 pt past open (about ten long swipes). Downward movement from any finger adds; upward counts only once one finger is left.
3. **It stays where it's left.** A one-finger give springs back to that spot; a swipe up still shuts it from any depth.
4. **"Designed by Ivan"** at the very back: plain, Caption 2 (11 pt), regular, `--fg3`, 224 pt from the tray's front; peeks on the ninth swipe, whole on the tenth. `aria-hidden`.
**Out of scope:** anything else at the back of the drawer.
**Where to look:** the drawer's gesture code, `css/app.css`, `screens.js` (the mark). Zoom blocking in `events.js` must not swallow the second pointer.
**Done when:** tests with synthetic two-finger pointers: ten 350 pt swipes reach 120 pt; it stays when let go; one finger can't start it; the mark only at the end; a swipe up shuts it; full suite passes.
**For your iPhone:** whether ten swipes feels earned or a chore; whether the mark is readable but quiet, especially in dark mode.
**Debrief:** shipped as 2.27, built in a fresh chat from this handoff. All four agreed points as written, with the prototype's haul code (its `haulStart`, `haulMove`, `haulEnd` and snap target).
- **How:** `haulDown`, `haulMove`, `haulEnd` after `drawerEnd` in `gestures.js`, numbers in `DRAWER.haul` and `DRAWER.pull`; `DR.rest` holds where an open drawer sits, and `drawerSnap(open, v, at)` springs to it. The mark is `#tillMark.tmark` in `tillDrawer()`. Details in `MAINTAINING.md` › The haul and the maker's mark (Q21).
- **Decided within scope:** (1) a tap on a hauled drawer leaves it where it is (the prototype sprang it back to plain open; that broke "it stays where it's left"). (2) A slow one-finger push up that doesn't shut it keeps where the push ended, as in the prototype. (3) Shutting forgets the haul: it reopens to plain open. (4) For 300 ms after the last finger lifts, a click on the line is ignored and a focus in either box is blurred, so the lifting fingers can't shut it or leave the cursor in the box. (5) Two fingers on a drawer still springing open count only once it's at 105 pt or more. (6) With `bottom: 224px`, the mark measures 0 of itself showing on swipe 8, about a third on swipe 9 and all on swipe 10, matching the spec with no tuning.
- **Zoom blocking:** checked, not changed. Real two-finger touches (Chromium's touch input, through `events.js`'s pinch blocker) haul it, and nothing zooms.
- **Tests:** new `test_haul.py`, 54 checks (Done when, all covered). Drawer 82 and drawerfill 72 still pass. Full suite: 1,272 of 1,277 side by side; the 5 were the known Log-sheet timing checks in `test_motion.py` and a launch timeout in `test_offline.py`, 63 of 63 and 9 of 9 on their own (Known test issues). On GitHub: the first run timed out at launch in `test_offline.py`; the one re-run passed it, 1,284 of 1,285, failing only the known `test_smart.py` fold check, its third time, so fixing it is now in the queue's ideas. Pages deployed 2.27.
- **For your iPhone:** (1) Open the drawer, hold it with one finger and swipe down with another, swapping fingers: does it move a little each swipe, and does ten feel earned or a chore? (2) Lift both fingers halfway: does it stay put? (3) At the back, is "Designed by Ivan" readable but quiet, in daylight and in dark mode? (4) Swipe up from the back: does it shut in one go, and does the next open go to plain open? (5) Does the second finger ever zoom the page or leave the cursor in the cash box?
- **Left for later:** nothing new. The till drawer is complete; the spec's "Apple-detail ideas" stay unbuilt.

## Q22 · Spending: pounds at the rate you paid
**Render:** 2 Nov 2026, 18:22, scope as below (with Q23) · **Build:** 3 Nov 2026, 17:28, Ivan: "Suki Q22 Build" · shipped as 2.22, with 2.22.1 for the day's format · Needs: 2.21 live.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: none (skipped at Ivan's word, like Q05 and Q06). Recon: project doc `idea_rate_history_notes.md` (Milestone A, and "A rate for one day").

**Goal:** every pound figure in Suki uses the rate of the day the money was spent.
**Agreed:**
1. **Totals in pounds add each purchase at its own rate** (`rateAtPurchase`): Home's summary card, Spending's total, and anywhere else "≈ £" sums purchases. A purchase with no rate counts at today's rate, and the total says so ("2 at today's rate").
2. **A purchase dated before today gets that day's ECB rate:** the last one published before that date, so a weekend or holiday takes the weekday before, and a Monday-morning purchase in Manila gets Friday's. This covers the form, logging from a calendar day, Smart add's dates ("yesterday", "on Friday") and changing a purchase's date. Today's and future dates keep today's saved rate, as now.
3. **Where that day's rate comes from, in order:** Frankfurter (ECB) for that date, v2 then v1; then Currency API's file for that date; otherwise today's saved rate, marked "estimated" on the purchase and corrected quietly the next time there's signal. *Default if unanswered:* if Currency API's dated address can't be confirmed at build, that step is left out. Every reply is checked against `RATE_RANGE`; a bad one is ignored.
4. **His data stays safe:** a correction only adds to a purchase (the rate, its source, its day, and "estimated" while it is). Price, date and words are never touched. Older purchases aren't rewritten in bulk; only "estimated" ones are corrected. The new fields survive editing, older versions and backups.
5. **The purchase's details** show the rate behind "In pounds then": "£1 = ₱83.11 · Thu 1 Oct · ECB", with "estimated" while it is.
**Out of scope:** the rate history page and its saved history (Q23); rewriting old purchases' rates in bulk; Convert.
**Where to look:** `events.js` (`submitForm`), `smart.js` (Smart add's saves), `rate.js` (a one-day lookup beside `rateFrom`), `storage.js` (`cleanPurchase` keeps the new fields), `screens.js` (Home's summary, Spending's totals, the purchase details), `backup.js`.
**Risks:** Save must never wait for the lookup: save first, then fill in the rate. Offline must still save at once.
**Done when:** tests: totals add each purchase's own rate; purchases with no rate are counted and labelled; a back-dated purchase gets that day's rate (Friday for a weekend, and for a Monday-morning purchase in Manila); offline gives "estimated", corrected after signal returns with nothing else changed; a bad reply is ignored; Save never waits; backups keep the new fields; full suite passes. **Checks:** screenshots at 375 and 402 px, light and dark.
**For your iPhone:** log something for yesterday and check "In pounds then"; in flight mode, log one, then reconnect and check it's no longer "estimated".
**Debrief:** Built as agreed. The default didn't apply: Currency API's dated address was confirmed at build (`currency-api@YYYY-MM-DD` on jsDelivr and `YYYY-MM-DD.currency-api.pages.dev`, both answering for 31 Oct 2026; older dates, such as 1 Mar 2024, don't answer, so it's simply skipped then). Frankfurter's dated v2 address answers a weekend with Friday (checked: 31 Oct → 30 Oct, ₱85.32). Decisions within scope:
- **Which day:** the purchase's date minus one, so the ECB answers with the last rate published before that day (Sunday and Monday both get Friday's). A reply for a later day, or more than 10 days earlier, is ignored, as is one outside `RATE_RANGE`.
- **Save first:** every save stamps a rate at once (today's, marked `rateEstimated` when the date is before today), then looks up the day's rate without being waited for. It runs again at launch, on going online and on coming back to the app. Only purchases marked estimated are ever corrected, and only their rate fields change.
- **The new fields:** `rateDate`, `rateSource` and `rateEstimated`. New purchases dated today also record today's rate's day and source, so their details can show the line. Older purchases show the rate without a day or source.
- **The note:** "2 at today's rate" for purchases with no rate, and "1 estimated" for ones still waiting, under Home's total and Spending's. While a bar is picked, Spending keeps the note's line (empty if need be) so clearing the pick doesn't move the list under the finger (the full suite caught this).
- **"You paid"** on an item's page now shows each purchase in pounds at its own rate, under the goal's "every pound figure". Catalogue prices and price notes still use today's rate, since they aren't money spent.
- **Tests' rate stand-in** (`rate_route`) now answers dated requests, with `days={…}` and a `log`.
- **2.22.1:** GitHub's Chromium wrote the day as "Fri, 30 Oct", so its run failed one check that passed here. The day is now written out by hand ("Fri 30 Oct") so every browser shows the same.
Tests: `test_rates.py` (44 checks, listed in `MAINTAINING.md`). Full suite: 896 of 896 side by side, pinned Playwright 1.56 pointed at a newer Chromium, as before; GitHub's run green on 2.22.1. Screenshots at 375 and 402 px, light and dark, checked by eye.
**For your iPhone:** (1) Log something for yesterday: does "In pounds then" show yesterday's day before, with "ECB"? (2) In flight mode, log one for yesterday: does it say "estimated", and does Home's total say "1 estimated"? (3) Turn flight mode off and reopen Suki: is "estimated" gone? (4) Does Home's total in pounds stay the same from one day to the next with no new spending?
**Left for later:** nothing new.

## Q23 · Convert: rate history
**Render:** 2 Nov 2026, 18:22, scope as below (with Q22) · **Build:** 3 Nov 2026, 18:10, Ivan: "Suki Q23 Build" · shipped as 2.23 · Needs: Q22 live (its one-day rate lookup is reused); 2.22.1 was live.
For: Ivan · Builder: Claude · Repo: imperialfox/Suki. Prototype: [Suki rate history prototype](https://claude.ai/artifact/PMTmqDCE7i2cXavLkqYekA) (version 1793642745-fdc9, on prototype kit 1.0.0; prototype only, the kit isn't built into Suki). Recon, findings 3–15 and the robustness plan: project doc `idea_rate_history_notes.md`.

**Goal:** see at a glance how the pound-to-peso rate has moved, and why.
**Agreed:**
1. **A Rate history page, pushed from Convert's rate row** (the rate text becomes the door; Refresh stays). Push on iPhone upright, zoom on iPad and Mac. Home's rate card still opens Convert.
2. **As prototyped:** range pill M · 6M · Y · 5Y · All (*default:* opens on Y); the big figure with its day; "£100 buys ₱…, ₱… more than a year ago"; the year strip ("Near the high of the year", low and high with dates); "Higher means your pound buys more pesos"; the line chart following the finger, snapping to a news dot within 12 pt and opening it on release; filled dots for peso news, hollow for pound news, in grey (no category colours); the "Why it moved" card, worked out from ECB pesos and dollars per pound, hidden if either end is missing; "What happened" (four rows, then Show all) and the news sheets with "£1 that week", "What's a central bank rate?" and the source link; a footer naming the sources and when rates arrive; no forecasts.
3. **Follows Convert's swap:** "₱100 = £…" and "Higher means your pesos buy more pounds".
4. **Every gap says why:** weekends, the Manila night gap (the ECB publishes about 23:00 there), offline, first open with no signal ("Connect once to load the history"), and a saved rate from Currency API, shown as its own hollow dot with its source.
5. **Since your trip started:** a faint line at the first purchase of the latest unbroken stretch (no gap of 14 days or more) and "Since <date>: ₱… more per £1". Hidden until there's a stretch.
6. **History in four layers:** saved on the phone in IndexedDB, asking only for missing days; Frankfurter's ECB series (v2, then v1), each reply checked whole (dates in order, inside `RATE_RANGE`, no day jumping more than about 5%); a snapshot from 2016 shipped with the app and cached by the service worker (about 42 KB); and Suki's own daily record from whichever source loaded today's rate, used only where the ECB has no figure. One year loads first; older years only when All is tapped. Not in backups. Bad saved history is thrown away and reloaded. If history can't load, the page says how far it goes and Settings › Last rate check says why.
7. **News notes:** one plain file: date, side, title, a short plain explanation, and a link to the official statement (bsp.gov.ph, bankofengland.co.uk or psa.gov.ph). 2026's notes from the prototype, linked to the official statements instead of press reports. *Default if unanswered:* the three older notes (2008, 2016, 2022) go in only with a reputable source found at build; otherwise they're left out. "News checked <date>", said plainly after a month, with the news lane greyed after that date.
8. **Help** gets "What's a central bank rate?", opened from the news sheets.
9. **VoiceOver** reads the chart as a sentence ("Up 10% in a year. High ₱85.35 on 26 October."). iPad and Mac show the chart and the news side by side.
**Out of scope:** comparing two dates, your real rate against the reference, copying a summary, rate alerts, forecasts, live news, news filters, a new tab; Q22's work; the prototype kit's tools.
**Where to look:** `rate.js`, `screens.js` (scrConvert's rate row and the new page), `events.js`, `gestures.js` (the chart's scrub beats swipe back), `storage.js` (IndexedDB), `sw.js` (the snapshot), `onboard.js` (Help), `css/app.css`, a new data file each for the snapshot and the news notes, and a `tools/` script to refresh the snapshot. `MAINTAINING.md` gets a "Rate history" section, including the monthly news upkeep.
**Risks:** the scrub must win over swipe back; a redraw mustn't snap the chart; the October dots sit close together.
**Done when:** tests: each history layer failing alone and all at once; a bad reply refused whole; the split card hiding with a missing end; the snapshot loading offline from the service worker; the news file's rules (a date, a side, a title under about 60 characters, an official link, no two on the same day and side, none in the future); the trip line rule; the swap followed; scrub, snap and open; swipe back; Reduce Motion; full suite and fuzzer pass. **Checks:** screenshots at 375 and 402 px, light and dark, plus on its side, iPad and Mac.
**For your iPhone:** dragging over the news dots, especially October's; reading the chart in sun; swipe back from the page; whether "Mostly the peso" answers why.
**Debrief:** Built as agreed, in `js/history.js` with two data files (`js/ratesnap.js`, `js/news.js`) and `tools/ratesnap.py`. Defaults used: the page opens on Y; the three older news notes went in, each with a Bank of England statement (2008: the 8 Oct rate cut after Lehman; 2016: the Governor's statement the day after the referendum; 2022: the 28 Sep gilt operation after the mini-budget). Decisions within scope:
- **Jump check at 10%, not "about 5%":** the real ECB series has a 6.8% day (24 Jun 2016), which 5% would refuse. A 20% jump is still refused. Recorded in the queue's Decided.
- **News links:** BSP notes link to BSP pages that state each decision (Monetary Policy Reports, the summary of decisions; for 22 Oct the BSP's indicators sheet until that meeting's highlights are out: swap it at the next news check). The 27 Oct note links to the BSP's daily peso–dollar rates. The prototype's 16 Oct note was left out: no BSP, Bank of England or PSA record says it (and October's dots are less crowded for it).
- **Where Frankfurter is asked:** v2 `/v2/providers/ecb/rates`, then v1 `/v1/a..b`, base GBP with PHP and USD, read from Frankfurter's own docs (the build workspace can't reach it, so the replies are the tests' stand-ins). Only missing days, at most every half hour. Nothing new is fetched at launch; it tops up when the page opens, on going online and on coming back to it.
- **The snapshot:** 2,773 weekdays, 4 Jan 2016 to 30 Oct 2026, 41 KB, made from the prototype's ECB series (Frankfurter was blocked here). Refresh with `python tools/ratesnap.py` from anywhere that can reach it. It's a normal versioned file, so the service worker already keeps it offline; `sw.js` didn't need changing.
- **First open with no signal:** the snapshot always shows, with "No signal. Connect once to load the history since 30 Oct." The empty "Connect once to load the history" card is only for no history at all.
- **The trip line** also needs the newest purchase to be under 14 days old, so a trip that ended months ago doesn't count as "your trip".
- **News sheets:** the header says Peso news or Pound news and the title sits in the body, so long titles wrap instead of being cut off. iPad and Mac open them as the usual centred sheet.
- **Swipe back** draws a still copy of Convert underneath while the finger moves. The page's text can't be selected (a mouse drag on selected text cancelled the swipe).
- **Not touched:** Q22's lookup still asks Frankfurter for a back-dated purchase even when the day is in the saved history; added to the queue's ideas.
- Suki has no screen IDs yet (its own idea in the queue), so none were added.
Tests: `test_history.py` (87 checks, listed in `MAINTAINING.md`), plus Rate history in `test_layout.py` (the page and both sheets at every size), `test_offline.py` (the page with no connection) and the fuzzer's taps. Full suite: 981 of 984 side by side on the pinned Playwright 1.56 pointed at a newer Chromium; the three were timing on this small machine (two Smart add fades and one history fade check), and passed on their own; the history check was then made timing-proof. Screenshots at 375 and 402 px, light and dark, on its side, iPad and Mac, checked by eye.
**For your iPhone:** (1) On Convert, tap the rate: does Rate history slide in, and swipe back from the middle of the page? (2) Drag along the chart over October's dots: can you pick each one, and does letting go open it? (3) Read the chart outside in the sun. (4) Does "Mostly the peso" answer why without reading the news? (5) In flight mode, open it: does it still draw, and say it's offline?
**Left for later:** back-dated purchases reading the saved history (queue idea 4); Rate history's later ideas (queue idea 14).
