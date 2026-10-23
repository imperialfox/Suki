# Suki

![Version 2.3](https://img.shields.io/badge/version-2.3-blue)

**Current version: 2.3 · 23 Oct 2026.** See the [changelog](CHANGELOG.md) for what's new.

Suki is a personal travel companion for the Philippines. It checks your change, converts pounds and pesos, looks up prices and keeps track of what you spend. It's a Home Screen web app for iPhone, iPad and Mac, and works offline.

## What it does

- **Log what you spend** in a few taps, with categories, places and notes, and see it by day and by category.
- **Check your change** before you walk away from the till.
- **Convert pounds and pesos** with a reference rate, even offline.
- **Look up prices**: official weekly averages from the Department of Agriculture (DA-AMAS) for selected groceries in Metro Manila (NCR) markets, plus your own price notes. Search understands Tagalog, English, misspellings and phrases like "1 kilo bigas".

The official prices are a snapshot for 5–11 October 2026, bundled with the app so they work offline. They cover NCR markets only and aren't a live feed. Your own price notes are kept separate and are never treated as market averages.

## Tabs

- **Home**: your total and today's spending, a quick form to log a purchase, and your recent purchases. The gear opens Settings.
- **Till** (Quick Till): enter the bill and the cash you hand over to see the change due, or what's still to pay. "Log this bill" saves it as a purchase.
- **Search**: the official prices and the catalogue. Open an item for its official price, a link to the DA report and your price notes.
- **Spending**: every purchase grouped by day, with category chips, a filter, details, editing, deleting (swipe left or from the details) and CSV export.
- **Convert**: linked pound and peso boxes, handy amounts, and Refresh for the latest reference rate.
- **Settings**: backup and restore, price notes, storage, Erase all data, and information about the app.

## Layouts

- **iPhone upright**: a floating tab bar at the bottom that shrinks to the current tab while you scroll.
- **iPhone on its side**: a compact tab bar with icons beside their labels, and two columns on Home.
- **iPad, or a Mac window**: tabs at the top, Home in two columns, and Search and Spending show details beside the list. Sheets open in the middle of the screen.
- **Mac, or iPad on its side**: a sidebar with every section and Settings.
- On a keyboard, Cmd (or Ctrl) + 1–5 switches sections and Esc closes a sheet.
- Light and dark appearance follow your device. Reduce Motion is respected: things fade instead of moving.

## Offline

Open Suki once while online. After that it opens with no signal, and everything works except refreshing the exchange rate (the last saved rate is used). When you're online, pull down on Home or Spending to check for an update.

## Add it to your Home Screen

**iPhone or iPad**
1. Open the Suki website in Safari.
2. Tap the Share button (the square with an arrow).
3. Tap **Add to Home Screen**, then **Add**.

**Mac**
1. Open the Suki website in Safari.
2. Choose **File › Add to Dock**.

## Changing the icon safely

iOS only reads the icon and launch screen when the app is added to the Home Screen. To pick up a new icon without losing anything:
1. In Suki, go to **Settings › Export a backup** and save it to Files.
2. Remove Suki from your Home Screen.
3. Add it again from Safari (steps above).
4. Go to **Settings › Restore a backup** and choose the file.

The launch images in `splash/` are made from `icon-512.png` by `python tools/splash.py`.

## Your data and privacy

- Everything you enter stays on your device, in the browser's storage. There's no account, server or cloud sync.
- iOS can clear a website's storage if it isn't opened for a few weeks, so export a backup now and then. Suki reminds you after two weeks.
- Backups are JSON files named by month and device (for example "Suki backup · 2026-10 · iPhone.json"), so backing up again in the same month replaces that month's file in Files.
- Refreshing the exchange rate contacts Frankfurter for the European Central Bank's rate (`api.frankfurter.dev`, then `api.frankfurter.app`). If neither answers, it falls back to the Currency API (`cdn.jsdelivr.net`, then `currency-api.pages.dev`). Only the currencies are sent, never your records.
- This repository and its website are public. Don't add private or licensed content.

## Adapting it

- The catalogue (names, English names, other spellings) is in `js/catalog.js`.
- The official price snapshot is in `js/prices.js`. Item ids must match the catalogue.
- Categories, places and payment methods are at the top of `js/storage.js`.
- See [MAINTAINING.md](MAINTAINING.md) for how the code fits together, the tests and releasing.

## Stack and licence

Vanilla HTML, CSS and JavaScript with no frameworks or build step, a web app manifest and a service worker, hosted on GitHub Pages. It shares its foundations (motion, offline support, layouts and tests) with Vocal Sessions. Licensed under MIT; see [LICENSE.txt](LICENSE.txt).
