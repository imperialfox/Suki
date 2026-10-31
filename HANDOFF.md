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
**Render:** 31 Oct 2026, 22:56, scope as below (wireframe skipped by Ivan) · **Build:** awaiting.

**Goal:** nothing he logged can vanish quietly. From the stress test, A2 (#1–4).
**Agreed:**
1. A backup with nothing usable in it (every record damaged) is refused, and nothing changes.
2. Before a restore or Erase, Suki keeps a safety copy of what's on the phone. Afterwards a message offers **Undo**, which puts it all back. *Default if unanswered:* the copy is kept until the next restore or erase.
3. Saved data Suki can't read, or records it has to drop, are copied somewhere safe **before** anything saves over them. Home shows a notice, and Settings › Your data gets a **Recovered data** row that saves the copy as a file. *Default if unanswered:* the copy is kept until he saves it, then he can clear it.
4. If the storage database won't open, Home says so. Purchases saved to the fallback spot are merged back in by id the next time the database opens, so none are hidden.
5. "Couldn't save" stays on screen until tapped, and an Undo message never hides it.
**Out of scope:** cloud backup, automatic backups.
**Done when:** tests reproduce each of the stress test's A2 cases and show them handled; full suite passes.

## Q06 · Tidy-ups: amounts, backup values, rate timeout, long totals
**Render:** 31 Oct 2026, 22:56, scope as below (wireframe skipped by Ivan) · **Build:** awaiting.

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
