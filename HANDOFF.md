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

## Q13 · Quick Till: bigger buttons and change as cash
**Render:** 1 Nov 2026, 09:45, scope as below · **Build:** awaiting · Needs: Q11 (built first: reuse its "settle" from `motion.js`).
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

## Q16 · Logging: location
**Render:** 1 Nov 2026, 08:26, scope as below · **Build:** awaiting · Needs: Q13 (built first; Q13 was slotted in after Q11 on 1 Nov, 09:45). Prototyped as "Q14" in the Q08–Q11 prototype (item 12); renumbered because the quick add Recon (`suki_quick_add_recon_2026-11-01.md`) suggests Q14 and Q15.

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

## Q17 · Home: exchange rate card
**Render:** 1 Nov 2026, 09:33, scope as below · **Build:** awaiting · Needs: Q16 (built first; Q08 changes the summary card under it).
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

## Q14 · Logging: Smart add
**Render:** 1 Nov 2026, 09:33, scope as below · **Build:** awaiting · Needs: Q17 (built first; Q11's "Saved" button and settle, and Q16's town, are reused).
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

## Q15 · Logging: the Siri inbox
**Render:** 1 Nov 2026, 09:45, scope as below · **Build:** awaiting · Needs: Q14 (built first). Recon: project doc `suki_quick_add_recon_2026-11-01.md` (findings 2 and 3, the Shortcut steps), cut down because Smart add's box already keeps line breaks and reads the Shortcut's time stamps.

**Goal:** say a purchase to Siri anywhere, paste the whole inbox into Smart add later, and nothing is saved twice.
**Agreed:**
1. **Already saved:** a pasted line that starts with a Shortcut stamp (`[2026-11-21 13:05]`) and matches a saved purchase's words and stamp shows as "Already saved", greyed, and is left out of Save. The header reads "3 new · 2 already saved". Purchases keep the stamp as `saidAt` beside Q14's `said` (a new field; older data and backups are unaffected).
2. *Default if unanswered:* lines without a stamp are never skipped, so typing "jeep 14" twice in a day still saves twice.
3. **Help › Log by voice with Siri:** the six Shortcut steps from the Recon (Dictate Text, Format Date as `yyyy-MM-dd HH:mm`, Text, Append to Note "Suki inbox", Copy to Clipboard, Show Notification), how to run it (Hey Siri, the Action Button, a Lock Screen control), and that clearing the note is optional.
**Out of scope:** opening Suki from the Shortcut (`webapp://`), a Paste button, any server or AI tidying ("Use Model"), building the Shortcut itself (Ivan does that on his phone).
**Where to look:** `js/reader.js` (from Q14), the Smart add preview, `storage.js` and `backup.js` (`saidAt`), the Help screen from Q07.
**Done when:** tests: a stamped inbox saves once, pasting it again marks every line "Already saved", a mix saves only the new lines, unstamped duplicates still save, `saidAt` survives a backup round trip, the Help section lists the steps; full suite passes. **Checks:** full suite; screenshots at 375 px.
**For your iPhone:** the Shortcut runs from Siri and the Action Button; dictation works with no signal; pasting the note keeps its line breaks.

## Q12 · Look: calendar tints and price range strip
**Render:** 1 Nov 2026, 09:56, scope as below · **Build:** awaiting · Needs: Q15 (built first; Q08's prices row and Q10's calendar door are in by then).
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
