/* Suki · register.js (2.29, Q25)
   The screen register: every screen, sheet and overlay the app can show, with a permanent ID (SK-001 onwards), its
   main parts' names, and the main journeys (flows, F-01 onwards). Plain data: nothing here runs. After Vocal Sessions'
   register (its Q36 and Q48).
   - render() and renderSheet() look the current screen up by its code key and stamp data-screen (and each part's
     data-name) on the page, so tests, the kit and notes read the ID straight off the screen (SCR in ui.js). See
     MAINTAINING › Screen IDs.
   - Code keys: 'tab:<U.tab>' (Help and Rate history are tabs in the code), 'sheet:<U.sheet>' (a confirmation is
     'sheet:confirm/<its action>', one per question), and 'overlay:<name>' for what's drawn outside render().
   - Numbered in the order the screens were first built (from the changelog). Append-only: a new screen takes the next
     number when it's built. Nothing is reused or renumbered; a screen that's removed stays, with status
     'Retired in <version>'. Renaming a screen or moving its code changes only its line here.
   - Part names follow Vocal Sessions' nine naming rules (MAINTAINING › Screen IDs › Naming rules). A note writes a part
     as 'SK-001 › save-button'. A screen's own parts win over shared, which wins over actions.
   - Public: screen names and code keys only, never personal data. */
const REGISTER = {
  prefix: 'SK',
  since: '2.29',
  // parts found another way that show in many places: the bars, a sheet's Close, the form fields
  shared: [
    { name: 'home-tab', sel: '#dock [data-a="tab"][data-v="home"], #barT [data-a="tab"][data-v="home"], #side [data-a="tab"][data-v="home"]' },
    { name: 'till-tab', sel: '[data-a="tab"][data-v="till"]' },
    { name: 'search-tab', sel: '[data-a="tab"][data-v="search"]' },
    { name: 'spending-tab', sel: '[data-a="tab"][data-v="spending"]' },
    { name: 'convert-tab', sel: '#dock [data-a="tab"][data-v="convert"], #barT [data-a="tab"][data-v="convert"], #side [data-a="tab"][data-v="convert"]' },
    { name: 'settings-tab', sel: '#side [data-a="tab"][data-v="settings"]' },
    { name: 'settings-button', sel: '#barR [data-a="tab"][data-v="settings"]' },
    { name: 'back-button', sel: '#barL [data-a="tab"]' },
    { name: 'close-button', sel: '.circ[data-a="close"], [data-a="tipX"]' },
    { name: 'cancel-button', sel: '.ghost[data-a="close"], [data-a="obsCancel"]' },
    { name: 'dim-layer', sel: '.scrim[data-a="close"]' },
    { name: 'grabber', sel: '.grab' },
    { name: 'save-button', sel: 'button[type="submit"], #homeSave' },
    { name: 'confirm-button', sel: '.cta.red[data-a$="Yes"]' },
    // fields, by what they hold (data-f is the form's field)
    { name: 'item-field', sel: '[data-f="item"], #smartItem' },
    { name: 'amount-field', sel: '[data-f="price"], #smartPrice' },
    { name: 'category-picker', sel: '[data-f="category"], [data-smart-cat]' },
    { name: 'date-field', sel: '[data-f="date"]' },
    { name: 'location-field', sel: '[data-f="location"]' },
    { name: 'venue-picker', sel: '[data-f="venue"]' },
    { name: 'payment-picker', sel: '[data-f="payment"]' },
    { name: 'notes-field', sel: '[data-f="notes"]' },
    { name: 'note-field', sel: '[data-f="note"]' },
    { name: 'search-field', sel: '#q' },
    { name: 'filter-field', sel: '#filter' },
    { name: 'line-field', sel: '#smartText' },
    { name: 'github-link', sel: 'a[href*="github.com"]' },
    { name: 'source-link', sel: 'a.link[href]' },
  ],
  // names by action: wherever the action shows, its button gets this name. One line per data-a (and data-v).
  actions: [
    { name: 'done-button', sel: '[data-a="ahsGot"]' },
    { name: 'later-button', sel: '[data-a="ahsLater"]' },
    { name: 'day-button', sel: '[data-a="calDay"]' },
    { name: 'period-button', sel: '[data-a="calFromSpend"]' },
    { name: 'earlier-month-button', sel: '[data-a="calStep"][data-v="-1"]' },
    { name: 'later-month-button', sel: '[data-a="calStep"][data-v="1"]' },
    { name: 'calendar-button', sel: '[data-a="calendar"]' },
    { name: 'note-button', sel: '[data-a="cashAdd"]' },
    { name: 'clear-button', sel: '[data-a="cashClear"]' },
    { name: 'exact-button', sel: '[data-a="cashExact"]' },
    { name: 'category-chip', sel: '[data-a="cat"]' },
    { name: 'clear-bar-button', sel: '[data-a="clearBar"]' },
    { name: 'clear-filter-button', sel: '[data-a="clearFilter"]' },
    { name: 'reset-filters-button', sel: '[data-a="clearFilters"]' },
    { name: 'clear-search-button', sel: '[data-a="clearQ"]' },
    { name: 'clear-button', sel: '[data-a="clearRescue"]' },
    { name: 'copy-button', sel: '[data-a="copyConv"]' },
    { name: 'export-csv-button', sel: '[data-a="csv"]' },
    { name: 'delete-button', sel: '[data-a="delObs"]' },
    { name: 'delete-button', sel: '[data-a="delPurchase"]' },
    { name: 'confirm-button', sel: '[data-a="delPurchaseYes"]' },
    { name: 'confirm-button', sel: '[data-a="delObsYes"]' },
    { name: 'confirm-button', sel: '[data-a="clearRescueYes"]' },
    { name: 'confirm-button', sel: '[data-a="eraseYes"]' },
    { name: 'confirm-button', sel: '[data-a="putBackYes"]' },
    { name: 'confirm-button', sel: '[data-a="restoreYes"]' },
    { name: 'edit-button', sel: '[data-a="editPurchase"]' },
    { name: 'erase-row', sel: '[data-a="erase"]' },
    { name: 'export-backup-row', sel: '[data-a="exportBackup"]' },
    { name: 'export-backup-button', sel: '[data-a="exportBackup"][data-v="push"]' },
    { name: 'forget-button', sel: '[data-a="forgetWord"]' },
    { name: 'rate-card', sel: '[data-a="goConvert"]' },
    { name: 'refresh-link', sel: '[data-a="goRefresh"]' },
    { name: 'search-link', sel: '[data-a="goSearch"]' },
    { name: 'smart-add-link', sel: '[data-a="goSmart"]' },
    { name: 'range-option', sel: '[data-a="hRange"]' },
    { name: 'show-all-button', sel: '[data-a="hShowAll"]' },
    { name: 'restore-backup-row', sel: '[data-a="importPick"]' },
    { name: 'locate-button', sel: '[data-a="locate"]' },
    { name: 'log-paid-button', sel: '[data-a="logItem"]' },
    { name: 'side-pill', sel: '[data-a="logSide"]' },
    { name: 'more-details-button', sel: '[data-a="more"]' },
    { name: 'show-more-row', sel: '[data-a="moreRows"]' },
    { name: 'log-purchase-button', sel: '[data-a="newPurchase"]' },
    { name: 'add-note-button', sel: '[data-a="obsForm"]' },
    { name: 'accessibility-row', sel: '[data-a="openAccess"]' },
    { name: 'home-screen-row', sel: '[data-a="openAhs"]' },
    { name: 'central-bank-rate-row', sel: '[data-a="openCbRate"]' },
    { name: 'help-row', sel: '[data-a="openHelp"]' },
    { name: 'rate-row', sel: '[data-a="openHistory"]' },
    { name: 'item-row', sel: '[data-a="openItem"]' },
    { name: 'learned-words-row', sel: '[data-a="openLearned"]' },
    { name: 'news-row', sel: '[data-a="openNews"]' },
    { name: 'price-notes-row', sel: '[data-a="openNotes"]' },
    { name: 'purchase-row', sel: '[data-a="openPurchase"]' },
    { name: 'recovered-data-row', sel: '[data-a="openRescue"]' },
    { name: 'siri-row', sel: '[data-a="openSiri"]' },
    { name: 'price-dot', sel: '[data-a="pickDot"]' },
    { name: 'put-back-row', sel: '[data-a="putBack"]' },
    { name: 'amount-chip', sel: '[data-a="quickConv"]' },
    { name: 'period-option', sel: '[data-a="range"]' },
    { name: 'earlier-period-button', sel: '[data-a="rangeStep"][data-v="1"]' },
    { name: 'later-period-button', sel: '[data-a="rangeStep"][data-v="-1"]' },
    { name: 'refresh-button', sel: '[data-a="refreshRate"]' },
    { name: 'save-backup-button', sel: '[data-a="saveBackup"]' },
    { name: 'save-copy-button', sel: '[data-a="saveRescue"]' },
    { name: 'category-chip', sel: '[data-a="scat"]' },
    { name: 'screen-ids-switch', sel: '[data-a="screenIds"]' },
    { name: 'show-in-spending-button', sel: '[data-a="searchToSpend"]' },
    { name: 'note-animation-option', sel: '[data-a="setNoteAnim"]' },
    { name: 'reduce-motion-option', sel: '[data-a="setReduce"]' },
    { name: 'welcome-row', sel: '[data-a="showWelcome"]' },
    { name: 'slow-motion-switch', sel: '[data-a="slowMotion"]' },
    { name: 'check-row', sel: '[data-a="smartCheck"]' },
    { name: 'clear-button', sel: '[data-a="smartClear"]' },
    { name: 'choice-chip', sel: '[data-a="smartPick"]' },
    { name: 'save-button', sel: '[data-a="smartSave"]' },
    { name: 'suggestion-row', sel: '[data-a="smartSugg"]' },
    { name: 'edit-in-form-link', sel: '[data-a="smartToForm"]' },
    { name: 'swap-button', sel: '[data-a="swapConv"]' },
    { name: 'log-bill-button', sel: '[data-a="tillLog"]' },
    { name: 'tips-switch', sel: '[data-a="tipsToggle"]' },
    { name: 'show-all-button', sel: '[data-a="toSpend"][data-v="all"]' },
    { name: 'today-card', sel: '[data-a="toSpend"][data-v="day"]' },
    { name: 'continue-button', sel: '[data-a="welcomeGo"]' },
  ],
  screens: [
    {
      id: 'SK-001', name: 'Home', area: 'Home', kind: 'Tab', key: 'tab:home', aliases: ['home', 'scrHome'],
      docs: 'README.md#tabs', status: 'Live',
      parts: [
        { name: 'total-card', sel: '.stat.door[data-v="all"]' },
        { name: 'show-all-row', sel: '.row.more[data-a="toSpend"]' },
        { name: 'backup-banner', sel: '.nudge[data-a="exportBackup"]' },
        { name: 'recovered-banner', sel: '.nudge[data-a="openRescue"]' },
        { name: 'log-card', sel: '#logwrap' },
      ],
    },
    {
      id: 'SK-002', name: 'Quick Till', area: 'Till', kind: 'Tab', key: 'tab:till', aliases: ['till', 'scrTill'],
      docs: 'MAINTAINING.md#quick-till-change-as-cash-q13', status: 'Live',
      parts: [
        { name: 'bill-field', sel: '#till-bill' },
        { name: 'cash-field', sel: '#till-cash' },
        { name: 'change-card', sel: '#tillOut' },
        { name: 'slot-line', sel: '#tillHdl' },
        { name: 'drawer', sel: '#tillDrawer' },
      ],
    },
    {
      id: 'SK-003', name: 'Search', area: 'Search', kind: 'Tab', key: 'tab:search', aliases: ['search', 'scrSearch'],
      docs: 'MAINTAINING.md#search-finds-your-records-q09', status: 'Live',
      parts: [],
    },
    {
      id: 'SK-004', name: 'Spending', area: 'Spending', kind: 'Tab', key: 'tab:spending', aliases: ['spending', 'scrSpending'],
      docs: 'MAINTAINING.md#spending-over-time-q03', status: 'Live',
      parts: [
        { name: 'add-button', sel: '#barR [data-a="newPurchase"]' },
        { name: 'category-row', sel: '.brk .row[data-a="cat"]' },
        { name: 'show-all-button', sel: '.tbtn[data-a="cat"]' },
        { name: 'chart', sel: '#chart' },
        { name: 'period-picker', sel: '#rangeSeg' },
      ],
    },
    {
      id: 'SK-005', name: 'Convert', area: 'Convert', kind: 'Tab', key: 'tab:convert', aliases: ['convert', 'scrConvert'],
      docs: 'README.md#tabs', status: 'Live',
      parts: [
        { name: 'peso-field', sel: '#conv-php' },
        { name: 'pound-field', sel: '#conv-gbp' },
      ],
    },
    {
      id: 'SK-006', name: 'Settings', area: 'Settings', kind: 'Tab', key: 'tab:settings', aliases: ['settings', 'scrSettings'],
      docs: 'MAINTAINING.md#door-rules-q24-228', status: 'Live',
      parts: [
        { name: 'last-backup-row', sel: '#lastBackupRow' },
        { name: 'saved-rate-row', sel: '.row[data-a="goConvert"]' },
      ],
    },
    {
      id: 'SK-007', name: 'Purchase', area: 'Spending', kind: 'Sheet', key: 'sheet:purchase', aliases: ['purchase', 'purchaseDetail'],
      docs: 'MAINTAINING.md#how-a-screen-is-drawn', status: 'Live',
      parts: [{ name: 'prices-row', sel: '[data-a="openItem"]' }],
    },
    {
      id: 'SK-008', name: 'Log or edit a purchase', area: 'Spending', kind: 'Sheet', key: 'sheet:edit', aliases: ['edit', 'Log sheet', 'Check purchase'],
      docs: 'MAINTAINING.md#how-a-screen-is-drawn', status: 'Live', parts: [],
    },
    {
      id: 'SK-009', name: 'Item', area: 'Search', kind: 'Sheet', key: 'sheet:item', aliases: ['item', 'itemDetail'],
      docs: 'MAINTAINING.md#calendar-tints-and-the-price-range-strip-q12', status: 'Live', parts: [],
    },
    {
      id: 'SK-010', name: 'Price notes', area: 'Search', kind: 'Sheet', key: 'sheet:notes', aliases: ['notes', 'observations'],
      docs: 'MAINTAINING.md#search-finds-your-records-q09', status: 'Live', parts: [],
    },
    {
      id: 'SK-011', name: 'Delete this purchase?', area: 'Spending', kind: 'Sheet', key: 'sheet:confirm/delPurchaseYes', aliases: ['confirm'],
      docs: 'MAINTAINING.md#door-rules-q24-228', status: 'Live', parts: [],
    },
    {
      id: 'SK-012', name: 'Delete this price note?', area: 'Search', kind: 'Sheet', key: 'sheet:confirm/delObsYes', aliases: [],
      docs: 'MAINTAINING.md#door-rules-q24-228', status: 'Live', parts: [],
    },
    {
      id: 'SK-013', name: 'Erase all data?', area: 'Settings', kind: 'Sheet', key: 'sheet:erase', aliases: ['erase'],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live', parts: [],
    },
    {
      id: 'SK-014', name: 'Export a backup', area: 'Settings', kind: 'Sheet', key: 'sheet:backup', aliases: ['backup'],
      docs: 'MAINTAINING.md#backups', status: 'Live', parts: [],
    },
    {
      id: 'SK-015', name: 'Restore this backup?', area: 'Settings', kind: 'Sheet', key: 'sheet:restore', aliases: ['restore'],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live', parts: [],
    },
    {
      id: 'SK-016', name: 'Toast', area: 'Everywhere', kind: 'Overlay', key: 'overlay:toast', aliases: ['toast'],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live',
      parts: [
        { name: 'undo-button', sel: '.toast:not(.sticky) button' },
        { name: 'ok-button', sel: '.toast.sticky button' },
      ],
    },
    {
      id: 'SK-017', name: 'Launch screen', area: 'Everywhere', kind: 'Overlay', key: 'overlay:launch', aliases: ['splash'],
      docs: 'MAINTAINING.md#files', status: 'Live', parts: [],
    },
    {
      id: 'SK-018', name: 'Calendar', area: 'Spending', kind: 'Sheet', key: 'sheet:calendar', aliases: ['calendar'],
      docs: 'MAINTAINING.md#calendar-tints-and-the-price-range-strip-q12', status: 'Live',
      parts: [{ name: 'log-day-row', sel: '.row.more[data-a="newPurchase"]' }],
    },
    {
      id: 'SK-019', name: 'Accessibility', area: 'Settings', kind: 'Sheet', key: 'sheet:access', aliases: ['access'],
      docs: 'MAINTAINING.md#screen-ids', status: 'Live',
      parts: [
        { name: 'reduce-motion-picker', sel: '#reduceSeg' },
        { name: 'note-animation-picker', sel: '#noteSeg' },
      ],
    },
    {
      id: 'SK-020', name: 'Recovered data', area: 'Settings', kind: 'Sheet', key: 'sheet:rescue', aliases: ['rescue'],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live', parts: [],
    },
    {
      id: 'SK-021', name: 'Put back what was here?', area: 'Settings', kind: 'Sheet', key: 'sheet:putback', aliases: ['putback'],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live', parts: [],
    },
    {
      id: 'SK-022', name: 'Clear recovered data?', area: 'Settings', kind: 'Sheet', key: 'sheet:confirm/clearRescueYes', aliases: [],
      docs: 'MAINTAINING.md#keeping-data-safe-q05', status: 'Live', parts: [],
    },
    {
      id: 'SK-023', name: 'Add to Home Screen', area: 'Settings', kind: 'Sheet', key: 'sheet:ahs', aliases: ['ahs'],
      docs: 'MAINTAINING.md#onboarding-q07', status: 'Live', parts: [],
    },
    {
      id: 'SK-024', name: 'Welcome', area: 'Home', kind: 'Sheet', key: 'sheet:welcome', aliases: ['welcome'],
      docs: 'MAINTAINING.md#onboarding-q07', status: 'Live', parts: [],
    },
    {
      id: 'SK-025', name: 'Help', area: 'Settings', kind: 'Screen', key: 'tab:help', aliases: ['help', 'scrHelp'],
      docs: 'MAINTAINING.md#onboarding-q07', status: 'Live', parts: [],
    },
    {
      id: 'SK-026', name: 'Tip', area: 'Everywhere', kind: 'Overlay', key: 'overlay:tip', aliases: ['tip'],
      docs: 'MAINTAINING.md#onboarding-q07', status: 'Live', parts: [],
    },
    {
      id: 'SK-027', name: 'Words Suki has learned', area: 'Settings', kind: 'Sheet', key: 'sheet:learned', aliases: ['learned'],
      docs: 'MAINTAINING.md#smart-add-q14', status: 'Live', parts: [],
    },
    {
      id: 'SK-028', name: 'Log by voice with Siri', area: 'Settings', kind: 'Sheet', key: 'sheet:siri', aliases: ['siri'],
      docs: 'MAINTAINING.md#the-siri-inbox-q15', status: 'Live', parts: [],
    },
    {
      id: 'SK-029', name: 'Rate history', area: 'Convert', kind: 'Screen', key: 'tab:history', aliases: ['history', 'scrHistory'],
      docs: 'MAINTAINING.md#rate-history-q23', status: 'Live',
      parts: [
        { name: 'range-picker', sel: '#hSeg' },
        { name: 'chart', sel: '#hchart' },
      ],
    },
    {
      id: 'SK-030', name: 'News note', area: 'Convert', kind: 'Sheet', key: 'sheet:news', aliases: ['news', 'Peso news', 'Pound news'],
      docs: 'MAINTAINING.md#rate-history-q23', status: 'Live',
      parts: [{ name: 'official-record-row', sel: 'a.row[href]' }],
    },
    {
      id: 'SK-031', name: 'Central bank rate', area: 'Convert', kind: 'Sheet', key: 'sheet:cbrate', aliases: ['cbrate'],
      docs: 'MAINTAINING.md#rate-history-q23', status: 'Live', parts: [],
    },
  ],
  // the main journeys: each step is a screen, with the part tapped (or typed in) to get to the next
  flows: [
    {
      id: 'F-01', name: 'Log a purchase on Home', status: 'Live',
      steps: [
        { screen: 'SK-001', part: 'item-field' },
        { screen: 'SK-001', part: 'amount-field' },
        { screen: 'SK-001', part: 'save-button' },
        { screen: 'SK-001', state: 'saved' },
      ],
    },
    {
      id: 'F-02', name: 'Pay at the Till and log the bill', status: 'Live',
      steps: [
        { screen: 'SK-002', part: 'bill-field' },
        { screen: 'SK-002', part: 'note-button' },
        { screen: 'SK-002', part: 'log-bill-button' },
        { screen: 'SK-008', part: 'save-button' },
        { screen: 'SK-002', state: 'logged' },
      ],
    },
    {
      id: 'F-03', name: 'Look up a price and add a note', status: 'Live',
      steps: [
        { screen: 'SK-003', part: 'search-field' },
        { screen: 'SK-003', part: 'item-row' },
        { screen: 'SK-009', part: 'add-note-button' },
        { screen: 'SK-009', part: 'save-button' },
        { screen: 'SK-009', state: 'note added' },
      ],
    },
    {
      id: 'F-04', name: 'Check Spending for a day', status: 'Live',
      steps: [
        { screen: 'SK-004', part: 'period-button' },
        { screen: 'SK-018', part: 'day-button' },
        { screen: 'SK-018', part: 'purchase-row', state: 'day picked' },
        { screen: 'SK-007' },
      ],
    },
  ],
};
