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
| `tests/` | The test suite (see below) |
| `.github/workflows/tests.yml` | Runs the tests on GitHub after every push |

### The code, in load order

| File | Holds |
|---|---|
| `js/motion.js` | **The shared springs** (`MOTION`), copied from Vocal Sessions: gentle, nav and ripple springs as CSS `linear()` easings and `--ease-*`/`--dur-*` variables, Reduce Motion, and the speed setting (`suki:motion`; 0 = off, used by the tests) |
| `js/catalog.js` | The catalogue (`CATALOG`), official price lookups (`refsFor`, `refFrom`) and the fuzzy search (`searchItems`) |
| `js/prices.js` | The official DA-AMAS price snapshot (`window.sukiPriceReferences`) |
| `js/typical.js` | Typical prices with their sources (`window.sukiTypical`, Q02): fares, DTI suggested retail prices, shop and menu prices, rough guides |
| `js/storage.js` | Categories, places and payment methods; checking (`cleanData`) and loading/saving data; the draft and last-backup date |
| `js/helpers.js` | Money and dates, icons, category tiles, layout (`MQ`, `layout()`), tabs and the on-screen state `U` |
| `js/screens.js` | Home, Till, Search, Spending, Convert and Settings, plus the shared purchase form, purchase details and item details |
| `js/ui.js` | Form state `F`, the top bar, tab bar, top tabs and sidebar, `render()` and `go()`, sheets and toasts |
| `js/rate.js` | The exchange rate (`refreshRate`, `autoRate`) and the linked converter boxes. The rate comes from the first source in `RATE_SOURCES` that answers with a rate inside `RATE_RANGE`; `RATE_CHECK` keeps why the last check failed, for Settings |
| `js/backup.js` | Saving files (share sheet or download), backups, restoring, erasing and the CSV export |
| `js/events.js` | Every button action (`ACT`), the forms, typing, swipe to delete, blocking zoom and keyboard shortcuts |
| `js/gestures.js` | Pull to refresh and the update check, scrolling (the top bar turning to glass), rotating, online/offline, sheet scrolling and dragging sheets down |
| `js/onboard.js` | Onboarding (Q07): the Home Screen steps in Safari, the welcome card, tips and the Help screen |
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
| IndexedDB `suki-db` (version 1), store `kv` | `purchases`, `observations`, `rate` | All saved data (`D`) |
| localStorage | `suki:purchases`, `suki:observations`, `suki:rate` | The same, only when IndexedDB isn't available |
| IndexedDB `kv` (or localStorage `suki:`) | `rescue` | Records Suki couldn't read, kept before anything saves over them (Q05). Not backed up; Settings › Recovered data saves them as a file |
| IndexedDB `kv` (or localStorage `suki:`) | `safety` | What was on the phone before the last restore or Erase, so it can be put back (Q05). Not backed up |
| localStorage | `suki:lastBackup` | When a backup was last saved (not backed up) |
| localStorage | `suki:draft` | A half-typed purchase on Home (not backed up) |
| localStorage | `suki:motion` | Motion speed on this device (not backed up) |
| localStorage | `suki:onboard` | Onboarding on this device: welcome seen, tips on, which tips are done (Q07). Not backed up |
| localStorage | `suki:reduceMotion` | Reduce Motion: `on`, `off`, or missing to match the iPhone (not backed up) |

**These names have been the same since Suki 2.0. Never change them**; the tests load data saved by the real 2.0 app (`tests/fixtures/app-2.0.0`) to prove updating keeps everything.

`cleanData()` checks anything loaded or restored: records without a name or an amount are dropped, ids are made unique, bad dates become today, unknown categories become Other, and fields it doesn't know are kept. Data changes should be additive: add fields with a default; don't rename or repurpose existing ones.

A purchase: `{id, item, price, date (YYYY-MM-DD), category, location, venue, payment, notes, gbpAtPurchase, rateAtPurchase, edited?}`.
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

## Backups

A backup is a JSON file: a plain-English `README`, `app: 'Suki'`, `schemaVersion: 1`, `appVersion`, `exportedAt`, `device`, `purchases`, `observations` and `rate`. Backups from 2.0 (without `README`, `appVersion` or `device`) still restore. Files are named `Suki backup · YYYY-MM · Device.json`.

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

- On a small machine (two processors), running the whole suite side by side can occasionally make one file time out waiting for the page; it passes when run again or with `--one-at-a-time`. GitHub's runner hasn't shown this.
- Checks on animations read the computed `animation-name`, not running animations: a short fade can finish before a busy machine looks.
- On 31 Oct 2026 the suite was run locally against a newer Chromium (the pinned Playwright 1.56.0 pointed at it), because 1.56's own browser couldn't be downloaded there. GitHub's run uses the pinned one.

## Style

Native iOS look (Liquid Glass imitated in CSS), no in-app branding, British English in plain, friendly words. Everything must work on iPhone, iPhone on its side, iPad and Mac, in light and dark.

- **Colours** are tokens: Apple's system colours are `--sys-*` (light and dark); category chart colours are `--cat-*`. No hex in rules; `test_release.py` checks.
- **Type** uses Apple's text styles only: 34, 28, 22, 20, 17, 16, 15, 13, 12, 11 (and 44, 56, 68 for big numerals). `test_release.py` checks.
- **Top bar** has no card; once you scroll, `.edge` (a soft blur from the top of the screen) and the compact title appear.
- **Tab bar** stays full size (Ivan, 31 Oct 2026). On iPhone upright it sits 21pt from the bottom with 21pt sides; `--dockb` is its bottom offset everywhere. Safe areas are `--sat/--sab/--sal/--sar`.
- **Reduce Motion** is `html.motion-reduced`, set from the iPhone or Settings › Accessibility (`suki:reduceMotion`, device-only, never in backups). Write new CSS against the class, not the media query.
- **Item glyphs**: `GLYPH` and `ITEM_GLYPH` in `helpers.js`. A new catalogue item needs a glyph (or it falls back to its kind's picture).
- **Shortcuts** use Cmd on Apple devices (`APPLE`) and Ctrl elsewhere, so Ctrl stays free for text editing on a Mac.
