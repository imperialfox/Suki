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
| `js/storage.js` | Categories, places and payment methods; checking (`cleanData`) and loading/saving data; the draft and last-backup date |
| `js/helpers.js` | Money and dates, icons, category tiles, layout (`MQ`, `layout()`), tabs and the on-screen state `U` |
| `js/screens.js` | Home, Till, Search, Spending, Convert and Settings, plus the shared purchase form, purchase details and item details |
| `js/ui.js` | Form state `F`, the top bar, tab bar, top tabs and sidebar, `render()` and `go()`, sheets and toasts |
| `js/rate.js` | The exchange rate (`refreshRate`, `autoRate`) and the linked converter boxes |
| `js/backup.js` | Saving files (share sheet or download), backups, restoring, erasing and the CSV export |
| `js/events.js` | Every button action (`ACT`), the forms, typing, swipe to delete, blocking zoom and keyboard shortcuts |
| `js/gestures.js` | Pull to refresh and the update check, scrolling (top bar and shrinking tab bar), rotating, online/offline, sheet scrolling and dragging sheets down |
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
| localStorage | `suki:lastBackup` | When a backup was last saved (not backed up) |
| localStorage | `suki:draft` | A half-typed purchase on Home (not backed up) |
| localStorage | `suki:motion` | Motion speed on this device (not backed up) |

**These names have been the same since Suki 2.0. Never change them**; the tests load data saved by the real 2.0 app (`tests/fixtures/app-2.0.0`) to prove updating keeps everything.

`cleanData()` checks anything loaded or restored: records without a name or an amount are dropped, ids are made unique, bad dates become today, unknown categories become Other, and fields it doesn't know are kept. Data changes should be additive: add fields with a default; don't rename or repurpose existing ones.

A purchase: `{id, item, price, date (YYYY-MM-DD), category, location, venue, payment, notes, gbpAtPurchase, rateAtPurchase, edited?}`.
A price note: `{id, itemId, itemName, price, date, location, venue, note}`. `itemId` points at a catalogue id, so **never rename a catalogue id**.

## Backups

A backup is a JSON file: a plain-English `README`, `app: 'Suki'`, `schemaVersion: 1`, `appVersion`, `exportedAt`, `device`, `purchases`, `observations` and `rate`. Backups from 2.0 (without `README`, `appVersion` or `device`) still restore. Files are named `Suki backup · YYYY-MM · Device.json`.

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

The tests drive the real app in Chromium, served from `localhost` as GitHub Pages would serve it, with motion off so nothing waits on a spring. The exchange rate is answered by the tests themselves, so they never need the internet. Screenshots of every screen go to `tests/output/`.

| File | Covers |
|---|---|
| `test_release.py` | The version agrees in the app, README and CHANGELOG, and every file `index.html` loads exists |
| `test_flows.py` | Logging (with errors and the draft), Spending (chips, filter, days, details, edit, delete, swipe, CSV), Quick Till, Convert, Search and price notes, Settings, empty states |
| `test_data.py` | Older and damaged data, the backup reminder, export, erase, restore (good, damaged, other and 2.0 files), the rate failing, and updating from the real Suki 2.0 |
| `test_offline.py` | Opening and working offline, and pull to refresh finding an update that then works offline too |
| `test_layout.py` | Every screen and sheet on iPhone (three sizes and on its side), iPad both ways and Mac, light and dark; the details pane, the sidebar, shortcuts, the shrinking tab bar, pull to refresh, and motion on and Reduce Motion |
| `test_fuzz.py` | Hundreds of random taps, typing, resizing and reloads, checking nothing breaks after each one |

---

## Style

Native iOS look (Liquid Glass imitated in CSS), no in-app branding, British English in plain, friendly words. Everything must work on iPhone, iPhone on its side, iPad and Mac, in light and dark.
