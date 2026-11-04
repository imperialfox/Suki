# Maintaining Suki

Notes for whoever works on the app next, whether that's Ivan, a new Claude session or anyone else. The [README](README.md) covers what the app does; this covers how it's built and how to change it safely.

Suki shares its foundations with Vocal Sessions (`imperialfox/Vocal-Sessions`): the motion file, offline support, the layouts for each device, the sheets, swipe to delete, pull to refresh, the release tool and the test runner. When one of those is improved in one app, it can usually be copied to the other.

---

## The short version

1. Change the files in `js/` and `css/` (or `index.html` for markup, `sw.js` for offline behaviour).
2. Run `python tests/run.py` (about two minutes). Everything must pass.
3. Run `python tools/release.py 2.2` with the new version, and write the changes in `CHANGELOG.md` (a dated heading, an *italic headline*, then plain-English bullets).
4. Run `python tests/run.py release` to check the version agrees everywhere.
5. Push to `main`. GitHub Pages publishes it within a minute or two, and the **Tests** check runs on GitHub.

**Working with Claude:** Ivan reviews ideas first (wireframe, then prototype). Nothing is built into the app or pushed until he says **"render"**.

---

## Files

| File | What it is |
|---|---|
| `index.html` | The page: markup, the launch screen, `APP_VERSION`, and the list of css/js files it loads |
| `css/app.css` | All styles. Light and dark colours are the `--variables` at the top |
| `js/*.js` | The app's code, in the order `index.html` loads them (below). No build step |
| `sw.js` | Offline support. The page is fetched fresh (4-second timeout, then the saved copy); a new version is saved for offline use only once the page and every file it loads have downloaded. Versioned css/js files and images come from the saved copy |
| `manifest.json`, `icon.svg`, `icon-512.png`, `apple-touch-icon.png` | Home Screen name and icons |
| `splash/` | iOS launch images, light and dark, made by `tools/splash.py` |
| `tools/release.py` | Sets the version number everywhere at once, or checks it |
| `tools/splash.py` | Makes the launch images from `icon-512.png` |
| `tools/towns.py` | Makes `js/towns.js`, the town outlines for Location (Q16) |
| `tools/ratesnap.py` | Makes `js/ratesnap.js`, the rate history shipped with the app (Q23) |
| `tests/` | The test suite (see below) |
| `.github/workflows/tests.yml` | Runs the tests on GitHub after every push |

### The code, in load order

| File | Holds |
|---|---|
| `js/motion.js` | **The shared springs** (`MOTION`), copied from Vocal Sessions: gentle, nav and ripple springs as CSS `linear()` easings and `--ease-*`/`--dur-*` variables, Reduce Motion, the speed setting (`suki:motion`; 0 = off, used by the tests), and Suki's own `settle` and `leave` (Q11) |
| `js/catalog.js` | The catalogue (`CATALOG`), official price lookups (`refsFor`, `refFrom`), the fuzzy search (`searchItems`) and the whole-word match for logged purchases (`wordMatch`, Q14) |
| `js/prices.js` | The official DA-AMAS price snapshot (`window.sukiPriceReferences`) |
| `js/typical.js` | Typical prices with their sources (`window.sukiTypical`, Q02): fares, DTI suggested retail prices, shop and menu prices, rough guides |
| `js/reader.js` | Smart add's sentence reader (`READER`, Q14): word rules only, no screen code |
| `js/storage.js` | Categories, places and payment methods; checking (`cleanData`) and loading/saving data; the draft and last-backup date |
| `js/helpers.js` | Money and dates, icons, category tiles, layout (`MQ`, `layout()`), tabs and the on-screen state `U` |
| `js/screens.js` | Home, Till (with the change as cash, Q13), Search, Spending, Convert and Settings, plus the shared purchase form, purchase details and item details |
| `js/ui.js` | Form state `F`, the top bar, tab bar, top tabs and sidebar, `render()` and `go()`, sheets and toasts |
| `js/rate.js` | The exchange rate (`refreshRate`, `autoRate`) and the linked converter boxes. The rate comes from the first source in `RATE_SOURCES` that answers with a rate inside `RATE_RANGE`; `RATE_CHECK` keeps why the last check failed, for Settings. Also the rate for the day a purchase was made (`stampRate`, `dayRate`, `fixRates`, Q22) |
| `js/backup.js` | Saving files (share sheet or download), backups, restoring, erasing and the CSV export |
| `js/events.js` | Every button action (`ACT`), the forms, typing, swipe to delete, blocking zoom and keyboard shortcuts, and Quick Till's note press (Q18) |
| `js/towns.js` | The outline of every Philippine city and municipality (`window.sukiTowns`), made by `tools/towns.py`. Don't edit by hand |
| `js/locate.js` | Location when logging (Q16): that day's town (`dayTown`), the town you're in (`townAt`) and the arrow (`ACT.locate`) |
| `js/smart.js` | Smart add (Q14): Home's Log card's two sides, the preview, learning words, saving, and the "Words Suki has learned" taps |
| `js/gestures.js` | Pull to refresh and the update check, scrolling (the top bar turning to glass), rotating, online/offline, sheet scrolling and dragging sheets down |
| `js/onboard.js` | Onboarding (Q07): the Home Screen steps in Safari, the welcome card, tips and the Help screen |
| `js/ratesnap.js` | The rate history shipped with the app (`window.sukiRateSnap`, Q23): ECB pesos and dollars per pound, every weekday from 2016. Made by `tools/ratesnap.py`. Don't edit by hand |
| `js/news.js` | Rate history's news notes (`window.sukiNews`, Q23). Hand-checked; see Rate history below |
| `js/history.js` | Rate history (Q23): the history layers, the page, the chart, swipe back, and the news and central bank sheets |
| `js/boot.js` | Starts the app. Always last |

They're plain scripts, not modules: they share one global scope, and the tests reach into the app through its globals (`D`, `U`, `go`, `openSheet`…).

### How a screen is drawn

`render()` draws the current tab from `U.tab`, then the bars, then any sheet from `U.sheet`. Buttons carry `data-a="action"` (and `data-k`/`data-v`), handled in `ACT` in `events.js`. Typing never triggers a full redraw: Search, the Spending filter, Quick Till and Convert update just their own parts, and form fields write into `F` so a redraw puts back what was typed.

Details are drawn once and shown wherever they're reached: `purchaseDetail()` and `itemDetail()` appear in a sheet on iPhone and in the pane beside the list on iPad and Mac (`split()`).

Sheets: `openSheet(name, details, push)`. With `push`, closing it goes back to the sheet underneath (Edit from a purchase's details, an item from Price notes). A sheet with nothing to show closes itself. Redrawing the same sheet doesn't make it rise again and keeps its scroll.

### Every file has a version in its address

`index.html` loads `js/storage.js?v=2.1.0` and so on, so no phone can mix an old file with a new page. `tools/release.py` updates every `?v=`. **Add a new file by adding its `<script>` (or `<link>`) to `index.html` with the same `?v=`.**

---

## Where data lives

Everything stays on the device. There is no server.

| Where | Key | Holds |
|---|---|---|
| IndexedDB `suki-db` (version 1), store `kv` | `purchases`, `observations`, `rate`, `learned` (Q14) | All saved data (`D`) |
| localStorage | `suki:purchases`, `suki:observations`, `suki:rate`, `suki:learned` | The same, only when IndexedDB isn't available |
| IndexedDB `kv` (or localStorage `suki:`) | `rescue` | Records Suki couldn't read, kept before anything saves over them (Q05). Not backed up; Settings › Recovered data saves them as a file |
| IndexedDB `kv` (or localStorage `suki:`) | `safety` | What was on the phone before the last restore or Erase, so it can be put back (Q05). Not backed up |
| localStorage | `suki:lastBackup` | When a backup was last saved (not backed up) |
| localStorage | `suki:draft` | A half-typed purchase on Home (not backed up) |
| localStorage | `suki:smart` | A half-typed Smart add line (Q14, not backed up) |
| localStorage | `suki:logSide` | Which side of Home's Log card shows: `smart`, or missing for the form (Q14, not backed up) |
| localStorage | `suki:motion` | Motion speed on this device (not backed up) |
| localStorage | `suki:onboard` | Onboarding on this device: welcome seen, tips on, which tips are done (Q07). Not backed up |
| localStorage | `suki:reduceMotion` | Reduce Motion: `on`, `off`, or missing to match the iPhone (not backed up) |
| localStorage | `suki:noteAnim` | Quick Till's note animation (Q18, 2.24): `slot`, or missing for Fly. This device only, not backed up |
| IndexedDB `suki-rates` (version 1), store `kv` | `ecb`, `own` | Rate history (Q23, 2.23): `ecb` is `{v: 1, days: {date: [php, usd]}, older}`, the ECB days loaded from Frankfurter (not the shipped snapshot); `own` is `{v: 1, days: {date: {php, src}}}`, every rate loaded for Convert with its source. Its own database, so it never touches his records. Not backed up, not erased by Erase all data: it isn't his data and can be downloaded again. Anything wrong in it is thrown away whole and loaded again |

**These names have been the same since Suki 2.0. Never change them**; the tests load data saved by the real 2.0 app (`tests/fixtures/app-2.0.0`) to prove updating keeps everything.

`cleanData()` checks anything loaded or restored: records without a name or an amount are dropped, ids are made unique, bad dates become today, unknown categories become Other, and fields it doesn't know are kept. Data changes should be additive: add fields with a default; don't rename or repurpose existing ones.

A purchase: `{id, item, price, date (YYYY-MM-DD), category, location, venue, payment, notes, gbpAtPurchase, rateAtPurchase, rateDate?, rateSource?, rateEstimated?, edited?, said?, saidAt?}`. `rateDate` and `rateSource` (Q22, 2.22) are the day and source of `rateAtPurchase` ("2026-10-30", "Frankfurter (ECB)"); purchases saved before 2.22 don't have them. `rateEstimated: true` (Q22) means today's saved rate is standing in for the purchase day's rate until it can be looked up; it's removed once corrected. All three are in backups; `cleanPurchase` drops any that's the wrong kind of thing. `said` (Q14) is the line typed in Smart add; only purchases saved from it have one. `saidAt` (Q15) is the Siri Shortcut's stamp, `"2026-11-21 13:05"` (or just the day), only on purchases from a stamped line; `cleanPurchase` drops one that isn't a real date and time.
A learned word (Q14): `{id, word, category, label}`; `id` is the word, so each word is kept once.
A price note: `{id, itemId, itemName, price, date, location, venue, note}`. `itemId` points at a catalogue id, so **never rename a catalogue id**.

## Keeping data safe (Q05)

- **Loading** (`loadData`): anything that can't be read (a key holding the wrong kind of thing, or records `cleanData` has to drop) is copied to `rescue` first, and Home shows a notice until it's saved as a file. Amounts written as "₱459" or "PHP 1,250" are read rather than dropped.
- **Storage that won't open:** `STORE_WARN` shows a notice on Home, and saves go to localStorage. The next time IndexedDB opens, records in localStorage that it doesn't have are merged in by id, then the localStorage copies are removed.
- **Restore and Erase** call `keepSafetyCopy()` first and change nothing if it fails. Afterwards a toast offers Undo, and Settings › Your data offers "Before your last restore/erase" (`putBack()`, which swaps, so it can be undone too).
- **A backup with nothing usable** (no purchases and no notes after cleaning) is refused before the restore sheet.
- **"Couldn't save"** is a sticky toast (`toast(text, null, true)`) that stays until OK is tapped; other toasts drop in below it.

## Amounts and limits (Q06)

- `amount()` reads "1,000", "1 000" and "₱12.50", and returns null for anything else ("12.50.5"); `cents()` rounds to the centavo, so anything that rounds to ₱0.00 isn't an amount.
- Saved or restored prices must be ₱0.01 to ₱10,000,000 (`money()`); others count as damaged and go to Recovered data. Dates must be real (`isoDate()` turns 30 Feb into today, like any bad date).
- The rate refresh stops after two sources time out, and doesn't start when the phone says it's offline.
- Home's summary card takes the `long` class for totals over 11 characters: a size smaller, with Today under the total.

## Onboarding (Q07)

Following Apple's onboarding guidance: no tour, one welcome card, tips next to what they explain.

- `onboardStart()` runs once the launch screen has gone. The first time, it sets `suki:onboard`: a fresh install gets the welcome and tips; an install that already has data gets neither (Ivan never sees them unless he asks in Settings › Help).
- **In a Safari tab on iPhone or iPad** (`navigator.standalone === false`): the Home Screen steps sheet, locked, with Got it and Not now, on every open. Never in the Home Screen app.
- **The welcome card** is a locked, tall sheet (`sheetWrap(…, {lock, tall})`): no ✕, no tapping outside, no dragging, no Escape. Continue closes it for good.
- **Tips** (`TIPS`, one at a time): Till's amount chips, pull to refresh on Home, swiping a purchase, dragging the first details sheet down. Each goes for good when you do the gesture (`tipDone()`, called from the gesture code) or tap ✕. A tip sits below its target unless that would cover a main button or the tab bar, waits while a sheet is open, and shows once its target scrolls into view. Touch-only tips don't show without a touch screen.
- **Help** is its own screen (`U.tab = 'help'`), pushed from Settings.
- The tests' harness marks onboarding as seen (tips off) unless `test:fresh` is set, so it never gets in the way of other tests.

## Doors (Q08)

The rule: one place per thing, with several doors to it, and every door opens the same sheet or page. Any text that names a place is a door to that place. Add a door, not a new choice.

- **One Log sheet:** `ACT.newPurchase` opens the `edit` sheet for a new purchase. `data-v` sets the date (a calendar day) and `data-item` the name (Search with no match, with the cursor put in the amount). It's pushed over any open sheet, so saving goes back to it (the calendar). Its doors: Spending's + (`renderBar`, only with purchases), a picked calendar day up to today, Search with no match, and empty Spending's button. Quick Till's "Log this bill" and an item's "Log what you paid" open the same sheet with their own actions.
- **Home's card** is a `div.sumcard.doors` holding two buttons (`ACT.toSpend`, `data-v` `all` or `day`). They reset the range, category, filter and picked bar. With nothing logged it's `.sumcard.static.none`.
- **A purchase's prices row** (`pricesRow()` in `screens.js`) uses `strictItemFor()` in `catalog.js`, not `itemFor()`. The item's name or English name has to appear in the purchase as whole words (plurals allowed, the longest name wins). Aliases don't count, so "Water" or "San Miguel" get no row; that keeps loose matches (Spaghetti → Massage) from offering the wrong prices. "You paid" on an item uses `wordMatch()` since Q14 (below).
- **Words as doors** are `.tlink` buttons inside the text: `goRefresh` (the old-rate note), `goSearch` (Price notes, which closes every sheet first) and `goConvert`. Settings rows become doors by passing an action to `row()`; Storage used and Works offline stay plain, because there's nothing to open.
- Spending with nothing logged returns early from `scrSpending()`: no chart, range switch, chips or filter.
- Left out on purpose (navigation audit): links on every detail row, a Settings tab, a Notes tab, a door from a calendar day to the Spending list.

## Search finds your records (Q09)

- **One matcher:** `matcher(q)` in `screens.js` splits what was typed into words; a record matches when every word appears somewhere in it, in any order. Purchases look at item, place, where bought, category, how paid and notes; price notes at the item name, place, where bought and note. **Spending's filter uses the same matcher** (Ivan, 1 Nov 2026), so "Show all N in Spending" always opens the same N. Change one and you change both.
- **With text,** `searchResults()` shows Prices (catalogue matches, as before), then `recordResults()`: **In your purchases** (`#mine`, newest first, `MINE_SHOWN` = 3 rows, then `ACT.searchToSpend`, which opens Spending on All with the filter set to the same words) and **In your price notes** (`#mynotes`, rows open the item). The category chips narrow the prices only, not his records.
- **No match:** "No clear match" shows only when nothing of his matches either. Q08's Log row shows whenever there's no price match.
- **All view** starts with `notesDoor()` (`#notesDoor`), opening the same Price notes sheet as Settings.
- Rows reuse `purchaseRow()` and open the same purchase and item sheets as everywhere else.
- Left out: the search circle beside the tab bar (still an idea).

## Time doors on Spending (Q10)

- **The period label** in `spendSummary()` is a button (`.plabel.cal`, `ACT.calFromSpend`) with `ICON.cal`. It opens the same calendar sheet as Home's title: on that period's month (All and this week: this month; never a month in the future), with the day picked for D or a picked day bar (`U.calD`). A picked week bar opens its Monday's month with no day picked. The picked bar stays, so closing the calendar comes back to the same view.
- **A picked bar narrows the list:** `spendRows()` filters to `pickedBar()` and starts with `#pickLine` ("Showing Yesterday only", the week of … for weekly bars) and a `clearBar` button whose words come from `wholePeriod()` ("Show this week", "Show all of November", "Show all since 23 Oct"). Anything that changes `U.bar` must redraw both `#spendSum` and `#spendList`: use `barChanged()`.
- **What keeps the pick:** `KEEPS_BAR` in `events.js`: the headline card, any sheet (and its scrim), a purchase row or Show more in the list, and the details pane on iPad and Mac. Any other tap clears it, as before Q10.
- **Clearing from a tap outside** (`widenListSoon()`) redraws the headline at once but widens the list only after the click lands (or 700 ms with no click, for a scroll). Widening on pointerdown moved whatever was below the list (Export as CSV) or, near the bottom of the page, above it (the filter's ✕) before the click landed, so the tap was lost.
- Help › Hidden gestures lists "Tap Home's title" (`scrHelp()` in `onboard.js`).
- Left out: a calendar tab, changing what the chart shows.

## Things arrive and leave (Q11)

- **Sheets leaving:** `renderSheet()` knows how deep the sheet on screen is (`shownDepth`). When a redraw has fewer sheets than before, the old `.scrim` is moved into `#leaving` (in `index.html`, `inert`, nothing in it takes a tap) and `sheetAway()` in `ui.js` plays its exit: iPhone slides it to `translateY(115%)` in 330 ms on `cubic-bezier(.3,0,.25,1)` from wherever it is (half-risen, or dragged); iPad and Mac shrink to .94 and fade in 220 ms; Reduce Motion fades in 200 ms. Times are × the slow-motion speed. Because every close path redraws, they all get it for free; a new way of closing needs nothing extra. Its ids are removed, so tests and `$()` never find a sheet twice.
- **Back to the sheet underneath:** `openSheet(…, push)` keeps the sheet's scroll in the stack (`top`), and the sheet underneath comes back with `.still` (no second rise) at that scroll. The leaving one has a clear background, so the dim isn't doubled, and sits at z-index 41.
- **The page behind** uses `--mspeed` (published by `motion.js`: the slow-motion speed, or 0 with motion off or Reduce Motion) in its transition, so Slow motion slows it too. While a sheet closes, `body.unsheet` switches it to the quicker 0.33 s curve.
- **Dragging a sheet down** past 90 px closes it at once; the exit carries on from the finger's position.
- **Rows:** `rowsBefore()` / `rowsAfter(before)` in `ui.js` wrap a change that redraws a list (FLIP, since lists are innerHTML). They're called where purchases change: `submitForm` (a new purchase), `delPurchaseYes`, its Undo, and `undoSave`. A purchase new to the list (`D.purchases` before and after) settles in with `MOTION.settle()`; purchase rows, "Show all" rows, `.hdr` and the `.grp` under each glide from where they were on `gentle`; a purchase row that went is copied into `#leaving` (`.rowghost`) and `MOTION.leave()` fades and shrinks it. Rows off screen don't move, and rows in a sheet that is itself closing go with the sheet. Editing a purchase doesn't use it yet.
- **Settle** is `MOTION.settle(el, i, drop)` in `motion.js`: a 12 px drop (or `drop`: the Till uses 10) with opacity 0 → 1 on the `ripple` spring, rows 45 ms apart, a fade with Reduce Motion. Reuse it for anything that lands. Keep it out of tabs, Settings, Convert and figures. `MOTION.leave(el, ms, to)` shrinks to .94 in 220 ms unless given its own time and size.
- **Home's Save button** shows "✓ Saved" (`#homeSave.saved`, `savedTick()` / `savedPop()` in `events.js`) for 1.4 s (× slow motion), with or without motion; `saveBtn()` in `screens.js` keeps it through a redraw.
- **Undo on "Purchase saved"** is `undoSave(id)`: it removes that purchase, saves and says "Purchase removed".

## Calendar tints and the price range strip (Q12)

The rule: a number next to something to compare it with. No good or bad words or colours, and nothing here animates.

- **Tints:** `tintSteps(spent)` in `helpers.js` ranks a month's spending days by amount and gives each a step 1–3 by thirds (`t1`/`t2`/`t3` on `.cday`, beside `has`). Days with the same amount share their average rank, so equal days sit together; fewer than three days all get step 2. The calendar sheet (`ui.js`) adds the `.tkey` ("Less ● ● ● More", hidden from VoiceOver, since each day's label keeps its amount) and the footnote only when the month has spending.
- **Colours:** `--tint-1/2/3` with `--tint-1-ink` and `--tint-3-ink` (the day number on each step), and `--band` for the strip. Light grows darker (`--tint-3` is a deeper blue than the accent), dark grows brighter. They passed the dataviz palette validator as an ordinal ramp against the surface in both modes (the prototype's softer .12/.32 tints failed its light-end check and their top two steps looked alike), and each ink is the one with the better APCA score. Change them together and re-run it.
- **A picked day** is `.cday.on`: solid `--fg` with `--bg` text and no outline, so it never reads as a big day.
- **The strip:** `priceStrip(rows, paid, obs)` in `screens.js`, passed into `typicalCard(id, strip)` and drawn under the price rows, before the sources. Only when the item has a typical price and at least one purchase or price note. One `.band` per typical row (5 px wider each side, so an exact price is a small pill); `.sdot.s-paid` and `.sdot.s-note` buttons (not `.paid`/`.note`: `.note` is a paragraph style). Dots within about a dot's width (3% of the strip) stack upwards 12 px a level, up to 5 levels; each dot's tap area is one level tall, with the top of a stack reaching up and the bottom down, so stacked dots don't steal each other's taps. The axis rounds to 5, 10, 50, 100, 500 or 1,000 depending on size.
- **Dot and row:** `U.dot` is `'paid:<id>'` or `'note:<id>'`. `ACT.pickDot` toggles a dot; a capture-phase click listener in `events.js` lights a row's dot (`data-dot` on You paid rows and price note rows; a button inside the row, like the bin, is its own tap) and clears it on any other tap, except while another sheet is open over the item (the purchase, deleting a note), so coming back finds it lit. `showDot()` changes only classes and the label in place, so nothing moves under the finger. `openItem` resets it.
- **The label** (`.slabel`) is placed with `left: x%` and `translateX(-x%)`, which keeps it inside the strip at any position without measuring. Long text ends in an ellipsis.
- Left out: the Home week strip (Spending's week chart already shows it), a strip on Search rows, budgets.

## Quick Till: change as cash (Q13)

- **Buttons:** `TILL_KEYS` in `screens.js` (₱20 coin, then the ₱50, ₱100, ₱500 and ₱1,000 notes) after Exact, in `.denoms` (a six-column grid, 44 pt). Keep the `.denoms` class: the Till tip (`TIPS.till` in `onboard.js`) points at it. They still use `cashAdd` / `cashExact`; the ✕ in the cash box is `#cashClear` (`cashClear`), hidden while the box is empty. A `pointerdown` on it is cancelled so the keyboard stays where it was.
- **The breakdown** is `asCash(centavos)`: notes `NOTES` (1000, 500, 100, 50), coins `COINS` in centavos (2000, 1000, 500, 100, 25, 5, 1). No ₱200 note, no ₱20 note, no 50¢ coin. Always work in centavos (`tillView()` does), so it's exact. `cashWords()` is the VoiceOver line on `#cashRow` (`role="img"`).
- **Drawing:** `cashWant()` lists the pieces, each with a key (`n100.0`, `c25.1`, `s1000` for a bundle) that stays the same while it's on screen. `tillOut()` draws them still (a full redraw); `updateTill()` (typing or a button) changes the words in place and calls `renderCash()`, which keeps pieces whose key stays, settles new ones in (`MOTION.settle(el, i, 10)`), shrinks the ones that went (a `.cghost` copy, `MOTION.leave(g, 160, .6)`) and glides the rest on `gentle`. The figure never animates, and a bundle's count changes in place. With five or more of one note (`BUNDLE_AT`) it's one bundle.
- **Colours** are `--note-50` … `--note-1000` (each with an `-ink`), `--coin`, `--coin-ink` and `--coin-ring`, in `:root` only, so they're the same in dark mode. No banknote artwork: copying any part of a note needs the BSP's approval.
- `.tillout` has a 148 px minimum height, so Log this bill only moves when coins wrap onto a second line.
- **Next:** Q18 restyled these notes and coins (2.24, below); Q19–Q21 add the drawer. Reuse `asCash` and the keys.

## Till drawer (Q18–Q21)

The till drawer idea, built in four phases, each its own queue item: the note press (Q18), the drawer (Q19), its contents and fullness (Q20), and the haul and maker's mark (Q21). Spec and plan: the Suki project docs `idea_till_note-press_notes.md` and `q18_till_drawer-and-note-press_blueprint.md`. Each phase adds its notes here.

### The note press (Q18, 2.24)

- **Where:** the code is one block in `events.js`, after `setTillCash`. The timings are named once at its top, `PRESS` (the tilt) and `FLIGHT` (Fly, Slot, the landing nod and how long the slot line stays), and are the prototype's, which Ivan approved.
- **Finger tilt:** a document `pointerdown` on any `#app .denoms .dn` (all six, Exact too) animates the button to `perspective(260px) rotateX rotateY scale(.94)`, up to 20° each way towards where the finger is, in 90 ms, held with `fill: forwards`. `pointerup`, `pointerleave` or `pointercancel` springs it back in 520 ms. Only with `MOTION.on()`; otherwise the old `.dn:active` scale is all there is.
- **Flight:** `ACT.cashAdd` calls `noteFly(button, value)`. Each flight is `{el, v, mode, a}` in `flights`; the element is a `.nfly` on `<body>` (fixed, `pointer-events: none`). It adds its value only when it lands (`noteLands`), with `tillPlus(v)` working from the amount at that moment, so fast taps each add once. Fly is a 13-step quadratic arc to the end of the typed amount (`amountEnd`, measured with a canvas), the ₱20 with `rotateY` to 720°. Slot ends on `#tillSlot` with `scaleY(.04)`.
- **What you did last wins:** typing in the cash box, ✕ and Exact call `dropNotes()` (gone, nothing added). `render()` calls `landNotes(true)` before it redraws, so a redraw, a sheet opening or switching tabs adds any note still in the air at once and leaves no `.nfly` behind.
- **The slot line** is `#tillSlot.slotln` inside `.cashbox`, absolutely placed in the 14 px gap above the buttons, so the layout doesn't move. Hidden at rest (opacity 0); `.show` while a note slots in and for 1.2 s after it lands (`slotLine(ms)`, × slow motion). Not a button yet: **Q19 makes it the drawer's handle** (and gives it its VoiceOver label).
- **The setting:** `noteAnim()` / `setNoteAnim(v)` in `storage.js`, key `suki:noteAnim` (`slot`, or missing for Fly; anything else reads as Fly). Settings › Accessibility › Note animation is `#noteSeg`, a two-segment `.segc` like Reduce motion, set in place by `ACT.setNoteAnim`.
- **Materials:** `--coin-hi`, `--coin-lo`, `--coin-edge` and `--ring-edge`, mixed from `--coin`, `--coin-ink`, `--coin-ring` and `--white` in `:root` only, so they're the same in dark mode. Notes in the change row and in flight get a paper `linear-gradient` and coins a metal `radial-gradient`, as `background-image` only, so each piece's `background-color` is still its Q13 colour (the Q13 tests read it). The drawer's own tokens (`--dr-*`) come with Q19, which is the first to use them.
- **Only the two boxes can be selected (2.24.1):** `#app.tab-till` turns off text selection and the long-press menu, and the two inputs turn selection back on. A new element on the Till is unselectable by default; give it `user-select: text` only if it should copy.
- **Reduce Motion and motion off:** no tilt, no flight; the amount changes at once, exactly as before Q18. That's why every older test (motion off by default) is unchanged. Tests with motion on that tap a note must wait for `.nfly` to be gone before reading the change row (`test_till.py` section 6 does).

## Location when logging (Q16)

- **That day's town:** `purchaseForm()` calls `dayTown(v)` for a new purchase (Home, or the Log sheet with no `U.sd.id`). It fills `v.location` from `townOn(day)`, the newest purchase that day with a place (`D.purchases` is newest first), and sets `v.locFrom = 'auto'`. An auto place is worked out again on every draw, so it follows the data (a deleted purchase, a new day, a half-typed draft reloaded tomorrow). `locSource(v)` gives the label: "from earlier today", "from that day" or "near you".
- **`v.locFrom`** lives in the form state `F` (and so in Home's draft), never in a saved purchase: `'auto'`, `'near'` (the arrow) or `'typed'`. `onField` sets `'typed'` on any typing in Location, including clearing it, and then nothing fills it. A new form state (after saving, or any Log sheet opener) starts again.
- **The arrow** (`.locbtn`, `ACT.locate`) calls `navigator.geolocation.getCurrentPosition` once, on the tap only: never at launch, no watching. Code 1 is "Location is off…"; any other error "Couldn't find where you are…". If the form changed meanwhile (saved, sheet closed, or he typed a place), the answer is dropped.
- **`townAt(lat, lng)`:** the town whose outline holds the point (the smallest wins, for a town inside another); else the town whose outline is nearest, within `NEAR_KM` (40 km), for beaches and boats; else null. The outlines are decoded on the first tap. Low-resolution outlines are about 110 m off at borders.
- **Updating the towns:** download `geojson-lowres.zip` from the latest release of [faeldon/philippines-json-maps](https://github.com/faeldon/philippines-json-maps/releases) and run `python tools/towns.py geojson-lowres.zip 2026-3q` (the PSGC quarter its `latest/manifest.json` names). Names are tidied as people say them ("City of Makati" is Makati, "City of Cebu" is Cebu City, because Cebu is also a province). Keep the credit in Settings › About: NAMRIA and PSA, through OCHA's COD-AB (CC BY-IGO).
- **Why not GeoNames** (the handoff's default): its download site is blocked from the build workspace, and the GitHub copy of its city list (`all-the-cities`, from cities1000) has no San Jose City (Nueva Ecija) and only 1,190 of the 1,642 towns. The PSA outlines are complete and current, and an outline beats a single point near borders (Cubao is in Quezon City, not San Juan).
- **Next:** prices by region (an idea in the queue) can use `townAt` or the saved place.

## Home's exchange rate card (Q17)

- `rateCard()` in `screens.js` draws it at the top of Home's `dash`, so on iPhone on its side, iPad and Mac it heads the left column. It's one `button.ratecard` with `data-a="goConvert"`: tapping opens Convert and never refreshes (`goRefresh` is the door that does).
- `rateAge(r)` gives "Updated just now", "N min ago", "Nh ago" (under a day), then `relDay` ("yesterday", "3 days ago", the date), from `D.rate.cachedAt`. `tickRateAge()` updates the age and the VoiceOver label in place every 30 s and on coming back to the app, with no redraw. Convert's own line (`rateLine()`) is unchanged.
- With no rate it's `.ratecard.none`: "Exchange rate · Get today's rate on Convert". An old rate is never red.
- Colours: `--suki-top`, `--suki-bottom`, `--suki-glow`, `--suki-fg`, `--suki-fg2`, `--suki-rim` and `--suki-shadow`, the same in light and dark. They're Suki's icon colours, a one-off for this card only (`test_ratecard.py` checks no other rule uses them). White is at least 11:1 on the navy and 7:1 under the glow; the softer white (label and age) at least 5:1.

## Pounds at the rate you paid (Q22)

- **Totals:** `poundsOf(list)` in `helpers.js` adds each purchase at its own `rateAtPurchase`; one with none counts at today's saved rate (`today`), and one marked `rateEstimated` is counted (`est`). `poundsNote()` gives "2 at today's rate · 1 estimated" (`.cap.rn` on Home's summary card, `.gb.rn` under Spending's total). With no rate saved and a purchase with none, no pounds are shown. While a bar is picked, Spending keeps the note's line (empty) if the whole period has a note, so clearing the pick doesn't move the list under the finger (Q10's rule). Home's summary card and `spendSummary()` (the period, a picked bar, a category or a filter) use it; `gbpThen(p)` does the same for one purchase ("You paid" on an item's page). Catalogue prices and price notes still use today's rate (`inGbp`).
- **Which day:** `rateDayFor(date)` is the day to ask for: the day before the purchase's date, or null for today and later. Frankfurter answers a weekend or holiday with the weekday before, so a Sunday or Monday purchase gets Friday's. That's the last rate published before the purchase's day, which is right in Manila too (the ECB publishes about 23:00 there).
- **Saving never waits:** `stampRate(p)` sets the rate as the purchase is made (the form, logging on a calendar day, the Till's Log this bill, Smart add, and an edit that changes the date): that day's rate if `DAY_CACHE` already has it, otherwise today's saved rate, with `rateEstimated` when the date is before today. Then the save goes through and `fixRates()` runs without being waited for. An edit that keeps the date leaves the rate alone.
- **The lookup:** `fixRates()` looks up each day that has an estimated purchase (`dayRate(day)`: `DAY_SOURCES`, Frankfurter v2 then v1 on `api.frankfurter.dev`, then the Currency API's file for that date on jsDelivr then `{date}.currency-api.pages.dev`; two timeouts stop it). A reply outside `RATE_RANGE`, for a later day, or more than `DAY_BACK` (10) days before, is ignored. When it finds one, it sets `rateAtPurchase`, `gbpAtPurchase`, `rateDate` and `rateSource` and removes `rateEstimated` on purchases still estimated for that day, judged after the reply (so one deleted or re-dated meanwhile is left alone), saves, and redraws unless a box has the cursor (`showFixed`). It runs after a save, at launch, on going online and on coming back to the app; one call at a time (`fixBusy`, `fixAgain`). Nothing else is ever rewritten: only purchases marked estimated.
- **The details:** `rateBehind(p)` is the line under "In pounds then" (`.ratewhy`): "£1 = ₱83.11 · Fri 30 Oct · ECB", plus "estimated". Any source naming Frankfurter or the ECB shows as ECB. The day is written out by hand, because browsers disagree on a comma after the weekday (GitHub's Chromium writes "Fri, 30 Oct"). Spaces inside each part don't break, so a long line wraps between parts.
- **Tests:** `rate_route` in `tests/harness.py` answers dated requests too (`days={'YYYY-MM-DD': rate}`; Frankfurter answers a weekend with the Friday before, Currency API the day itself) and can log every address asked for (`log=[]`).
- Left out: older purchases aren't given their day's rate in bulk. Rate history (Q23) doesn't feed `dayRate()` yet: a back-dated purchase still asks Frankfurter, even when the day is in the saved history (an idea in the queue).

## Rate history (Q23)

The rule: the page never depends on one service. Each layer can fail and the page still shows what it has, and says why.

- **The door:** Convert's rate row is `button.rdoor` (`ACT.openHistory`), with Refresh beside it. Home's rate card still opens Convert. The page is a tab of its own, `U.tab = 'history'` (`SCREENS.history = scrHistory`), that belongs to Convert (`tabOf`), with a back button in the bar. `go()` slides it in on iPhone and zooms it on iPad and Mac; back slides Convert in from the left, except after a swipe back (`SB_GONE`).
- **Layers** (`history.js`): `histSeries()` is the ECB series, the snapshot (`snapDays()`, from `js/ratesnap.js`) merged with the days saved in `suki-rates` (`H.ecb`, which win). `ownPoints()` is Suki's own record (`H.own`, kept by `histKeep()` from `refreshRate`, plus today's saved rate), only on days the ECB series lacks; they're drawn as hollow dots (`.hown`), never on the line. `histInit()` reads the saved copy once (`cleanECB`, `cleanOwn`: anything wrong and the whole key is deleted, `H.threw`).
- **Asking:** `histTopUp()` asks for the days after the newest one Suki has, at most every `HIST_GAP` (half an hour) unless forced (going online), and not when the newest day is already the last weekday (`hWorkday`). With nothing at all, the last year first, then the rest. `histOlder()` asks for April 2005 to the day before the snapshot, only when All is tapped (`H.older` once loaded). `HIST_SOURCES`: Frankfurter v2 (`/v2/providers/ecb/rates`, an array of `{date, quote, rate}`), then v1 (`/v1/a..b`, `{rates: {date: {PHP, USD}}}`), both base GBP, quotes PHP and USD; two timeouts stop it.
- **Checking a reply** (`histCheck`): real dates in order, inside the dates asked for (v1 may start up to a week early), pesos inside `RATE_RANGE`, dollars 0.8–3, and no day more than `HIST_JUMP` (10%) from the one before, including the saved day before the reply when it's under a week earlier. Not 5%, the handoff's "about 5%": the real ECB series has a 6.8% day (24 Jun 2016, the day after the EU referendum), which 5% would refuse. Anything wrong refuses the whole reply. `tools/ratesnap.py` uses the same checks.
- **What it says:** `HIST_CHECK` keeps why the last check failed, for Settings › Last rate check (`rateCheckText()`, only when it failed). `statusHTML()` is every gap's line: offline (and "Connect once to load the history since…" when nothing has loaded yet), checking, "History up to … Couldn't reach Frankfurter", weekends, "Monday's rate comes at about 4 pm UK time, 11 pm in Manila", a saved rate from another source, and All without the older years. With no history at all it's the "Connect once to load the history" card, never an empty chart.
- **The page:** `scrHistory()` draws the title and the range pill (`#hSeg`, `ACT.hRange`; the knob moves in place and only `#hbody` is redrawn, by `histRedraw()`), then `histBody()`: the headline (`headHTML`), status lines, the strip, the direction line, the chart, "Why it moved" (`whyHTML`, hidden unless both ends have a dollar rate), What happened (`newsListHTML`, four then `hShowAll`) and the footer. `render()` calls `histAfter()` to draw the chart once it has a width, and the chart redraws on resize. `HV` holds the range (Y each time it's opened) and Show all. Dates are written by hand (`hDate`), never with `toLocaleDateString`, so every browser shows the same.
- **The chart** (`drawHistChart`): an SVG as wide as its box (so 1 unit = 1 pt), the line (`.hline`, thinned to about 600 points for 5Y and All), the newest day (`.hend`), own points, news dots in a lane below (`.hdot.peso` filled, `.hdot.pound` hollow, in grey: green and purple are categories), the lane greyed after `sukiNews.checked` (`.hlate`) and the trip line (`.htrip`). Its `aria-label` is `sentence()`. `HGEO` keeps its geometry for the finger.
- **The finger:** pointer events on `#hchart` (`touch-action: pan-y`, so up-and-down still scrolls) set `HSCRUB` and redraw only `#hHead` and the cursor (`hPick`); a news dot within 12 pt wins. Lifting on a dot opens its sheet (and eats the click after it). While a finger is down, `render()` waits (`histHold`, `HPEND`) and redraws once it lifts.
- **Swipe back:** pointer events on the page (not the chart, a box, or on iPad and Mac) start once the finger moves 10 pt right and mostly sideways. `sbUnder()` draws a still copy of Convert in `#under` (ids and actions removed, `inert`), `body.swiping` lifts `.wrap` above it, and `.wrap` follows the finger. Past a fifth of the screen or a quick flick it goes back; otherwise it springs back. The page can't be text-selected (a mouse drag on selected text would start a native drag and cancel the swipe).
- **The trip line** (`tripStart`): the first purchase of the latest unbroken stretch, no gap of 14 days or more, and only while the newest purchase is under 14 days old. Shown when it's inside the range, before the newest day.
- **Sheets:** `news` (`newsSheet`, `U.sd.id` is `date|side`) and `cbrate` (`cbSheet`), both in `sheetHTML()`. From a news sheet, the central bank sheet is pushed, so closing it goes back. Help › Money has the same sheet.
- **Upkeep, about monthly** (when Ivan asks, or with the price refresh): Claude drafts new notes in `js/news.js` and Ivan approves them; check every link still opens (official pages move); update `checked`. A note needs a real date (not in the future), a side (`peso` or `pound`), a title under about 60 characters, a plain explanation, a tag, its source's name and a link to bsp.gov.ph, bankofengland.co.uk or psa.gov.ph; no two on the same day and side (`test_history.py` checks). At the 3 Nov 2026 check: the 22 Oct note links to the BSP's *Selected Economic and Financial Indicators* (which states the decision), until the BSP publishes that meeting's highlights or its next Monetary Policy Report, so swap it then. The prototype's 16 Oct note ("Peso passes ₱63", put down to US inflation) was left out: no BSP, Bank of England or PSA record says it.
- **The snapshot:** refresh it with any normal build: `python tools/ratesnap.py` (asks Frankfurter for 2016 to today), or `--json file` from a saved list, `--check` to see what's shipped. 2.23's was made from the prototype's ECB series (fetched 2 Nov 2026), because the build workspace couldn't reach Frankfurter.
- Left out: comparing two dates, your real rate against the reference, copying a summary, rate alerts, forecasts, live news, news filters, a new tab.

## Smart add (Q14)

- **The two sides:** `logCard()` in `smart.js` draws the "Log a purchase" heading with its pill (`#sidePill`, `ACT.logSide`) and `#logwrap` holding one `.face`: the form (`formFace()`, the same `form[data-form=home]` as before) or Smart add (`smartFace()`, `#smartCard`). `LOGSIDE` is `'form'` or `'smart'`, kept in `suki:logSide`. `switchSide(to)` swaps the face in place (no page redraw) and calls `MOTION.fold()`.
- **The fade** (`MOTION.fold` in `motion.js`): the old face is copied (`.lghost`, ids and actions removed, `inert`) over the new one. The typing box is the hinge and slides between its spots; the other rows blur by distance from it (cubic) and fade, 28 ms apart, and the new rows resolve from blur and dimness, 45 ms apart. Only rows blur, never the card. Reduce Motion is a crossfade; motion off does nothing. A switch mid-way removes the copy first, and a full redraw replaces `#logwrap`, so nothing is ever left behind. If two frames take over 120 ms during a fold, later folds that session are crossfades. Don't name a class `ghost`: it's a button style.
- **Typing** (`#smartText`) writes `F.smart.text`, saves `suki:smart`, and calls `updateSmart()`, which redraws only `#smartSugg` and `#smartOut`. Never call `rerender()` from typing: the box would lose the keyboard.
- **The reader** (`READER.read(text, now, learned, rate)` in `reader.js`): lines first; within a line, a day, `both|all|each by …` and an opening `At SHOP in TOWN,` are shared; then sure splits (`also`, `;`) and soft splits (commas, and, then, plus) only between two amounts. A comma inside 1,250 is never a split. Each purchase: day, how paid, the amount (the last sure one: ₱ P PHP pesos £, else the last plain number; quantities like `2 kilos`, `for 2 nights` and names like `Terminal 3` aren't prices), places (`from X to Y`, `in`, `sa`, `at`, `to`), the shop (`SHOPS`: where bought and a category hint), the item (what's left), then the category: learned word → price list (`wordMatch` + `catOf`) → clue words (`CLUES`) → shop → a guess. A Shortcut stamp `[yyyy-mm-dd hh:mm]` at the start of a line sets the day words count from (Q15 builds on it).
- **What `smart.js` adds:** the town from earlier that day when no place was said (`townOn`, `locAuto`), Your usual when no amount was said (`usualFor`: the middle of the last three of the same thing, by `thingOf`, at the same place first), and changes made in the preview (`F.smart.over[i]`, cleared when the line changes). `SMART_LAST` is the list shown.
- **The preview** asks only what's missing (`#smartPrice`, `#smartItem`, typed in place), offers an either/or for a tie (`ACT.smartPick`), tints a guessed category, flags a future day and pounds in `--warnbg`. The typical note (`versus()`) shows only for a whole-word match with a typical price. A list's rows (`ACT.smartCheck`) open the `edit` sheet with `U.sd.smart = i`: titled "Check purchase", its Done (`smartChecked()`) writes back into `F.smart.over` and saves nothing.
- **Saving** (`smartSave()`) adds each with `said`, the rate and its own id, keeps Home's "✓ Saved" (`#homeSave[data-side=smart]`, which `savedTick()` hands back to `updateSmart()`), settles the rows (`rowsBefore`/`rowsAfter`) and offers one Undo for all (`undoSaves`). Edit in the form (`ACT.smartToForm`) moves the one purchase into `F.home` (with `said`) and switches sides; the form keeps `said` through `readPurchase`.
- **Learning:** a category changed in the preview or the check sheet calls `learnWord()`, saving `{word: learnKey, category, label}` in `D.learned` (`learnKey`: the name up to two words, else its first word). `learnedMap()` feeds the reader. The `learned` sheet (Settings › Your data, and a link under Smart add) lists and forgets them. They're in backups, the safety copy, Erase and the restore sheet; a backup or safety copy without `learned` leaves the phone's words alone.
- **Matching:** `wordMatch(text)` in `catalog.js` is the whole-word match for logged purchases: name, English name (up to three words) and other spellings, whole words only, plurals, one-letter slips in words of six letters or more, the longest wins, and `whole` when it covers everything typed. The reader, Your usual and "You paid" (`paidFor`) use it; Search keeps `searchItems`, and the prices row keeps `strictItemFor`.
- **The form's amount box** reads P50, "50 pesos" and 2k through `formAmount()` in `helpers.js`, falling back to `amount()`.
- **Tests:** `tests/fixtures/smart_phrases.json` holds 123 made-up phrases and what each should read as (read on Sunday 1 Nov 2026 at noon, £1 = ₱76.12). Add a phrase there for any reader change. Everything in it is invented: no real purchases.
- Left out: any AI, a bottom sheet (turned down), the flip, the prototype's "Try" example chips (they'd put made-up purchases a tap away from his real log).

## The Siri inbox (Q15)

- **The Shortcut** (built by Ivan on his phone; the steps are in Settings › Help › Log by voice with Siri, `siriBody()` and `SIRI_STEPS` in `onboard.js`, sheet `siri`) appends `[yyyy-MM-dd HH:mm] what he said` to a note called Suki inbox and copies the whole note. He pastes it into Smart add, as often as he likes.
- **The stamp:** `READER.read` takes a valid stamp off the start of a line (the day still counts from it, as in Q14) and puts it on every purchase from that line as `saidAt` (`READER.stampOf` checks it's a real date and time). Saving keeps it beside `said`, and so do `readPurchase` (the form, Edit in the form, the check sheet, editing a saved purchase) and backups.
- **Already saved:** `READER.sameKey(p)` is `saidAt|said` (lower case, spaces squeezed), or `''` without a stamp. `smartRead()` marks `p.already` when a saved purchase has the same key. The preview shows those rows greyed (`.row.done`, a `div`, not a button), the header is `#smartHead` ("3 new · 2 already saved", "All 5 already saved", "Already saved"), and `smartSave()` saves only the rest. With nothing new there's no Save button: `#smartNone` with Clear the box (`ACT.smartClear`).
- **Lines without a stamp are never skipped,** so "jeep 14" typed twice saves twice. The same words with another stamp are new. Two identical stamped lines in one paste both save (they're the same minute and words, so they could be two real purchases); pasted again, both show as already saved.
- A purchase saved by Q14 from a stamped line before 2.21 has no `saidAt`, so that one line could save again once. Delete the copy if it does.
- Help's "Smart add" is a door (`ACT.goSmart`): Home, on Smart add, with the cursor in the box.
- Left out: opening Suki from the Shortcut (`webapp://`), a Paste button, any server or AI tidying.

## Backups

A backup is a JSON file: a plain-English `README`, `app: 'Suki'`, `schemaVersion: 1`, `appVersion`, `exportedAt`, `device`, `purchases`, `observations`, `rate` and `learned` (Q14; older backups without it still restore, keeping the phone's learned words). Backups from 2.0 (without `README`, `appVersion` or `device`) still restore. Files are named `Suki backup · YYYY-MM · Device.json`.

## Updating the typical prices (Q02)

`js/typical.js` maps a catalogue id to a list of prices: `{label, low, high, unit, area, kind, source, url, date, note?}`. `kind` is one of `fare` (set by LTFRB), `srp` (DTI suggested retail price), `shop` (a supermarket shelf price), `menu` (the chain's own menu), `listed` (published by the company or a news report) or `guide` (a rough guide from travel writers). Change a price, its source, link and date together, and update `checked` at the top. **Never add a number without a source.** Search shows the official DA price in a row where there is one, otherwise the typical range. Every catalogue item belongs to one Search chip through `browseOf()`; "You paid" matches logged purchases to an item with `itemFor()`.

## Updating the official prices

Replace the snapshot in `js/prices.js` with the new period, area, source link and records. Each record's `itemId` must be a catalogue id. Mention the new period in the changelog.

---

## Tests

```
pip install playwright==1.56.0
python -m playwright install chromium
python tests/run.py                  # everything, side by side: about two minutes (before every push)
python tests/run.py quick            # all but layout and random taps
python tests/run.py data flows       # just some files
SUKI_FUZZ_STEPS=2000 python tests/run.py fuzz   # a longer random-tap run
```

The tests drive the real app in Chromium, served from `localhost` as GitHub Pages would serve it, with motion off so nothing waits on a spring. Every exchange-rate source is answered by the tests themselves (`rate_route` in `tests/harness.py`, which can also take a source down or give it a bad rate), so they never need the internet. Add a new source's address to `RATE_HOSTS` there too. Screenshots of every screen go to `tests/output/`.

| File | Covers |
|---|---|
| `test_release.py` | The version agrees in the app, README and CHANGELOG, and every file `index.html` loads exists |
| `test_flows.py` | Logging (with errors and the draft), Spending (chips, filter, days, details, edit, delete, swipe, CSV), Quick Till, Convert, Search and price notes, Settings, empty states |
| `test_doors.py` | Q08's doors: Home's two figures, Spending's +, logging on a calendar day, a purchase's prices row (whole words only, and on iPad), the old-rate link, Price notes' links to Search, Search's Log row and Settings rows that open things |
| `test_search.py` | Q09: Prices, In your purchases (three rows, Show all with the same count in Spending), In your price notes, every word in any order (Search and Spending's filter), no match only when nothing of his matches, the notes row on All, the placeholder, screenshots at 375 px light and dark |
| `test_compare.py` | Q12: the calendar's three tints (thirds, under three days, equal days), the key and footnote, the picked day in solid ink, today's outline; the price range strip's bands, dots, rings, stacking, axis and key, the dot–row link both ways (and back from a purchase), clearing, the label inside at both ends at 375 px, nothing animating, no strip with nothing to compare; screenshots at 375 and 402 px, light and dark |
| `test_location.py` | Q16, with a stand-in for the phone's position: nothing asked at launch; today's town on Home (beside More details, kept in a reloaded draft, the newest wins) and Spending's +; that day's town from a calendar day, and none; the arrow (allowed, nothing within 40 km, denied, no answer, typing or closing while it looks); 11 real places in the right town; typing and clearing stop the filling; editing never changes a place; the About credit; screenshots at 375 px, light and dark |
| `test_ratecard.py` | Q17: the card above the summary card, its ages (just now, minutes, hours, yesterday, days, the date) and in-place tick, two decimals, the VoiceOver label, the door to Convert with no refresh, a refresh showing on it, no rate yet and a fresh install, white staying white, the tokens, contrast and the card only using them, the same look in dark mode, the left column on its side and iPad; screenshots at 375 and 402 px, light and dark |
| `test_rates.py` | Q22: totals adding each purchase at its own rate (Home, Spending, a category), "1 at today's rate" and no note when every purchase has its own, no pounds guessed with no rate at all; a Sunday purchase getting Friday's rate, yesterday's, today's and a future date keeping today's with no lookup, the details line, changing a date; a Monday in Manila getting Friday's; Smart add's "yesterday"; a bad Frankfurter reply ignored for Currency API's, all bad leaving it estimated; offline saving as estimated (Home's note, the details) and corrected when back online with nothing else changed; Save not waiting for a held reply; cleaning, a backup and a restore keeping the new fields, junk dropped; an edit keeping the date keeping the rate; screenshots at 375 and 402 px, light and dark |
| `test_history.py` | Q23: the door (and Home's card still opening Convert), the page and pill, asking only for missing days and saving them, a reload asking for one day, bad saved history thrown away, v2 down (v1), both down (the snapshot, and Settings saying why), no snapshot (a year first), every layer down ("Connect once…"), bad replies refused whole (a bad rate, dates out of order, a 20% jump, the wrong shape), the why card hiding without a dollar rate, a Currency API rate as its own dot, the own record, the trip line, weekends, Monday morning in Manila, offline and no signal yet, older years only for All, the news file's rules and its age, scrubbing, snapping and opening, the redraw waiting, the sheets, swipe back (and not from the chart), the push with motion on and Reduce Motion, and screenshots at 375 and 402 px light and dark, on its side, iPad and Mac. `series_route` in `harness.py` answers the series requests, carrying on from the snapshot's last day (`SNAP_END`) |
| `test_smart.py` | Q14: the reader on the 123 made-up phrases, a long line and 300 lines; the two sides and the remembered side; typing in place; each ask, the either/or and learning; the typical note; saving one (Saved, Undo, his words, You typed, editing keeps them); Your usual and suggestions; the day's town; a list of five, checking one in the Log sheet, saving and Undo; Edit in the form; the form's amount box; Words Suki has learned (Settings, forgetting, Erase, a backup round trip, an older backup); "You paid" by whole words; with motion on, the fade mid-way at 4×, rapid switching and a redraw leaving no copy, Reduce Motion's crossfade, rows settling; screenshots at 375 and 402 px, light and dark |
| `test_inbox.py` | Q15: the reader keeping the stamp as `saidAt` (and not an impossible one); a stamped inbox saving once; pasting it again marking every line Already saved, greyed, with no Save and Clear the box; a mix saving only the new lines, with its header, the check sheet and Undo for just those; the same words at another time and lines with no stamp saving again; the stamp kept through Edit in the form, the draft and editing; a backup round trip, a junk stamp dropped; Help's six steps, how to run it, the note being optional and the door to Smart add; screenshots at 375 px, light and dark |
| `test_notepress.py` | Q18, with motion on: the tilt towards the finger (and Exact's), held and sprung back; Fly's arc and the ₱20's spin, the amount changing only on landing, ten fast taps adding once each, a redraw and a tab switch landing notes at once with none left behind, ✕, typing and Exact dropping them, Enter on a button; Slot's line hidden at rest, showing for the slot and fading after, the note ending on it; the setting (Fly first, Slot kept through a reload, not in backups, back to Fly removing the key); Reduce Motion (iPhone and Suki's) and motion off with no tilt or flight; the materials, the same in dark mode; screenshots at 375 and 402 px, light and dark, and mid-flight |
| `test_till.py` | Q13: the six 44 pt buttons on one row at 375 and 402 px with their VoiceOver labels, the ✕ in the cash box, 20,000 random amounts breaking down exactly, fans, bundles (₱34,750 and ₱999,999 inside the card), the ₱20 and ₱5 coins, colours the same in dark mode, Log this bill staying put; with motion on, settle, shrink and glide, the figure and a bundle's count still, rapid taps leaving no strays, Reduce Motion fading only; screenshots at 375 and 402 px, light and dark |
| `test_motion.py` | Q11, with motion on: a closing sheet is still on screen mid-way and gone after, by ✕, Escape, the dim, Cancel and dragging down; back to the sheet underneath with no second rise; two quick closes; taps go through a leaving sheet; new rows settle in and the rows below move; a deleted row shrinks away and Undo settles it back; Home's Saved and Undo; iPad's shrink and Reduce Motion's fades; tabs, Settings and Convert stay still; frames at 4× slow motion, light and dark |
| `test_timedoors.py` | Q10: the period label opening the calendar for each range (and a picked day or week), the picked bar narrowing the list with its line and way back, the pick kept when opening a purchase (✕, tapping outside, and the iPad pane), the filter's ✕ and Export as CSV working first time with a day picked, the Help row, screenshots at 375 px light and dark |
| `test_data.py` | Older and damaged data, the backup reminder, export, erase, restore (good, damaged, other and 2.0 files), the rate failing, and updating from the real Suki 2.0 |
| `test_offline.py` | Opening and working offline, and pull to refresh finding an update that then works offline too |
| `test_layout.py` | Every screen and sheet on iPhone (three sizes and on its side), iPad both ways and Mac, light and dark; the details pane, the sidebar, shortcuts, the tab bar clearing the end of every page, pull to refresh, and motion on and Reduce Motion |
| `test_onboard.py` | The Home Screen steps in Safari, the welcome card on a fresh install (and never on an existing one), each tip, Settings › Help, and backups leaving onboarding alone |
| `test_fuzz.py` | Hundreds of random taps, typing, resizing and reloads, checking nothing breaks after each one |

---

## Spending over time (Q03)

`period()` gives the range switch's period (`U.range`, `U.roff`), `buckets()` its bars and `spendBreakdown()` the categories. The list, total, chart and breakdown all follow the period; typing in the filter updates them in place (`updateSpending`). The range knob slides in place (never redraw it mid-slide). Chart scrubbing is pointer events on `#chart` (`touch-action: pan-y`), updating only `#spendSum`.

- The list draws `SHOW_STEP` (60) purchases, then a "Show more" row (`U.shown`); day totals and everything above the list still count every purchase. With 3,000 purchases and the processor slowed 4×, Spending opens in about 0.2 s.
- `dayCheck()` redraws when the date moves on (every minute and on coming back to the app), but not while a sheet is open or a box has the cursor.
- Category colours are `--cat-*`, checked with the dataviz palette validator in light and dark. Shopping is purple so it never sits next to green.
- Deleting shows a toast with Undo (`toast(text, undo)`).

### Known test issues

- On a small machine (two processors), running the whole suite side by side can occasionally make one file time out waiting for the page; it passes when run again or with `--one-at-a-time`. GitHub's runner hasn't shown this. On 1 Nov 2026 (Q13) it showed as three Q11 checks in `test_motion.py` (saving from the Log sheet) finding no animation; the file passed 63 of 63 on its own.
- On 1 Nov 2026 (Q16) the whole suite side by side failed one check in `test_data.py` ("Export shows Preparing first"); the file passed 67 of 67 on its own, with and without the change. Same small-machine timing.
- On 4 Nov 2026 (Q18) the whole suite side by side failed two fold checks in `test_smart.py` (the side showing fully there, and Reduce Motion's crossfade); the file passed 100 of 100 on its own. Same small-machine timing; Q18 doesn't touch Home's Log card.
- Checks on animations read the computed `animation-name`, not running animations: a short fade can finish before a busy machine looks.
- On 31 Oct and 1 Nov 2026 the suite was run locally against a newer Chromium (the pinned Playwright 1.56.0 pointed at it), because 1.56's own browser couldn't be downloaded there. GitHub's run uses the pinned one.
- Rows and headers only move when they're on screen, so a motion test must scroll the list into view first (Spending's list starts below the chart at 844 px tall), and keep clear of the tab bar.
- Don't name a class `gap`: it's the 16px spacer in the restore sheet, so `.grp.gap` collapses to 16px. Use `.grp.spaced` for a group with space above it.
- A service worker serves versioned files from its own copy, so `ctx.route` can't swap one (like `js/ratesnap.js`) after the first load. To test without the snapshot, `test_history.py` makes `window.sukiRateSnap` read-only `null` before the page loads.
- Don't name a class `note` or reuse it on a new element: `.note` is a paragraph style with a bottom margin (it shifted the strip's rings up 16 px until they became `.s-note`).

## Style

Native iOS look (Liquid Glass imitated in CSS), no in-app branding, British English in plain, friendly words. Everything must work on iPhone, iPhone on its side, iPad and Mac, in light and dark.

- **Colours** are tokens: Apple's system colours are `--sys-*` (light and dark); category chart colours are `--cat-*`. No hex in rules; `test_release.py` checks.
- **Type** uses Apple's text styles only: 34, 28, 22, 20, 17, 16, 15, 13, 12, 11 (and 44, 56, 68 for big numerals). `test_release.py` checks.
- **Top bar** has no card; once you scroll, `.edge` (a soft blur from the top of the screen) and the compact title appear.
- **Tab bar** stays full size (Ivan, 31 Oct 2026). On iPhone upright it sits 21pt from the bottom with 21pt sides; `--dockb` is its bottom offset everywhere. Safe areas are `--sat/--sab/--sal/--sar`.
- **Reduce Motion** is `html.motion-reduced`, set from the iPhone or Settings › Accessibility (`suki:reduceMotion`, device-only, never in backups). Write new CSS against the class, not the media query.
- **Item glyphs**: `GLYPH` and `ITEM_GLYPH` in `helpers.js`. A new catalogue item needs a glyph (or it falls back to its kind's picture).
- **Shortcuts** use Cmd on Apple devices (`APPLE`) and Ctrl elsewhere, so Ctrl stays free for text editing on a Mac.
