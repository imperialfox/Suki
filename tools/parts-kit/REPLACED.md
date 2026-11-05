# What the parts kit replaced in Suki

One row per old value or part that Suki dropped when it moved onto Parts kit 1.2.0, so the reference sheets and the element sheet (Q30) can see where each came from. Newest first.

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
