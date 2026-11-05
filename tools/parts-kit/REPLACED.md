# What the parts kit replaced in Suki

One row per old value or part that Suki dropped when it moved onto Parts kit 1.2.0, so the reference sheets and the element sheet (Q30) can see where each came from. Newest first.

## Q28 · 2.32 · Controls and presses (5 Nov 2026)

| Was (Suki 2.31.1) | Where | Now (kit) | Decision |
|---|---|---|---|
| Glass circles and capsules (`.circ`, `.btn`) shrinking to `--press` (0.93) and back over 0.5 s on `--ease-pop` | `css/app.css` | Part 12: `.pk-press`, grows 17 pt and lights up (`--lift-max`), the `press` and `release` springs | Q28 |
| The soft highlight on those buttons in `.glass::after` | `css/app.css` | In their background (`.glass.pk-press`), as the kit's light takes `::after`; the same at rest | Q28 |
| Solid capsules (`.cta`) shrinking to 0.93 and back over 0.5 s on `--ease-pop` | `css/app.css` | Part 14: `.pk-press-solid`, `--press` in over `--dur-quick`, back on the `release` spring | Q28 |
| Rows shrinking to `--press-row` (0.98) and back over 0.5 s | `css/app.css` | Part 35: highlight with `--pk-row-press`, no shrink | D06 |
| Home's figures shrinking to 0.96 and fading to 70%; the rate card shrinking to 0.98 | `css/app.css` | Part 35: one highlight for both card doors (the row press colour) | D06 |
| Chips shrinking to 0.93 | `css/app.css` | Part 18: `.pk-chip` in a `.pk-static` row, no shrink (Suki's ink picked colour kept) | Q28 |
| Segmented controls: a glass knob sliding over 450 ms on `--ease-knob` and a 450 ms squish (`squish()` in `events.js`), no drag | `css/app.css`, `js/events.js`, `js/history.js` | Part 23: `.pk-seg` with `.pk-seg-ind`, a 350 ms spring, swells while pressed, draggable, no squish | D04 |
| Switches: Suki's `.sw-ui`, 51 × 31, a knob moving over 0.3 s on `--ease-knob`, no drag | `css/app.css`, `js/ui.js`, `js/onboard.js` | Part 21: `.pk-switch`, 64 × 28, 380 ms, swells, drag or flick at 200 px/s | Q28 |
| The tab bar: the picked tab's own `--fill` jumping to the new tab; tabs shrinking to 0.93; 5 pt padding, 2 pt gaps | `css/app.css`, `js/ui.js` | Parts 4 and 15: `.pk-tabbar` with `.pk-tab-ind` sliding on its spring, swelling, draggable; tabs only light up; 4 pt padding, equal tabs | D01 |
| iPad's top tabs: the same, tabs as wide as their words | `css/app.css`, `js/ui.js` | Part 4: the same highlight, equal tabs | Q28 |
| The soft edge: `--bg` at 62% with a 14 px blur, solid to 62% then clear, in over `--dur-appear` (0.25 s) | `css/app.css` | Parts 2 and 51: `.pk-edge.pk-text-heavy`, the page colour fading out, no blur, in over `--dur-fade` (0.2 s) on `--ease-out` | Q28 |

## Q27 · 2.31 · Pop-ups (5 Nov 2026)

| Was (Suki 2.30) | Where | Now (kit) | Decision |
|---|---|---|---|
| Suki's own springs `gentle`, `nav`, `ripple` (the same numbers), speed and Reduce Motion, published by `js/motion.js` | `js/motion.js` | `Parts.motion`: the kit's springs, `--pk-speed`, `.motion-off`, `.motion-reduced` | D18 |
| `--mspeed` (the speed, written by `motion.js`) | `css/app.css`, everywhere | `--pk-speed` | D18 |
| `MOTION.settle()` (a row or coin landing) | `js/motion.js`, `ui.js`, `screens.js` | `MOTION.land()` (Suki's own, renamed) | S02 |
| `MOTION`'s fallback curve for a browser without `linear()` springs, `cubic-bezier(.25,.9,.3,1)` | `js/motion.js` | the kit's own fallback | D18 |
| Reduce Motion fades of 150, 180 and 200 ms | `motion.js` (`animate`, `leave`, `fold`) | `--dur-reduced`, 100 ms (`MOTION.reducedMs()`) | D20 |
| The blanket Reduce Motion rule's forced 0.2 s | `css/app.css` | `--dur-reduced` × `--pk-speed` (the rule keeps transitions to fades) | D20 |
| The iPhone sheet: `.sheet` rising 40 px from 40% opacity on `gentle`, 34 corners, max 90% tall, `@keyframes up` | `css/app.css` | Part 41: from below the screen on the `sheet` spring, 46 corners (`--r-sheet`), 90 pt from the top | D14, D15, D17 |
| The sheet leaving: `translateY(115%)` in 330 ms on `cubic-bezier(.3,0,.25,1)` (`sheetAway()`) | `js/ui.js` | Part 41: 350 ms on `--ease-accel` (`--dur-leave`) | D14 |
| Dragging a sheet by its header past 90 px (`touchstart` on `.shead`), no flick, no drag from the content, no mouse | `js/gestures.js` | Part 41: pointer drag from the head or the content at the top, 40% or a 700 pt/s flick | D14 |
| A dragged sheet springing back over 0.32 s on its own curve (iPhone) | `css/app.css` `.sheet.back` | the `sheet` spring (kept for iPad and Mac's centred sheet only) | D14 |
| The dim: `--scrim` (22% light, 50% dark) fading over `--dur-fade` | `css/app.css` `#layer .scrim` | `.pk-dim`, `--pk-dim` 54% (kept for iPad and Mac's centred sheet only) | D15 |
| The page behind: 0.94 over 0.45 s on `cubic-bezier(0.3, 1.3, 0.5, 1)`, back over 0.33 s on `cubic-bezier(0.3, 0, 0.25, 1)` (`body.unsheet`) | `css/app.css` `.wrap` | the `sheet` spring in, `--dur-leave` on `--ease-accel` out | D21 |
| A sheet over a sheet: the old one copied into `#leaving` as `.under` until the new one has risen (iPhone) | `js/ui.js` `sheetUnderKeep()` | the kit's sheets stack: the first stays open underneath (kept for iPad and Mac) | Q24, D14 |
| The tab bar hidden while a sheet is open | `js/ui.js` `renderDock()` | stays, under the dim | shared default 6 |
| iPad and Mac's sheet pop over 0.42 s, leaving over 220 ms | `css/app.css`, `js/ui.js` | Suki's own, now `--dur-appear` (250 ms) and `--dur-close` (170 ms), `--r-form` 28 | S01 |
| Confirmation sheets: Delete this purchase?, Delete this price note?, Clear recovered data?, Put back what was here?, Restore this backup? (with a comparison table) | `js/ui.js` `confirmBody()`, `sheetHTML()` | Part 48: alerts (Restore says what's here and in the backup in words) | D08 |
| Erase all data as a sheet | `js/ui.js` | stays a sheet until kit 1.3.0's three-button alert | S03 (D23 waits) |
| Toasts: a glass capsule dropping 18 px on `gentle`, 2.2 s (4.5 s with Undo), fading out over 0.22 s | `js/ui.js` `toast()`, `css/app.css` `.toast` | Part 49: 500 ms in on `--ease-decel`, 350 ms out, 3 s with or without Undo | D16 |
| The sticky "Couldn't save" warning | `js/ui.js`, `css/app.css` | stays Suki's own | S04 |
