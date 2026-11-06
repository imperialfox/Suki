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
  // a new purchase starts from that day's town (Q16); editing an old one never changes its place
  if (form === 'home' || (form === 'edit' && !U.sd.id)) dayTown(v);
  const src = locSource(v);
  const more =
    field(form + '-date', 'Date', inp(form, 'date', v.date || localISO(), 'type="date" max="' + localISO(new Date(Date.now() + 864e5 * 366)) + '"')) +
    field(
      form + '-location',
      'Location' + (src ? ' <small class="locsrc">· ' + src + '</small>' : ''),
      '<div class="locbox">' + inp(form, 'location', v.location, 'placeholder="e.g. Cebu City" autocomplete="off"') +
        '<button type="button" class="locbtn" data-a="locate" data-k="' + form + '" aria-label="Fill in the town you’re in">' + ICON.locate + '</button></div>'
    ) +
    field(form + '-venue', 'Where bought', sel(form, 'venue', VENUES, v.venue, 'Not specified')) +
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
      : '<button type="button" class="disclose" data-a="more" aria-expanded="' + !!showMore + '">' +
        (showMore || !String(v.location || '').trim() ? (showMore ? 'Fewer details' : 'More details') : '<em class="dlplace">More details<small> · ' + esc(v.location) + '</small></em>') +
        '<span aria-hidden="true">' + (showMore ? '−' : '+') + '</span></button>' +
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
    p.rateAtPurchase && ['In pounds then', '≈ ' + gbp(p.price / p.rateAtPurchase), rateBehind(p)],
  ].filter(Boolean);
  return (
    '<div class="dhead">' + tile(p.category, true) + '<div class="dmain"><div class="dprice">' + cash(p.price) + '</div><h3>' + esc(p.item) + '</h3></div></div>' +
    '<div class="grp">' + rows.map((r) => '<div class="row kv"><span class="k">' + r[0] + '</span><span class="v">' + esc(r[1]) + (r[2] ? '<small class="ratewhy">' + esc(r[2]) + '</small>' : '') + '</span></div>').join('') + '</div>' +
    // the words he typed in Smart add (Q14)
    (p.said ? '<p class="said">You typed: “' + esc(p.said) + '”</p>' : '') +
    pricesRow(p) +
    (p.notes ? hdr('Notes') + '<div class="card prose">' + esc(p.notes) + '</div>' : '') +
    (inPane
      ? '<div class="actions"><button class="btn glass pk-press" data-a="editPurchase" data-k="' + esc(p.id) + '">' + ICON.pencil + 'Edit</button><button class="btn glass pk-press red" data-a="delPurchase" data-k="' + esc(p.id) + '">' + ICON.bin + 'Delete</button></div>'
      : '<button class="ghost red" data-a="delPurchase" data-k="' + esc(p.id) + '">Delete purchase</button>')
  );
}

// a purchase leads to its item's prices, opened over the purchase (Q08). Only on a whole-word match (strictItemFor).
function pricesRow(p) {
  const id = strictItemFor(p.item),
    it = id && itemById(id);
  if (!it) return '';
  const r = priceOf(id),
    unit = r && (r.unit || it.unit);
  return (
    '<div class="grp tiled spaced"><button class="row" data-a="openItem" data-k="' + esc(id) + '" data-v="push">' + tile(it.group, false, id) +
    '<span class="lbl"><b>' + esc(it.english && it.english !== it.name ? it.english : it.name) + ' prices</b><small>' +
    (r ? 'Usually ' + pesoRange(r.low, r.high) + (unit ? ' · ' + esc(unit) : '') : 'What you paid and your notes') + '</small></span>' + ICON.chev + '</button></div>'
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
function typicalCard(id, strip) {
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
    (strip || '') +
    '<p class="small">Sources, checked ' + shortDate(window.sukiTypical.checked) + ':</p>' +
    srcs.map((s) => '<a class="link src" href="' + esc(s.url) + '" target="_blank" rel="noopener"><span>' + esc(s.source) + (dateOf(s.date) ? ', ' + dateOf(s.date) : '') + '</span>' + ICON.out + '</a>').join('') +
    '</section>'
  );
}
// what you paid for this item, from your own log
// "You paid" uses the whole-word match for logged purchases (Q14), so Mango never counts as Mang Inasal
const paidFor = (id) => D.purchases.filter((p) => wordItemFor(p.item) === id).sort(byNewest);

/* ===== The price range strip (Q12) =====
   At the foot of the typical-prices card: one band per typical price (two ranges never merge), a solid dot for each
   time you paid and a ring for each price note. Where a dot sits says it all: no good or bad words or colours.
   Dots at the same spot stack upwards. A dot and its row are linked: tapping either lights both and shows the dot's
   label, kept inside the strip's edges (U.dot, updated in place by showDot() in events.js). Nothing on it animates. */
const STRIP_STEP = 12, // px between stacked dots
  STRIP_MAX = 5; // levels drawn before dots at one spot share the top one
function stripRound(x, up) {
  const s = x <= 50 ? 5 : x <= 200 ? 10 : x <= 1000 ? 50 : x <= 5000 ? 100 : x <= 20000 ? 500 : 1000;
  return (up ? Math.ceil(x / s) : Math.floor(x / s)) * s;
}
const dotLabel = (price, date, where) => [peso(price), relDay(date), where].filter(Boolean).join(' · ');
function priceStrip(rows, paid, obs) {
  if (!rows.length || (!paid.length && !obs.length)) return '';
  const low = Math.min(...rows.map((r) => r.low)),
    high = Math.max(...rows.map((r) => r.high)),
    vals = [low, high, ...paid.map((p) => +p.price), ...obs.map((o) => +o.price)],
    lo = Math.max(0, stripRound(Math.min(...vals) * 0.8)),
    hi = Math.max(lo + 5, stripRound(Math.max(...vals) * 1.12, true)),
    pos = (x) => Math.min(100, Math.max(0, ((x - lo) / (hi - lo)) * 100));
  // stack dots that land on the same spot (about a dot's width apart)
  const marks = obs
    .map((o) => ({ k: 'note:' + o.id, cls: 's-note', v: +o.price, label: dotLabel(o.price, o.date, o.location || o.venue || o.note), say: 'Price note' }))
    .concat(paid.map((p) => ({ k: 'paid:' + p.id, cls: 's-paid', v: +p.price, label: dotLabel(p.price, p.date, p.location || p.venue), say: 'You paid' })));
  const spots = {};
  marks.forEach((m) => {
    const b = Math.round(pos(m.v) / 3);
    m.level = Math.min(STRIP_MAX - 1, (spots[b] = (spots[b] || 0) + 1) - 1);
    m.spot = b;
  });
  const top = {};
  marks.forEach((m) => (top[m.spot] = Math.max(top[m.spot] || 0, m.level)));
  const levels = Math.max(...marks.map((m) => m.level)),
    lit = U.dot && marks.find((m) => m.k === U.dot);
  const dot = (m) => {
    // each dot's tap area is one stack step tall, so stacked dots don't steal each other's taps;
    // the top of a stack reaches up and the bottom one down, so a lone dot is easy to hit
    const up = m.level === top[m.spot] ? 18 : 0,
      down = m.level === 0 ? 8 : 0;
    return (
      '<button class="sdot ' + m.cls + (lit === m ? ' on' : '') + '" data-a="pickDot" data-dot="' + esc(m.k) + '" data-label="' + esc(m.label) + '" data-x="' + pos(m.v).toFixed(2) + '"' +
      ' style="left:' + pos(m.v).toFixed(2) + '%;bottom:' + (5 + m.level * STRIP_STEP - down) + 'px;height:' + (STRIP_STEP + up + down) + 'px;--down:' + down + 'px"' +
      ' aria-label="' + esc(m.say + ' ' + m.label.replace(/ · /g, ', ')) + '" aria-pressed="' + (lit === m) + '"><i></i></button>'
    );
  };
  const range = pesoRange(low, high);
  return (
    '<div class="strip" role="group" aria-label="' + esc('What you paid and your price notes, against the typical ' + range) + '">' +
    '<div class="track" style="height:' + (46 + levels * STRIP_STEP) + 'px"><span class="line"></span>' +
    rows.map((r) => '<span class="band" style="left:calc(' + pos(r.low).toFixed(2) + '% - 5px);width:calc(' + (pos(r.high) - pos(r.low)).toFixed(2) + '% + 10px)"></span>').join('') +
    marks.map(dot).join('') +
    '<span class="slabel' + (lit ? ' on' : '') + '" aria-hidden="true"' + (lit ? ' style="left:' + pos(lit.v).toFixed(2) + '%;--x:' + pos(lit.v).toFixed(2) + '%"' : '') + '>' + (lit ? esc(lit.label) : '') + '</span>' +
    '</div><div class="axis" aria-hidden="true"><span>' + peso(lo) + '</span><span>' + peso(hi) + '</span></div>' +
    '<div class="skey" aria-hidden="true"><span><i class="kband"></i>Typical</span>' + (paid.length ? '<span><i class="kpaid"></i>You paid</span>' : '') + (obs.length ? '<span><i class="knote"></i>Price notes</span>' : '') + '</div>' +
    '</div>'
  );
}
function itemDetail(id, inPane) {
  const it = itemById(id);
  if (!it) return '';
  const obs = D.observations.filter((o) => o.itemId === id).sort((a, b) => b.date.localeCompare(a.date));
  const open = U.obsFor === id;
  const f = F.obs;
  const paid = paidFor(id);
  const prices = typicalCard(id, priceStrip(typicalFor(id), paid, obs)) + officialCard(id);
  const lit = (k) => (U.dot === k ? ' lit' : '');
  return (
    '<div class="dhead">' + tile(it.group, true, it.id) + '<div class="dmain"><h3>' + esc(it.name) + '</h3><div class="sub">' + esc(it.english !== it.name ? it.english + ' · ' + it.unit : it.unit) + '</div></div></div>' +
    (prices || '<div class="card quiet">No published price for this yet. Add what you see below, and it’ll show here next time.</div>') +
    (paid.length
      ? hdr('You paid', '<span class="hint">' + plural(paid.length, 'time') + '</span>') +
        '<div class="grp">' + paid.slice(0, 5).map((p) => '<button class="row' + lit('paid:' + p.id) + '" data-a="openPurchase" data-k="' + esc(p.id) + '" data-v="push" data-dot="paid:' + esc(p.id) + '"><span class="lbl"><b>' + cash(p.price) + (gbpThen(p) ? ' <span class="gb">' + esc(gbpThen(p)) + '</span>' : '') + '</b><small>' + esc([relDay(p.date), p.location].filter(Boolean).join(' · ')) + '</small></span>' + ICON.chev + '</button>').join('') + '</div>'
      : '') +
    '<button class="btn glass pk-press wide logit" data-a="logItem" data-k="' + esc(id) + '">' + ICON.plus + 'Log what you paid</button>' +
    hdr('Your price notes', open ? '' : '<button class="tbtn" data-a="obsForm" data-k="' + esc(id) + '">Add</button>') +
    (open
      ? '<form class="card form" data-form="obs" data-k="' + esc(id) + '" novalidate>' +
        '<div class="two">' + field('obs-price', 'Price you saw · ₱', money$('obs', 'price', f.price)) + field('obs-date', 'Date', inp('obs', 'date', f.date || localISO(), 'type="date"')) + '</div>' +
        '<div class="two">' + field('obs-location', 'Location', inp('obs', 'location', f.location, 'placeholder="e.g. Cebu City" autocomplete="off"')) + field('obs-venue', 'Where', sel('obs', 'venue', VENUES, f.venue, 'Not specified')) + '</div>' +
        field('obs-note', 'Size or note', inp('obs', 'note', f.note, 'placeholder="e.g. 500 ml bottle, large serving" autocomplete="off"')) +
        '<p class="err" id="obs-err" role="alert"></p>' +
        '<div class="actions"><button type="button" class="btn glass pk-press" data-a="obsCancel">Cancel</button><button type="submit" class="btn glass pk-press tinted">Save note</button></div></form>'
      : '') +
    (obs.length
      ? '<div class="grp">' +
        obs
          .map(
            (o) =>
              '<div class="row' + lit('note:' + o.id) + '" data-dot="note:' + esc(o.id) + '"><span class="lbl"><b>' + cash(o.price) + (inGbp(o.price) ? ' <span class="gb">' + esc(inGbp(o.price)) + '</span>' : '') + '</b><small>' + esc([relDay(o.date), o.location, o.venue, o.note].filter(Boolean).join(' · ')) + '</small></span>' +
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
    recent = D.purchases.slice().sort(byNewest).slice(0, 4),
    lb = total ? poundsOf(D.purchases) : null,
    lbNote = poundsNote(lb);
  // two doors in one card: the total opens all your spending, Today opens today's (Q08)
  const dash =
    rateCard() +
    // still loading after the launch screen (a slow start): say so, never "Nothing spent yet" (Q31)
    (!READY
      ? '<div class="card sumcard static none loading" role="status"><span class="stat"><span class="mid">Loading your purchases…</span><span class="cap">This can take a moment after the phone restarts.</span></span></div>'
      : D.purchases.length
      ? '<div class="card sumcard doors' + (cash(total).length > 11 || cash(today).length > 11 ? ' long' : '') + '">' +
        '<button class="stat door" data-a="toSpend" data-v="all" aria-label="Total spent ' + cash(total) + '. Open all spending"><span class="big">' + cash(total) + '</span><span class="cap">Total spent' + (lb ? ' · ≈ ' + gbp(lb.g) : '') + '<span class="cv" aria-hidden="true"> ›</span></span>' + (lbNote ? '<span class="cap rn">' + lbNote + '</span>' : '') + '</button>' +
        '<button class="stat r door" data-a="toSpend" data-v="day" aria-label="Today ' + cash(today) + '. Open today’s spending"><span class="mid">' + cash(today) + '</span><span class="cap">Today<span class="cv" aria-hidden="true"> ›</span></span></button></div>'
      : '<div class="card sumcard static none"><span class="stat"><span class="mid">Nothing spent yet</span><span class="cap">Your total and today’s spending show here once you log something.</span></span></div>') +
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
  // two sides: the form, and Smart add (Q14, smart.js), switched by the pill on the heading
  const log = logCard();
  // both Show all doors open All, with every purchase, like Total spent (Q24)
  const rec =
    hdr('Recent', D.purchases.length ? '<button class="tbtn" data-a="toSpend" data-v="all">Show all</button>' : '') +
    (recent.length
      ? '<div class="grp tiled">' + recent.map((p) => purchaseRow(p)).join('') +
        (D.purchases.length > recent.length ? '<button class="row more" data-a="toSpend" data-v="all"><span class="lbl">Show all ' + D.purchases.length + ' purchases</span>' + ICON.chev + '</button>' : '') + '</div>'
      : '<div class="grp"><div class="empty">' + (READY ? 'No purchases yet. Log your first one ' + (split() ? 'here.' : 'above.') : 'Loading your purchases…') + '</div></div>');
  return (
    // the date and the title both open the calendar (Apple Books style)
    '<button class="dateline hometitle" data-a="calendar" tabindex="-1" aria-hidden="true">' + longDate(localISO()) + '</button>' +
    '<h1><button class="hometitle" data-a="calendar" aria-label="Home. Open the calendar, ' + esc(longDate(localISO())) + '">Home' + ICON.chev + '</button></h1>' +
    (split() || MQ.land.matches
      ? '<div class="dash"><div>' + dash + log + '</div><div>' + rec + '</div></div>'
      : dash + log + rec)
  );
}
// Home's exchange rate card (Q17): today's rate first, for anyone glancing at Home. The whole card is one door to
// Convert; tapping it doesn't refresh (Convert's own Refresh does). An old rate stays white, never red.
function rateAge(r) {
  const at = new Date(r.cachedAt);
  if (isNaN(at)) return 'Rate from ' + shortDate(r.date);
  const mins = Math.floor((Date.now() - at) / 6e4);
  if (mins < 1) return 'Updated just now';
  if (mins < 60) return 'Updated ' + mins + ' min ago';
  if (mins < 1440) return 'Updated ' + Math.floor(mins / 60) + 'h ago';
  return 'Updated ' + relDay(localISO(at)).replace(/^Yesterday$/, 'yesterday');
}
const rateLabel = (r) => 'Exchange rate £1 = ' + cash(r.value) + ', ' + rateAge(r).replace(/^U/, 'u') + '. Open Convert';
function rateCard() {
  const r = D.rate;
  if (!r)
    return '<button class="ratecard none" data-a="goConvert" aria-label="Exchange rate. Get today’s rate on Convert"><span class="rc"><span class="rk">Exchange rate</span><b class="rget">Get today’s rate on Convert</b></span>' + ICON.chev + '</button>';
  return (
    '<button class="ratecard" id="rateCard" data-a="goConvert" aria-label="' + esc(rateLabel(r)) + '"><span class="rc"><span class="rk">Exchange rate</span>' +
    '<b class="rv">£1 = ' + cash(r.value) + '</b><span class="ra" id="rateAge">' + esc(rateAge(r)) + '</span></span>' + ICON.chev + '</button>'
  );
}
// the age moves on while Home is open ("2 min ago" → "3 min ago"), in place, with no redraw
function tickRateAge() {
  const c = $('rateCard'),
    a = $('rateAge');
  if (!c || !a || !D.rate) return;
  a.textContent = rateAge(D.rate);
  c.setAttribute('aria-label', rateLabel(D.rate));
}
setInterval(tickRateAge, 30000);
document.addEventListener('visibilitychange', tickRateAge);
// Home's Save button confirms where he tapped: "✓ Saved" for about 1.4 s (Q11). A redraw in that time keeps it
let savedUntil = 0;
const saveBtn = () =>
  Date.now() < savedUntil
    ? '<button type="submit" class="cta pk-press-solid ink saved" id="homeSave"><span class="tk">' + ICON.tick + '</span>Saved</button>'
    : '<button type="submit" class="cta pk-press-solid ink" id="homeSave">Save purchase</button>';
const byNewest = (a, b) => b.date.localeCompare(a.date) || D.purchases.indexOf(a) - D.purchases.indexOf(b);

/* ===== Quick Till ===== */
// the notes and coin you hand over (Q13): Exact, the ₱20 coin, then the four polymer notes, 44 pt on one row.
// Labels match the notes ("1000"); VoiceOver says what each one is.
const TILL_KEYS = [
  [20, 'c20b', 'Add a ₱20 coin'],
  [50, 'n50', 'Add a ₱50 note'],
  [100, 'n100', 'Add a ₱100 note'],
  [500, 'n500', 'Add a ₱500 note'],
  [1000, 'n1000', 'Add a ₱1,000 note'],
];
function scrTill() {
  return (
    '<h1>Quick Till</h1><p class="note">Check your change before you walk away. Works offline.</p>' +
    '<div class="card form">' +
    field('till-bill', 'Total bill · ₱', '<input class="inp big" id="till-bill" data-till="bill" type="text" inputmode="decimal" autocomplete="off" placeholder="e.g. 789.50" value="' + esc(U.till.bill) + '">') +
    field(
      'till-cash',
      'Cash handed over · ₱',
      '<div class="cwell"><div class="cashbox"><input class="inp big" id="till-cash" data-till="cash" type="text" inputmode="decimal" autocomplete="off" placeholder="e.g. 1,000" value="' + esc(U.till.cash) + '">' +
        '<button type="button" class="cx" id="cashClear" data-a="cashClear" aria-label="Clear cash"' + (U.till.cash ? '' : ' hidden') + '><span>' + ICON.x + '</span></button></div>' +
        tillPeek() + '</div><span class="vh" id="tillOver" aria-live="polite">' + (tillOverloaded() ? TILL_OVER_SAYS : '') + '</span>'
    ) +
    tillDrawer() +
    '<div class="denoms" role="group" aria-label="Notes you hand over"><button type="button" class="dn ex" data-a="cashExact" aria-label="Cash is exactly the bill">Exact</button>' +
    TILL_KEYS.map((k) => '<button type="button" class="dn ' + k[1] + '" data-a="cashAdd" data-v="' + k[0] + '" aria-label="' + k[2] + '">' + k[0] + '</button>').join('') +
    '</div>' +
    '<div class="tillout" id="tillOut" aria-live="polite">' + tillOut() + '</div>' +
    '<button class="cta pk-press-solid ink" id="tillLog" data-a="tillLog"' + (tillState().bill > 0 ? '' : ' disabled') + '>Log this bill</button></div>' +
    '<p class="foot">Tap each note or ₱20 coin you hand over: 20 + 20 makes ₱40.</p>'
  );
}
/* The till drawer (Q19): hidden under the cash box. Four note slots at the back (₱1,000, ₱500, ₱100, ₱50) and five coin
   cups in front (₱20, ₱10, ₱5, ₱1, 25¢), each labelled on its front lip. The slot line under it is its handle: a real
   button, hidden at rest. Always drawn shut: a redraw closes it (gestures.js, drawerReset).
   Its contents (Q20) are a fullness gauge, not a count: only the cash handed over decides how full it looks. Coins fill
   first, then the 50s and 100s, then the 500s, then the 1000s; everything is full at ₱20,000. From ₱50,000 it's
   overloaded: notes tip out, coins spill, and with the drawer shut notes peek out from under the cash box.
   drawerFill() draws them still (a redraw); fillDrawer() in events.js changes them with calm fades (typing, a note, ✕). */
const DRAWER_SLOTS = [1000, 500, 100, 50];
const DRAWER_CUPS = ['20', '10', '5', '1', '25c'];
const CUP_LABELS = { 20: '20', 10: '10', 5: '5', 1: '1', '25c': '25¢' };
const TILL_FULL = { over: 50000, sheets: 10, overSheets: 12, popFrom: 8, coins: [4, 4, 5, 5, 5], overCoins: 8 };
const TILL_OVER_SAYS = 'Till overloaded. Check the amount.';
// two coins at the bottom of each heap, the rest landing where they fall (dx, dy, tilt), mirrored in every other cup;
// overloaded, three more spill out of the cup
const HEAP = [[-3, 13, 0], [7, 12, -8], [-9, 10, 6], [2, 8, -4], [-5, 6, 9]];
const SPILL = [[-26, 17], [16, 18], [-4, 20]];
const tillTotal = () => Math.max(0, amount(U.till.cash) || 0);
const tillOverloaded = () => tillTotal() >= TILL_FULL.over;
// how full each part looks for the cash handed over, 0 to 1, on a log scale (the prototype's curve)
function drawerLevels(t) {
  const L = Math.log10(Math.max(t, 1)),
    c = (x) => Math.max(0, Math.min(1, x));
  return { coin: t > 0 ? c(L / 2) : 0, 50: c((L - 1.5) / 1.4), 100: c((L - 1.8) / 1.5), 500: c((L - 2.6) / 1.5), 1000: c((L - 3) / 1.3) };
}
// how many sheets stand in each slot and how many coins lie in each cup
function drawerCounts(t) {
  const lv = drawerLevels(t),
    ov = t >= TILL_FULL.over;
  return {
    over: ov,
    slots: DRAWER_SLOTS.map((n) => (ov ? TILL_FULL.overSheets : Math.round(lv[n] * TILL_FULL.sheets))),
    cups: DRAWER_CUPS.map((c, ci) => (ov ? TILL_FULL.overCoins : Math.round(lv.coin * TILL_FULL.coins[ci]))),
  };
}
// a sheet standing in its slot: upright against the floor's 26° tilt; overloaded, the last four are taller and tip out
function sheetStyle(i, ov) {
  const pop = ov && i >= TILL_FULL.popFrom;
  return { left: (6 + i * 6.6).toFixed(1) + '%', height: (pop ? 46 : 34) + 'px', transform: 'rotateX(-26deg)' + (pop ? ' rotateZ(' + (i % 2 ? 12 : -10) + 'deg)' : '') };
}
function coinStyle(ci, i) {
  if (i < HEAP.length) {
    const [dx, dy, r] = HEAP[i],
      m = ci % 2 ? -1 : 1;
    return { top: dy + 'px', marginLeft: -10 + dx * m + 'px', transform: 'rotate(' + r * m + 'deg)' };
  }
  const sp = SPILL[(i - HEAP.length) % SPILL.length];
  return { top: sp[1] + 'px', marginLeft: sp[0] - 10 + 'px', transform: '' };
}
const styleText = (s) => 'left:' + (s.left || '') + ';top:' + (s.top || '') + ';height:' + (s.height || '') + ';margin-left:' + (s.marginLeft || '') + ';transform:' + (s.transform || 'none');
function drawerFill() {
  const k = drawerCounts(tillTotal());
  return {
    slot: (si) => Array.from({ length: k.slots[si] }, (_, i) => '<i style="' + styleText(sheetStyle(i, k.over)) + '"></i>').join(''),
    cup: (ci) => Array.from({ length: k.cups[ci] }, (_, i) => '<i' + (ci === 0 ? ' class="r"' : '') + ' style="' + styleText(coinStyle(ci, i)) + '"></i>').join(''),
  };
}
// overloaded, notes poke out from under the cash box even with the drawer shut (and on an iPhone on its side)
function tillPeek() {
  return '<div class="peek' + (tillOverloaded() ? ' on' : '') + '" id="tillPeek" aria-hidden="true"><i class="n1000" style="left:16%;transform:rotate(-6deg)"></i><i class="n500" style="left:44%;transform:rotate(4deg)"></i><i class="n1000" style="left:70%;transform:rotate(-3deg)"></i></div>';
}
function tillDrawer() {
  const f = drawerFill();
  return (
    '<div class="dws" id="tillDrawer"><div class="tray" id="tillTray" aria-hidden="true">' +
    '<div class="tnotes">' + DRAWER_SLOTS.map((n, si) => '<div class="tslot n' + n + '" data-n="' + n + '"><span>' + n + '</span>' + f.slot(si) + '</div>').join('') + '</div>' +
    '<div class="tcoins">' + DRAWER_CUPS.map((c, ci) => '<div class="tcup" data-c="' + c + '"><span>' + CUP_LABELS[c] + '</span>' + f.cup(ci) + '</div>').join('') + '</div>' +
    '<div class="tmark" id="tillMark" aria-hidden="true">Designed by Ivan</div>' + // at the very back: only the haul reaches it (Q21)
    '</div></div>' +
    '<button type="button" class="hdl" id="tillHdl" aria-expanded="false" aria-label="Open till drawer"><span class="slotln" id="tillSlot" aria-hidden="true"></span></button>'
  );
}
function tillState() {
  const bill = amount(U.till.bill),
    paid = amount(U.till.cash);
  const b = cents(bill) > 0 ? bill : 0;
  return { bill: b, paid: paid >= 0 ? paid : null, ok: b > 0 && paid !== null && paid >= 0 };
}
// what the till says: the eyebrow, the figure, the line under it, and the change as cash (null when there's none)
function tillView() {
  const t = tillState();
  if (!t.ok) return { eb: 'Change due', fig: '—', cls: 'metric dim', small: 'Enter the bill and the cash you handed over.', cash: null };
  const d = Math.round(t.paid * 100) - Math.round(t.bill * 100); // in centavos, so the breakdown is exact
  if (d > 0) return { eb: 'Change due', fig: cash(d / 100), cls: 'metric', small: cash(t.paid) + ' handed over for a ' + cash(t.bill) + ' bill.', cash: asCash(d) };
  if (d < 0) return { eb: 'Still to pay', red: true, fig: cash(-d / 100), cls: 'metric red', small: 'The cash is short of the ' + cash(t.bill) + ' bill.', cash: null };
  return { eb: 'Exact payment', fig: cash(0), cls: 'metric', small: 'No change needed.', cash: null };
}
function tillOut() {
  const v = tillView(),
    w = cashWant(v.cash);
  return (
    '<div class="eyebrow' + (v.red ? ' red' : '') + '" id="tillEb">' + v.eb + '</div><div class="' + v.cls + '" id="tillFig">' + v.fig + '</div>' +
    '<div class="cashrow" id="cashRow"' + (v.cash ? ' role="img" aria-label="' + esc(cashWords(v.cash)) + '"' : ' aria-hidden="true"') + '>' +
    '<span class="stacks">' + w.filter((x) => x.stack).map(pieceHTML).join('') + '</span>' +
    '<span class="fan">' + w.filter((x) => x.note).map(pieceHTML).join('') + '</span>' +
    '<span class="coins">' +
    COINS.filter((k) => w.some((x) => x.coin === k)).map((k) => '<span class="pile" data-den="' + k + '">' + w.filter((x) => x.coin === k).map(pieceHTML).join('') + '</span>').join('') +
    '</span></div>' +
    '<p class="small" id="tillSmall">' + v.small + '</p>'
  );
}

/* ===== Change as cash (Q13): the fewest notes and coins, the way a cashier hands them over =====
   Notes: ₱1,000, ₱500, ₱100, ₱50. No ₱200 (the BSP stopped making them in 2021) and no ₱20 note (it's a coin now).
   Coins, in centavos: ₱20, ₱10, ₱5, ₱1, 25¢, 5¢, 1¢. There's no 50¢ coin, so 50¢ comes as two 25¢.
   No banknote artwork: copying any part of a note needs the BSP's approval, so they're plain colours and numbers. */
const NOTES = [1000, 500, 100, 50];
const COINS = [2000, 1000, 500, 100, 25, 5, 1];
const BUNDLE_AT = 5; // up to four of a note fan out, so the edges can be counted; five or more become one bundle
function asCash(c) {
  const notes = [],
    coins = [];
  NOTES.forEach((n) => {
    const m = Math.floor(c / (n * 100));
    for (let i = 0; i < m; i++) notes.push(n);
    c -= m * n * 100;
  });
  COINS.forEach((k) => {
    const m = Math.floor(c / k);
    if (m) coins.push([k, m]);
    c -= m * k;
  });
  return { notes, coins };
}
const coinLabel = (k) => (k >= 100 ? String(k / 100) : k + '¢');
const wholePeso = (n) => cash(n).replace(/\.00$/, '');
function cashWords(b) {
  const parts = [],
    count = {};
  b.notes.forEach((n) => (count[n] = (count[n] || 0) + 1));
  NOTES.forEach((n) => {
    if (count[n]) parts.push(wholePeso(n) + ' note' + (count[n] > 1 ? ' × ' + count[n].toLocaleString('en-GB') : ''));
  });
  b.coins.forEach(([k, m]) => parts.push((k >= 100 ? wholePeso(k / 100) : k + '¢') + ' coin' + (m > 1 ? ' × ' + m : '')));
  return 'As cash: ' + parts.join(', ');
}
// the pieces to show, each with a key that stays the same while it's on screen, so only what changes moves
function cashWant(b) {
  const want = [];
  if (!b) return want;
  const count = {};
  b.notes.forEach((n) => (count[n] = (count[n] || 0) + 1));
  NOTES.forEach((n) => {
    const c = count[n] || 0;
    if (c >= BUNDLE_AT) want.push({ k: 's' + n, stack: n, count: c });
    else for (let i = 0; i < c; i++) want.push({ k: 'n' + n + '.' + i, note: n });
  });
  b.coins.forEach(([k, m]) => {
    for (let i = 0; i < m; i++) want.push({ k: 'c' + k + '.' + i, coin: k });
  });
  return want;
}
function pieceHTML(w) {
  if (w.stack) {
    const n = w.stack;
    return '<span class="stk" data-k="' + w.k + '"><i class="nt n' + n + '"></i><i class="nt n' + n + '"></i><span class="nt n' + n + '"><b>' + n + '</b><em>×' + w.count.toLocaleString('en-GB') + '</em></span></span>';
  }
  if (w.note) return '<span class="nt n' + w.note + '" data-k="' + w.k + '"><b>' + w.note + '</b></span>';
  if (w.coin === 2000) return '<span class="cn c20" data-k="' + w.k + '"><i>20</i></span>';
  return '<span class="cn' + (w.coin === 500 ? ' c5' : '') + (w.coin < 25 ? ' tiny' : '') + '" data-k="' + w.k + '">' + coinLabel(w.coin) + '</span>';
}
// redraws the cash row in place: new pieces settle in (10 px, 45 ms apart), removed ones shrink away in 160 ms where
// they were, and the rest glide to their new place on gentle. The bundle's count changes without moving.
function renderCash(b) {
  const row = $('cashRow');
  if (!row) return;
  const boxes = { stacks: row.querySelector('.stacks'), fan: row.querySelector('.fan'), coins: row.querySelector('.coins') };
  const items = [...row.querySelectorAll('.stacks > [data-k], .fan > [data-k], .pile > [data-k]')];
  const small = $('tillSmall'),
    smallTop = small ? small.getBoundingClientRect().top : 0,
    rr = row.getBoundingClientRect(),
    before = new Map(items.map((el) => [el.dataset.k, el.getBoundingClientRect()]));
  const want = cashWant(b),
    keep = new Set(want.map((w) => w.k)),
    old = {};
  items.forEach((el) => {
    if (keep.has(el.dataset.k)) return void (old[el.dataset.k] = el);
    cashLeave(row, el, before.get(el.dataset.k), rr);
    el.remove();
  });
  const fresh = [],
    piles = [];
  want.forEach((w) => {
    let el = old[w.k];
    if (!el) {
      const t = document.createElement('template');
      t.innerHTML = pieceHTML(w);
      el = t.content.firstChild;
      fresh.push(el);
    }
    if (w.stack) {
      el.querySelector('em').textContent = '×' + w.count.toLocaleString('en-GB');
      boxes.stacks.appendChild(el);
    } else if (w.note) boxes.fan.appendChild(el);
    else {
      let p = piles.find((x) => x.dataset.den === String(w.coin)) || boxes.coins.querySelector('.pile[data-den="' + w.coin + '"]');
      if (!p) {
        p = document.createElement('span');
        p.className = 'pile';
        p.dataset.den = w.coin;
      }
      if (!piles.includes(p)) piles.push(p);
      p.appendChild(el);
    }
  });
  boxes.coins.querySelectorAll('.pile').forEach((p) => {
    if (!piles.includes(p)) p.remove();
  });
  piles.forEach((p) => boxes.coins.appendChild(p));
  if (b) {
    row.setAttribute('role', 'img');
    row.setAttribute('aria-label', cashWords(b));
    row.removeAttribute('aria-hidden');
  } else {
    row.removeAttribute('role');
    row.removeAttribute('aria-label');
    row.setAttribute('aria-hidden', 'true');
  }
  Object.keys(old).forEach((k) => {
    const a = before.get(k),
      n = old[k].getBoundingClientRect(),
      dx = a.left - n.left,
      dy = a.top - n.top;
    if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) MOTION.animate(old[k], [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }], { spring: 'gentle' });
  });
  fresh.forEach((el, i) => MOTION.land(el, i, 10));
  if (small) {
    const dy = smallTop - small.getBoundingClientRect().top;
    if (Math.abs(dy) > 0.5) MOTION.animate(small, [{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }], { spring: 'gentle' });
  }
}
// a piece that went: a copy shrinks away where it was (160 ms), or fades with Reduce Motion; nothing with motion off
function cashLeave(row, el, r, rr) {
  if (!r) return;
  const g = el.cloneNode(true);
  g.removeAttribute('data-k');
  g.classList.add('cghost');
  g.setAttribute('aria-hidden', 'true');
  Object.assign(g.style, { left: r.left - rr.left + 'px', top: r.top - rr.top + 'px', width: r.width + 'px', height: r.height + 'px' });
  row.appendChild(g);
  const a = MOTION.leave(g, 160, 0.6);
  if (a) a.onfinish = () => g.remove();
  else g.remove();
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
  return '<p class="foot stale" id="staleRate">Pound values use a rate from ' + (n < 7 ? n + ' days ago' : shortDate(localISO(at))) + '. <button class="tlink" data-a="goRefresh">Refresh it on Convert</button></p>';
}
/* Finding his own records (Q09). One matcher for Search and Spending's filter, so "Show all N in Spending" opens
   exactly the N that Search counted: every word typed has to appear somewhere in the record, in any order. */
function matcher(q) {
  const words = norm(q).split(' ').filter(Boolean),
    has = (parts) => {
      const t = norm(parts.join(' '));
      return words.every((w) => t.includes(w));
    };
  return {
    any: words.length > 0,
    purchase: (p) => !words.length || has([p.item, p.location, p.venue, p.category, p.payment, p.notes]),
    note: (o) => !words.length || has([o.itemName, o.location, o.venue, o.note]),
  };
}
const noteRow = (o) => {
  const it = itemById(o.itemId);
  return (
    '<button class="row" data-a="openItem" data-k="' + esc(o.itemId) + '">' + tile(it ? it.group : '', false, o.itemId) +
    '<span class="lbl"><b>' + esc(o.itemName) + ' · ' + cash(o.price) + '</b><small>' + esc([relDay(o.date), o.location, o.venue, o.note].filter(Boolean).join(' · ')) + '</small></span>' + ICON.chev + '</button>'
  );
};
const MINE_SHOWN = 3;
function recordResults(q) {
  const m = matcher(q),
    mine = D.purchases.filter(m.purchase).sort(byNewest),
    notes = D.observations.filter(m.note).sort((a, b) => b.date.localeCompare(a.date));
  let h = '';
  if (mine.length)
    h +=
      hdr('In your purchases', '<span class="hint">' + plural(mine.length, 'purchase') + '</span>') +
      '<div class="grp tiled" id="mine">' + mine.slice(0, MINE_SHOWN).map((p) => purchaseRow(p)).join('') +
      (mine.length > MINE_SHOWN ? '<button class="row more" data-a="searchToSpend"><span class="lbl">Show all ' + mine.length + ' in Spending</span>' + ICON.chev + '</button>' : '') + '</div>';
  if (notes.length) h += hdr('In your price notes', '<span class="hint">' + plural(notes.length, 'note') + '</span>') + '<div class="grp tiled" id="mynotes">' + notes.map(noteRow).join('') + '</div>';
  return { html: h, found: mine.length + notes.length };
}
// Search's All view starts with a door to every price note (the Settings row is the second door)
const notesDoor = () =>
  '<div class="grp tiled" id="notesDoor"><button class="row" data-a="openNotes">' + stile('tag', 'orange') +
  '<span class="lbl"><b>Your price notes</b><small>' + (D.observations.length ? plural(D.observations.length, 'note') + ' from the trip' : 'Prices you’ve seen, saved from any item') + '</small></span>' + ICON.chev + '</button></div>';
// items with a price come first, then the rest in catalogue order
const byPriced = (a, b) => (priceOf(a.id) ? 0 : 1) - (priceOf(b.id) ? 0 : 1);
const inBrowse = (it) => U.scat === 'all' || browseOf(it) === U.scat;
function searchResults() {
  const q = U.q.trim(),
    R = REFS(),
    daNote = '<p class="foot">Market prices are weekly averages from ' + esc(R.source || 'the Department of Agriculture') + ', ' + esc(R.area || '') + ', ' + esc(R.period || '') + '.</p>';
  if (q) {
    // prices first, then his own purchases and price notes (Q09)
    const hits = searchItems(q).filter(inBrowse),
      mine = recordResults(q);
    return (
      (hits.length ? hdr('Prices', '<span class="hint">' + plural(hits.length, 'result') + '</span>') + '<div class="grp tiled">' + hits.map(itemRow).join('') + '</div>' : '') +
      mine.html +
      (hits.length
        ? staleRate()
        : // nothing in the price list: say so only if nothing of his matched either, and offer to log it (Q08)
          (mine.found ? '' : hdr('Matches', '<span class="hint">0 results</span>') + '<div class="grp"><div class="empty"><b>No clear match</b><br>Try fewer words, another spelling or the English name' + (U.scat !== 'all' ? ', or search All' : '') + '.</div></div>') +
          '<div class="grp tiled spaced"><button class="row more" data-a="newPurchase" data-item="' + esc(q) + '"><span class="lbl">Log “' + esc(q) + '” as a purchase</span>' + ICON.chev + '</button></div>')
    );
  }
  // one category: everything in it
  if (U.scat !== 'all') {
    const list = CATALOG.filter(inBrowse).slice().sort(byPriced);
    return hdr(BROWSE.find((b) => b[0] === U.scat)[1], '<span class="hint">' + plural(list.length, 'item') + '</span>') + '<div class="grp tiled">' + list.map(itemRow).join('') + '</div>' + (U.scat === 'market' ? daNote : '') + staleRate();
  }
  // All: the price notes door, then a few from each category, each with a door to the rest
  return (
    notesDoor() +
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
  '<div class="chips pk-static scroller" id="browse" data-own-gesture="1" role="group" aria-label="Browse by category">' +
  BROWSE.map((b) => '<button class="chip pk-chip' + (U.scat === b[0] ? ' on' : '') + '" data-a="scat" data-v="' + b[0] + '" aria-pressed="' + (U.scat === b[0]) + '">' + b[1] + '</button>').join('') + '</div>';
function scrSearch() {
  const list =
    '<label class="searchbox">' + ICON.search +
    '<input id="q" type="search" placeholder="Prices, your purchases, your notes" aria-label="Search prices, your purchases and your notes" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="search" value="' + esc(U.q) + '">' +
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
  const m = matcher(U.filter),
    per = period();
  return D.purchases
    .filter((p) => inPeriod(p, per))
    .filter((p) => ignoreCat || U.cat === 'all' || p.category === U.cat)
    .filter(m.purchase)
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
    lb = total ? poundsOf(pick ? list.filter((p) => p.date >= pick.from && p.date <= pick.to) : list) : null,
    lbNote = poundsNote(lb),
    // the note's line stays while a bar is picked, empty if need be, so clearing the pick moves nothing under the finger (Q10)
    lbLine = lbNote || (pick && poundsNote(poundsOf(list))),
    days = Math.max(1, dayDiff(per.from) - Math.max(0, dayDiff(per.to)) + 1),
    avg = U.range !== 'day' && !pick && total ? total / days : 0,
    canBack = U.range !== 'all',
    canFwd = U.range !== 'all' && (U.roff || 0) > 0,
    filtered = U.cat !== 'all' || U.filter.trim();
  return (
    '<div class="eyebrow">' + (pick ? (U.range === 'all' && bs.weekly ? 'Week' : 'Day') : filtered ? (U.cat !== 'all' ? esc(U.cat) : 'Matching') : 'Total') + '</div>' +
    '<div class="tot"><span class="big">' + cash(total) + '</span>' + (lb ? '<span class="gb">≈ ' + gbp(lb.g) + '</span>' : '') + (lbLine ? '<span class="gb rn"' + (lbNote ? '>' + lbNote : ' aria-hidden="true">&nbsp;') + '</span>' : '') + '</div>' +
    '<div class="perline">' +
    (canBack ? '<button class="pstep" data-a="rangeStep" data-v="1" aria-label="Earlier">‹</button>' : '') +
    // the period's name is a door to the calendar on that month (Q10)
    '<button class="plabel cal" data-a="calFromSpend" aria-label="' + esc(pick ? barLabel(pick, bs.weekly) : per.label) + '. Open the calendar"><span class="pt">' + esc(pick ? barLabel(pick, bs.weekly) : per.label) + '</span>' + ICON.cal + '</button>' +
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
// the bar picked on the chart, if any: {b, weekly}
function pickedBar(list) {
  if (U.bar == null) return null;
  const bs = buckets(list, period());
  return bs[U.bar] ? { b: bs[U.bar], weekly: bs.weekly } : null;
}
// "Show this week", "Show all of October", "Show all since 23 Oct": back to the whole period from a picked bar
function wholePeriod() {
  const per = period(),
    off = U.roff || 0;
  if (U.range === 'week') return off === 0 ? 'Show this week' : off === 1 ? 'Show last week' : 'Show the whole week';
  if (U.range === 'month') return 'Show all of ' + per.label;
  return 'Show ' + per.label.replace(/^Since/, 'all since');
}
function spendRows(list) {
  if (!D.purchases.length) return '<div class="grp"><div class="empty">Purchases you log on Home appear here.</div></div>';
  // a picked bar narrows the list to that day (or week), so the headline and the list say the same thing (Q10)
  const pk = pickedBar(list);
  let pickLine = '';
  if (pk) {
    pickLine =
      '<div class="pickline" id="pickLine"><span>Showing ' + esc(pk.weekly ? 'the week of ' + shortDate(pk.b.from) : dayHeading(pk.b.from)) + ' only</span>' +
      '<button class="tbtn" data-a="clearBar">' + esc(wholePeriod()) + '</button></div>';
    list = list.filter((p) => p.date >= pk.b.from && p.date <= pk.b.to);
  }
  if (!list.length)
    return (
      pickLine +
      '<div class="grp"><div class="empty">' + (U.cat !== 'all' || U.filter ? 'No purchases match.' : 'Nothing spent ' + (U.range === 'day' || (pk && !pk.weekly) ? 'on this day.' : pk ? 'in this week.' : 'in this period.')) +
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
    pickLine +
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
  segHTML('rangeSeg', 'Period', RANGES, U.range, 'range');
function scrSpending() {
  // nothing logged yet: no empty chart or range switch, just one calm card with the way in (Q08)
  if (!D.purchases.length)
    return (
      '<h1>Spending</h1><div class="card nospend">' + '<span class="ic" aria-hidden="true">' + ICON.spending + '</span><b>No spending yet</b>' +
      '<p>Log what you buy and it adds up here, by day and by category.</p>' +
      '<button class="cta pk-press-solid ink" data-a="newPurchase">Log a purchase</button></div>'
    );
  const list = spendingList();
  const counts = {};
  spendingList(true).forEach((p) => (counts[p.category] = (counts[p.category] || 0) + 1));
  const chips =
    D.purchases.length && Object.keys(counts).length
      ? '<div class="chips pk-static scroller" data-own-gesture="1" role="group" aria-label="Filter by category">' +
        [['all', 'All', Object.values(counts).reduce((a, b) => a + b, 0)]]
          .concat(CATS.filter((c) => counts[c]).map((c) => [c, c, counts[c]]))
          .map((c) => '<button class="chip pk-chip' + (U.cat === c[0] ? ' on' : '') + '" data-a="cat" data-v="' + esc(c[0]) + '" aria-pressed="' + (U.cat === c[0]) + '">' + (c[0] === 'all' ? '' : tileDot(c[0])) + esc(c[1]) + '<span class="n">' + c[2] + '</span></button>')
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
    (list.length ? '<button class="btn glass pk-press wide csv" data-a="csv">' + ICON.upload + 'Export as CSV</button><p class="foot">Exports the purchases shown above, for Numbers or Excel.</p>' : '');
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
    '<div class="swapline"><button type="button" class="circ swap pk-press" data-a="swapConv" aria-label="Swap currencies"' + (r ? '' : ' disabled') + '>' + ICON.swap + '</button></div>' +
    '<div class="cbox" data-c="' + bottom + '">' + convBox(bottom, r) + '</div>' +
    '</div>' +
    // the rate is the door to Rate history (Q23); Refresh stays beside it
    '<div class="raterow"><button class="rdoor" data-a="openHistory" aria-label="' + esc((r ? '£1 = ' + cash(r.value) + '. ' : '') + 'Rate history') + '"><span class="rtx"><b id="rateBadge">' + (r ? '£1 = ' + cash(r.value) : 'No rate yet') + '</b><small><span id="rateLine">' + esc(rateLine()) + '</span> · <em>Rate history</em></small></span>' + ICON.chev + '</button>' +
    '<button class="btn glass pk-press" id="refreshRate" data-a="refreshRate">' + ICON.refresh + 'Refresh</button></div>' +
    (r
      ? '<button class="btn glass pk-press wide" data-a="copyConv">' + ICON.copy + 'Copy conversion</button>' +
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
    lower = (s) => s.charAt(0).toLowerCase() + s.slice(1),
    h = HIST_CHECK,
    // Rate history's last check (Q23): only said when it failed, so the reason is one tap from the page
    hist = h && !h.ok ? 'History: couldn’t load · ' + lower(whenAgo(new Date(h.at))) + '<br>' + esc(h.why) : '';
  if (!c) return { t: hist, cls: 'wrap red' };
  const when = whenAgo(new Date(c.at)),
    fails = c.fails.map((f) => esc(f.source) + ': ' + esc(f.why)).join('<br>');
  if (c.ok) return { t: 'Loaded from ' + esc(c.source) + ' · ' + lower(when) + (fails ? '<br>Tried first: ' + fails : '') + (hist ? '<br>' + hist : ''), cls: hist ? 'wrap red' : 'wrap' };
  return { t: 'Couldn’t load a rate · ' + lower(when) + '<br>' + fails + (hist ? '<br>' + hist : ''), cls: 'wrap red' };
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
    row('clock', overdue || !lb ? 'orange' : 'gray', 'Last backed up', { t: lb ? whenAgo(lb) + (overdue ? ' · over two weeks ago' : '') : 'Not backed up yet', cls: overdue ? 'red' : '' }, 'exportBackup', ' id="lastBackupRow"') +
    '</div><p class="foot">iOS can clear a website’s data if it isn’t opened for a few weeks, so keep a recent backup in Files.</p>' +
    hdr('Your data') +
    '<div class="grp tiled set">' +
    row('tag', 'orange', 'Price notes', plural(D.observations.length, 'note'), 'openNotes') +
    row('bulb', 'indigo', 'Words Suki has learned', D.learned.length ? plural(D.learned.length, 'word') : 'Change a category in Smart add and Suki remembers the word', 'openLearned') +
    (SAFETY ? row('refresh', 'indigo', 'Before your last ' + (SAFETY.why === 'erase' ? 'erase' : 'restore'), plural((SAFETY.data.purchases || []).length, 'purchase') + ' · ' + whenAgo(new Date(SAFETY.at)), 'putBack') : '') +
    (RESCUE.length ? row('download', 'orange', 'Recovered data', plural(rescueCount(), 'record') + ' Suki couldn’t read, kept safe', 'openRescue') : '') +
    row('disk', 'gray', 'Storage used', '<span id="storageUsed">' + esc(STORAGE_USED) + '</span>') +
    '<button class="row danger" data-a="erase">' + stile('erase', 'red') + '<span class="lbl"><b>Erase all data</b><small>Purchases, price notes and the saved rate</small></span></button>' +
    '</div>' +
    hdr('This device') +
    '<div class="grp tiled set">' +
    row('access', 'blue', 'Accessibility', { t: 'Reduce motion: ' + { auto: 'Match iPhone', on: 'On', off: 'Off' }[MOTION.reducePref()] + (MOTION.speed() > 1 ? ' · Slow motion on' : '') }, 'openAccess') +
    '</div>' +
    '<div class="grp tiled set">' + row('help', 'blue', 'Help', 'Welcome, tips and hidden gestures', 'openHelp') + '</div>' +
    hdr('About') +
    '<div class="grp tiled set">' +
    row('wifi', 'teal', 'Works offline', '<span id="swStatus">' + esc(SW_STATE) + '</span>') +
    row('peso', 'indigo', 'Saved exchange rate', D.rate ? '£1 = ' + cash(D.rate.value) + ' · ' + shortDate(D.rate.date) + '<br>From ' + esc(D.rate.source) : 'Not loaded yet', 'goConvert') +
    (RATE_CHECK || (HIST_CHECK && !HIST_CHECK.ok) ? row('refresh', (RATE_CHECK ? RATE_CHECK.ok : true) && (!HIST_CHECK || HIST_CHECK.ok) ? 'green' : 'orange', 'Last rate check', rateCheckText()) : '') +
    row('book', 'green', 'Official prices', esc((R.source || '') + ' · ' + (R.area || '') + ' · ' + (R.period || ''))) +
    row('locate', 'blue', 'Towns for Location', 'Outlines from NAMRIA and PSA, through OCHA (CC BY-IGO)' + (window.sukiTowns && window.sukiTowns.psgc ? ' · PSGC ' + esc(window.sukiTowns.psgc.replace(/^(\d{4})-(\d)q$/i, 'Q$2 $1')) : '') + '<br>Found on your phone, never sent anywhere') +
    row('phone', 'blue', 'Add to your Home Screen', 'The steps, for a new phone', 'openAhs') +
    '<a class="row" href="https://github.com/imperialfox/Suki" target="_blank" rel="noopener">' + stile('code', 'ink') + '<span class="lbl"><b>View on GitHub</b></span>' + ICON.out + '</a>' +
    '</div>' +
    '<p class="ver">Suki ' + APP_VERSION + ' · ' + RELEASE_DATE + '</p>'
  );
}
