# Suki

![Version 2.21](https://img.shields.io/badge/version-2.21-blue)

**Current version: 2.21 · 2 Nov 2026.** See the [changelog](CHANGELOG.md) for what's new.

Suki is a personal travel companion for the Philippines. It checks your change, converts pounds and pesos, looks up prices and keeps track of what you spend. It's a Home Screen web app for iPhone, iPad and Mac, and works offline.

## What it does

- **Log what you spend** in a few taps, or in one line with Smart add ("jeep to cubao 14"), with categories, places and notes, and see it by day and by category. The place starts as the town you were in earlier that day, and an arrow fills the town you're in, worked out on your phone.
- **Check your change** before you walk away from the till.
- **Convert pounds and pesos** with a reference rate, even offline.
- **Look up prices**: official weekly averages from the Department of Agriculture (DA-AMAS) for selected groceries in Metro Manila (NCR) markets, plus your own price notes. Search understands Tagalog, English, misspellings and phrases like "1 kilo bigas".

The official prices are a snapshot for 5–11 October 2026, bundled with the app so they work offline. They cover NCR markets only and aren't a live feed. Your own price notes are kept separate and are never treated as market averages.

## Tabs

- **Home**: today's exchange rate (tap it to open Convert), your total and today's spending (tap either to open it in Spending), a card to log a purchase (the form, or Smart add: type, say or paste a purchase in one line and check what Suki understood before saving; a note from the Siri Shortcut in Settings › Help can be pasted again and again, since lines already saved are skipped), and your recent purchases. The gear opens Settings.
- **Till** (Quick Till): enter the bill, then type or tap the notes and ₱20 coins you hand over, to see the change due (shown as the notes and coins to expect) or what's still to pay. "Log this bill" saves it as a purchase.
- **Search**: the official prices and the catalogue, plus your own purchases and price notes. Open an item for its official price, a link to the DA report and your price notes. Where there's a typical price, a strip under it shows it as a band, with a dot for each time you paid and a ring for each price note. All starts with a door to every price note.
- **Spending**: every purchase grouped by day, with category chips, a filter, details, editing, deleting (swipe left or from the details) and CSV export. The + logs a purchase. A purchase that names a catalogue item links to that item's prices. The period's name opens the calendar, where days are tinted in three steps by how much you spent, and tapping a bar shows just that day.
- **Convert**: linked pound and peso boxes, handy amounts, and Refresh for the latest reference rate.
- **Settings**: backup and restore, price notes, the words Smart add has learned, storage, Erase all data, and information about the app.

## Layouts

- **iPhone upright**: a floating tab bar at the bottom that stays full size, with the end of every page clear of it.
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
- Smart add reads what you type on your phone, with word rules. Nothing you type is sent anywhere, and no AI is involved.
- Location's arrow reads your position once, when you tap it (iPhone asks first). It's matched against the town outlines kept inside the app, so it works offline and is never sent anywhere. Suki doesn't track you in the background, and never asks when it opens.
- Refreshing the exchange rate contacts Frankfurter for the European Central Bank's rate (`api.frankfurter.dev`, then `api.frankfurter.app`). If neither answers, it falls back to the Currency API (`cdn.jsdelivr.net`, then `currency-api.pages.dev`). Only the currencies are sent, never your records.
- This repository and its website are public. Don't add private or licensed content.

## Adapting it

- The catalogue (names, English names, other spellings) is in `js/catalog.js`.
- The official price snapshot is in `js/prices.js`. Item ids must match the catalogue.
- The town outlines for Location are in `js/towns.js`, made by `tools/towns.py` (see MAINTAINING.md).
- Categories, places and payment methods are at the top of `js/storage.js`.
- See [MAINTAINING.md](MAINTAINING.md) for how the code fits together, the tests and releasing.

## Stack and licence

Vanilla HTML, CSS and JavaScript with no frameworks or build step, a web app manifest and a service worker, hosted on GitHub Pages. It shares its foundations (motion, offline support, layouts and tests) with Vocal Sessions. Licensed under MIT; see [LICENSE.txt](LICENSE.txt).
