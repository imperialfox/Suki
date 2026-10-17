# Suki

**Current version: 2.0.0 · 17 Oct 2026** · [Changelog](CHANGELOG.md)

Suki is a personal Philippines travel companion designed for iPhone, iPad and desktop browsers.

## What it does

- Search a Tagalog-first starter catalogue with English aliases, fuzzy spelling and partial phrase matching.
- Calculate change, exact payment or the amount still owed with Quick Till.
- Convert GBP and PHP using a reference exchange rate, including the last saved rate while offline.
- Keep personal purchase and price-observation records on this device.
- Export purchases as CSV and export or restore a JSON backup.
- Work offline after the app has loaded once online.

Search includes a bundled official weekly price snapshot for selected grocery items from the Philippine Department of Agriculture (DA-AMAS). The checked snapshot is for NCR markets for 5–11 October 2026; it is not nationwide and is not a live feed. Prices are shown with their reported commodity specifications. Items without a matching official reference continue to show personal observations only. Personal observations remain separate from market-wide price information.

## Tabs and tools

- **Home:** quick actions, spending summary and recent purchases.
- **Search:** find catalogue items and save your own price observations.
- **Quick Till:** calculate change and carry a bill into the purchase form.
- **Convert:** calculate a GBP or PHP reference value, refresh the rate, or copy a conversion.
- **Spending:** add, filter, remove and export purchase records.
- **Settings:** backup and restore, offline status, saved rate, installation help and repository information.

## Layout

The interface adapts to phone, landscape, tablet and desktop widths. It uses system type, automatic light and dark appearances, safe-area spacing, large touch targets, a floating glass-style navigation bar and native-style confirmation sheets.

## Offline and storage

Suki uses vanilla HTML, CSS and JavaScript with no framework or build step. Purchase records, personal observations and the saved exchange rate stay in browser storage on the device. There is no account, backend or cloud sync. The service worker caches the app shell and tries the network first for page loads.

Clearing browser data can erase records, so export a backup regularly. Backups contain purchases, observations and the cached exchange rate. Official price references are bundled with the app for offline use. The exchange-rate refresh contacts `api.frankfurter.app`; purchase records are not sent to that service.

## Add to the Home Screen

On iPhone or iPad, open the GitHub Pages site in Safari, tap **Share**, then **Add to Home Screen**. Open Suki once while online before relying on offline use.

## Privacy

This is a public repository and site. Do not add private or licensed content. Personal app records are stored locally in your browser and are not published to GitHub.

## Stack and licence

Vanilla HTML, CSS and JavaScript, a web app manifest, and a service worker. Licensed under MIT; see [LICENSE.txt](LICENSE.txt).
