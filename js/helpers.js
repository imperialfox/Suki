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
// a peso amount in pounds at the saved rate, e.g. "≈ £1.23"; empty until a rate has loaded
function inGbp(n) {
  const r = D.rate;
  if (!r || !(r.value > 0) || !Number.isFinite(Number(n))) return '';
  const g = Number(n) / r.value;
  return '≈ ' + (g > 0 && g < 0.01 ? '<£0.01' : gbp(g));
}
// one purchase in pounds at its own rate, or today's when it has none (Q22)
const gbpThen = (p) => (p.rateAtPurchase > 0 ? '≈ ' + gbp(p.price / p.rateAtPurchase) : inGbp(p.price));
// the rate behind a purchase's pounds: "£1 = ₱83.11 · Thu 1 Oct · ECB", "· estimated" while it is (Q22)
function rateBehind(p) {
  if (!(p.rateAtPurchase > 0)) return '';
  const d = isoDate(p.rateDate) === p.rateDate ? atNoon(p.rateDate) : null,
    src = p.rateSource ? (/ECB|Frankfurter/i.test(p.rateSource) ? 'ECB' : p.rateSource) : '';
  return [
    '£1 = ' + cash(p.rateAtPurchase),
    // written out by hand: browsers disagree on a comma after the weekday ("Fri, 30 Oct")
    d && ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()] + ' ' + d.getDate() + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getMonth()] + (d.getFullYear() === new Date().getFullYear() ? '' : ' ' + d.getFullYear()),
    src,
    p.rateEstimated && 'estimated',
  ]
    .filter(Boolean)
    .map((s) => s.replace(/ /g, '\u00a0')) // a long line breaks between the parts, never inside one
    .join(' · ');
}
// purchases in pounds, each at the rate it was saved with, so a total doesn't drift as the rate moves (Q22).
// One with no rate counts at today's saved rate (today), and one whose day's rate is still to come is
// counted at the rate it has (est); the total says how many of each. null when there's no way to say
function poundsOf(list) {
  const r = D.rate && D.rate.value > 0 ? D.rate.value : 0;
  let g = 0,
    today = 0,
    est = 0;
  for (const p of list) {
    const pr = +p.price || 0;
    if (p.rateAtPurchase > 0) {
      g += pr / p.rateAtPurchase;
      if (p.rateEstimated) est++;
    } else if (r) {
      g += pr / r;
      today++;
    } else return null;
  }
  return { g: Math.round(g * 100) / 100, today, est };
}
// "2 at today's rate · 1 estimated", or '' when every purchase has its own day's rate
const poundsNote = (t) =>
  t ? [t.today && t.today + ' at today’s rate', t.est && t.est + ' estimated'].filter(Boolean).join(' · ') : '';
const sum = (list) => Math.round(list.reduce((s, p) => s + (+p.price || 0), 0) * 100) / 100;
// a typed amount: "1,000", "1 000", "₱12.50" and " 12.5 " all work; "12.50.5" or "abc" is null (Q06)
const amount = (v) => {
  const s = String(v == null ? '' : v).replace(/₱|php/gi, '').replace(/[,\s]/g, '');
  if (!/^(\d+\.?\d*|\.\d+)$/.test(s)) return null;
  const n = parseFloat(s);
  return Number.isFinite(n) ? n : null;
};
// the purchase form's amount box (Q14) also takes amounts as they're written on menus and said aloud:
// "P50", "PHP 50", "50 pesos", "2k", "₱1.5k". Anything else goes through amount()
function formAmount(v) {
  const m = String(v == null ? '' : v)
    .trim()
    .match(/^(?:p|₱|php)?\s*(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?|\.\d+)\s*(k)?\s*(?:pesos?|piso|php)?$/i);
  if (m) return parseFloat(m[1].replace(/,/g, '')) * (m[2] ? 1000 : 1);
  return amount(v);
}
// pesos to the centavo: anything that rounds to ₱0.00 doesn't count as an amount
const cents = (n) => (n === null ? null : Math.round(n * 100) / 100);

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
  tick: GL('<path d="m5 12.5 4.5 4.5L19 7.5"/>'),
  copy: GL('<rect x="8.5" y="8.5" width="11" height="11" rx="2.5"/><path d="M15.5 8.5V6a1.5 1.5 0 0 0-1.5-1.5H6A1.5 1.5 0 0 0 4.5 6v8A1.5 1.5 0 0 0 6 15.5h2.5"/>'),
  refresh: GL('<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4h-4"/>'),
  out: GL('<path d="M14 4.5h5.5V10M19.5 4.5 11 13M17 14v4.5a1 1 0 0 1-1 1H5.5a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1H10"/>'),
  swap: GL('<path d="M8 4v16l-3.5-3.5M16 20V4l3.5 3.5"/>'),
  locate: GL('<path d="M20 4 4 11l7 2 2 7z"/>'),
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
  chevdown: GL('<path d="M6 9l6 6 6-6"/>'),
  star: GL('<path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>'),
  bulb: GL('<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.4 1.1 2.2h5c0-.8.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>'),
  help: GL('<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.5a2.5 2.5 0 0 1 4.8.9c0 1.7-2.4 2-2.4 3.6M12 17h.01"/>'),
  access: GL('<circle cx="12" cy="4.8" r="1.6"/><path d="M5 8.5c2.4.8 4.7 1.2 7 1.2s4.6-.4 7-1.2M12 9.7v4.3M12 14l-3 6.5M12 14l3 6.5"/>'),
  tag: GL('<path d="M3.5 12V4.5a1 1 0 0 1 1-1H12l8.5 8.5-8.5 8.5z"/><circle cx="8" cy="8" r="1.4"/>'),
  mic: GL('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M9 21h6"/>'),
  cal: GL('<rect x="4" y="5" width="16" height="15" rx="2.5"/><path d="M4 10h16M8 3v4M16 3v4"/>'),
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
/* Item glyphs (Q04): every catalogue item gets a meaningful picture, coloured by its kind */
const GLYPH = {
  bowl: '<path d="M3.5 11h17a8.5 8.5 0 0 1-17 0zM8 19.5h8M9 7.5c0-1.5 1.5-1.5 1.5-3M13.5 7.5c0-1.5 1.5-1.5 1.5-3"/>',
  plate: '<circle cx="12" cy="12.5" r="8"/><circle cx="12" cy="12.5" r="4.5"/>',
  skewer: '<path d="m4 20 16-16M9.5 11.5l3 3M12.5 8.5l3 3"/><circle cx="9" cy="15" r="2.4"/><circle cx="13" cy="11" r="2.4"/><circle cx="17" cy="7" r="2.4"/>',
  cup: '<path d="M6.5 9h11l-1.4 11h-8.2zM5 9h14M12 9l2-5.5"/><path d="M8.5 9a3.5 3.5 0 0 1 7 0"/>',
  bread: '<path d="M5 11a3.5 3.5 0 0 1 1-6.9c1.8-.3 3.6.5 6-.1 2.4.6 4.2-.2 6 .1A3.5 3.5 0 0 1 19 11v8a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/>',
  dumpling: '<path d="M4 15c0-4.4 3.6-8 8-8s8 3.6 8 8zM4 15h16M9 9.5l.8 2M12 8.5v2M15 9.5l-.8 2"/>',
  rice: '<path d="M7.5 7.5 6 20h12l-1.5-12.5zM7.5 7.5h9M9.5 4.5l2.5 3 2.5-3"/><path d="M10 13.5h.01M12.5 12.5h.01M14 15h.01M11 16h.01"/>',
  egg: '<path d="M12 3.5c3.6 0 6.5 5.6 6.5 10a6.5 6.5 0 0 1-13 0c0-4.4 2.9-10 6.5-10z"/>',
  meat: '<path d="M14.5 4.5c3.2 0 5.5 2.3 5.5 5.2 0 5-5.4 9.8-11 9.8-2.8 0-5-1.6-5-4.3 0-3.5 3.6-4.3 5.3-6.6 1.3-1.9 2.4-4.1 5.2-4.1z"/><circle cx="14.2" cy="9.6" r="1.8"/>',
  drumstick: '<path d="M14.5 3.5a6 6 0 0 1 3.9 10.6l-3.4 1-5.1 5.1a1.9 1.9 0 0 1-2.7-2.7l-.4-.4a1.9 1.9 0 0 1-2.7-2.7 1.9 1.9 0 0 1 2.7 0l.4.4L12.3 9l1-3.4a6 6 0 0 1 1.2-2.1z"/>',
  fish: '<path d="M3.5 12c2.6-3.6 6-5.5 9.5-5.5 3.5 0 6 2.4 7.5 5.5-1.5 3.1-4 5.5-7.5 5.5-3.5 0-6.9-1.9-9.5-5.5zM3.5 12 2 8.5M3.5 12 2 15.5"/><circle cx="16" cy="11" r=".7"/>',
  veg: '<path d="M12 8.5c4 0 7 3 7 6.5S15.9 20.5 12 20.5 5 18.5 5 15s3-6.5 7-6.5zM12 8.5c0-2 .5-4 2.5-5M12 8.5C11 6.5 9 5.5 7.5 5.5"/>',
  bottle: '<path d="M10 3.5h4M10.5 3.5v3.2c-1.8.9-3 2.7-3 4.8v8a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1v-8c0-2.1-1.2-3.9-3-4.8V3.5M7.5 13h9"/>',
  water: '<path d="M10 3h4M10.5 3v2.5l-2 2.5v12a1 1 0 0 0 1 1h5a1 1 0 0 0 1-1V8l-2-2.5V3M8.5 11h7M8.5 15h7"/>',
  can: '<rect x="6.5" y="4" width="11" height="16" rx="2.5"/><path d="M6.5 8h11M6.5 16h11"/>',
  coffee: '<path d="M5 9h11v6a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5zM16 10.5h1.5a2.5 2.5 0 0 1 0 5H16M9 3.5v2.5M12 3.5v2.5"/>',
  carton: '<path d="M7 8 9 4h6l2 4v11.5a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1zM7 8h10M12 11v5"/>',
  beer: '<path d="M6 7h9v12.5a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1zM15 9.5h2a2 2 0 0 1 2 2V14a2 2 0 0 1-2 2h-2M6 7a2.5 2.5 0 0 1 2.5-3.2c.7-.8 2.6-.8 3.3 0A2.5 2.5 0 0 1 15 7M9 11v6M12 11v6"/>',
  noodles: '<path d="M3.5 12h17a8.5 8.5 0 0 1-17 0zM15 12 20.5 3.5M12.5 12 16 3.5M7 12c0-2 1.5-2 1.5-4M10 12c0-2 1.5-2 1.5-4"/>',
  jar: '<path d="M8 4h8M8.5 4v2.5C6.7 7.5 6 9 6 11v8a1.5 1.5 0 0 0 1.5 1.5h9A1.5 1.5 0 0 0 18 19v-8c0-2-.7-3.5-2.5-4.5V4"/><path d="M10 13h.01M13.5 12h.01M12 15.5h.01"/>',
  soap: '<rect x="4" y="9" width="16" height="10" rx="4"/><circle cx="9" cy="5" r="1.6"/><circle cx="14" cy="4" r="1"/>',
  tube: '<path d="M8 3.5h8l-1 14H9zM10 17.5v3h4v-3M9 8h6"/>',
  box: '<path d="M4.5 8 12 4l7.5 4v8.5L12 20.5l-7.5-4zM4.5 8 12 12l7.5-4M12 12v8.5"/>',
  burger: '<path d="M4.5 10.5a7.5 5.5 0 0 1 15 0zM4 13.5h16M4.5 16.5h15a3 3 0 0 1-3 3h-9a3 3 0 0 1-3-3z"/>',
  jeep: '<path d="M4 16V9.5l2-4h12l2 4V16zM4 12.5h16M8 16v2.5M16 16v2.5M3 9.5h18"/><circle cx="7.5" cy="14" r=".6"/><circle cx="16.5" cy="14" r=".6"/>',
  bus: '<rect x="5" y="3.5" width="14" height="15" rx="3"/><path d="M5 11h14M5 7h14M8 18.5v2M16 18.5v2"/><circle cx="8.5" cy="14.5" r=".6"/><circle cx="15.5" cy="14.5" r=".6"/>',
  trike: '<circle cx="6" cy="17" r="2.5"/><circle cx="18" cy="17" r="2.5"/><path d="M8.5 17h7M6 14.5 9 9h4l2 5M13 9V6h5v8.5M15 14.5h3"/>',
  car: '<path d="M4 15.5v-3l2.2-5h11.6l2.2 5v3zM4 15.5V18h3v-2.5M17 15.5V18h3v-2.5M4 12.5h16"/><circle cx="7.5" cy="14" r=".6"/><circle cx="16.5" cy="14" r=".6"/>',
  train: '<rect x="6" y="3.5" width="12" height="14" rx="3"/><path d="M6 10h12M9 17.5 7 21M15 17.5l2 3.5M10 6.5h4"/><circle cx="9.5" cy="14" r=".6"/><circle cx="14.5" cy="14" r=".6"/>',
  sim: '<path d="M7 3.5h7.5L18 7v12.5a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-15a1 1 0 0 1 1-1z"/><rect x="9" y="11" width="6" height="6" rx="1"/>',
  signal: '<path d="M5 19.5v-3M9.5 19.5v-6M14 19.5v-9M18.5 19.5V5"/>',
  washer: '<rect x="4.5" y="3.5" width="15" height="17" rx="2.5"/><circle cx="12" cy="13" r="4.5"/><path d="M4.5 7.5h15M8 5.5h.01"/>',
  scissors: '<circle cx="6.5" cy="17" r="2.5"/><circle cx="17.5" cy="17" r="2.5"/><path d="M8.5 15.5 18 4M15.5 15.5 6 4"/>',
  fruit: '<path d="M12 7.5c4.1 0 7 3.4 7 7.2 0 3.4-2.7 5.8-7 5.8s-7-2.4-7-5.8c0-3.8 2.9-7.2 7-7.2zM12 7.5V4.5M12 6c1-1.8 3-2.5 4.5-2"/>',
  pill: '<rect x="3.6" y="8.4" width="16.8" height="7.2" rx="3.6" transform="rotate(-45 12 12)"/><path d="m9.5 9.5 5 5"/>',
  hand: '<path d="M8 13V6a1.5 1.5 0 0 1 3 0v5.5M11 11V4.5a1.5 1.5 0 0 1 3 0V11M14 11V6a1.5 1.5 0 0 1 3 0v8c0 3.6-2.5 6.5-6 6.5-2.6 0-4.3-1.4-5.5-3.6L4 13.5a1.5 1.5 0 0 1 2.6-1.5L8 14"/>',
};
const ITEM_GLYPH = {
  bowl: 'adobo-p adobo-c sinigang-p sinigang-h tinola menudo afritada karekare paksiw giniling laing pinakbet lugaw carinderia',
  plate: 'sisig talong pm1',
  skewer: 'liempo kwek fishball isaw bananacue kikiam turon',
  cup: 'taho halo leche',
  bread: 'pandesal ensaymada puto bibingka tasty',
  dumpling: 'siomai',
  rice: 'bigas',
  egg: 'itlog',
  meat: 'baboy baka',
  drumstick: 'manok chickenjoy chickenmcdo',
  fish: 'isda bangus tilapia pusit',
  veg: 'sibuyas bawang kamatis patatas ampalaya talong-gulay pechay sitaw kalabasa repolyo karot sayote habichuelas sili luya',
  fruit: 'mangga saging kalamansi papaya pakwan suha melon abokado',
  pill: 'paracetamol ors cetirizine loperamide',
  bottle: 'mantika toyo suka gatorade shampoo',
  water: 'tubig',
  can: 'softdrinks sardinas cornedbeef',
  coffee: 'kape latte',
  carton: 'gatas milo',
  beer: 'beer',
  noodles: 'noodles',
  jar: 'asin asukal',
  soap: 'sabon',
  tube: 'toothpaste',
  box: 'detergent',
  burger: 'yumburger',
  jeep: 'jeepney',
  bus: 'bus-city bus-sanjose bus-naia uv',
  trike: 'tricycle',
  car: 'grab taxi taxi-naia',
  train: 'mrt3 lrt1 lrt2',
  sim: 'sim sim-tourist',
  signal: 'data',
  washer: 'laundry',
  scissors: 'haircut',
  hand: 'massage',
};
const glyphFor = {};
Object.keys(ITEM_GLYPH).forEach((g) => ITEM_GLYPH[g].split(' ').forEach((id) => (glyphFor[id] = g)));
// a category or catalogue tile; give an item id to draw that item's own glyph
const tile = (group, big, id) =>
  '<span class="tile k-' + (group === 'Services' ? 'service' : kindOf(group)) + (big ? ' big' : '') + '" aria-hidden="true"><svg viewBox="0 0 24 24">' +
  (id && glyphFor[id] ? GLYPH[glyphFor[id]] : KINDS[kindOf(group)]) + '</svg></span>';
// a coloured Settings tile with a white glyph
const stile = (icon, colour) => '<span class="stile" style="background:var(--sys-' + colour + ')" aria-hidden="true">' + ICON[icon] + '</span>';

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
// Apple devices use Cmd for shortcuts (and show ⌘); others use Ctrl
const APPLE = /Mac|iPhone|iPad|iPod/.test(navigator.platform || '') || /Macintosh|iPhone|iPad/.test(navigator.userAgent || '');
const TABS = [
  ['home', 'Home', ICON.home],
  ['till', 'Till', ICON.till],
  ['search', 'Search', ICON.search],
  ['spending', 'Spending', ICON.spending],
  ['convert', 'Convert', ICON.convert],
];
const TAB_TITLE = { home: 'Home', till: 'Quick Till', search: 'Search', spending: 'Spending', convert: 'Convert', settings: 'Settings' };
// Settings opens from the gear on Home, so it belongs to Home
// Rate history is pushed from Convert, so it belongs to Convert (Q23)
const tabOf = (t) => (t === 'settings' || t === 'help' ? 'home' : t === 'history' ? 'convert' : t);

/* ===== On-screen state (not saved, except where noted) ===== */
const freshU = () => ({
  tab: 'home',
  sheet: null, // the sheet showing: purchase, edit, item, confirm, backup, restore, observations
  sd: {}, // that sheet's details
  stack: [], // sheets to return to when this one closes
  q: '', // the search box
  scat: 'all', // Search's category chip (Q02)
  cat: 'all', // Spending's category chip
  range: 'all', // Spending's period: day, week, month or all
  roff: 0, // how many periods back the arrows have stepped
  bar: null, // the bar picked on Spending's chart (its index), or null for the whole period
  shown: 60, // how many purchases Spending's list draws before "Show more"
  calM: null, // the calendar sheet's month (YYYY-MM-01) and picked day
  calD: null,
  filter: '', // Spending's filter box
  sel: null, // iPad and Mac: the purchase shown beside the list
  item: null, // iPad and Mac: the catalogue item shown beside the results
  more: false, // Home: "More details" open
  obsFor: null, // the item whose "Add a price note" form is open
  dot: null, // the item sheet's price range strip: the lit dot and row ('paid:<id>' or 'note:<id>'), or null (Q12)
  till: { bill: '', cash: '' },
  conv: { gbp: '100', php: '', last: 'gbp', top: 'gbp' }, // top: which currency you type into first (the swap button flips it)
});
let U = freshU();

/* ===== Calendar tints (Q12) =====
   A month's spending days in three steps, by thirds of that month's days ranked by amount: the lightest third is 1,
   the strongest is 3. Days with the same amount share a step (their average rank), so a month of equal days sits in
   the middle. Fewer than three days are too few to compare, so they all get the middle step. */
function tintSteps(spent) {
  const days = Object.keys(spent).filter((d) => spent[d] > 0),
    n = days.length,
    out = {};
  if (n < 3) {
    days.forEach((d) => (out[d] = 2));
    return out;
  }
  const c = (d) => Math.round(spent[d] * 100),
    sorted = days.slice().sort((a, b) => c(a) - c(b));
  for (let i = 0; i < n; ) {
    let j = i;
    while (j + 1 < n && c(sorted[j + 1]) === c(sorted[i])) j++;
    const rank = (i + j) / 2;
    for (let k = i; k <= j; k++) out[sorted[k]] = 1 + Math.min(2, Math.floor((rank * 3) / n));
    i = j + 1;
  }
  return out;
}

