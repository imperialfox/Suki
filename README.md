# Suki

My little filipino travel companion

A mobile-first installable web app, built with vanilla HTML/CSS/JS for personal use.

## Features
- Tagalog-first starter catalogue with English aliases, fuzzy spelling and partial search.
- Quick Till: change, exact payment and short-cash calculations.
- GBP↔PHP converter using a reference-rate API and cached last successful rate.
- Personal purchase log with date, category, location, venue, payment method and notes.
- Personal price observations kept separate from market-wide price intelligence.
- CSV purchase export, JSON backup/restore, IndexedDB with localStorage fallback.
- PWA manifest and service worker for app-shell offline support.

## Price-data limitation
This build intentionally has **no verified nationwide or destination price ranges**. Catalogue entries help identify products but do not assert current prices. The app does not label items cheap/typical/expensive without a reliable comparison dataset. Personal observations are not treated as representative market data.

## Publish with GitHub Pages
1. In this repository, open **Settings → Pages**.
2. Choose deployment from the `main` branch and `/ (root)`, then save.
3. Wait for GitHub Pages to publish the HTTPS URL.
4. Open that URL in Safari on iPhone → Share → Add to Home Screen.
5. Open the app once online before relying on offline use.

## Test checklist
- Search `sinigan baboy`, `1 kilo bigas`, `tubig bote`, `kwek kwek`, `baboy adobo`.
- Quick Till: ₱789 bill + ₱1,000 cash should show ₱211 change.
- Test short payment and exact payment.
- Refresh the reference exchange rate online; check date and saved rate.
- Save/filter/delete/export purchases; download and restore JSON backup.
- Add a personal price observation and confirm it is not called a market average.
- After first online load, test airplane mode and local records.
- Verify on actual iPhone Safari. iOS installation/storage/offline behaviour has not been independently verified here.

## Privacy and technical notes
No account, backend, or cloud sync. Records stay in browser storage on the device. Clearing Safari website data can erase them, so back up regularly. Rate refresh requests `api.frankfurter.app`; purchase records are not sent to that service. `index.html` contains the UI and app logic; `sw.js` and `manifest.json` are separate because installable PWAs require them.
