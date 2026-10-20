/* Suki · helpers.js
   Small helpers (money, dates, text, icons, layout) and the on-screen state (U).
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Text and money ===== */
const $ = (id) => document.getElementById(id);
const esc = (s) =>
  String(s == null ? '' : s).replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]
  );
const plural = (n, w, ws) => n + ' ' + (n === 1 ? w : ws || w + 's');
const fmt = {};
function cash(n, cur = 'PHP') {
  if (!fmt[cur]) fmt[cur] = new Intl.NumberFormat('en-GB', { style: 'currency', currency: cur });
  return fmt[cur].format(Number(n) || 0);
}
const gbp = (n) => cash(n, 'GBP');
const sum = (list) => Math.round(list.reduce((s, p) => s + (+p.price || 0), 0) * 100) / 100;
// a typed amount: "1,000" and " 12.5 " both work; anything else is null
const amount = (v) => {
  const n = parseFloat(String(v == null ? '' : v).replace(/,/g, '').trim());
  return Number.isFinite(n) ? n : null;
};

/* ===== Dates (British, and relative where it helps) ===== */
const atNoon = (iso) => new Date(iso + 'T12:00:00');
const dayDiff = (iso) => Math.round((atNoon(localISO()) - atNoon(iso)) / 864e5);
const shortDate = (iso) =>
  atNoon(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: atNoon(iso).getFullYear() === new Date().getFullYear() ? undefined : 'numeric',
  });
const longDate = (iso) =>
  atNoon(iso).toLocaleDateString('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: atNoon(iso).getFullYear() === new Date().getFullYear() ? undefined : 'numeric',
  });
// "today", "yesterday", "3 days ago", then the date
function relDay(iso) {
  const n = dayDiff(iso);
  if (n === 0) return 'Today';
  if (n === 1) return 'Yesterday';
  if (n > 1 && n < 7) return n + ' days ago';
  return shortDate(iso);
}
// headings for a day of purchases: Today, Yesterday, then "Monday 12 October"
function dayHeading(iso) {
  const n = dayDiff(iso);
  if (n === 0) return 'Today';
  if (n === 1) return 'Yesterday';
  return longDate(iso);
}
const fileDate = (d) => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
const timeOf = (d) => d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
function whenAgo(d) {
  const iso = localISO(d),
    n = dayDiff(iso);
  if (n === 0) return 'Today at ' + timeOf(d);
  if (n === 1) return 'Yesterday at ' + timeOf(d);
  return fileDate(d);
}

/* ===== Icons ===== */
const GL = (p, cls) => '<svg class="i' + (cls ? ' ' + cls : '') + '" viewBox="0 0 24 24" aria-hidden="true">' + p + '</svg>';
const ICON = {
  home: GL('<path d="m3.5 10.7 8.5-7 8.5 7"/><path d="M5.5 9.5v10h13v-10M9.5 19.5v-6h5v6"/>'),
  till: GL('<rect x="4" y="3" width="16" height="18" rx="2.5"/><path d="M7.5 7.5h9M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>'),
  search: GL('<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>'),
  spending: GL('<path d="M6 3.5h12v17l-2.4-1.6-3.6 1.6-3.6-1.6L6 20.5z"/><path d="M9 8h6M9 12h6M9 16h3"/>'),
  convert: GL('<path d="M4 8h15l-3-3"/><path d="M20 16H5l3 3"/>'),
  gear: GL(
    '<circle cx="12" cy="12" r="3.2"/><path d="M19.4 13.5a7.6 7.6 0 0 0 0-3l2-1.5-2-3.4-2.3.9a7.6 7.6 0 0 0-2.6-1.5L14.1 2.5h-4.2l-.4 2.5a7.6 7.6 0 0 0-2.6 1.5l-2.3-.9-2 3.4 2 1.5a7.6 7.6 0 0 0 0 3l-2 1.5 2 3.4 2.3-.9a7.6 7.6 0 0 0 2.6 1.5l.4 2.5h4.2l.4-2.5a7.6 7.6 0 0 0 2.6-1.5l2.3.9 2-3.4z"/>'
  ),
  back: GL('<path d="M15 5l-7 7 7 7"/>'),
  x: GL('<path d="M6 6l12 12M18 6 6 18"/>'),
  pencil: GL('<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>'),
  bin: GL('<path d="M4.5 7h15M10 11v6M14 11v6M6.5 7l1 12.5h9l1-12.5M9.5 7V4.5h5V7"/>'),
  chev: '<span class="chev" aria-hidden="true">›</span>',
  plus: GL('<path d="M12 5v14M5 12h14"/>'),
  copy: GL('<rect x="8.5" y="8.5" width="11" height="11" rx="2.5"/><path d="M15.5 8.5V6a1.5 1.5 0 0 0-1.5-1.5H6A1.5 1.5 0 0 0 4.5 6v8A1.5 1.5 0 0 0 6 15.5h2.5"/>'),
  refresh: GL('<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4h-4"/>'),
  out: GL('<path d="M14 4.5h5.5V10M19.5 4.5 11 13M17 14v4.5a1 1 0 0 1-1 1H5.5a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1H10"/>'),
  swap: GL('<path d="M8 4v16l-3.5-3.5M16 20V4l3.5 3.5"/>'),
  // Settings tiles
  upload: GL('<path d="M12 15V4M7.5 8.5 12 4l4.5 4.5M5 14v4.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V14"/>'),
  download: GL('<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5M5 14v4.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V14"/>'),
  clock: GL('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
  disk: GL('<ellipse cx="12" cy="6" rx="7.5" ry="2.8"/><path d="M4.5 6v12c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8V6M4.5 12c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8"/>'),
  wifi: GL('<path d="M3 9.5a13 13 0 0 1 18 0M6 12.8a8.5 8.5 0 0 1 12 0M9 16a4 4 0 0 1 6 0"/><circle cx="12" cy="19" r=".6"/>'),
  peso: GL('<path d="M8 20V4h5a4.5 4.5 0 0 1 0 9H8M5.5 7.5h13M5.5 10h13"/>'),
  book: GL('<path d="M4.5 5.5c3-1.5 5.5-1.2 7.5.5 2-1.7 4.5-2 7.5-.5v13c-3-1.5-5.5-1.2-7.5.5-2-1.7-4.5-2-7.5-.5zM12 6v13"/>'),
  phone: GL('<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>'),
  code: GL('<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4M13.5 5l-3 14"/>'),
  erase: GL('<path d="M4.5 7h15M10 11v6M14 11v6M6.5 7l1 12.5h9l1-12.5M9.5 7V4.5h5V7"/>'),
  tag: GL('<path d="M3.5 12V4.5a1 1 0 0 1 1-1H12l8.5 8.5-8.5 8.5z"/><circle cx="8" cy="8" r="1.4"/>'),
};

/* ===== Category tiles =====
   Purchases use the seven categories in CATS; catalogue items use their group. Both map onto these kinds. */
const KINDS = {
  food: '<circle cx="12" cy="13" r="7"/><path d="M5 13h14M8 4v2M5 4v2M17 4v5M19 4v5M18 9v3"/>',
  grocery: '<path d="M4 9h16l-1.5 11h-13zM8 9l4-5 4 5M8 13v4M12 13v4M16 13v4"/>',
  drink: '<path d="M6 5h12l-1.2 15H7.2zM8 9h8M14 5l3-3"/>',
  essentials: '<path d="M9 9.5h6v10.5a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1zM10.5 9.5V6h3v3.5M13.5 6h3M16.5 6v2"/>',
  transport: '<rect x="4" y="4" width="16" height="15" rx="3"/><path d="M7 4V2M17 4V2M4 11h16M8 15h.01M16 15h.01M7 19v2M17 19v2"/>',
  shopping: '<path d="M5 8h14l1 12H4zM9 8a3 3 0 0 1 6 0"/>',
  stay: '<path d="M4 19V6M4 13h16v6M4 10h5a3 3 0 0 1 3 3M12 13v-2a2 2 0 0 1 2-2h3a3 3 0 0 1 3 3"/>',
  activity: '<path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
  other: '<path d="M6 3.5h12v17l-2.4-1.6-3.6 1.6-3.6-1.6L6 20.5zM9 8h6M9 12h6M9 16h3"/>',
};
const CAT_KIND = {
  'Food & drink': 'food',
  Transport: 'transport',
  Groceries: 'grocery',
  Shopping: 'shopping',
  Accommodation: 'stay',
  Activities: 'activity',
  Other: 'other',
};
function kindOf(group) {
  if (CAT_KIND[group]) return CAT_KIND[group];
  const g = String(group || '');
  if (/inumin|drink/i.test(g)) return 'drink';
  if (/grocer|palengke/i.test(g)) return 'grocery';
  if (/essential|household/i.test(g)) return 'essentials';
  if (/ulam|meryenda|dessert|tinapay|kakanin|street|inihaw|pulutan|food/i.test(g)) return 'food';
  return 'other';
}
const tile = (group, big) =>
  '<span class="tile k-' + kindOf(group) + (big ? ' big' : '') + '" aria-hidden="true"><svg viewBox="0 0 24 24">' + KINDS[kindOf(group)] + '</svg></span>';
// a coloured Settings tile with a white glyph
const stile = (icon, colour) => '<span class="stile" style="background:' + colour + '" aria-hidden="true">' + ICON[icon] + '</span>';

/* ===== Layout: phone (compact), phone on its side (land), iPad or Mac window (reg), wide enough for a sidebar (wide) ===== */
const MQ = {
  reg: matchMedia('(min-width:700px) and (min-height:501px)'),
  wide: matchMedia('(min-width:1100px) and (min-height:501px)'),
  land: matchMedia('(orientation:landscape) and (max-height:500px)'),
};
const split = () => MQ.reg.matches;
function layout() {
  const b = document.body.classList;
  b.toggle('reg', MQ.reg.matches);
  b.toggle('wide', MQ.wide.matches);
  b.toggle('land', MQ.land.matches && !MQ.reg.matches);
}
const TABS = [
  ['home', 'Home', ICON.home],
  ['till', 'Till', ICON.till],
  ['search', 'Search', ICON.search],
  ['spending', 'Spending', ICON.spending],
  ['convert', 'Convert', ICON.convert],
];
const TAB_TITLE = { home: 'Home', till: 'Quick Till', search: 'Search', spending: 'Spending', convert: 'Convert', settings: 'Settings' };
// Settings opens from the gear on Home, so it belongs to Home
const tabOf = (t) => (t === 'settings' ? 'home' : t);

/* ===== On-screen state (not saved, except where noted) ===== */
const freshU = () => ({
  tab: 'home',
  sheet: null, // the sheet showing: purchase, edit, item, confirm, backup, restore, observations
  sd: {}, // that sheet's details
  stack: [], // sheets to return to when this one closes
  q: '', // the search box
  cat: 'all', // Spending's category chip
  filter: '', // Spending's filter box
  sel: null, // iPad and Mac: the purchase shown beside the list
  item: null, // iPad and Mac: the catalogue item shown beside the results
  more: false, // Home: "More details" open
  obsFor: null, // the item whose "Add a price note" form is open
  till: { bill: '', cash: '' },
  conv: { gbp: '100', php: '', last: 'gbp' },
});
let U = freshU();
