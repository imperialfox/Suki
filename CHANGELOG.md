# Changelog

## 2.19 · 1 Nov 2026
*Today's exchange rate at the top of Home (Q17)*

**The rate card**
- Home now opens with the rate: "Exchange rate", then **£1 = ₱76.12** in large type, then how old it is ("Updated 2h ago", "Updated yesterday", "Updated 3 days ago", then the date). Anyone glancing at Home sees it first.
- The age moves on by itself while Home is open.
- An old rate keeps its white text. It's never shown in red.
- With no rate saved yet, the card reads "Exchange rate · Get today's rate on Convert".

**One door**
- The whole card opens Convert. Tapping it doesn't refresh the rate; Convert's own Refresh, and pulling down on Home, still do.

**Look**
- It uses Suki's own icon colours, as a one-off: the icon's navy with its soft blue glow and white text, the same in light and dark. No other screen uses them.
- On iPhone on its side, iPad and Mac it heads Home's left column, above the summary card.

## 2.18 · 1 Nov 2026
*Location fills itself in, privately and offline (Q16)*

**From earlier that day**
- A new purchase's Location starts as the place of your newest purchase that day that has one: today's on Home and Spending's +, that day's when you log on a calendar day. The label says "Location · from earlier today" or "· from that day".
- On Home, with More details closed, the place shows beside it ("More details · Quezon City"), so you can see where it'll be saved.
- Typing in Location, or clearing it, is yours: Suki stops filling it in for that purchase. The next purchase starts from the day's town again.
- Editing an old purchase never changes its place.

**The town you're in**
- An arrow inside Location fills the town you're in, labelled "· near you", and the box tints briefly.
- iPhone asks for permission the first time you tap the arrow, never when Suki opens. If it's off: "Location is off for Suki. Type the town, or allow it in Settings." Away from any town: "No town found near you. Type it in instead."
- The outlines of all 1,642 Philippine cities and municipalities are kept inside the app, so it works with no signal, and your position never leaves your phone. Settings › About credits them (NAMRIA and PSA, through OCHA, CC BY-IGO).

**Layout**
- Location now has the full width, with Where bought underneath.

## 2.17 · 1 Nov 2026
*Quick Till: bigger buttons, and your change shown as the notes and coins to expect (Q13)*

**Buttons**
- The amount buttons are now 44 pt tall and all on one row: Exact, 20, 50, 100, 500 and 1000. They're easier to hit with a cashier waiting.
- They're coloured like the notes, and labelled the way the notes are ("1000"). VoiceOver says "Add a ₱1,000 note".
- ₱20 is a coin now, so its button looks like one: grey with a bronze ring. ₱50 replaces ₱200, which the BSP stopped making in 2021.
- Clear is now a ✕ inside the cash box, as in Search. Tapping it keeps the keyboard where it was.

**Change as cash**
- Under the change figure, the notes and coins to expect: notes first, largest first, fanned with their number up the left edge, then coins in small piles. The ₱20 coin is two-tone and the ₱5 has nine sides.
- Five or more of one note become a bundle with the count on the front ("×34"), so big amounts never spill out of the card.
- The breakdown uses the notes and coins in use today: no ₱200 note, no ₱20 note, and no 50¢ coin, so 50¢ shows as two 25¢.
- Only what changes moves: new pieces settle in, ones that go shrink away, and the rest slide over. The figure never moves. With Reduce Motion, pieces only fade.
- Note and coin colours stay the same in dark mode, like cards in Wallet. They're plain colours and numbers, with no banknote artwork.

## 2.16 · 1 Nov 2026
*Calendar tints and the price range strip: a number next to something to compare it with (Q12)*

**Calendar**
- Days you spent on are now tinted in three steps, light to strong, by how much you spent compared with the rest of that month's spending days. A big day stands out at a glance. With fewer than three spending days in a month, they all get the middle step, and days with the same amount always share a step.
- A small "Less ● ● ● More" key sits under the days, and the note under the calendar says what the tints mean.
- A picked day is now solid black (white in dark mode), so it never looks like a big day. Today keeps its outline.
- VoiceOver still reads each day's amount. Tapping a day works as before.

**Prices**
- An item's typical-prices card now ends with a strip that puts what you paid next to what it usually costs. Each typical price is a band (two prices stay two bands), each time you paid is a dot and each price note is a ring. Dots at the same price stack upwards. The ends of the strip show a rounded low and high, and a key says which is which.
- Tap a dot to light its row in You paid or Your price notes, with a label like "₱17 · 3 days ago · Bulakan to Barrio". Tap a row and its dot lights up. A You paid row still opens the purchase, and its dot is lit when you come back. Tap anywhere else to clear it.
- There are no good or bad words or colours: where the dot sits says it all. Nothing on the strip or the tints moves.

## 2.15 · 1 Nov 2026
*Things arrive and leave: sheets slide away, purchases settle in (Q11)*

**Sheets**
- Closing a sheet now slides it down off the screen while the page behind grows back, as one movement, a little quicker than it rose. Before, it vanished in one frame. This works however it's closed: ✕, Cancel, tapping the dim, Escape, dragging it down (it carries on from where your finger let go), and after saving or deleting.
- Going back to a sheet underneath (closing Edit over a purchase, or saving a purchase logged from the calendar) finds that sheet simply there, scrolled where it was, while the top one slides off over it.
- On iPad and Mac a closing sheet shrinks a little and fades. With Reduce Motion it fades.
- A sheet on its way out never gets in the way: you can tap whatever is behind it straight away.

**Purchases**
- A saved purchase settles into its list with a small drop, wherever it lands (Home's Recent, Spending, a calendar day), and the rows below move down to make room.
- A deleted purchase shrinks away where it was and the rows below close the gap. Undo brings it back the same way a new one arrives.
- On Home, the Save button itself confirms: it shows "✓ Saved" for a moment, then goes back.
- "Purchase saved" now has **Undo**, which removes it again.

**Slow motion**
- Settings › Accessibility › Slow motion also slows the page shrinking behind a sheet.

Tabs still switch instantly, figures never animate, and Settings, Help and Convert stay still.

## 2.14 · 1 Nov 2026
*Spending: the date opens the calendar, and a picked bar narrows the list (Q10)*

**Spending**
- The period under the total ("This week", "October", "Since 23 Oct", "Today") is now blue, with a small calendar. Tap it to open the calendar on that month. On D, or with a day's bar picked, that day is already picked.
- Tapping a bar now narrows the list to that day (or week) too, so the total and the list always say the same thing. A line says "Showing Yesterday only", with a button back to the whole period ("Show this week", "Show all of November").
- Opening a purchase from that narrowed list keeps the day picked, so closing it brings you back to the same view. Tapping anywhere else goes back to the whole period, as before.
- With a day picked, the filter's ✕ and Export as CSV work first time: the list widens just after the tap, so nothing jumps away from under your finger.

**Help**
- Hidden gestures lists "Tap Home's title", which opens the calendar (Spending's date does too).

## 2.13 · 1 Nov 2026
*Search finds what you've logged, not only prices (Q09)*

**Search**
- Typing in Search now shows your own records under the prices: **In your purchases** (the newest three, then "Show all … in Spending") and **In your price notes**.
- A purchase is found when every word you type appears in its name, place, where bought, category, how you paid or its notes, in any order. So "cubao jeepney" finds a jeepney ride in Cubao.
- When only your own records match, there's no "No clear match". "Log … as a purchase" is still there.
- Search's All view starts with **Your price notes**, which opens every note. The row in Settings still works too.
- The search box reads "Prices, your purchases, your notes".

**Spending**
- The filter finds every word in any order too, so "Show all" from Search always opens the same purchases it counted. Typing one word works as before.

## 2.12 · 1 Nov 2026
*No dead ends: every place named is a door to it (Q08)*

**Home**
- The summary card is two doors: tap the total for all your spending, or Today for today's.
- With nothing logged, it says "Nothing spent yet" instead of two zeros.

**Logging from anywhere**
- Spending has a + in its top bar that opens the same Log sheet as Quick Till's "Log this bill".
- In the calendar, a day you've picked (today or earlier) has "Log a purchase on 28 Oct", with that date filled in. Saving takes you back to the calendar.
- Search with no match offers "Log … as a purchase", with the name filled in and the cursor in the amount.
- With nothing logged, Spending shows one card and a Log a purchase button, not an empty chart.

**From a purchase to its prices**
- A purchase that names a catalogue item, like "Jeepney to Cubao", shows "Jeepney prices · Usually ₱14–17 · first 4 km". It opens the item over the purchase.
- It only shows when the item's name appears as whole words, so a spaghetti purchase never offers massage prices.

**Words that are doors**
- "Refresh it on Convert" (under Search when the rate is old) opens Convert and refreshes.
- Price notes link to Search when they're empty, and in their footer.
- In Settings, Last backed up opens Export a backup, Saved exchange rate opens Convert, and Add to your Home Screen opens the steps.

## 2.11 · 1 Nov 2026
*Getting started, without a tour (Q07)*

**For someone new**
- Opened in Safari on an iPhone or iPad, Suki shows the three steps to add it to the Home Screen (with Open as Web App left on), so it works with no signal. It shows each time it's opened in Safari, never from the Home Screen.
- The first time it's opened from the Home Screen with nothing saved, one welcome card says what Suki does. Continue, and it doesn't come back.
- Tips, one at a time, next to the things you can't see: Quick Till's amount buttons, pulling down to refresh, swiping a purchase to delete it, and dragging a card down to close it. Each goes for good once you've done it or tapped ✕.

**For you**
- Nothing pops up, because Suki already has your data.
- Settings › Help plays the welcome again, has a Show tips switch (on shows every tip again), lists the hidden gestures, and has the Home Screen steps for a new phone.
- What's been seen stays on this device and isn't saved in backups.

## 2.10 · 31 Oct 2026
*Tidy-ups (Q06)*

**Amounts**
- An amount with two dots, like 12.50.5, asks you to check it instead of quietly saving ₱12.50.
- A pasted 1 000 reads as ₱1,000.
- Anything that rounds to ₱0.00 is refused, on the forms and in Quick Till.

**Saved data and backups**
- A price above ₱10,000,000 or below ₱0.01 counts as damaged (it goes to Recovered data, so it isn't lost).
- An impossible date like 30 February becomes today, like other bad dates.

**Exchange rate**
- With no signal, a refresh gives up after two sources time out, in about 12 seconds instead of 24. The saved rate keeps working.

**Home**
- A very long total steps down a size, with Today underneath, instead of breaking across lines.

## 2.9 · 31 Oct 2026
*Your data stays safe (Q05)*

**Backups**
- A backup with nothing usable in it, because every record is damaged or it's empty, is turned away and nothing changes. Before, it could empty the phone.
- Before a restore or Erase, Suki keeps a copy of what's on the phone. Undo appears straight afterwards, and Settings › Your data has Before your last restore (or erase) to put it back at any time. Putting back swaps, so it can be undone too.

**Saved data**
- Anything saved that Suki can't read is now kept safe instead of being dropped and later written over. Home says so, and Settings › Your data › Recovered data saves it as a file.
- Amounts written like "₱459" or "PHP 1,250" in older or hand-made records are read rather than lost.
- If the iPhone's storage won't open, Home says so. Purchases saved meanwhile are merged back in once it opens again, so none go missing.
- "Couldn't save" now stays on screen until you tap OK, and an Undo message never hides it.

## 2.8 · 31 Oct 2026
*The updated look (Q04)*

**Look**
- The top bar no longer becomes a card. When you scroll, a soft blurred edge appears at the top of the screen with the small title, as in iOS 27.
- On iPhone upright the tab bar sits lower, 21pt from the bottom edge, where Apple's own apps put it. It still stays full size.
- Colours come from Apple's system colours in light and dark, and text sizes follow Apple's text styles.
- Every item in Search has its own picture: rice, eggs, meat, fish, jeepney, tricycle, train, SIM card, scissors and more.

**Settings**
- A new Accessibility page. Reduce motion can match your iPhone or be turned on or off just for Suki; with it on, things fade instead of sliding. Slow motion plays every movement four times slower. Both stay on this device and aren't saved in backups.

**Keyboard**
- On a Mac or iPad keyboard, ⌘1 to ⌘5 switch sections; other computers use Ctrl.

## 2.7 · 31 Oct 2026
*A price for what you'll actually buy and ride (Q02)*

**Prices**
- About 100 prices, each with where it came from and when, checked 31 Oct 2026. They cover:
  - jeepney, bus, taxi, Grab, airport and train fares, including the new fares from 28 Sep 2026 (traditional jeepney ₱14, modern ₱17)
  - the DTI's suggested retail prices for water, noodles, sardines, coffee, bread, soap and more
  - supermarket prices for beer and soft drinks
  - fast-food menu prices
  - SIM cards and data promos
  - rough guides for street food, carinderia meals, laundry, haircuts and massage
- 32 new things to search for, from jeepney and tricycle to beer, Chickenjoy and SIM cards.
- Each price says what kind it is (set fare, suggested retail price, supermarket price, menu price or rough guide), with links to its sources.

**Search**
- Chips under the search box to browse by category: Transport, Food, Market, Drinks, Services and Essentials. They narrow a search too.
- With nothing typed, Search shows a few of each category, each with a Show all row.

**An item's page**
- Typical prices first, then the official Department of Agriculture price where there is one.
- You paid: what you logged for it, newest first.
- A Log what you paid button that starts the form with the item and its category.

## 2.6 · 31 Oct 2026
*Spending over time (Q03)*

**Spending**
- A D · W · M · All switch at the top, with arrows to step back through earlier days, weeks and months. The total, the list and everything below follow it.
- A bar for each day, stacked by category. Tap or slide across the bars to read a day.
- A breakdown by category, with each one's share. Tap a category to show only its purchases.
- Rows show one detail under the name (the place), so nothing is cut off. The rest is in the purchase's details.
- A long list shows the newest 60 purchases, then a Show more row, so Spending stays quick however much you log.
- Delete now offers Undo for a few seconds.
- Category chips fade at the edge when there are more to scroll to.

**Home**
- Tap the date or the Home title to open a calendar. Days you spent on are tinted, today is outlined, and tapping a day lists what you bought.
- Left open past midnight, the app moves on to the new day by itself.

## 2.5 · 31 Oct 2026
*Fixes before the trip (Q01)*

**Confirm sheets**
- The red button on every "Are you sure?" sheet shows its words again (Delete purchase, Delete note, Erase everything, Replace with this backup). They were red on red.

**Search**
- Stricter matching: a clear match is no longer followed by unrelated items, so "water" doesn't show Kwek-kwek and "adobo" doesn't show Banana cue. Misspellings like "sinigan baboy" still work.
- The example search is spelt "sinigang baboy".

**Convert**
- The swap button works: it puts the other currency on top and puts the cursor there. Handy amounts follow, so with pesos on top they go from ₱20 to ₱5,000 in pounds.
- The rate line says when it was updated in plain words ("Updated today", "3 days ago"), without a clock time or a second date.

**Settings**
- The saved rate shows ₱, like everywhere else.

## 2.4 · 23 Oct 2026
*A tab bar that stays put*

**Navigation**
- The tab bar on iPhone now stays full size however far you scroll, instead of shrinking to the current tab. All five tabs are always one tap away.
- Every page now ends 20px above the tab bar, upright and on its side, so nothing at the bottom is hidden behind it and there's no extra empty space.

## 2.3 · 23 Oct 2026
*An exchange rate you can rely on*

**Exchange rate**
- The rate now has backups. Suki asks Frankfurter for the European Central Bank's rate first, then Frankfurter's older address, then the Currency API and its mirror, and uses the first that answers.
- It stays on the European Central Bank's rate whenever Frankfurter answers, so the number matches what Suki used before.
- Every rate is checked before it's saved. Anything outside ₱30 to ₱120 per pound is turned away, so a bad reply can never replace a good saved rate.
- The messages are honest now. "You're offline" only appears when you really are. Otherwise it says the rate service couldn't be reached, and whether your saved rate is still in use.

**Settings**
- Saved exchange rate now says where the rate came from.
- A new Last rate check row shows what happened the last time the rate was checked, and why each source failed if it did.
- Settings now opens instantly, like the five main tabs.

**Search**
- When the saved rate is more than two days old, a quiet line under the prices says how old it is. It disappears once the rate is fresh.

**Spending**
- With nothing logged yet, the total and the message underneath no longer touch.

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
