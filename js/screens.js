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
    '<button class="row' + (U.sel === p.id && split() && U.tab === 'spending' ? ' sel' : '') + '" data-a="openPurchase" data-k="' + esc(p.id) + '"' + (opts.push ? ' data-v="push"' : '') + '>' +
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
  if (!rows.length) return '';
  return (
    '<section class="card official" aria-label="Official price reference"><div class="ofhead"><div><div class="eyebrow">Official price · ' + esc(R.area) + '</div><b>' + esc(R.period) + '</b></div><span class="badge">Weekly average</span></div>' +
    rows.map((r) => '<div class="ofrow"><span><b>' + esc(r.item) + '</b><small>' + esc(r.unit) + '</small></span><span class="amt">' + cash(r.price) + (inGbp(r.price) ? '<small>' + esc(inGbp(r.price)) + '</small>' : '') + '</span></div>').join('') +
    '<p class="small">' + esc(R.source) + ', ' + R.marketCount + ' markets. Prices are for the product described and can differ outside ' + esc(R.area.replace(' markets', '')) + '.</p>' +
    '<a class="link" href="' + esc(R.sourceUrl) + '" target="_blank" rel="noopener">View the DA report ' + ICON.out + '</a></section>'
  );
}
// "₱14" or "₱54.50–57": whole pesos lose their .00
const peso = (n) => cash(n).replace(/\.00$/, '');
const pesoRange = (lo, hi) => (lo === hi ? peso(lo) : peso(lo) + '–' + peso(hi).replace('₱', ''));
const gbpRange = (lo, hi) => {
  const a = inGbp(lo),
    b = inGbp(hi);
  return !a ? '' : lo === hi ? a : a + '–' + b.replace('≈ ', '').replace('£', '');
};
const KIND_LABEL = { fare: 'Set fare', srp: 'Suggested retail price', shop: 'Supermarket price', menu: 'Menu price', listed: 'Published price', guide: 'Rough guide' };
const dateOf = (d) => (/^\d{4}-\d{2}-\d{2}$/.test(d) ? shortDate(d) : /^\d{4}-\d{2}$/.test(d) ? monthName(d + '-01', true) : '');
// typical prices with where each came from: one row per price, the sources listed once underneath (Q02)
function typicalCard(id) {
  const rows = typicalFor(id);
  if (!rows.length) return '';
  const srcs = [],
    areas = [...new Set(rows.map((r) => r.area))],
    one = areas.length === 1;
  rows.forEach((r) => !srcs.some((s) => s.url === r.url || (s.source === r.source && s.date === r.date)) && srcs.push(r));
  return (
    '<section class="card official typical" aria-label="Typical prices"><div class="ofhead"><div><div class="eyebrow">Typical price' + (rows.length > 1 ? 's' : '') + '</div><b>' + esc(one ? areas[0] : 'Several places') + '</b></div></div>' +
    rows
      .map(
        (r) =>
          '<div class="ofrow"><span><b>' + esc(r.label) + '</b><small>' + esc(r.unit) + '</small><small class="kind k-' + r.kind + '">' + KIND_LABEL[r.kind] + (!one && r.area ? ' · ' + esc(r.area) : '') + '</small>' +
          (r.note ? '<small class="tnote">' + esc(r.note) + '</small>' : '') + '</span>' +
          '<span class="amt">' + pesoRange(r.low, r.high) + (gbpRange(r.low, r.high) ? '<small>' + esc(gbpRange(r.low, r.high)) + '</small>' : '') + '</span></div>'
      )
      .join('') +
    '<p class="small">Sources, checked ' + shortDate(window.sukiTypical.checked) + ':</p>' +
    srcs.map((s) => '<a class="link src" href="' + esc(s.url) + '" target="_blank" rel="noopener"><span>' + esc(s.source) + (dateOf(s.date) ? ', ' + dateOf(s.date) : '') + '</span>' + ICON.out + '</a>').join('') +
    '</section>'
  );
}
// what you paid for this item, from your own log
const paidFor = (id) => D.purchases.filter((p) => itemFor(p.item) === id).sort(byNewest);
function itemDetail(id, inPane) {
  const it = itemById(id);
  if (!it) return '';
  const obs = D.observations.filter((o) => o.itemId === id).sort((a, b) => b.date.localeCompare(a.date));
  const open = U.obsFor === id;
  const f = F.obs;
  const paid = paidFor(id);
  const prices = typicalCard(id) + officialCard(id);
  return (
    '<div class="dhead">' + tile(it.group, true, it.id) + '<div class="dmain"><h3>' + esc(it.name) + '</h3><div class="sub">' + esc(it.english !== it.name ? it.english + ' · ' + it.unit : it.unit) + '</div></div></div>' +
    (prices || '<div class="card quiet">No published price for this yet. Add what you see below, and it’ll show here next time.</div>') +
    (paid.length
      ? hdr('You paid', '<span class="hint">' + plural(paid.length, 'time') + '</span>') +
        '<div class="grp">' + paid.slice(0, 5).map((p) => '<button class="row" data-a="openPurchase" data-k="' + esc(p.id) + '" data-v="push"><span class="lbl"><b>' + cash(p.price) + (inGbp(p.price) ? ' <span class="gb">' + esc(inGbp(p.price)) + '</span>' : '') + '</b><small>' + esc([relDay(p.date), p.location].filter(Boolean).join(' · ')) + '</small></span>' + ICON.chev + '</button>').join('') + '</div>'
      : '') +
    '<button class="btn glass wide logit" data-a="logItem" data-k="' + esc(id) + '">' + ICON.plus + 'Log what you paid</button>' +
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
    // data safety first: storage that wouldn't open, or records that couldn't be read (Q05)
    (STORE_WARN
      ? '<button class="nudge warn" data-a="exportBackup">' + ICON.upload + '<span>Suki couldn’t open its main storage on this device, so it’s saving to a smaller spot. Back up soon.</span></button>'
      : '') +
    (rescueDue()
      ? '<button class="nudge warn" data-a="openRescue">' + ICON.tag + '<span>Some saved data couldn’t be read. A copy is kept safe; tap to save it.</span></button>'
      : '') +
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
    // the date and the title both open the calendar (Apple Books style)
    '<button class="dateline hometitle" data-a="calendar" tabindex="-1" aria-hidden="true">' + longDate(localISO()) + '</button>' +
    '<h1><button class="hometitle" data-a="calendar" aria-label="Home. Open the calendar, ' + esc(longDate(localISO())) + '">Home' + ICON.chev + '</button></h1>' +
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
function itemRow(it) {
  const r = priceOf(it.id);
  return (
    '<button class="row' + (split() && U.item === it.id ? ' sel' : '') + '" data-a="openItem" data-k="' + esc(it.id) + '">' + tile(it.group, false, it.id) +
    '<span class="lbl"><b>' + esc(it.name) + '</b><small>' + esc(it.english !== it.name ? it.english : it.unit) + '</small></span>' +
    (r
      ? '<span class="amt">' + (r.many && r.low === r.high ? '<small class="from">from</small>' : '') + pesoRange(r.low, r.high) + '<small>' + esc([gbpRange(r.low, r.high), r.unit || it.unit].filter(Boolean).join(' · ')) + '</small></span>'
      : '<span class="amt dim" aria-label="No price yet">—</span>') +
    ICON.chev + '</button>'
  );
}
// a quiet note when the pound values come from a rate over two days old; nothing when it's fresh or missing
const RATE_OLD = 2 * 864e5;
function staleRate() {
  const r = D.rate;
  if (!r) return '';
  const at = new Date(r.cachedAt);
  if (isNaN(at) || Date.now() - at < RATE_OLD) return '';
  const n = dayDiff(localISO(at));
  return '<p class="foot stale" id="staleRate">Pound values use a rate from ' + (n < 7 ? n + ' days ago' : shortDate(localISO(at))) + '. Refresh it on Convert.</p>';
}
// items with a price come first, then the rest in catalogue order
const byPriced = (a, b) => (priceOf(a.id) ? 0 : 1) - (priceOf(b.id) ? 0 : 1);
const inBrowse = (it) => U.scat === 'all' || browseOf(it) === U.scat;
function searchResults() {
  const q = U.q.trim(),
    R = REFS(),
    daNote = '<p class="foot">Market prices are weekly averages from ' + esc(R.source || 'the Department of Agriculture') + ', ' + esc(R.area || '') + ', ' + esc(R.period || '') + '.</p>';
  if (q) {
    const hits = searchItems(q).filter(inBrowse);
    return (
      hdr('Matches', '<span class="hint">' + plural(hits.length, 'result') + '</span>') +
      (hits.length
        ? '<div class="grp tiled">' + hits.map(itemRow).join('') + '</div>'
        : '<div class="grp"><div class="empty"><b>No clear match</b><br>Try fewer words, another spelling or the English name' + (U.scat !== 'all' ? ', or search All' : '') + '.</div></div>') +
      (hits.length ? staleRate() : '')
    );
  }
  // one category: everything in it
  if (U.scat !== 'all') {
    const list = CATALOG.filter(inBrowse).slice().sort(byPriced);
    return hdr(BROWSE.find((b) => b[0] === U.scat)[1], '<span class="hint">' + plural(list.length, 'item') + '</span>') + '<div class="grp tiled">' + list.map(itemRow).join('') + '</div>' + (U.scat === 'market' ? daNote : '') + staleRate();
  }
  // All: a few from each category, each with a door to the rest
  return (
    BROWSE.slice(1)
      .map((b) => {
        const list = CATALOG.filter((it) => browseOf(it) === b[0]).slice().sort(byPriced),
          show = list.slice(0, 4);
        return (
          hdr(b[1]) + '<div class="grp tiled">' + show.map(itemRow).join('') +
          (list.length > show.length ? '<button class="row more" data-a="scat" data-v="' + b[0] + '"><span class="lbl">Show all ' + list.length + '</span>' + ICON.chev + '</button>' : '') + '</div>' +
          (b[0] === 'market' ? daNote : '')
        );
      })
      .join('') + staleRate()
  );
}
const browseChips = () =>
  '<div class="chips scroller" id="browse" data-own-gesture="1" role="group" aria-label="Browse by category">' +
  BROWSE.map((b) => '<button class="chip' + (U.scat === b[0] ? ' on' : '') + '" data-a="scat" data-v="' + b[0] + '" aria-pressed="' + (U.scat === b[0]) + '">' + b[1] + '</button>').join('') + '</div>';
function scrSearch() {
  const list =
    '<label class="searchbox">' + ICON.search +
    '<input id="q" type="search" placeholder="Try “jeepney” or “1 kilo bigas”" aria-label="Search prices" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" value="' + esc(U.q) + '">' +
    '<button type="button" class="clr" data-a="clearQ" aria-label="Clear search"' + (U.q ? '' : ' hidden') + '>' + ICON.x + '</button>' + '</label>' +
    browseChips() +
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
/* Over time (Health style): a range switch D · W · M · All, the total for the period with arrows to step back,
   a bar a day stacked by category, and a breakdown by category. The list below follows the same period. */
const RANGES = [['day', 'D', 'Day'], ['week', 'W', 'Week'], ['month', 'M', 'Month'], ['all', 'All', 'All time']];
const addDays = (iso, n) => {
  const d = atNoon(iso);
  d.setDate(d.getDate() + n);
  return localISO(d);
};
const monthName = (iso, withYear) =>
  atNoon(iso).toLocaleDateString('en-GB', { month: 'long', year: withYear || atNoon(iso).getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined });
// the period the range switch and arrows point at: {from, to, label}
function period() {
  const t = localISO(),
    off = U.roff || 0;
  if (U.range === 'day') {
    const d = addDays(t, -off);
    return { from: d, to: d, label: dayHeading(d) };
  }
  if (U.range === 'week') {
    const mon = addDays(t, -((atNoon(t).getDay() + 6) % 7) - 7 * off),
      sun = addDays(mon, 6);
    return { from: mon, to: sun, label: off === 0 ? 'This week' : off === 1 ? 'Last week' : shortDate(mon) + ' – ' + shortDate(sun) };
  }
  if (U.range === 'month') {
    const d = atNoon(t);
    d.setDate(1);
    d.setMonth(d.getMonth() - off);
    const from = localISO(d),
      to = localISO(new Date(d.getFullYear(), d.getMonth() + 1, 0, 12));
    return { from, to, label: monthName(from) };
  }
  const dates = D.purchases.map((p) => p.date).sort();
  const from = dates[0] || t,
    to = dates.length && dates[dates.length - 1] > t ? dates[dates.length - 1] : t;
  return { from, to, label: dates.length ? 'Since ' + shortDate(from) : 'All time' };
}
const inPeriod = (p, per) => p.date >= per.from && p.date <= per.to;
function spendingList(ignoreCat) {
  const q = norm(U.filter),
    per = period();
  return D.purchases
    .filter((p) => inPeriod(p, per))
    .filter((p) => ignoreCat || U.cat === 'all' || p.category === U.cat)
    .filter((p) => !q || norm([p.item, p.location, p.venue, p.category, p.payment, p.notes].join(' ')).includes(q))
    .sort(byNewest);
}
// a round number just above the tallest bar, for the axis
function niceMax(m) {
  if (!(m > 0)) return 100;
  const p = Math.pow(10, Math.floor(Math.log10(m))),
    f = m / p;
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
}
// the bars: a day each (a week each when "All" spans more than two months)
function buckets(list, per) {
  if (U.range === 'day') return [];
  const span = dayDiff(per.from) - dayDiff(per.to) + 1,
    weekly = U.range === 'all' && span > 62,
    out = [];
  let d = weekly ? addDays(per.from, -((atNoon(per.from).getDay() + 6) % 7)) : per.from;
  while (d <= per.to && out.length < 200) {
    const to = weekly ? addDays(d, 6) : d;
    out.push({ from: d, to, total: 0, by: {} });
    d = addDays(to, 1);
  }
  list.forEach((p) => {
    const b = out.find((x) => p.date >= x.from && p.date <= x.to);
    if (!b) return;
    b.total += +p.price || 0;
    b.by[p.category] = (b.by[p.category] || 0) + (+p.price || 0);
  });
  out.forEach((b) => (b.total = Math.round(b.total * 100) / 100));
  out.weekly = weekly;
  return out;
}
const barLabel = (b, weekly) => (weekly ? 'Week of ' + shortDate(b.from) : dayHeading(b.from));
function spendChart(bs) {
  if (!bs.length) return '';
  const max = niceMax(Math.max(...bs.map((b) => b.total))),
    n = bs.length,
    tick = (i) => {
      if (U.range === 'week') return 'MTWTFSS'[i];
      if (U.range === 'month') return (i % 7 === 0 ? String(i + 1) : '');
      return i === 0 || i === n - 1 ? shortDate(bs[i].from) : '';
    };
  const cols = bs
    .map((b, i) => {
      const segs = CATS.filter((c) => b.by[c] > 0)
        .map((c) => '<i class="seg-' + kindOf(c) + '" style="flex-grow:' + b.by[c] + '"></i>')
        .join('');
      return (
        '<span class="col' + (U.bar === i ? ' on' : '') + '" data-i="' + i + '"><span class="bfill" style="height:' + ((b.total / max) * 100).toFixed(2) + '%">' + segs + '</span></span>'
      );
    })
    .join('');
  return (
    '<div class="chart' + (U.bar != null ? ' picking' : '') + (n > 14 ? ' dense' : '') + '" id="chart" data-own-gesture="1" role="img" aria-label="Spending per ' + (bs.weekly ? 'week' : 'day') + ', up to ' + cash(max) + '">' +
    '<div class="plot"><span class="grid g1"></span><span class="grid g2"></span><div class="cols">' + cols + '</div></div>' +
    '<div class="axis"><span>' + cash(max).replace(/\.00$/, '') + '</span><span>' + cash(max / 2).replace(/\.00$/, '') + '</span><span>₱0</span></div>' +
    '<div class="ticks">' + bs.map((b, i) => '<span>' + tick(i) + '</span>').join('') + '</div></div>'
  );
}
function spendSummary(list) {
  const per = period(),
    bs = buckets(list, per),
    pick = U.bar != null && bs[U.bar] ? bs[U.bar] : null,
    total = pick ? pick.total : sum(list),
    days = Math.max(1, dayDiff(per.from) - Math.max(0, dayDiff(per.to)) + 1),
    avg = U.range !== 'day' && !pick && total ? total / days : 0,
    canBack = U.range !== 'all',
    canFwd = U.range !== 'all' && (U.roff || 0) > 0,
    filtered = U.cat !== 'all' || U.filter.trim();
  return (
    '<div class="eyebrow">' + (pick ? (U.range === 'all' && bs.weekly ? 'Week' : 'Day') : filtered ? (U.cat !== 'all' ? esc(U.cat) : 'Matching') : 'Total') + '</div>' +
    '<div class="tot"><span class="big">' + cash(total) + '</span>' + (D.rate && total ? '<span class="gb">≈ ' + gbp(total / D.rate.value) + '</span>' : '') + '</div>' +
    '<div class="perline">' +
    (canBack ? '<button class="pstep" data-a="rangeStep" data-v="1" aria-label="Earlier">‹</button>' : '') +
    '<span class="plabel">' + esc(pick ? barLabel(pick, bs.weekly) : per.label) + '</span>' +
    (canBack ? '<button class="pstep" data-a="rangeStep" data-v="-1" aria-label="Later"' + (canFwd ? '' : ' disabled') + '>›</button>' : '') +
    '<span class="avg">' + (avg ? cash(avg).replace(/\.\d\d$/, '') + ' a day' : plural(pick ? list.filter((p) => p.date >= pick.from && p.date <= pick.to).length : list.length, 'purchase')) + '</span></div>' +
    spendChart(bs)
  );
}
// money by category for the period, biggest first: also the doors to filter the list
function spendBreakdown() {
  const list = spendingList(true),
    total = sum(list);
  if (!total) return '';
  const rows = CATS.map((c) => [c, sum(list.filter((p) => p.category === c))])
    .filter((r) => r[1] > 0)
    .sort((a, b) => b[1] - a[1]);
  return (
    hdr('By category', U.cat !== 'all' ? '<button class="tbtn" data-a="cat" data-v="all">Show all</button>' : '') +
    '<div class="grp brk">' +
    rows
      .map((r) => {
        const pc = Math.round((r[1] / total) * 100),
          pcs = pc < 1 ? '<1%' : pc + '%';
        return (
          '<button class="row' + (U.cat === r[0] ? ' sel' : '') + '" data-a="cat" data-v="' + esc(U.cat === r[0] ? 'all' : r[0]) + '" aria-pressed="' + (U.cat === r[0]) + '">' +
          tileDot(r[0]) + '<span class="lbl"><b>' + esc(r[0]) + '</b><span class="share"><i class="seg-' + kindOf(r[0]) + '" style="width:' + Math.max(2, pc) + '%"></i></span></span>' +
          '<span class="amt">' + cash(r[1]) + '<small>' + pcs + '</small></span></button>'
        );
      })
      .join('') +
    '</div>'
  );
}
function spendRows(list) {
  if (!D.purchases.length) return '<div class="grp"><div class="empty">Purchases you log on Home appear here.</div></div>';
  if (!list.length)
    return (
      '<div class="grp"><div class="empty">' + (U.cat !== 'all' || U.filter ? 'No purchases match.' : 'Nothing spent ' + (U.range === 'day' ? 'on this day.' : 'in this period.')) +
      (U.cat !== 'all' || U.filter ? ' <button class="tbtn inline" data-a="clearFilters">Show all</button>' : '') + '</div></div>'
    );
  // the newest SHOW_STEP purchases are drawn, then a "Show more" row, so a long trip (or several) stays quick (Q03)
  const shown = list.slice(0, U.shown || SHOW_STEP),
    dayTotal = {};
  list.forEach((p) => (dayTotal[p.date] = (dayTotal[p.date] || 0) + (+p.price || 0)));
  const days = [];
  shown.forEach((p) => {
    const last = days[days.length - 1];
    if (last && last.date === p.date) last.items.push(p);
    else days.push({ date: p.date, items: [p] });
  });
  const left = list.length - shown.length;
  return (
    days
      .map(
        (d) =>
          hdr(dayHeading(d.date), '<span class="hint">' + cash(Math.round(dayTotal[d.date] * 100) / 100) + '</span>') +
          // one detail under the name (the place, or the kind of shop); the rest is in the purchase's details
          '<div class="grp tiled">' + d.items.map((p) => purchaseRow(p, { swipe: true, meta: p.location || p.venue || p.category })).join('') + '</div>'
      )
      .join('') +
    (left > 0 ? '<div class="grp morerows"><button class="row more" data-a="moreRows"><span class="lbl">Show ' + Math.min(left, SHOW_STEP) + ' more</span><span class="hint">' + plural(left, 'left', 'left') + '</span></button></div>' : '')
  );
}
const SHOW_STEP = 60;
const rangeSeg = () =>
  '<div class="segc" id="rangeSeg" role="group" aria-label="Period" style="--n:' + RANGES.length + ';--i:' + Math.max(0, RANGES.findIndex((r) => r[0] === U.range)) + '"><span class="knob glass" aria-hidden="true"></span>' +
  RANGES.map((r) => '<button data-a="range" data-v="' + r[0] + '" aria-label="' + r[2] + '" aria-pressed="' + (U.range === r[0]) + '">' + r[1] + '</button>').join('') + '</div>';
function scrSpending() {
  const list = spendingList();
  const counts = {};
  spendingList(true).forEach((p) => (counts[p.category] = (counts[p.category] || 0) + 1));
  const chips =
    D.purchases.length && Object.keys(counts).length
      ? '<div class="chips scroller" data-own-gesture="1" role="group" aria-label="Filter by category">' +
        [['all', 'All', Object.values(counts).reduce((a, b) => a + b, 0)]]
          .concat(CATS.filter((c) => counts[c]).map((c) => [c, c, counts[c]]))
          .map((c) => '<button class="chip' + (U.cat === c[0] ? ' on' : '') + '" data-a="cat" data-v="' + esc(c[0]) + '" aria-pressed="' + (U.cat === c[0]) + '">' + (c[0] === 'all' ? '' : tileDot(c[0])) + esc(c[1]) + '<span class="n">' + c[2] + '</span></button>')
          .join('') + '</div>'
      : '';
  const main =
    '<h1>Spending</h1>' +
    (D.purchases.length ? rangeSeg() : '') +
    '<div class="card stats" id="spendSum">' + spendSummary(list) + '</div>' +
    '<div id="spendBrk">' + spendBreakdown() + '</div>' +
    (D.purchases.length ? hdr('Purchases') : '') + chips +
    (D.purchases.length
      ? '<label class="searchbox">' + ICON.search + '<input id="filter" type="search" placeholder="Filter by item, place or note" aria-label="Filter purchases" autocomplete="off" value="' + esc(U.filter) + '">' +
        '<button type="button" class="clr" data-a="clearFilter" aria-label="Clear filter"' + (U.filter ? '' : ' hidden') + '>' + ICON.x + '</button>' + '</label>'
      : '') +
    '<div id="spendList">' + spendRows(list) + '</div>' +
    (list.length ? '<button class="btn glass wide csv" data-a="csv">' + ICON.upload + 'Export as CSV</button><p class="foot">Exports the purchases shown above, for Numbers or Excel.</p>' : '');
  if (!split()) return main;
  const p = D.purchases.find((x) => x.id === U.sel);
  return (
    '<div class="split"><div class="sl">' + main + '</div><aside class="pane" aria-label="Purchase details">' +
    (p ? purchaseDetail(p, true) : '<div class="pane-empty">' + ICON.spending + '<p>Pick a purchase to see its details.</p></div>') +
    '</aside></div>'
  );
}
const tileDot = (cat) => '<i class="dot seg-' + kindOf(cat) + '" aria-hidden="true"></i>';

/* ===== Convert ===== */
// handy amounts follow whichever currency is on top: pounds to pesos, or pesos to pounds
const QUICK = { gbp: [1, 5, 10, 20, 50, 100], php: [20, 50, 100, 500, 1000, 5000] };
function rateLine() {
  const r = D.rate;
  if (!r) return navigator.onLine ? 'No rate saved yet. Tap Refresh to load one.' : 'You’re offline and no rate is saved yet. Connect once to load one.';
  const at = new Date(r.cachedAt),
    when = isNaN(at) ? '' : 'Updated ' + relDay(localISO(at)).replace(/^(Today|Yesterday)$/, (m) => m.toLowerCase());
  return (when || 'Saved rate') + (navigator.onLine ? '' : ' · offline, using the saved rate');
}
function convBox(c, r) {
  const sym = c === 'gbp' ? '£' : '₱';
  return field(
    'conv-' + c,
    c === 'gbp' ? 'British pounds' : 'Philippine pesos',
    '<div class="cur"><span aria-hidden="true">' + sym + '</span><input class="inp big" id="conv-' + c + '" data-conv="' + c + '" type="text" inputmode="decimal" autocomplete="off" placeholder="0.00" value="' + esc(U.conv[c]) + '"' + (r ? '' : ' disabled') + '></div>'
  );
}
function scrConvert() {
  const r = D.rate,
    top = U.conv.top === 'php' ? 'php' : 'gbp',
    bottom = top === 'gbp' ? 'php' : 'gbp',
    money = (c, n) => (c === 'gbp' ? gbp(n) : cash(n)).replace(/\.00$/, '');
  return (
    '<h1>Convert</h1><p class="note">A reference rate only. Your card or Revolut may use a different rate or add fees.</p>' +
    '<div class="card form conv" id="convCard">' + '<div class="cbox" data-c="' + top + '">' + convBox(top, r) + '</div>' +
    '<div class="swapline"><button type="button" class="circ swap" data-a="swapConv" aria-label="Swap currencies"' + (r ? '' : ' disabled') + '>' + ICON.swap + '</button></div>' +
    '<div class="cbox" data-c="' + bottom + '">' + convBox(bottom, r) + '</div>' +
    '</div>' +
    '<div class="raterow"><div><b id="rateBadge">' + (r ? '£1 = ' + cash(r.value) : 'No rate yet') + '</b><small id="rateLine">' + esc(rateLine()) + '</small></div>' +
    '<button class="btn glass" id="refreshRate" data-a="refreshRate">' + ICON.refresh + 'Refresh</button></div>' +
    (r
      ? '<button class="btn glass wide" data-a="copyConv">' + ICON.copy + 'Copy conversion</button>' +
        hdr('Handy amounts') +
        '<div class="grp quick">' +
        QUICK[top].map((n) => '<button class="row" data-a="quickConv" data-c="' + top + '" data-v="' + n + '"><span class="lbl">' + money(top, n) + '</span><span class="amt">' + (top === 'gbp' ? cash(n * r.value) : gbp(n / r.value)) + '</span></button>').join('') +
        '</div>'
      : '')
  );
}

/* ===== Settings ===== */
// what happened the last time the rate was checked this session, so a failure can be explained
function rateCheckText() {
  const c = RATE_CHECK,
    when = whenAgo(new Date(c.at)),
    fails = c.fails.map((f) => esc(f.source) + ': ' + esc(f.why)).join('<br>');
  if (c.ok) return { t: 'Loaded from ' + esc(c.source) + ' · ' + when.charAt(0).toLowerCase() + when.slice(1) + (fails ? '<br>Tried first: ' + fails : ''), cls: 'wrap' };
  return { t: 'Couldn’t load a rate · ' + when.charAt(0).toLowerCase() + when.slice(1) + '<br>' + fails, cls: 'wrap red' };
}
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
    row('upload', 'blue', 'Export a backup', 'Purchases, price notes and the saved rate', 'exportBackup') +
    row('download', 'green', 'Restore a backup', 'You’ll see what’s in it before anything changes', 'importPick') +
    row('clock', overdue || !lb ? 'orange' : 'gray', 'Last backed up', { t: lb ? whenAgo(lb) + (overdue ? ' · over two weeks ago' : '') : 'Not backed up yet', cls: overdue ? 'red' : '' }) +
    '</div><p class="foot">iOS can clear a website’s data if it isn’t opened for a few weeks, so keep a recent backup in Files.</p>' +
    hdr('Your data') +
    '<div class="grp tiled set">' +
    row('tag', 'orange', 'Price notes', plural(D.observations.length, 'note'), 'openNotes') +
    (SAFETY ? row('refresh', 'indigo', 'Before your last ' + (SAFETY.why === 'erase' ? 'erase' : 'restore'), plural((SAFETY.data.purchases || []).length, 'purchase') + ' · ' + whenAgo(new Date(SAFETY.at)), 'putBack') : '') +
    (RESCUE.length ? row('download', 'orange', 'Recovered data', plural(rescueCount(), 'record') + ' Suki couldn’t read, kept safe', 'openRescue') : '') +
    row('disk', 'gray', 'Storage used', '<span id="storageUsed">' + esc(STORAGE_USED) + '</span>') +
    '<button class="row danger" data-a="erase">' + stile('erase', 'red') + '<span class="lbl"><b>Erase all data</b><small>Purchases, price notes and the saved rate</small></span></button>' +
    '</div>' +
    hdr('This device') +
    '<div class="grp tiled set">' +
    row('access', 'blue', 'Accessibility', { t: 'Reduce motion: ' + { auto: 'Match iPhone', on: 'On', off: 'Off' }[MOTION.reducePref()] + (MOTION.speed() > 1 ? ' · Slow motion on' : '') }, 'openAccess') +
    '</div>' +
    hdr('About') +
    '<div class="grp tiled set">' +
    row('wifi', 'teal', 'Works offline', '<span id="swStatus">' + esc(SW_STATE) + '</span>') +
    row('peso', 'indigo', 'Saved exchange rate', D.rate ? '£1 = ' + cash(D.rate.value) + ' · ' + shortDate(D.rate.date) + '<br>From ' + esc(D.rate.source) : 'Not loaded yet') +
    (RATE_CHECK ? row('refresh', RATE_CHECK.ok ? 'green' : 'orange', 'Last rate check', rateCheckText()) : '') +
    row('book', 'green', 'Official prices', esc((R.source || '') + ' · ' + (R.area || '') + ' · ' + (R.period || ''))) +
    row('phone', 'blue', 'Add to your Home Screen', 'In Safari: Share › Add to Home Screen') +
    '<a class="row" href="https://github.com/imperialfox/Suki" target="_blank" rel="noopener">' + stile('code', 'ink') + '<span class="lbl"><b>View on GitHub</b></span>' + ICON.out + '</a>' +
    '</div>' +
    '<p class="ver">Suki ' + APP_VERSION + ' · ' + RELEASE_DATE + '</p>'
  );
}
