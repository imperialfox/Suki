/* Suki · parts.settings.js (Q27)
   The parts kit's settings for Suki: one line per decision in Suki's register (the project note
   suki_parts_decisions.md), with its ID in a comment, so searching a decision's ID finds its line. Vocal Sessions' IDs
   (D01 …) where it's the same choice, S01 onwards for Suki's own. The kit itself (js/parts-kit.js, css/parts-kit.css)
   is a pinned copy of imperialfox/parts-kit 1.2.0, never edited here (tools/parts-kit/, MAINTAINING › Parts kit).
   The kit leads (D18): its springs, speed and Reduce Motion are Suki's. Where Suki differs from the kit, the difference
   gets its own line with a decision ID: a spring in springs: {…} below, a timing in css/app.css, or one element's
   style. tests/test_parts.py checks Parts.differences() against its list.
   Decisions that are stylesheet values or Suki's own code, not kit settings, are listed under own: so every ID has
   its line here: D17 (--r-sheet 46), D20 (--dur-reduced 100 ms, the kit's), D21 (the page behind follows the sheet),
   D22 (the push, Q24), S01 (--r-form 28), S02 (MOTION.land), S06 (--press-fade 0.35, Q29). */
Parts.settings({
  app: 'Suki',
  root: '#layer', // the kit's overlays go in #layer, above the app (the sheet host, ui.js)
  motion: 'kit', // D18 the kit runs the motion: its springs, speed and Reduce Motion
  springs: {}, // D18 Suki's own springs, one line each with its ID (none today)
  tabBar: { fold: false, searchGap: 8 }, // D01 the tab bar never folds (31 Oct 2026); its search circle isn't used
  segmented: { style: 'gallery' }, // D04 the gallery's knob: 350 ms spring, swells to glass, draggable (from Q28)
  row: { press: 'highlight' }, // D06 rows and card doors highlight while pressed, no shrink (from Q28)
  choices: 'actionSheet', // the kit's default; Suki has no choice lists
  confirm: 'alert', // D08 a yes or no question is an alert with Cancel and a red action; a delete then shows Undo
  sheet: {
    withStops: [], // Suki's sheets fit their content
    growsToFull: [],
    fullScreen: [],
    dragShrink: false, // D14 sheets follow the finger without shrinking
    glass: 'strong', // D15 sheets keep the strong glass
  },
  menu: { submenus: [] }, // Suki has no menus
  glass: { appear: [] },
  press: { glint: [] },
  timing: { hold: 700, lift: 200, toast: 3000 }, // D16 toasts stay 3 s, with or without Undo
  own: {
    sheetCorners: 46, // D17 iPhone sheets have the screen's own 46 corners (--r-sheet in css/app.css)
    topBar: { barTop: 'safe area' }, // D19 the top bar's buttons at Suki's own top area, not the kit's 54 pt (Q28)
    reducedFade: 100, // D20 Reduce Motion fades are the kit's 100 ms (--dur-reduced): nothing in Suki changes it
    pageBehind: 'follows', // D21 the page behind a sheet shrinks on the sheet spring and comes back on its leave
    push: { under: 0.33, dim: 0.1 }, // D22 a pushed page moves the one underneath 33% and dims it 10% (Q24, history.js)
    erase: 'sheet', // D23 waits for kit 1.3.0's three-button alert; on 1.2.0 Erase all data stays a sheet (S03)
    formSheet: 'centre', // S01 iPad and Mac sheets stay Suki's own, centred, with --r-form 28 corners
    land: 'MOTION.land', // S02 Suki's settle is called land, so --ease-settle means only the kit's spring
    stickyToast: 'own', // S04 "Couldn't save" warnings stay Suki's own sticky toast, with OK
    details: 'sheet', // S05 details open as sheets on iPhone and panes on iPad and Mac (Q24)
    pressFade: 0.35, // S06 text buttons, Cancel and word links fade to 35% while pressed (--press-fade, Q29)
  },
});
