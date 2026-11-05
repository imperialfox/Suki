# Changelog

## 2.31 · 5 Nov 2026
*Interface: sheets, alerts and toasts from the parts kit (Q27)*

**Sheets**
- On iPhone every sheet is the parts kit's, the same as Vocal Sessions': it rises from the bottom of the screen and leaves faster as it goes, with the screen's own rounder corners.
- Drag it down by its top, or by its content when that's scrolled to the top. A quick flick closes it; a short, slow pull springs back.
- A sheet opened from a sheet (Edit from a purchase, Log what you paid from an item) rises over the first, which waits underneath and is there again when you close the top one.
- The page behind shrinks and comes back in step with the sheet. The tab bar stays, under the dim, instead of disappearing.
- iPad and Mac keep Suki's own sheet in the middle of the screen, opening and closing a little quicker.

**Questions are alerts**
- Delete a purchase, Delete a price note, Clear recovered data, Put back what was here and Restore this backup now ask in a small alert with Cancel and a red button. A delete still shows Undo after.
- Restore says in words what's on the device and what's in the backup.
- Erase all data stays a sheet for now, with Export a backup first. It becomes an alert with the next parts kit.

**Toasts**
- Messages drop in from the top and stay 3 seconds, with or without Undo. A longer one wraps onto a second line.
- "Couldn't save" still stays until you tap OK.

**Motion**
- The parts kit runs Suki's springs, Slow motion and Reduce Motion. Your settings in Accessibility are kept as before.
- With Reduce Motion on, every fade is a quick 0.1 seconds.

Screens: SK-007, SK-008, SK-009, SK-010, SK-011, SK-012, SK-013, SK-014, SK-015, SK-016, SK-018, SK-019, SK-020, SK-021, SK-022, SK-023, SK-024, SK-027, SK-028, SK-030, SK-031

## 2.30 · 5 Nov 2026
*Interface: every corner, press, curve and duration has a name (Q26)*

**The value set**
- Every corner, press, curve, duration and shadow Suki uses is now a named value at the top of the stylesheet, using the parts kit's names and numbers (`--r-card`, `--press`, `--ease-pop`, `--dur-fade` and so on), plus four of Suki's own: the iPad and Mac sheet corner (28), the text button press fade (0.35) and the Till's corner and coin cups.
- 59 hand-written values were swapped for their name, with no change you'd see. The ones the kit has no name for stay as they are, each listed with why, and that list can only get shorter as the parts kit moves in (Q27, Q28).
- Code has the same three curves as `MOTION.EASE` (pop, knob, out).
- A new test stops new hand-written corners, presses, curves, durations and shadows, in the stylesheet and in the code.

**Slow motion**
- Every fade and timing in the stylesheet now follows Slow motion, so the sheet's dim, the iPad sheet's pop, the toast's fade and Reduce Motion's fades slow down with everything else, and stop with motion off.

**Tidied**
- The tab bar's padding, width and height transitions are gone. They were left from Vocal Sessions' folding tab bar, which Suki never had.

**Unchanged**
- Nothing looks or moves differently at normal speed.

Screens: none

## 2.29 · 5 Nov 2026
*Interface: every screen, sheet and part has a permanent ID (Q25)*

**Screen IDs**
- Every screen, sheet and pop-up has an ID that never changes, SK-001 to SK-031, so a note or a request can point at it in a few characters ("SK-002, the button's too low"). Home is SK-001, Quick Till SK-002, the Calendar SK-018, Rate history SK-029.
- Every button, field and control on them has a name too, such as SK-001 › save-button, and the four main journeys have IDs: F-01 Log a purchase on Home, F-02 Pay at the Till and log the bill, F-03 Look up a price and add a note, F-04 Check Spending for a day.
- They're kept in one list in the code, the screen register, which the parts kit and later builds read.

**Show screen IDs**
- Settings › Accessibility has a new Show screen IDs switch, off at first. On, a small grey label just under the top bar shows the screen's ID, and the sheet's after it when one is open (SK-006 · SK-019). It stays on this device and isn't saved in backups.

**Unchanged**
- Nothing else looks or moves differently.

Screens: SK-019

## 2.28 · 5 Nov 2026
*Navigation: every door follows one rule (Q24)*

**Pushes show the page underneath**
- On iPhone, the gear now pushes Settings in, and Back pops it. It used to cut straight to Settings.
- Settings, Help and Rate history all move the same way. The new page slides in over a still copy of the page you left, which moves a third to the left and dims a little. Back runs it in reverse.
- Rate history's swipe back moves Convert the same third, with the same dim, and lets go on the same spring as the pushes.
- On iPad, Settings and Help zoom in and out, like Rate history.

**Settings on a Mac**
- Settings is a section of its own in the sidebar. It switches like a tab, only Settings is lit (not Home as well), and there's no Back button. Help lights only Settings and zooms in from it.

**Home's Show all**
- Both Show all doors under Recent now open Spending on All, with every purchase, like Total spent. Before, they opened whatever period, category or filter Spending was last left on.

**A sheet over a sheet**
- Edit from a purchase, its prices row, Log what you paid, Log a purchase on a calendar day, a note in Price notes, and Delete from a sheet: the new sheet rises over the old one, and the dim stays put. Before, the first sheet and the dim vanished and the dim faded back.

**Deleting**
- The delete message says what goes, for example "Chickenjoy bucket, ₱459.00.", with no promise about backups. Undo brings it back.

**Unchanged**
- Reduce Motion: pushes and zooms are still a short fade. With motion off, everything happens at once. Tabs still switch instantly.

## 2.27 · 4 Nov 2026
*Quick Till: the haul and the maker's mark (Q21)*

**Hand over hand**
- The Easter egg inside the Easter egg. With the drawer fully open, hold it with one finger and swipe down with another. Swap fingers and keep going, as long as one stays down.
- One finger never starts it, so neither does a mouse. It doesn't start on a shut or half-open drawer either.
- It's heavy and steady on purpose: a long swipe moves it about 12 pt, in a straight line, with no easing towards the end. About ten long swipes take it 120 pt past open, where it stops.
- Any finger moving down pulls it. Moving up only counts once a single finger is left.

**It stays where you leave it**
- Let go and it stays put, so the effort isn't lost.
- A one-finger pull on a hauled drawer gives a little and springs back to where you left it. A slow push up that doesn't shut it leaves it where the push ended.
- A swipe up, the line, Enter, typing, or switching away still shuts it from any depth. Next time it opens to plain open: the haul is forgotten, and nothing is saved.

**At the very back**
- "Designed by Ivan", in plain small text (11 pt, regular) in the faint grey, on the drawer floor. It peeks out on the ninth swipe and is whole on the tenth. VoiceOver skips it.

**Behind the scenes**
- The fingers lifting after a haul don't count as a tap, so they don't shut the drawer or leave the cursor in the cash box.
- Tested with real two-finger touches as well as made-up ones, so blocking pinch-zoom doesn't swallow the second finger.

## 2.26 · 4 Nov 2026
*Quick Till: the drawer fills up with the cash you hand over (Q20)*

**How full it looks**
- The drawer now shows roughly how much cash is in it. It's a gauge, not a count: only the cash handed over decides it, and the bill changes nothing.
- Coins fill first, then the ₱50s and ₱100s, then the ₱500s, then the ₱1,000s. Everything is full at ₱20,000.
- Notes stand on edge in their slots as a block of paper, and coins lie in loose heaps in the scooped cups. Each compartment is labelled on its front lip: 1000, 500, 100, 50, then 20, 10, 5, 1 and 25¢.

**Overloaded from ₱50,000**
- Notes tip out of their slots and coins spill out of their cups.
- With the drawer shut, notes peek out from under the cash box, so you see it without opening it. On an iPhone on its side, where there's no drawer, the peek still shows.
- VoiceOver says "Till overloaded. Check the amount."

**Notes land in the drawer**
- With the drawer fully open, a tapped note flies straight into its own slot and the ₱20 into its cup, in both Fly and Slot. That compartment gives a small nod as it lands, and the amount changes then, as before.
- With the drawer shut, notes go into the cash box as before.

**Calm and physical**
- Pieces fade in and out over about 0.2 s, so nothing jumps. ✕ empties the drawer the same calm way.
- When the drawer opens or shuts, the coins lag a moment and settle, and the notes sway about 1.6° and right themselves. A hard shut makes the coins jump with the knock.
- Reduce Motion: pieces still fade, but nothing jiggles.
- Nothing new is saved: the drawer only reflects the cash box.

## 2.25 · 4 Nov 2026
*Quick Till: a hidden till drawer under the cash box (Q19)*

**The drawer**
- An Easter egg: pull the cash box down and a till drawer slides out from under it. Nothing points to it, and it isn't in Help.
- It's a deep tray tilted away from you, with four note slots at the back and five coin cups in front. It's empty for now.
- The six buttons ride on its front, and the cash box casts a soft shadow onto it that deepens as it opens.

**Opening and shutting the iOS way**
- It follows your finger exactly. Let go and it settles at whichever end it would coast to: past halfway it opens, short of that it springs back shut. A real flick opens it from a shorter pull.
- Pull past open and it stretches, then springs back. Grab it while it's moving and it stops under your finger.
- A tap still types. Only a drag is the drawer's, and holding still in the box first, or dragging sideways, leaves it to the cursor and Select.
- Swipe up to shut it. Once it's shut, the rest of the same swipe scrolls the page, and a flick glides on until you touch again.
- Shut it hard and it knocks the counter: only the cash box nudges up, the instant the drawer hits. A gentle push or a tap closes it quietly.

**The slot line is its handle**
- The line under the cash box is hidden at rest. It shows when you touch the cash box, while the drawer is open, and when it's reached with the keyboard or VoiceOver.
- It's a real button: "Open till drawer" or "Close till drawer". Tap it, or press Space or Enter.

**Always starts shut**
- It's shut every time you come to the Till, and shuts when you start typing in either box, open Log this bill or switch tabs.
- iPhone upright only: on its side there's no drawer. On iPad and Mac it's the card's width, and opens with a click, Space or Enter, or a mouse drag.
- Reduce Motion: it fades in and out in 0.2 s, with no spring and no knock.

## 2.24.1 · 4 Nov 2026
*Quick Till: only the two boxes can be selected (Q18)*

- Holding a note, Exact, a label or your change no longer highlights it or brings up the copy menu.
- Total bill and Cash handed over still select as before, so you can move the cursor, select and paste.

## 2.24 · 4 Nov 2026
*Quick Till: tapping a note feels like handing over cash (Q18)*

**The note press**
- Press and hold a note, the ₱20 or Exact: the button tips towards your thumb, and springs back when you let go.
- Tap a note and it flies in an arc into the cash box. The ₱20 spins like a tossed coin.
- The amount changes when the note lands, and the notes and coins of your change settle in straight after. Nothing counts up.
- Tap as fast as you like: each note adds once. Typing in the cash box, ✕ or Exact while a note is still in the air drops it, so what you did last wins. Switching tabs lands it at once.

**Fly or Slot**
- Settings › Accessibility › Note animation: Fly (the starting setting) or Slot.
- Slot: the note slides up into a slot line under the cash box. The line fades in for it, and out about a second later. It's hidden the rest of the time.
- The setting stays on this phone and isn't saved in backups.

**Notes and coins have a look of their own**
- In your change, and in the air, notes are a block of paper lit from the top left, and coins have a hint of metal with a thin edge, so a pile has thickness. The same in dark mode.

**Reduce Motion**
- With Reduce Motion on (on the iPhone, or in Suki), nothing tips or flies: the amount changes as soon as you tap.

## 2.23 · 3 Nov 2026
*Rate history: how the rate has moved, and why (Q23)*

**Rate history**
- On Convert, the rate is now a door: tap "£1 = ₱…" for Rate history. Refresh stays beside it, and Home's rate card still opens Convert.
- Pick a month, 6 months, a year (where it opens), 5 years or everything since April 2005. The big figure is the newest ECB rate with its day, then what £100 buys against the start of the period.
- A strip shows where today sits between the period's low and high, with their dates, and a line says which way is good: "Higher means your pound buys more pesos."
- Drag along the chart to read any day. Near a news dot it snaps to it and shows its title; let go there to read it.
- "Why it moved" splits the change into the peso and the pound, each against the US dollar, worked out on your phone from ECB rates. It hides if a figure is missing, rather than guess.
- "What happened": news notes in plain words, filled dots for the peso and hollow for the pound, each with £1 that week and a link to the official record from the BSP or the Bank of England. 2026's rate decisions, plus the 2008 crisis, the 2016 referendum and the 2022 mini-budget for the longer views. "News checked 3 Nov 2026", said plainly once it's over a month old.
- Settings › Help › What's a central bank rate?, also one tap from every news note.
- Once you've started a trip (purchases with no gap of two weeks), a faint line marks its first day, with "Since 7 Nov: ₱0.42 more per £1".
- Swap Convert to pesos first and the page follows: "₱100 = £…", and which way is good for pesos.
- Every gap says why: weekends, the Manila night gap (the ECB publishes about 11 pm there), offline, no signal yet, and a saved rate from Currency API, shown as its own hollow dot.
- Swipe back from anywhere on the page except the chart. On iPad and Mac the chart and the news sit side by side.
- VoiceOver reads the chart as a sentence: "Up 10.4% in a year. High ₱85.35 on 26 October 2026."

**History that doesn't depend on one service**
- Rates from 2016 to 30 Oct 2026 come with the app, so 6M, Y and 5Y work with no signal and even if Frankfurter stops.
- Newer days are asked for only when they're missing, and kept on your phone. Every reply is checked whole (dates in order, sensible rates, no day jumping more than 10%), and a bad one is refused.
- The years before 2016 load only when you tap All.
- Every rate Suki loads for Convert is kept with its source, and fills a gap where the ECB has no figure.
- None of it goes in backups: it isn't your data, and it can be downloaded again. If it couldn't be loaded, Settings › Last rate check says why.

## 2.22.1 · 3 Nov 2026
*The rate's day reads the same on every device (Q22)*

- The day under "In pounds then" is always written like "Fri 30 Oct", with no comma after the weekday, whatever the browser.

## 2.22 · 3 Nov 2026
*Pounds at the rate you paid (Q22)*

**Totals in pounds stay put**
- Home's total and Spending's total (a period, a day, a category or a filter) now add each purchase in pounds at its own rate, the one saved with it. Before, the whole peso total was divided by today's rate, so the pounds changed every day with no new spending.
- A purchase with no rate of its own (one saved before a rate had ever loaded) counts at today's rate, and the total says how many: "2 at today's rate". One still waiting for its day's rate says "1 estimated".
- "You paid" on an item's page shows each purchase in pounds at its own rate too.

**A purchase for an earlier day gets that day's rate**
- Log something for yesterday, on a calendar day, with Smart add's "yesterday" or "on Friday", or change a purchase's date, and it gets the European Central Bank rate published before that day. A weekend or holiday takes the weekday before, so a Monday-morning purchase in Manila gets Friday's (Monday's comes out at about 11 pm there).
- Today's and future dates keep today's saved rate, as before.
- Saving never waits: the purchase is saved at once with today's rate, and that day's rate is filled in straight after. With no signal it stays "estimated" and is corrected quietly the next time Suki has signal. Only the rate changes, never the price, date or words.
- The rate comes from Frankfurter (the ECB), then the Currency API's file for that day. A reply that isn't a sensible rate, or is for the wrong day, is ignored.

**In pounds then**
- A purchase's details show the rate behind its pounds: "£1 = ₱83.11 · Thu 1 Oct · ECB", with "estimated" while it is.
- The rate's day and source are kept with the purchase, through editing, backups and restoring. Older purchases keep their rates as they were.

## 2.21 · 2 Nov 2026
*Log by voice with Siri, and nothing saved twice (Q15)*

**Already saved**
- Paste your Siri note into Smart add as often as you like. A line that starts with the Shortcut's time, like "[2026-11-21 13:05] tricycle 50 pesos", and matches a purchase you've already saved shows greyed as "Already saved" and is left out of Save.
- The heading says how many are new: "3 new · 2 already saved", and Save counts only the new ones. Undo takes back just those.
- When everything pasted is already saved, there's nothing to save, and "Clear the box" empties it in one tap.
- Lines without a time are never skipped, so typing "jeep 14" twice in a day still saves twice. The same words said at a different time count as new.
- Each purchase from a Siri line keeps its time with it, through editing, checking it in the Log sheet, Edit in the form and backups. Older purchases and backups are unaffected.

**Help › Log by voice with Siri**
- The six Shortcut steps to build on your phone (Dictate Text, Format Date, Text, Append to Note "Suki inbox", Copy to Clipboard, Show Notification), how to run it (Hey Siri, the Action Button or a Lock Screen control), and that clearing the note is optional.
- "Smart add" in the steps opens Home on Smart add, ready to paste.

## 2.20 · 2 Nov 2026
*Smart add: type, say or paste a purchase in one line (Q14)*

**Two sides of the Log card**
- Home's Log card now has two sides: the form, as before, and Smart add. A pill on the "Log a purchase" heading switches them ("Smart add" ↔ "Full form"), and Suki remembers the side you used last on this device.
- Switching is a soft fade: the card stays put, the box you type in slides to its new spot, and everything else blurs out and the other side comes into focus. With Reduce Motion it's a plain crossfade.

**Smart add reads what you type**
- Type a line like "jeep to cubao 14", "tricycle fifty pesos from Bulakan to Barrio" or "lunch carinderia kahapon", or use the keyboard's microphone, and Suki shows what it understood before anything is saved: the item, amount, category, day, place, where you bought it and how you paid.
- Amounts can be ₱50, P50, PHP 50, "50 pesos", 2k, words ("a hundred and twenty", "one twenty") and Tagalog (bente, singkwenta, isang daan). An amount in pounds is changed at your saved rate, with a note.
- Days can be today, yesterday, kahapon, kanina, last night, "on Friday", "2 days ago" or a date like "21 November". A date in the future is flagged.
- Several purchases at once: one per line, or "also", or two amounts in one line ("jeepney 14, halo-halo 120 and water 25"). A day, a place or "both by card" said once applies to the whole line.
- It reads everything on your phone with word rules. No AI or server sees what you type.

**It asks only what's missing**
- No amount: "How much?". No name: "What was it?". When two categories fit, it asks which, and a category it had no clue for is tinted so you check it.
- One purchase: Save purchase, or Edit in the form to finish it there. Several: Save 5 purchases, with Undo for all of them. Tap one in the list to check it in the usual Log sheet first.
- When the line names no place, Location starts as the town you were in earlier that day.

**Smart from the start**
- Your usual: say "jeep" with no amount and it fills the middle of your last three, at the same place first. You can change it.
- While you type a name, up to three of your own purchases show underneath. Tap one to fill the line.
- A purchase that's a whole price-list item gets a plain note: "Within the typical ₱14–17", "More than…" or "Less than…", with the item's prices one tap away. Never a warning colour.

**It learns**
- Change a category and Suki remembers the word for next time. Settings › Your data › Words Suki has learned lists them, and you can forget any. They're kept in backups. An older backup without them leaves yours as they are.

**Your words are kept**
- Each purchase saved from Smart add keeps the line you typed. A purchase's details show it as "You typed: …".

**Also**
- The form's amount box now takes P50, "50 pesos" and 2k too.
- "You paid" on an item now matches whole words only, so a mango purchase never shows under Mang Inasal, or spaghetti under Massage.

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
