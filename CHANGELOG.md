# Changelog

## 2.2 · 22 Oct 2026
*Prices in pounds on Search, and snappier navigation*

**Search**
- Every price now shows roughly what it is in pounds (for example ≈ £2.40) under the peso amount, so you can gauge the cost without working it out. This covers the results list, the official price in an item's details and your own price notes.
- The pound value appears once an exchange rate has loaded, and uses the same saved rate as Convert.

**Navigation**
- Switching between Home, Till, Search, Spending and Convert is now instant, with no fade. The launch animation into Home is unchanged, and Settings still fades in.

## 2.1.0 · 20 Oct 2026
*Polished, faster to use and at home on every screen*

**Spending**
- Tap any purchase to see all its details, then tap the pencil to edit it. Changes keep the pound value worked out from the rate on the day.
- Category chips at the top filter the list and the total. Only categories you've used appear, each with a count.
- Purchases are grouped by day (Today, Yesterday, then the date), each with its own total.
- Swipe a purchase left to delete it, or use Delete in its details. Both ask first.
- Export as CSV now saves what's shown, so you can export one category on its own.

**Home**
- A summary card with your total (and roughly what it is in pounds) and what you've spent today. Tap it to open Spending.
- A half-typed purchase is kept if you close the app, and the form remembers your last category and payment.
- Clear messages if a purchase is missing its name or amount.
- The backup reminder appears when you haven't backed up for two weeks.

**Quick Till**
- Amount buttons now add up (₱500 + ₱100 + ₱100), with Exact and Clear.
- "Log this bill" opens the purchase form with the amount filled in, so you can name and categorise it.

**Search**
- Opens on the official DA prices, with the price beside each item, then popular dishes.
- Items open as a sheet (or beside the list on iPad and Mac) with the official price, the DA report link and your price notes.
- Price notes can now be deleted, and Settings lists them all.

**Convert**
- The pounds and pesos boxes are linked: type in either and the other fills in.
- Handy amounts (£1 to £100) at a glance, and Copy works in both directions.
- The rate refreshes quietly when it's more than 12 hours old, rather than only when there's none.

**Settings**
- Coloured icons, the last backup shown in red after two weeks, and Erase all data (with Export first).
- Backups are named by month and device, open in the share sheet on iPhone, and show what's inside before replacing anything.

**Every screen**
- iPhone on its side: a compact tab bar and two columns, instead of a large panel over the page.
- iPad: tabs move to the top bar without overlapping anything; lists show details beside them; sheets open in the middle.
- Mac and iPad on its side: a sidebar with Settings.
- The tab bar shrinks to the current tab while you scroll down. Pull down on Home or Spending to refresh and check for updates.
- An Offline label appears only when you're offline. No more "Could not load a rate" message when the app opens.
- Dates read the British way (Today, Yesterday, 3 days ago, Monday 12 October).

**Fixes**
- Item details no longer open cut off.
- The Spending filter box is visible in light mode.
- Groceries purchases show the groceries icon.
- A damaged backup or damaged saved data can no longer stop the app opening; bad records are left out and everything else is kept.

**Behind the scenes**
- Rebuilt on the same foundations as Vocal Sessions: shared motion, offline support, layouts and a full test suite.
- Your saved purchases, price notes and rate stay exactly where they were, so nothing is lost on updating.

## 2.0.0 · 17 Oct 2026
*A native iOS look*

- Updated Suki with a native iOS-inspired layout, system colours and automatic dark appearance.
- Restyled navigation, quick actions, forms, lists and price details while retaining the existing travel tools and local data format.
- Added review and confirmation sheets for backup restore and purchase deletion.
- Added a backup date reminder and updated offline page loading.
- Expanded the README with installation, privacy and feature information.
