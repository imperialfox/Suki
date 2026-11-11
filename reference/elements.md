# Element sheet · Suki

Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is (by its gallery number), how it presses, its corner and its motion, the decision behind it, and its status. Suki's own part, with no kit part, says why. Written by `tools/reference/elements.py` from `js/register.js`, `js/parts.settings.js` and the app itself (headless, the tests' sample data, motion off), so the values are what the page really uses, mapped back to their names in the value set; don't edit by hand. The same columns as Vocal Sessions' element sheet, plus Decision. The naming rules: [MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).

A note points at a part as `SK-001 › log-card`; a shared or by-action part is named the same on every screen it shows on.

**How to read the values.** Kit part: the gallery number in `tools/parts-kit/README.md` › Parts. Press: how it presses ([Presses](#presses)). Corner: a named corner (`--r-card` …), `capsule`, `circle` or `none`. Motion: the springs and named timings its own transitions use (`gentle`, `--ease-out`, `--dur-fade` …), `none` when it doesn't move at rest; a press's own motion is in Presses. Decision: the IDs in `js/parts.settings.js` ([Decisions](#decisions)). A part that shows in more than one place lists each value it has (`a · b`). A dash: the sample data doesn't reach it ([Not reached](#not-reached)). Statuses: In use · Phasing out · Retired.

**28 shared parts, 85 names by action, 28 parts named on their screens. 105 of 141 in use read from the app.**

## Shared

Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status |
|---|---|---|---|---|---|---|---|---|
| `home-tab` | `#dock [data-a="tab"][data-v="home"], #barT [data-a="tab"][data-v="home"], #side [data-a="tab"][data-v="home"]` | 4 Tab bar | none | capsule | none |  | D01 | In use |
| `till-tab` | `[data-a="tab"][data-v="till"]` | 4 Tab bar | none | capsule | none |  | D01 | In use |
| `search-tab` | `[data-a="tab"][data-v="search"]` | 4 Tab bar | none | capsule | none |  | D01 | In use |
| `spending-tab` | `[data-a="tab"][data-v="spending"]` | 4 Tab bar | none | capsule | none |  | D01 | In use |
| `convert-tab` | `#dock [data-a="tab"][data-v="convert"], #barT [data-a="tab"][data-v="convert"], #side [data-a="tab"][data-v="convert"]` | 4 Tab bar | none | capsule | none |  | D01 | In use |
| `settings-tab` | `#side [data-a="tab"][data-v="settings"]` | 35 List row | Row, highlights | 12px | `--ease-out` |  | D06 | In use |
| `settings-button` | `#barR [data-a="tab"][data-v="settings"]` | 12 Glass button | Glass, grows | circle | `release` |  | D19 | In use |
| `back-button` | `#barL [data-a="tab"]` | 12 Glass button | Glass, grows | circle | `release` |  | D19 | In use |
| `close-button` | `.circ[data-a="close"], [data-a="tipX"]` | 12 Glass button | Glass, grows | circle | `release` |  |  | In use |
| `cancel-button` | `.ghost[data-a="close"], [data-a="obsCancel"], .pk-alert [data-a="no"]` | 1 Glass, 48 Alert | Text, fades · none | capsule · none | `--ease-out` · none |  | D08, S06 | In use |
| `dim-layer` | `.scrim[data-a="close"], .pk-dim` | 41 Sheet | — | — | — |  |  | In use |
| `grabber` | `.grab, .pk-grabber` | 41 Sheet | none | capsule | none |  | D14, D15, D17 | In use |
| `save-button` | `button[type="submit"], #homeSave` | 14 Solid press | Solid, shrinks | capsule | `release` |  |  | In use |
| `confirm-button` | `.cta.red[data-a$="Yes"], .pk-alert [data-a="yes"]` | 1 Glass, 14 Solid press, 48 Alert | Solid, shrinks · none | capsule | `release` · none |  | D08 | In use |
| `item-field` | `[data-f="item"], #smartItem` |  | none | 10px · 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `amount-field` | `[data-f="price"], #smartPrice` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `category-picker` | `[data-f="category"], [data-smart-cat]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `date-field` | `[data-f="date"]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `location-field` | `[data-f="location"]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `venue-picker` | `[data-f="venue"]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `payment-picker` | `[data-f="payment"]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `notes-field` | `[data-f="notes"]` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |
| `note-field` | `[data-f="note"]` |  | — | — | — |  |  | In use |
| `search-field` | `#q` |  | none | none | none | Suki's own form field, not kit part 27 |  | In use |
| `filter-field` | `#filter` |  | none | none | none | Suki's own form field, not kit part 27 |  | In use |
| `line-field` | `#smartText` |  | — | — | — |  |  | In use |
| `github-link` | `a[href*="github.com"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `source-link` | `a.link[href]` |  | Text, fades | none | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |

## By action

Wherever the action shows, its button gets this name. A screen's own parts and the shared ones win over these.

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status |
|---|---|---|---|---|---|---|---|---|
| `done-button` | `[data-a="ahsGot"]` |  | — | — | — |  |  | In use |
| `later-button` | `[data-a="ahsLater"]` |  | — | — | — |  |  | In use |
| `day-button` | `[data-a="calDay"]` | 35 List row | Row, highlights | circle | none |  | D06 | In use |
| `period-button` | `[data-a="calFromSpend"]` |  | Text, fades | 8px | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `earlier-month-button` | `[data-a="calStep"][data-v="-1"]` | 12 Glass button | Glass, grows | circle | `release` |  |  | In use |
| `later-month-button` | `[data-a="calStep"][data-v="1"]` | 12 Glass button | Glass, grows | circle | `release` |  |  | In use |
| `calendar-button` | `[data-a="calendar"]` |  | none | none | none | Home's date line and title, a door to the calendar (Q08); the kit's large title isn't used |  | In use |
| `note-button` | `[data-a="cashAdd"]` |  | Own, shrinks | 12px | `--ease-pop` | The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21) |  | In use |
| `clear-button` | `[data-a="cashClear"]` |  | — | — | — |  |  | In use |
| `exact-button` | `[data-a="cashExact"]` |  | Own, shrinks | 12px | `--ease-pop` | The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21) |  | In use |
| `category-chip` | `[data-a="cat"]` | 18 Chips | none | capsule | `--ease-out` |  |  | In use |
| `clear-bar-button` | `[data-a="clearBar"]` |  | — | — | — |  |  | In use |
| `clear-filter-button` | `[data-a="clearFilter"]` |  | — | — | — |  |  | In use |
| `reset-filters-button` | `[data-a="clearFilters"]` |  | — | — | — |  |  | In use |
| `clear-search-button` | `[data-a="clearQ"]` |  | — | — | — |  |  | In use |
| `clear-button` | `[data-a="clearRescue"]` |  | — | — | — |  |  | In use |
| `copy-button` | `[data-a="copyConv"]` | 12 Glass button | Glass, grows | capsule | `release` |  |  | In use |
| `export-csv-button` | `[data-a="csv"]` | 12 Glass button | Glass, grows | capsule | `release` |  |  | In use |
| `delete-button` | `[data-a="delObs"]` |  | Text, fades | circle | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `delete-button` | `[data-a="delPurchase"]` |  | Text, fades · none | none | `--ease-out` · none | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `confirm-button` | `[data-a="delPurchaseYes"]` |  | — | — | — |  |  | In use |
| `confirm-button` | `[data-a="delObsYes"]` |  | — | — | — |  |  | In use |
| `confirm-button` | `[data-a="clearRescueYes"]` |  | — | — | — |  |  | In use |
| `confirm-button` | `[data-a="eraseYes"]` |  | — | — | — |  |  | In use |
| `confirm-button` | `[data-a="putBackYes"]` |  | — | — | — |  |  | In use |
| `confirm-button` | `[data-a="restoreYes"]` |  | — | — | — |  |  | In use |
| `edit-button` | `[data-a="editPurchase"]` | 12 Glass button | Glass, grows | circle | `release` |  |  | In use |
| `erase-row` | `[data-a="erase"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `export-backup-row` | `[data-a="exportBackup"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `export-backup-button` | `[data-a="exportBackup"][data-v="push"]` | 12 Glass button | Glass, grows | capsule | `release` |  |  | In use |
| `forget-button` | `[data-a="forgetWord"]` |  | — | — | — |  |  | In use |
| `rate-card` | `[data-a="goConvert"]` | 35 List row | Row, highlights | 20px | none |  | D06 | In use |
| `refresh-link` | `[data-a="goRefresh"]` |  | — | — | — |  |  | In use |
| `search-link` | `[data-a="goSearch"]` |  | Text, fades | none | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `smart-add-link` | `[data-a="goSmart"]` |  | Text, fades | none | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `range-option` | `[data-a="hRange"]` | 23 Segmented control | none | capsule | none |  | D04 | In use |
| `show-all-button` | `[data-a="hShowAll"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `restore-backup-row` | `[data-a="importPick"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `locate-button` | `[data-a="locate"]` |  | none | 12px | none | The form's own arrow inside the Location field (Q16) |  | In use |
| `log-paid-button` | `[data-a="logItem"]` | 12 Glass button | Glass, grows | capsule | `release` |  |  | In use |
| `side-pill` | `[data-a="logSide"]` |  | Text, fades | capsule | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `more-details-button` | `[data-a="more"]` |  | Text, fades | none | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `show-more-row` | `[data-a="moreRows"]` |  | — | — | — |  |  | In use |
| `log-purchase-button` | `[data-a="newPurchase"]` |  | — | — | — |  |  | In use |
| `add-note-button` | `[data-a="obsForm"]` |  | Text, fades | 8px | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `accessibility-row` | `[data-a="openAccess"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `home-screen-row` | `[data-a="openAhs"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `central-bank-rate-row` | `[data-a="openCbRate"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `help-row` | `[data-a="openHelp"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `rate-row` | `[data-a="openHistory"]` |  | Own, highlights | 14px | none | Convert's own rate row, with its own highlight (Q23) |  | In use |
| `item-row` | `[data-a="openItem"]` | 35 List row | Row, highlights · none | none | `--ease-out` · none |  | D06 | In use |
| `learned-words-row` | `[data-a="openLearned"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `news-row` | `[data-a="openNews"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `price-notes-row` | `[data-a="openNotes"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `purchase-row` | `[data-a="openPurchase"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `recovered-data-row` | `[data-a="openRescue"]` |  | — | — | — |  |  | In use |
| `siri-row` | `[data-a="openSiri"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `price-dot` | `[data-a="pickDot"]` |  | — | — | — |  |  | In use |
| `put-back-row` | `[data-a="putBack"]` |  | — | — | — |  |  | In use |
| `amount-chip` | `[data-a="quickConv"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `period-option` | `[data-a="range"]` | 23 Segmented control | none | capsule | none |  | D04 | In use |
| `earlier-period-button` | `[data-a="rangeStep"][data-v="1"]` |  | — | — | — |  |  | In use |
| `later-period-button` | `[data-a="rangeStep"][data-v="-1"]` |  | — | — | — |  |  | In use |
| `refresh-button` | `[data-a="refreshRate"]` | 12 Glass button | Glass, grows | capsule | `release` |  |  | In use |
| `save-backup-button` | `[data-a="saveBackup"]` | 14 Solid press | Solid, shrinks | capsule | `release` |  |  | In use |
| `save-copy-button` | `[data-a="saveRescue"]` | 14 Solid press | Solid, shrinks | capsule | `release` |  |  | In use |
| `category-chip` | `[data-a="scat"]` | 18 Chips, 35 List row | Row, highlights · none | capsule · none | `--ease-out` |  | D06 | In use |
| `screen-ids-switch` | `[data-a="screenIds"]` |  | none | none | none | Suki's own form field, not kit part 27 |  | In use |
| `show-in-spending-button` | `[data-a="searchToSpend"]` |  | — | — | — |  |  | In use |
| `note-animation-option` | `[data-a="setNoteAnim"]` | 23 Segmented control | none | capsule | none |  | D04 | In use |
| `reduce-motion-option` | `[data-a="setReduce"]` | 23 Segmented control | none | capsule | none |  | D04 | In use |
| `welcome-row` | `[data-a="showWelcome"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |
| `slow-motion-switch` | `[data-a="slowMotion"]` |  | none | none | none | Suki's own form field, not kit part 27 |  | In use |
| `check-row` | `[data-a="smartCheck"]` |  | — | — | — |  |  | In use |
| `clear-button` | `[data-a="smartClear"]` |  | — | — | — |  |  | In use |
| `choice-chip` | `[data-a="smartPick"]` |  | — | — | — |  |  | In use |
| `save-button` | `[data-a="smartSave"]` |  | — | — | — |  |  | In use |
| `suggestion-row` | `[data-a="smartSugg"]` |  | — | — | — |  |  | In use |
| `edit-in-form-link` | `[data-a="smartToForm"]` |  | — | — | — |  |  | In use |
| `swap-button` | `[data-a="swapConv"]` | 12 Glass button | Glass, grows | circle | `release` |  |  | In use |
| `log-bill-button` | `[data-a="tillLog"]` | 14 Solid press | Solid, shrinks | capsule | `release` |  |  | In use |
| `tips-switch` | `[data-a="tipsToggle"]` |  | none | none | none | Suki's own form field, not kit part 27 |  | In use |
| `show-all-button` | `[data-a="toSpend"][data-v="all"]` |  | Text, fades | 8px | `--ease-out` | A text button or word link; the kit has no text button with a press yet (S06) | S06 | In use |
| `today-card` | `[data-a="toSpend"][data-v="day"]` | 35 List row | Row, highlights | 14px | `--ease-out` |  | D06 | In use |
| `continue-button` | `[data-a="welcomeGo"]` | 14 Solid press | Solid, shrinks | capsule | `release` |  |  | In use |

## Presses

How each kind of part presses. A kit press is a class in the markup (Q28); the rest are `css/app.css`'s `:active` rules. A new button with one of these classes gets the press for free. Chips (part 18) don't press; the segmented control's knob (part 23, D04) and the switch (part 21) swell to glass while held.

| Kind | Kit part | Press | Parts | Decision | Status |
|---|---|---|---|---|---|
| Glass button | 12 · `.pk-press` | Grows 17 pt on its longest side and lights up, on the kit's `press` and `release` springs (Q28) | 13 |  | In use |
| Solid capsule | 14 · `.pk-press-solid` | Shrinks to `--press` (0.93) over `--dur-quick`, back on `release` (Q28) | 6 |  | In use |
| Row and card door | 35 · the kit's `--pk-row-press` | Highlights at once, fades out over `--dur-fade`; no shrink | 29 | D06 | In use |
| Text button and word link | Suki's own | Fades to `--press-fade` (0.35) at once, back over `--dur-fade` | 11 | S06 | In use |
| The Till's notes | Suki's own | Shrinks to `--press`, back over 0.5 s on `--ease-pop`, with its own tilt (Q18) | 2 |  | In use |
| Own highlight | Suki's own | Its own fill while pressed | 1 |  | In use |

## Decisions

Every decision in `js/parts.settings.js`, in its order. A row above names the ones that cover it; the rest cover the whole app. The register of them, with dates and reasons, is the project note `suki_parts_decisions.md`.

| Decision | Setting | What it says |
|---|---|---|
| D18 | `motion` | the kit runs the motion: its springs, speed and Reduce Motion |
| D18 | `springs` | Suki's own springs, one line each with its ID (none today) |
| D01 | `tabBar` | the tab bar never folds (31 Oct 2026); its search circle isn't used |
| D04 | `segmented` | the gallery's knob: 350 ms spring, swells to glass, draggable (from Q28) |
| D06 | `row` | rows and card doors highlight while pressed, no shrink (from Q28) |
| D08 | `confirm` | a yes or no question is an alert with Cancel and a red action; a delete then shows Undo |
| D14 | `dragShrink` | sheets follow the finger without shrinking |
| D15 | `glass` | sheets keep the strong glass |
| D16 | `timing` | toasts stay 3 s, with or without Undo |
| D17 | `sheetCorners` | iPhone sheets have the screen's own 46 corners (--r-sheet in css/app.css) |
| D19 | `topBar` | the top bar's buttons at Suki's own top area, not the kit's 54 pt (Q28) |
| D20 | `reducedFade` | Reduce Motion fades are the kit's 100 ms (--dur-reduced): nothing in Suki changes it |
| D21 | `pageBehind` | the page behind a sheet shrinks on the sheet spring and comes back on its leave |
| D22 | `push` | a pushed page moves the one underneath 33% and dims it 10% (Q24, history.js) |
| D23 | `erase` | waits for kit 1.3.0's three-button alert; on 1.2.0 Erase all data stays a sheet (S03) |
| S01 | `formSheet` | iPad and Mac sheets stay Suki's own, centred, with --r-form 28 corners |
| S02 | `land` | Suki's settle is called land, so --ease-settle means only the kit's spring |
| S04 | `stickyToast` | "Couldn't save" warnings stay Suki's own sticky toast, with OK |
| S05 | `details` | details open as sheets on iPhone and panes on iPad and Mac (Q24) |
| S06 | `pressFade` | text buttons, Cancel and word links fade to 35% while pressed (--press-fade, Q29) |

## Retired values

Values Suki dropped. None may come back on a part: `test_screens.py` › `reference` fails if one does. Where each came from: `tools/parts-kit/REPLACED.md` and MAINTAINING › Value set.

| Value | Was | Now | Status |
|---|---|---|---|
| `cubic-bezier(0.25, 0.9, 0.3, 1)` | MOTION's fallback curve for a browser without linear() springs | the kit's own fallback | Retired · Q27 · 2.31 |
| `cubic-bezier(0.3, 1.3, 0.5, 1)` | The page behind a sheet shrinking | the `sheet` spring | Retired · Q27 · 2.31 |
| `cubic-bezier(0.3, 0, 0.25, 1)` | A sheet leaving, the page behind coming back | `--ease-accel` over `--dur-leave` | Retired · Q27 · 2.31 |
| `@up` | The iPhone sheet rising (`@keyframes up`) | kit part 41 on the `sheet` spring | Retired · Q27 · 2.31 |
| `@squish` | The segmented control's squish (`squish()` in events.js) | kit part 23, no squish (D04) | Retired · Q28 · 2.32 |
| `padding` | The tab bar's padding transition | nothing: Suki never had a folding tab bar (D01) | Retired · Q26 · 2.30 |
| `max-width` | The tab buttons' max-width transition | nothing (D01) | Retired · Q26 · 2.30 |
| `height` | The tab buttons' height transition | nothing (D01) | Retired · Q26 · 2.30 |
| `width` | Any size transition | nothing transitions a size (Value set) | Retired · Q26 · 2.30 |

## On their screens

### SK-001 · Home

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `total-card` | `.stat.door[data-v="all"]` | 35 List row | Row, highlights | 14px | `--ease-out` |  | D06 | In use |  |
| `show-all-row` | `.row.more[data-a="toSpend"]` |  | — | — | — |  |  | In use |  |
| `backup-banner` | `.nudge[data-a="exportBackup"]` |  | none | 16px | none | Home's own notices, drawn with Home (Q05) |  | In use |  |
| `recovered-banner` | `.nudge[data-a="openRescue"]` |  | — | — | — |  |  | In use |  |
| `log-card` | `#logwrap` |  | none | none | none | Home's own cards, drawn with Home (Q03, Q17) |  | In use |  |

### SK-002 · Quick Till

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `bill-field` | `#till-bill` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |  |
| `cash-field` | `#till-cash` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |  |
| `change-card` | `#tillOut` |  | none | none | none | The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21) |  | In use |  |
| `slot-line` | `#tillHdl` |  | none | none | none | The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21) |  | In use |  |
| `drawer` | `#tillDrawer` |  | none | none | none | The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21) |  | In use |  |

### SK-004 · Spending

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `add-button` | `#barR [data-a="newPurchase"]` | 12 Glass button | Glass, grows | circle | `release` |  | D19 | In use |  |
| `category-row` | `.brk .row[data-a="cat"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |
| `show-all-button` | `.tbtn[data-a="cat"]` |  | — | — | — |  |  | In use |  |
| `chart` | `#chart` |  | none | none | none | Spending's own chart, drawn with its bars (Q03, Q10) |  | In use |  |
| `period-picker` | `#rangeSeg` | 23 Segmented control | none | capsule | none |  | D04 | In use |  |

### SK-005 · Convert

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `peso-field` | `#conv-php` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |  |
| `pound-field` | `#conv-gbp` |  | none | 12px | none | Suki's own form field, not kit part 27 |  | In use |  |

### SK-006 · Settings

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `last-backup-row` | `#lastBackupRow` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |
| `saved-rate-row` | `.row[data-a="goConvert"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |

### SK-007 · Purchase

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `prices-row` | `[data-a="openItem"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |

### SK-016 · Toast

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `undo-button` | `.toast:not(.sticky) button` | 1 Glass, 49 Toast | none | capsule | none |  | D16 | In use |  |
| `ok-button` | `.toast.sticky button` |  | none | capsule | none | The sticky warning stays Suki's own (S04) | S04 | In use |  |

### SK-018 · Calendar

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `log-day-row` | `.row.more[data-a="newPurchase"]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |

### SK-019 · Accessibility

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `reduce-motion-picker` | `#reduceSeg` | 23 Segmented control | none | capsule | none |  | D04 | In use |  |
| `note-animation-picker` | `#noteSeg` | 23 Segmented control | none | capsule | none |  | D04 | In use |  |

### SK-029 · Rate history

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `range-picker` | `#hSeg` | 23 Segmented control | none | capsule | none |  | D04 | In use |  |
| `chart` | `#hchart` |  | none | none | none | Rate history's own chart (Q23) |  | In use |  |

### SK-030 · News note

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status | Was |
|---|---|---|---|---|---|---|---|---|---|
| `official-record-row` | `a.row[href]` | 35 List row | Row, highlights | none | `--ease-out` |  | D06 | In use |  |

## Not reached

Parts in use that the sample data doesn't show (a state such as a full drawer, an empty list or a tip), so their values are a dash. Their kit part, if any, is read from how they're found. Reaching more of them is a change to `collect()` in `tools/reference/elements.py`.

<details><summary>Not reached (36)</summary>

- `dim-layer`
- `note-field`
- `line-field`
- `done-button` (by action: `[data-a="ahsGot"]`)
- `later-button` (by action: `[data-a="ahsLater"]`)
- `clear-button` (by action: `[data-a="cashClear"]`)
- `clear-bar-button` (by action: `[data-a="clearBar"]`)
- `clear-filter-button` (by action: `[data-a="clearFilter"]`)
- `reset-filters-button` (by action: `[data-a="clearFilters"]`)
- `clear-search-button` (by action: `[data-a="clearQ"]`)
- `clear-button` (by action: `[data-a="clearRescue"]`)
- `confirm-button` (by action: `[data-a="delPurchaseYes"]`)
- `confirm-button` (by action: `[data-a="delObsYes"]`)
- `confirm-button` (by action: `[data-a="clearRescueYes"]`)
- `confirm-button` (by action: `[data-a="eraseYes"]`)
- `confirm-button` (by action: `[data-a="putBackYes"]`)
- `confirm-button` (by action: `[data-a="restoreYes"]`)
- `forget-button` (by action: `[data-a="forgetWord"]`)
- `refresh-link` (by action: `[data-a="goRefresh"]`)
- `show-more-row` (by action: `[data-a="moreRows"]`)
- `log-purchase-button` (by action: `[data-a="newPurchase"]`)
- `recovered-data-row` (by action: `[data-a="openRescue"]`)
- `price-dot` (by action: `[data-a="pickDot"]`)
- `put-back-row` (by action: `[data-a="putBack"]`)
- `earlier-period-button` (by action: `[data-a="rangeStep"][data-v="1"]`)
- `later-period-button` (by action: `[data-a="rangeStep"][data-v="-1"]`)
- `show-in-spending-button` (by action: `[data-a="searchToSpend"]`)
- `check-row` (by action: `[data-a="smartCheck"]`)
- `clear-button` (by action: `[data-a="smartClear"]`)
- `choice-chip` (by action: `[data-a="smartPick"]`)
- `save-button` (by action: `[data-a="smartSave"]`)
- `suggestion-row` (by action: `[data-a="smartSugg"]`)
- `edit-in-form-link` (by action: `[data-a="smartToForm"]`)
- `SK-001 › show-all-row`
- `SK-001 › recovered-banner`
- `SK-004 › show-all-button`

</details>
