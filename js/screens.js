/* Suki · screens.js
   The five tabs (Home, Till, Search, Spending, Convert), Settings, and the pieces they share:
   the purchase form, a purchase's details and a catalogue item's details. Each of those details is drawn once
   and shown wherever it's reached from: a sheet on iPhone, the pane beside the list on iPad and Mac.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Shared pieces ===== */
const hdr = (t, right) => '<div class="hdr"><h2>' + t + '</h2>' + (right || '') + '</div>';
const opts = (list, v, blank) =>
  (blank ? '<option value="">' + blank + '</option>' : '') +
  list.map((o) => '<option' + (o === v ? ' selected' : '') + '>' + esc(o) + '</option>').join('');
const field = (id, label, input) => '<div class="fld"><label for="' + id + '">' + label + '</label>' + input + '</div>';
const inp = (form, f, v, extra) =>
  '<input class="inp" id="' + form + '-' + f + '" data-form="' + form + '" data-f="' + f + '" value="' + esc(v == null ? '' : v) + '" ' + (extra || '') + '>';
const sel = (form, f, list, v, blank) =>
  '<select class="inp" id="' + form + '-' + f + '" data-form="' + form + '" data-f="' + f + '">' + opts(list, v, blank) + '</select>';
const money$ = (form, f, v, ph) =>
  inp(form, f, v, 'type="text" inputmode="decimal" autocomplete="off" placeholder="' + (ph || '0.00') + '"');

// the purchase form: Home's quick log and the add/edit sheet
function purchaseForm(form, v, showMore) {
  const more =
    field(form + '-date', 'Date', inp(form, 'date', v.date || localISO(), 'type="date" max="' + localISO(new Date(Date.now() + 864e5 * 366)) + '"')) +
    '<div class="two">' +
    field(form + '-location', 'Location', inp(form, 'location', v.location, 'placeholder="e.g. Cebu City" autocomplete="off"')) +
    field(form + '-venue', 'Where bought', sel(form, 'venue', VENUES, v.venue, 'Not specified')) +
    '</div>' +
    field(form + '-payment', 'Paid with', sel(form, 'payment', PAYMENTS, v.payment || 'Cash')) +
    field(
      form + '-notes',
      'Notes',
      '<textarea class="inp" id="' + form + '-notes" data-form="' + form + '" data-f="notes" rows="2" placeholder="Anything to remember">' + esc(v.notes || '') + '</textarea>'
    );
  return (
    field(form + '-item', 'What did you buy?', inp(form, 'item', v.item, 'placeholder="e.g. Lunch, groceries, jeepney fare" autocomplete="off" enterkeyhint="next"')) +
    '<div class="two">' +
    field(form + '-price', 'Amount · ₱', money$(form, 'price', v.price)) +
    field(form + '-category', 'Category', sel(form, 'category', CATS, v.category || 'Food & drink')) +
    '</div>' +
    (showMore === undefined
      ? more
      : '<button type="button" class="disclose" data-a="more" aria-expanded="' + !!showMore + '">' + (showMore ? 'Fewer details' : 'More details') + '<span aria-hidden="true">' + (showMore ? '−' : '+') + '</span></button>' +
        (showMore ? '<div class="more">' + more + '</div>' : ''))
  );
}

function purchaseRow(p, opts) {
  opts = opts || {};
  const meta = opts.meta || [relDay(p.date), p.location].filter(Boolean).join(' · ');
  const row =
    '<button class="row' + (U.sel === p.id && split() && U.tab === 'spending' ? ' sel' : '') + '" data-a="openPurchase" data-k="' + esc(p.id) + '">' +
    tile(p.category) +
    '<span class="lbl"><b>' + esc(p.item) + '</b><small>' + esc(meta || p.category) + '</small></span>' +
    '<span class="amt">' + cash(p.price) + '</span></button>';
  return opts.swipe ? sw(row, 'delPurchase', p.id) : row;
}
// swipe-to-delete wrapper (from Vocal Sessions): slide the row left to show Delete, which asks first
const sw = (inner, action, k) =>
  '<div class="sw" data-own-gesture="1"><button class="swdel" data-a="' + action + '" data-k="' + esc(k) + '" tabindex="-1">Delete</button><div class="fg">' + inner + '</div></div>';

function purchaseDetail(p, inPane) {
  if (!p) return '';
  const rows = [
    ['Date', longDate(p.date)],
    ['Category', p.category],
    p.location && ['Location', p.location],
    p.venue && ['Where bought', p.venue],
    p.payment && ['Paid with', p.payment],
    p.rateAtPurchase && ['In pounds then', '≈ ' + gbp(p.price / p.rateAtPurchase)],
  ].filter(Boolean);
  return (
    '<div class="dhead">' + tile(p.category, true) + '<div class="dmain"><div class="dprice">' + cash(p.price) + '</div><h3>' + esc(p.item) + '</h3></div></div>' +
    '<div class="grp">' + rows.map((r) => '<div class="row kv"><span class="k">' + r[0] + '</span><span class="v">' + esc(r[1]) + '</span></div>').join('') + '</div>' +
    (p.notes ? hdr('Notes') + '<div class="card prose">' + esc(p.notes) + '</div>' : '') +
    (inPane
      ? '<div class="actions"><button class="btn glass" data-a="editPurchase" data-k="' + esc(p.id) + '">' + ICON.pencil + 'Edit</button><button class="btn glass red" data-a="delPurchase" data-k="' + esc(p.id) + '">' + ICON.bin + 'Delete</button></div>'
      : '<button class="ghost red" data-a="delPurchase" data-k="' + esc(p.id) + '">Delete purchase</button>')
  );
}

function officialCard(id) {
  const rows = refsFor(id),
    R = REFS();
  if (!rows.length)
    return '<div class="card quiet">There’s no official price for this item in the current snapshot. Your own price notes are below.</div>';
  return (
    '<section class="card official" aria-label="Official price reference"><div class="ofhead"><div><div class="eyebrow">Official price · ' + esc(R.area) + '</div><b>' + esc(R.period) + '</b></div><span class="badge">Weekly average</span></div>' +
    rows.map((r) => '<div class="ofrow"><span><b>' + esc(r.item) + '</b><small>' + esc(r.unit) + '</small></span><span class="amt">' + cash(r.price) + (inGbp(r.price) ? '<small>' + esc(inGbp(r.price)) + '</small>' : '') + '</span></div>').join('') +
    '<p class="small">' + esc(R.source) + ', ' + R.marketCount + ' markets. Prices are for the product described and can differ outside ' + esc(R.area.replace(' markets', '')) + '.</p>' +
    '<a class="link" href="' + esc(R.sourceUrl) + '" target="_blank" rel="noopener">View the DA report ' + ICON.out + '</a></section>'
  );
}
function itemDetail(id, inPane) {
  const it = itemById(id);
  if (!it) return '';
  const obs = D.observations.filter((o) => o.itemId === id).sort((a, b) => b.date.localeCompare(a.date));
  const open = U.obsFor === id;
  const f = F.obs;
  return (
    '<div class="dhead">' + tile(it.group, true) + '<div class="dmain"><h3>' + esc(it.name) + '</h3><div class="sub">' + esc(it.english) + ' · ' + esc(it.unit) + '</div></div></div>' +
    officialCard(id) +
    hdr('Your price notes', open ? '' : '<button class="tbtn" data-a="obsForm" data-k="' + esc(id) + '">Add</button>') +
    (open
      ? '<form class="card form" data-form="obs" data-k="' + esc(id) + '" novalidate>' +
        '<div class="two">' + field('obs-price', 'Price you saw · ₱', money$('obs', 'price', f.price)) + field('obs-date', 'Date', inp('obs', 'date', f.date || localISO(), 'type="date"')) + '</div>' +
        '<div class="two">' + field('obs-location', 'Location', inp('obs', 'location', f.location, 'placeholder="e.g. Cebu City" autocomplete="off"')) + field('obs-venue', 'Where', sel('obs', 'venue', VENUES, f.venue, 'Not specified')) + '</div>' +
        field('obs-note', 'Size or note', inp('obs', 'note', f.note, 'placeholder="e.g. 500 ml bottle, large serving" autocomplete="off"')) +
        '<p class="err" id="obs-err" role="alert"></p>' +
        '<div class="actions"><button type="button" class="btn glass" data-a="obsCancel">Cancel</button><button type="submit" class="btn glass tinted">Save note</button></div></form>'
      : '') +
    (obs.length
      ? '<div class="grp">' +
        obs
          .map(
            (o) =>
              '<div class="row"><span class="lbl"><b>' + cash(o.price) + (inGbp(o.price) ? ' <span class="gb">' + esc(inGbp(o.price)) + '</span>' : '') + '</b><small>' + esc([relDay(o.date), o.location, o.venue, o.note].filter(Boolean).join(' · ')) + '</small></span>' +
              '<button class="ibtn" data-a="delObs" data-k="' + esc(o.id) + '" aria-label="Delete this price note">' + ICON.bin + '</button></div>'
          )
          .join('') +
        '</div>'
      : open
        ? ''
        : '<div class="grp"><div class="empty">No notes yet. Tap Add when you see a price.</div></div>') +
    '<p class="foot">Your notes are your own, not verified market averages.</p>'
  );
}

/* ===== Home ===== */
function scrHome() {
  const total = sum(D.purchases),
    today = sum(D.purchases.filter((p) => p.date === localISO())),
    recent = D.purchases.slice().sort(byNewest).slice(0, 4);
  const dash =
    '<button class="card sumcard" data-a="tab" data-v="spending" aria-label="Total spent ' + cash(total) + '. Open Spending">' +
    '<span class="stat"><span class="big">' + cash(total) + '</span><span class="cap">Total spent' + (D.rate && total ? ' · ≈ ' + gbp(total / D.rate.value) : '') + '</span></span>' +
    '<span class="stat r"><span class="mid">' + cash(today) + '</span><span class="cap">Today</span></span>' + ICON.chev + '</button>' +
    (backupDue()
      ? '<button class="nudge" data-a="exportBackup">' + ICON.upload + '<span>' + (lastBackup() ? 'Your last backup was ' + relDay(localISO(lastBackup())).toLowerCase() + '. Save a fresh copy.' : 'Back up your records so they’re safe if your browser data is cleared.') + '</span></button>'
      : '');
  const log =
    hdr('Log a purchase') +
    '<form class="card form" data-form="home" novalidate>' + purchaseForm('home', F.home, U.more) +
    '<p class="err" id="home-err" role="alert"></p><button type="submit" class="cta ink">Save purchase</button></form>';
  const rec =
    hdr('Recent', D.purchases.length ? '<button class="tbtn" data-a="tab" data-v="spending">Show all</button>' : '') +
    (recent.length
      ? '<div class="grp tiled">' + recent.map((p) => purchaseRow(p)).join('') +
        (D.purchases.length > recent.length ? '<button class="row more" data-a="tab" data-v="spending"><span class="lbl">Show all ' + D.purchases.length + ' purchases</span>' + ICON.chev + '</button>' : '') + '</div>'
      : '<div class="grp"><div class="empty">No purchases yet. Log your first one ' + (split() ? 'here.' : 'above.') + '</div></div>');
  return (
    '<div class="dateline">' + longDate(localISO()) + '</div><h1>Home</h1>' +
    (split() || MQ.land.matches
      ? '<div class="dash"><div>' + dash + log + '</div><div>' + rec + '</div></div>'
      : dash + log + rec)
  );
}
const byNewest = (a, b) => b.date.localeCompare(a.date) || D.purchases.indexOf(a) - D.purchases.indexOf(b);

/* ===== Quick Till ===== */
function scrTill() {
  return (
    '<h1>Quick Till</h1><p class="note">Check your change before you walk away. Works offline.</p>' +
    '<div class="card form">' +
    field('till-bill', 'Total bill · ₱', '<input class="inp big" id="till-bill" data-till="bill" type="text" inputmode="decimal" autocomplete="off" placeholder="e.g. 789.50" value="' + esc(U.till.bill) + '">') +
    field('till-cash', 'Cash handed over · ₱', '<input class="inp big" id="till-cash" data-till="cash" type="text" inputmode="decimal" autocomplete="off" placeholder="e.g. 1,000" value="' + esc(U.till.cash) + '">') +
    '<div class="chips denoms" role="group" aria-label="Common amounts"><button class="chip" data-a="cashExact">Exact</button>' +
    [100, 200, 500, 1000].map((n) => '<button class="chip" data-a="cashAdd" data-v="' + n + '">+' + cash(n).replace('.00', '') + '</button>').join('') +
    '<button class="chip" data-a="cashClear" aria-label="Clear cash">Clear</button></div>' +
    '<div class="tillout" id="tillOut" aria-live="polite">' + tillOut() + '</div>' +
    '<button class="cta ink" id="tillLog" data-a="tillLog"' + (tillState().bill > 0 ? '' : ' disabled') + '>Log this bill</button></div>' +
    '<p class="foot">The amount buttons add to the cash, so ₱500 + ₱100 + ₱100 makes ₱700.</p>'
  );
}
function tillState() {
  const bill = amount(U.till.bill),
    paid = amount(U.till.cash);
  return { bill: bill > 0 ? bill : 0, paid: paid >= 0 ? paid : null, ok: bill > 0 && paid !== null && paid >= 0 };
}
function tillOut() {
  const t = tillState();
  if (!t.ok) return '<div class="eyebrow">Change due</div><div class="metric dim">—</div><p class="small">Enter the bill and the cash you handed over.</p>';
  const diff = Math.round((t.paid - t.bill) * 100) / 100;
  if (diff > 0) return '<div class="eyebrow">Change due</div><div class="metric">' + cash(diff) + '</div><p class="small">' + cash(t.paid) + ' handed over for a ' + cash(t.bill) + ' bill.</p>';
  if (diff < 0) return '<div class="eyebrow red">Still to pay</div><div class="metric red">' + cash(-diff) + '</div><p class="small">The cash is short of the ' + cash(t.bill) + ' bill.</p>';
  return '<div class="eyebrow">Exact payment</div><div class="metric">' + cash(0) + '</div><p class="small">No change needed.</p>';
}

/* ===== Search ===== */
const EXAMPLES = ['sinigan baboy', '1 kilo bigas', 'tubig bote', 'kwek kwek', 'baboy adobo'];
function itemRow(it) {
  const r = refFrom(it.id);
  return (
    '<button class="row' + (split() && U.item === it.id ? ' sel' : '') + '" data-a="openItem" data-k="' + esc(it.id) + '">' + tile(it.group) +
    '<span class="lbl"><b>' + esc(it.name) + '</b><small>' + esc(it.english) + (r ? '' : ' · ' + esc(it.unit)) + '</small></span>' +
    (r ? '<span class="amt">' + (r.many ? '<small class="from">from</small>' : '') + cash(r.price) + '<small>' + esc([inGbp(r.price), r.unit].filter(Boolean).join(' · ')) + '</small></span>' : '') +
    ICON.chev + '</button>'
  );
}
function searchResults() {
  const q = U.q.trim();
  if (q) {
    const hits = searchItems(q);
    return (
      hdr('Matches', '<span class="hint">' + plural(hits.length, 'result') + '</span>') +
      (hits.length
        ? '<div class="grp tiled">' + hits.map(itemRow).join('') + '</div>'
        : '<div class="grp"><div class="empty"><b>No clear match</b><br>Try fewer words, another spelling or the English name.</div></div>')
    );
  }
  const R = REFS();
  return (
    hdr('Official prices · ' + esc(R.area || 'NCR')) +
    '<div class="grp tiled">' + OFFICIAL_IDS().map((id) => itemRow(itemById(id))).join('') + '</div>' +
    '<p class="foot">Weekly averages from ' + esc(R.source || 'the Department of Agriculture') + ', ' + esc(R.period || '') + '.</p>' +
    hdr('Dishes and street food') +
    '<div class="grp tiled">' + CATALOG.filter((i) => kindOf(i.group) === 'food').slice(0, 8).map(itemRow).join('') + '</div>'
  );
}
function scrSearch() {
  const list =
    '<label class="searchbox">' + ICON.search +
    '<input id="q" type="search" placeholder="Try “sinigan baboy” or “1 kilo bigas”" aria-label="Search the catalogue" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" value="' + esc(U.q) + '">' +
    '<button type="button" class="clr" data-a="clearQ" aria-label="Clear search"' + (U.q ? '' : ' hidden') + '>' + ICON.x + '</button>' + '</label>' +
    '<div class="chips scroller" id="examples" data-own-gesture="1" aria-label="Example searches"' + (U.q ? ' hidden' : '') + '>' +
    EXAMPLES.map((e) => '<button class="chip" data-a="example" data-v="' + esc(e) + '">' + esc(e) + '</button>').join('') + '</div>' +
    '<div id="results">' + searchResults() + '</div>';
  const head = '<h1>Search</h1>';
  if (!split()) return head + list;
  return (
    '<div class="split"><div class="sl">' + head + list + '</div><aside class="pane" aria-label="Item details">' +
    (U.item && itemById(U.item) ? itemDetail(U.item, true) : '<div class="pane-empty">' + ICON.search + '<p>Pick an item to see its prices and your notes.</p></div>') +
    '</aside></div>'
  );
}

/* ===== Spending ===== */
function spendingList() {
  const q = norm(U.filter);
  return D.purchases
    .filter((p) => U.cat === 'all' || p.category === U.cat)
    .filter((p) => !q || norm([p.item, p.location, p.venue, p.category, p.payment, p.notes].join(' ')).includes(q))
    .sort(byNewest);
}
function spendSummary(list) {
  const total = sum(list),
    filtered = U.cat !== 'all' || U.filter.trim();
  return (
    '<span class="stat"><span class="big">' + cash(total) + '</span><span class="cap">' + (filtered ? (U.cat !== 'all' ? esc(U.cat) : 'Matching') : 'Total spent') + (D.rate && total ? ' · ≈ ' + gbp(total / D.rate.value) : '') + '</span></span>' +
    '<span class="stat r"><span class="mid">' + list.length + '</span><span class="cap">' + (list.length === 1 ? 'Purchase' : 'Purchases') + '</span></span>'
  );
}
function spendRows(list) {
  if (!D.purchases.length) return '<div class="grp"><div class="empty">Purchases you log on Home appear here.</div></div>';
  if (!list.length) return '<div class="grp"><div class="empty">No purchases match.' + (U.cat !== 'all' || U.filter ? ' <button class="tbtn inline" data-a="clearFilters">Show all</button>' : '') + '</div></div>';
  const days = [];
  list.forEach((p) => {
    const last = days[days.length - 1];
    if (last && last.date === p.date) last.items.push(p);
    else days.push({ date: p.date, items: [p] });
  });
  return days
    .map(
      (d) =>
        hdr(dayHeading(d.date), '<span class="hint">' + cash(sum(d.items)) + '</span>') +
        '<div class="grp tiled">' + d.items.map((p) => purchaseRow(p, { swipe: true, meta: [p.location, p.venue, p.payment].filter(Boolean).join(' · ') })).join('') + '</div>'
    )
    .join('');
}
function scrSpending() {
  const list = spendingList();
  const counts = {};
  D.purchases.forEach((p) => (counts[p.category] = (counts[p.category] || 0) + 1));
  const chips =
    D.purchases.length
      ? '<div class="chips scroller" data-own-gesture="1" role="group" aria-label="Filter by category">' +
        [['all', 'All', D.purchases.length]]
          .concat(CATS.filter((c) => counts[c]).map((c) => [c, c, counts[c]]))
          .map((c) => '<button class="chip' + (U.cat === c[0] ? ' on' : '') + '" data-a="cat" data-v="' + esc(c[0]) + '" aria-pressed="' + (U.cat === c[0]) + '">' + (c[0] === 'all' ? '' : tileDot(c[0])) + esc(c[1]) + '<span class="n">' + c[2] + '</span></button>')
          .join('') + '</div>'
      : '';
  const main =
    '<h1>Spending</h1>' +
    '<div class="card sumcard static" id="spendSum">' + spendSummary(list) + '</div>' + chips +
    (D.purchases.length
      ? '<label class="searchbox">' + ICON.search + '<input id="filter" type="search" placeholder="Filter by item, place or note" aria-label="Filter purchases" autocomplete="off" value="' + esc(U.filter) + '">' +
        '<button type="button" class="clr" data-a="clearFilter" aria-label="Clear filter"' + (U.filter ? '' : ' hidden') + '>' + ICON.x + '</button>' + '</label>'
      : '') +
    '<div id="spendList">' + spendRows(list) + '</div>' +
    (D.purchases.length ? '<button class="btn glass wide csv" data-a="csv">' + ICON.upload + 'Export as CSV</button><p class="foot">Exports the purchases shown above, for Numbers or Excel.</p>' : '');
  if (!split()) return main;
  const p = D.purchases.find((x) => x.id === U.sel);
  return (
    '<div class="split"><div class="sl">' + main + '</div><aside class="pane" aria-label="Purchase details">' +
    (p ? purchaseDetail(p, true) : '<div class="pane-empty">' + ICON.spending + '<p>Pick a purchase to see its details.</p></div>') +
    '</aside></div>'
  );
}
const tileDot = (cat) => '<i class="dot k-' + kindOf(cat) + '" aria-hidden="true"></i>';

/* ===== Convert ===== */
const QUICK_GBP = [1, 5, 10, 20, 50, 100];
function rateLine() {
  const r = D.rate;
  if (!r) return navigator.onLine ? 'No rate saved yet. Tap Refresh to load one.' : 'You’re offline and no rate is saved yet. Connect once to load one.';
  const when = whenAgo(new Date(r.cachedAt));
  return 'Reference date ' + shortDate(r.date) + ' · updated ' + when.charAt(0).toLowerCase() + when.slice(1) + (navigator.onLine ? '' : ' · offline, using the saved rate');
}
function scrConvert() {
  const r = D.rate;
  return (
    '<h1>Convert</h1><p class="note">A reference rate only. Your card or Revolut may use a different rate or add fees.</p>' +
    '<div class="card form conv">' +
    field('conv-gbp', 'British pounds', '<div class="cur"><span aria-hidden="true">£</span><input class="inp big" id="conv-gbp" data-conv="gbp" type="text" inputmode="decimal" autocomplete="off" placeholder="0.00" value="' + esc(U.conv.gbp) + '"' + (r ? '' : ' disabled') + '></div>') +
    '<div class="swapline" aria-hidden="true">' + ICON.swap + '</div>' +
    field('conv-php', 'Philippine pesos', '<div class="cur"><span aria-hidden="true">₱</span><input class="inp big" id="conv-php" data-conv="php" type="text" inputmode="decimal" autocomplete="off" placeholder="0.00" value="' + esc(U.conv.php) + '"' + (r ? '' : ' disabled') + '></div>') +
    '</div>' +
    '<div class="raterow"><div><b id="rateBadge">' + (r ? '£1 = ' + cash(r.value) : 'No rate yet') + '</b><small id="rateLine">' + esc(rateLine()) + '</small></div>' +
    '<button class="btn glass" id="refreshRate" data-a="refreshRate">' + ICON.refresh + 'Refresh</button></div>' +
    (r
      ? '<button class="btn glass wide" data-a="copyConv">' + ICON.copy + 'Copy conversion</button>' +
        hdr('Handy amounts') +
        '<div class="grp quick">' + QUICK_GBP.map((g) => '<button class="row" data-a="quickGbp" data-v="' + g + '"><span class="lbl">' + gbp(g).replace('.00', '') + '</span><span class="amt">' + cash(g * r.value) + '</span></button>').join('') + '</div>'
      : '')
  );
}

/* ===== Settings ===== */
let SW_STATE = 'Checking…',
  STORAGE_USED = 'Checking…';
function scrSettings() {
  const lb = lastBackup(),
    R = REFS(),
    overdue = lb && Date.now() - lb > 14 * 864e5;
  const row = (icon, colour, title, value, a, extra) =>
    (a ? '<button class="row" data-a="' + a + '"' + (extra || '') + '>' : '<div class="row">') + stile(icon, colour) +
    '<span class="lbl"><b>' + title + '</b>' + (value ? '<small' + (value.cls ? ' class="' + value.cls + '"' : '') + '>' + (value.t || value) + '</small>' : '') + '</span>' +
    (a ? ICON.chev + '</button>' : '</div>');
  return (
    '<h1>Settings</h1><p class="note">Your records stay on this device. No account, no cloud.</p>' +
    hdr('Backup') +
    '<div class="grp tiled set">' +
    row('upload', '#007aff', 'Export a backup', 'Purchases, price notes and the saved rate', 'exportBackup') +
    row('download', '#34c759', 'Restore a backup', 'You’ll see what’s in it before anything changes', 'importPick') +
    row('clock', overdue || !lb ? '#ff9500' : '#8e8e93', 'Last backed up', { t: lb ? whenAgo(lb) + (overdue ? ' · over two weeks ago' : '') : 'Not backed up yet', cls: overdue ? 'red' : '' }) +
    '</div><p class="foot">iOS can clear a website’s data if it isn’t opened for a few weeks, so keep a recent backup in Files.</p>' +
    hdr('Your data') +
    '<div class="grp tiled set">' +
    row('tag', '#ff9f0a', 'Price notes', plural(D.observations.length, 'note'), 'openNotes') +
    row('disk', '#8e8e93', 'Storage used', '<span id="storageUsed">' + esc(STORAGE_USED) + '</span>') +
    '<button class="row danger" data-a="erase">' + stile('erase', '#ff3b30') + '<span class="lbl"><b>Erase all data</b><small>Purchases, price notes and the saved rate</small></span></button>' +
    '</div>' +
    hdr('About') +
    '<div class="grp tiled set">' +
    row('wifi', '#30b0c7', 'Works offline', '<span id="swStatus">' + esc(SW_STATE) + '</span>') +
    row('peso', '#5856d6', 'Saved exchange rate', D.rate ? '£1 = ' + D.rate.value.toFixed(2) + ' PHP · ' + shortDate(D.rate.date) : 'Not loaded yet') +
    row('book', '#34c759', 'Official prices', esc((R.source || '') + ' · ' + (R.area || '') + ' · ' + (R.period || ''))) +
    row('phone', '#007aff', 'Add to your Home Screen', 'In Safari: Share › Add to Home Screen') +
    '<a class="row" href="https://github.com/imperialfox/Suki" target="_blank" rel="noopener">' + stile('code', '#1c1c1e') + '<span class="lbl"><b>View on GitHub</b></span>' + ICON.out + '</a>' +
    '</div>' +
    '<p class="ver">Suki ' + APP_VERSION + ' · ' + RELEASE_DATE + '</p>'
  );
}
