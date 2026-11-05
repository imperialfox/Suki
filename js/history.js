/* Suki · history.js (Q23)
   Rate history: how the pound-to-peso rate has moved, and why. Pushed from Convert's rate row.

   The history never depends on one service. Four layers, used in this order:
     1. Saved on the phone (IndexedDB 'suki-rates'), so only the missing days are asked for.
     2. Frankfurter's ECB series, live: v2, then v1. Each reply is checked whole (dates in order, every rate inside
        RATE_RANGE, no day jumping more than HIST_JUMP from the one before) and a bad one is refused whole.
     3. The snapshot shipped with the app (js/ratesnap.js, from 2016), cached by the service worker like every file.
     4. Suki's own daily record: every rate Suki loads for Convert, from any source, kept with its source. Used only
        where the ECB has no figure, and drawn as hollow dots, never as part of the ECB line.
   One year (and the snapshot) is all that's needed first; the years before 2016 load only when All is tapped.
   None of it is his data, so none of it is in backups, and saved history that can't be read is thrown away and
   loaded again. Only the currencies are ever sent.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const HIST_DB = 'suki-rates';
const HIST_JUMP = 0.1; // the biggest real one-day move since 2005 is 6.8% (the day after the EU referendum)
const HIST_FIRST = '2005-04-01'; // the ECB's first peso rate
const HIST_TIMEOUT = 10000;
const HIST_GAP = 30 * 60e3; // ask again for new days at most every half hour
const NEWS_STALE = 31; // days after which "News checked" says it's over a month old
const HIST_RANGES = [
  ['M', 'M', 'A month'],
  ['6M', '6M', '6 months'],
  ['Y', 'Y', 'A year'],
  ['5Y', '5Y', '5 years'],
  ['All', 'All', 'All since 2005'],
];
const HIST_SOURCES = [
  {
    name: 'frankfurter.dev (v2)',
    url: (a, b) => 'https://api.frankfurter.dev/v2/providers/ecb/rates?from=' + a + '&to=' + b + '&base=GBP&quotes=PHP,USD',
    // an array of {date, base, quote, rate}, one per currency per day
    read: (j) => {
      if (!Array.isArray(j)) throw new Error('not a list of rates');
      const out = [];
      for (const x of j) {
        if (!x || typeof x.date !== 'string') throw new Error('a rate without a date');
        let d = out[out.length - 1];
        if (!d || d.d !== x.date) {
          if (d && x.date < d.d) throw new Error('dates out of order');
          out.push((d = { d: x.date, php: null, usd: null }));
        }
        if (x.quote === 'PHP') d.php = Number(x.rate);
        if (x.quote === 'USD') d.usd = Number(x.rate);
      }
      return out;
    },
  },
  {
    name: 'frankfurter.dev (v1)',
    url: (a, b) => 'https://api.frankfurter.dev/v1/' + a + '..' + b + '?base=GBP&symbols=PHP,USD',
    // {rates: {"2026-10-30": {PHP, USD}, …}}, in date order
    read: (j) => {
      if (!j || !j.rates || typeof j.rates !== 'object' || Array.isArray(j.rates)) throw new Error('no rates in the reply');
      return Object.keys(j.rates).map((d) => ({ d, php: Number(j.rates[d] && j.rates[d].PHP), usd: j.rates[d] && j.rates[d].USD != null ? Number(j.rates[d].USD) : null }));
    },
  },
];

/* ===== Dates, written out by hand: browsers disagree on commas ("Fri, 30 Oct") ===== */
const H_MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const H_MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const H_WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const H_WDAY = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const hT = (d) => Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10));
const hISO = (t) => new Date(t).toISOString().slice(0, 10);
const hAdd = (d, n) => hISO(hT(d) + n * 864e5);
const hReal = (d) => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d) && hISO(hT(d)) === d;
function hDate(d, how) {
  const x = new Date(hT(d)),
    dd = x.getUTCDate(),
    m = x.getUTCMonth(),
    y = x.getUTCFullYear(),
    thisYear = y === new Date().getFullYear();
  if (how === 'wk') return H_WD[x.getUTCDay()] + ' ' + dd + ' ' + H_MON[m] + (thisYear ? '' : ' ' + y); // Fri 30 Oct
  if (how === 'day') return H_WDAY[x.getUTCDay()] + ' ' + dd + ' ' + H_MON[m]; // Friday 30 Oct
  if (how === 'long') return H_WDAY[x.getUTCDay()] + ' ' + dd + ' ' + H_MONTH[m] + ' ' + y; // Friday 30 October 2026
  if (how === 'full') return dd + ' ' + H_MONTH[m] + ' ' + y; // 30 October 2026
  if (how === 'my') return H_MON[m] + ' ' + y; // Oct 2026
  if (how === 'monthyear') return H_MONTH[m] + ' ' + y; // October 2026
  if (how === 'year') return dd + ' ' + H_MON[m] + ' ' + y; // 30 Oct 2026
  return dd + ' ' + H_MON[m] + (thisYear ? '' : ' ' + y); // 30 Oct, or 30 Oct 2025
}
// the weekday that should have the newest ECB rate: today on a weekday, else the Friday before
const hWorkday = (d) => {
  const wd = new Date(hT(d)).getUTCDay();
  return wd === 6 ? hAdd(d, -1) : wd === 0 ? hAdd(d, -2) : d;
};

/* ===== The layers in memory ===== */
const H = {
  ecb: {}, // days from Frankfurter saved on the phone: {date: [php, usd]}
  own: {}, // Suki's own daily record: {date: {php, src}}
  older: false, // the years before the snapshot have loaded
  series: null, // the merged ECB series, sorted (snapshot + saved), rebuilt when either changes
  busy: false,
  olderBusy: false,
  olderFail: null,
  askedAt: 0,
  fail: null, // why the last top-up failed, for the page
  threw: false, // saved history couldn't be read and was thrown away
};
let HIST_CHECK = null; // the last history check this session, for Settings › Last rate check: {at, ok, why}
let HREADY = null;
let SNAP = null;
function snapDays() {
  if (SNAP) return SNAP;
  SNAP = {};
  const s = window.sukiRateSnap;
  if (!s || !Array.isArray(s.days) || !hReal(s.from)) return SNAP;
  let t = hT(s.from);
  for (const r of s.days) {
    if (!Array.isArray(r) || r.length < 3) continue;
    t += r[0] * 864e5;
    SNAP[hISO(t)] = [r[1] / 100, r[2] / 1e4];
  }
  return SNAP;
}
// the ECB series as one sorted list: [{d, php, usd}]
function histSeries() {
  if (H.series) return H.series;
  const all = Object.assign({}, snapDays(), H.ecb);
  H.series = Object.keys(all)
    .sort()
    .map((d) => ({ d, php: all[d][0], usd: all[d][1] }));
  return H.series;
}
// Suki's own record, only on days the ECB has no figure: [{d, php, src}]. Today's saved rate counts too
function ownPoints() {
  const ecb = new Set(histSeries().map((x) => x.d)),
    own = Object.assign({}, H.own);
  if (D.rate && hReal(D.rate.date) && D.rate.value > 0) own[D.rate.date] = { php: D.rate.value, src: D.rate.source || '' };
  return Object.keys(own)
    .sort()
    .filter((d) => !ecb.has(d))
    .map((d) => ({ d, php: own[d].php, src: own[d].src }));
}
const isECB = (src) => /ECB|Frankfurter/i.test(src || '');

/* ===== Saved on the phone: its own small database, away from his records ===== */
let HDB = null;
function hdb() {
  return (
    HDB ||
    (HDB = new Promise((resolve) => {
      if (!('indexedDB' in window)) return resolve(null);
      let r;
      try {
        r = indexedDB.open(HIST_DB, 1);
      } catch (e) {
        return resolve(null);
      }
      r.onupgradeneeded = () => {
        if (!r.result.objectStoreNames.contains('kv')) r.result.createObjectStore('kv');
      };
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => resolve(null);
      r.onblocked = () => resolve(null);
    }))
  );
}
function hTx(mode, fn) {
  return hdb().then(
    (db) =>
      new Promise((resolve) => {
        if (!db) return resolve(undefined);
        try {
          const t = db.transaction('kv', mode),
            q = fn(t.objectStore('kv'));
          t.oncomplete = () => resolve(mode === 'readonly' ? q.result : true);
          t.onerror = () => resolve(mode === 'readonly' ? undefined : false);
          t.onabort = () => resolve(mode === 'readonly' ? undefined : false);
        } catch (e) {
          resolve(mode === 'readonly' ? undefined : false);
        }
      })
  );
}
const hGet = (k) => hTx('readonly', (s) => s.get(k));
const hPut = (k, v) => hTx('readwrite', (s) => s.put(v, k));
const hDel = (k) => hTx('readwrite', (s) => s.delete(k));
const hSaveECB = () => hPut('ecb', { v: 1, days: H.ecb, older: H.older });
const hSaveOwn = () => hPut('own', { v: 1, days: H.own });

// saved ECB days, checked like a reply; null if anything about them is wrong
function cleanECB(o) {
  if (!o || typeof o !== 'object' || !o.days || typeof o.days !== 'object' || Array.isArray(o.days)) return null;
  const list = Object.keys(o.days)
    .sort()
    .map((d) => ({ d, php: Array.isArray(o.days[d]) ? o.days[d][0] : NaN, usd: Array.isArray(o.days[d]) ? o.days[d][1] : NaN }));
  try {
    histCheck(list, HIST_FIRST, hAdd(localISO(), 1));
  } catch (e) {
    return null;
  }
  const days = {};
  list.forEach((x) => (days[x.d] = [x.php, x.usd]));
  return { days, older: o.older === true };
}
function cleanOwn(o) {
  if (!o || typeof o !== 'object' || !o.days || typeof o.days !== 'object' || Array.isArray(o.days)) return null;
  const days = {};
  for (const d of Object.keys(o.days)) {
    const x = o.days[d];
    if (!hReal(d) || !x || typeof x !== 'object' || !(x.php >= RATE_RANGE[0] && x.php <= RATE_RANGE[1]) || typeof x.src !== 'string' || x.src.length > 80) return null;
    days[d] = { php: x.php, src: x.src };
  }
  return days;
}
function histInit() {
  return (
    HREADY ||
    (HREADY = (async () => {
      const [e, o] = await Promise.all([hGet('ecb'), hGet('own')]);
      if (e !== undefined) {
        const c = cleanECB(e);
        if (c) {
          // anything added this session (before the saved copy was read) wins
          H.ecb = Object.assign(c.days, H.ecb);
          H.older = H.older || c.older;
        } else {
          H.threw = true;
          await hDel('ecb');
        }
      }
      if (o !== undefined) {
        const c = cleanOwn(o);
        if (c) H.own = Object.assign(c, H.own);
        else await hDel('own');
      }
      H.series = null;
    })())
  );
}

/* ===== Asking Frankfurter, and checking what comes back ===== */
// the whole reply, or an error saying why not: dates real, in order and in the range asked; pesos inside RATE_RANGE;
// dollars sensible; no day more than HIST_JUMP from the one before (including the saved day before the reply)
function histCheck(days, a, b, before) {
  let prev = before && hT(days.length ? days[0].d : a) - hT(before.d) <= 7 * 864e5 ? before : null;
  for (const x of days) {
    if (!hReal(x.d)) throw new Error('a bad date');
    if (x.d > b || x.d < hAdd(a, -7)) throw new Error('a day outside the dates asked for');
    if (!Number.isFinite(x.php) || x.php < RATE_RANGE[0] || x.php > RATE_RANGE[1]) throw new Error('rate out of range (' + x.php + ')');
    if (x.usd != null && !(Number.isFinite(x.usd) && x.usd >= 0.8 && x.usd <= 3)) throw new Error('a bad dollar rate');
    if (prev) {
      if (x.d <= prev.d && prev !== before) throw new Error('dates out of order');
      if (x.d > prev.d && hT(x.d) - hT(prev.d) <= 7 * 864e5 && Math.abs(x.php / prev.php - 1) > HIST_JUMP) throw new Error('a day jumps more than ' + Math.round(HIST_JUMP * 100) + '%');
    }
    if (!prev || x.d > prev.d) prev = x;
  }
  return days;
}
async function histFrom(src, a, b, before) {
  const ctl = new AbortController(),
    t = setTimeout(() => ctl.abort(), HIST_TIMEOUT);
  let r, j;
  try {
    r = await fetch(src.url(a, b), { cache: 'no-store', signal: ctl.signal });
  } catch (e) {
    throw new Error(e && e.name === 'AbortError' ? 'timed out' : 'blocked or unreachable');
  } finally {
    clearTimeout(t);
  }
  if (!r.ok) throw new Error('error ' + r.status);
  try {
    j = await r.json();
  } catch (e) {
    throw new Error('unreadable reply');
  }
  return histCheck(src.read(j), a, b, before);
}
// days a..b from the first source that answers with a reply that passes every check
async function histFetch(a, b) {
  const s = histSeries(),
    before = s.filter((x) => x.d < a).pop() || null,
    fails = [];
  for (const src of HIST_SOURCES) {
    if (fails.filter((f) => /timed out/.test(f)).length >= 2) break;
    try {
      return await histFrom(src, a, b, before);
    } catch (e) {
      fails.push(src.name + ': ' + e.message);
    }
  }
  throw new Error(fails.join('; '));
}
function histMerge(days) {
  let n = 0;
  const have = histSeries();
  const known = new Set(have.map((x) => x.d));
  for (const x of days) {
    if (!known.has(x.d)) n++;
    H.ecb[x.d] = [x.php, x.usd];
  }
  H.series = null;
  return n;
}
// ask only for the days since the newest one Suki has: a few rates, not a year. With nothing saved and no
// snapshot, the last year first, then the rest of the gap
async function histTopUp(force) {
  await histInit();
  if (H.busy || !navigator.onLine) return;
  const s = histSeries(),
    today = localISO(),
    last = s.length ? s[s.length - 1].d : null;
  if (last && last >= hWorkday(today)) return;
  if (!force && Date.now() - H.askedAt < HIST_GAP) return;
  H.busy = true;
  H.askedAt = Date.now();
  histRedraw();
  const yearAgo = hAdd(today, -366),
    from = last ? hAdd(last, 1) : yearAgo,
    parts = from < yearAgo ? [[yearAgo, today], [from, hAdd(yearAgo, -1)]] : [[from, today]];
  try {
    for (const [a, b] of parts) {
      const got = await histFetch(a, b);
      histMerge(got);
      await hSaveECB();
      histRedraw();
    }
    H.fail = null;
    HIST_CHECK = { at: new Date().toISOString(), ok: true };
  } catch (e) {
    H.fail = e.message;
    HIST_CHECK = { at: new Date().toISOString(), ok: false, why: e.message };
  } finally {
    H.busy = false;
  }
  histRedraw();
}
// the years before the snapshot (from April 2005), only when All is tapped
async function histOlder() {
  await histInit();
  const s = histSeries(),
    first = s.length ? s[0].d : null;
  if (!first || first <= HIST_FIRST) H.older = true;
  if (H.older || H.olderBusy || !navigator.onLine) return;
  H.olderBusy = true;
  H.olderFail = null;
  histRedraw();
  try {
    histMerge(await histFetch(HIST_FIRST, hAdd(first, -1)));
    H.older = true;
    await hSaveECB();
  } catch (e) {
    H.olderFail = e.message;
    HIST_CHECK = { at: new Date().toISOString(), ok: false, why: 'older years: ' + e.message };
  } finally {
    H.olderBusy = false;
  }
  histRedraw();
}
// layer 4: every rate Suki loads for Convert, from whichever source answered, kept with its source (called by refreshRate)
async function histKeep(date, php, src) {
  if (!hReal(date) || !(php >= RATE_RANGE[0] && php <= RATE_RANGE[1])) return;
  await histInit();
  H.own[date] = { php, src: String(src || '').slice(0, 80) };
  await hSaveOwn();
}

/* ===== What the page shows ===== */
const HV = { range: 'Y', showAll: false }; // the page's own state, this session only
let HSCRUB = null, // a finger on the chart: {id, d, ev}
  HPEND = false, // a redraw waited for the finger to lift
  HGEO = null; // the chart's geometry, for the finger
const gbpTop = () => U.conv.top !== 'php';
const hVal = (php) => (gbpTop() ? php : 100 / php);
const hFmt = (v) => (gbpTop() ? cash(v) : '£' + v.toLocaleString('en-GB', { minimumFractionDigits: 3, maximumFractionDigits: 3 }));
const hUnit = () => (gbpTop() ? 'per £1' : 'per ₱100');
const peso0 = (n) => '₱' + Math.round(n).toLocaleString('en-GB');
function hStart(range, end) {
  const y = +end.slice(0, 4),
    m = +end.slice(5, 7) - 1,
    d = +end.slice(8, 10),
    at = (yy, mm) => hISO(Date.UTC(yy, mm, Math.min(d, new Date(Date.UTC(yy, mm + 1, 0)).getUTCDate())));
  if (range === 'M') return at(y, m - 1);
  if (range === '6M') return at(y, m - 6);
  if (range === 'Y') return at(y - 1, m);
  if (range === '5Y') return at(y - 5, m);
  return '0000-00-00';
}
const H_AGO = { M: 'a month ago', '6M': '6 months ago', Y: 'a year ago', '5Y': '5 years ago' };
const H_PER = { M: 'month', '6M': '6 months', Y: 'year', '5Y': '5 years', All: 'whole history' };
const H_WHY = { M: 'past month', '6M': 'past 6 months', Y: 'past year', '5Y': 'past 5 years' };
// the points in the range picked, from the newest day Suki has
function hPoints() {
  const s = histSeries();
  if (!s.length) return [];
  const st = hStart(HV.range, s[s.length - 1].d);
  return s.filter((x) => x.d >= st);
}
const hNotes = () => ((window.sukiNews && window.sukiNews.notes) || []).filter((n) => hReal(n.date) && n.date <= localISO());
const newsKey = (n) => n.date + '|' + n.side;
const newsChecked = () => (window.sukiNews && hReal(window.sukiNews.checked) ? window.sukiNews.checked : null);
function hNotesIn(pts) {
  if (!pts.length) return [];
  const ck = newsChecked() || localISO();
  return hNotes().filter((n) => n.date >= pts[0].d && n.date <= ck);
}
// "Since your trip started": the first purchase of the latest unbroken stretch (no gap of 14 days or more), while
// it's still going (the newest purchase under 14 days ago). A test entry logged weeks before doesn't count
function tripStart() {
  const today = localISO(),
    days = [...new Set(D.purchases.map((p) => p.date).filter((d) => hReal(d) && d <= today))].sort();
  if (!days.length || (hT(today) - hT(days[days.length - 1])) / 864e5 >= 14) return null;
  let s = days[days.length - 1];
  for (let i = days.length - 2; i >= 0; i--) {
    if ((hT(s) - hT(days[i])) / 864e5 >= 14) break;
    s = days[i];
  }
  return s;
}
// the ECB rate on a day (the last one published on or before it)
function hOn(d, pts) {
  let r = null;
  for (const x of pts) {
    if (x.d > d) break;
    r = x;
  }
  return r || pts[0] || null;
}

function scrHistory() {
  return (
    '<h1>Rate history</h1>' +
    segHTML('hSeg', 'Range', HIST_RANGES, HV.range, 'hRange', 'hseg') +
    '<div id="hbody">' + histBody() + '</div>'
  );
}
function histBody() {
  const pts = hPoints(),
    none = !pts.length;
  return (
    '<div class="hcols"><div class="hmain">' +
    '<div class="hhead" id="hHead">' + headHTML(pts) + '</div>' +
    '<div class="hstatus" id="hStatus">' + statusHTML(pts) + '</div>' +
    (none
      ? H.busy
        ? '<div class="grp"><div class="empty">Loading the history…</div></div>'
        : '<div class="card hempty"><b>Connect once to load the history</b><span>Your saved rate still works on Convert. The news notes below come with the app.</span></div>'
      : stripHTML(pts) +
        '<p class="hdir">' + (gbpTop() ? 'Higher means your pound buys more pesos.' : 'Higher means your pesos buy more pounds.') + '</p>' +
        '<div class="hchart' + (HV.range === 'All' && H.olderBusy ? ' fade' : '') + '" id="hchart">' +
        (HV.range === 'All' && H.olderBusy ? '<div class="hload">Loading older years…</div>' : '') +
        '<svg id="hsvg" role="img" aria-label="' + esc(sentence(pts)) + '"></svg></div>' +
        '<div class="hkey" aria-hidden="true"><span>● Peso news</span><span>○ Pound news</span></div>' +
        whyHTML(pts)) +
    '</div><div class="hside">' + newsListHTML(pts) + footHTML() + '</div></div>'
  );
}
function headHTML(pts) {
  const sc = HSCRUB && HSCRUB.d;
  if (sc) {
    return (
      '<div class="hbig">' + hFmt(hVal(sc.php)) + '<small>' + hUnit() + '</small></div>' +
      '<div class="hsub">' + hDate(sc.d, 'long') + '</div>' +
      '<div class="hsub2' + (HSCRUB.ev ? ' ev' : '') + '">' + (HSCRUB.ev ? (HSCRUB.ev.side === 'peso' ? '● ' : '○ ') + esc(HSCRUB.ev.title) + ' · let go to read' : '') + '</div>'
    );
  }
  if (!pts.length) {
    const r = D.rate;
    return r
      ? '<div class="hbig">' + hFmt(hVal(r.value)) + '<small>' + hUnit() + '</small></div><div class="hsub">Saved rate · ' + (hReal(r.date) ? hDate(r.date, 'wk') : '') + '</div><div class="hsub2"></div>'
      : '<div class="hbig">—</div><div class="hsub">No rate saved yet</div><div class="hsub2"></div>';
  }
  const a = pts[0],
    b = pts[pts.length - 1],
    ago = H_AGO[HV.range] || 'in ' + hDate(a.d, 'monthyear');
  let sub;
  if (gbpTop()) {
    const d = Math.round(100 * b.php) - Math.round(100 * a.php);
    sub = '£100 buys ' + peso0(100 * b.php) + ', ' + (d === 0 ? 'the same as ' + ago : peso0(Math.abs(d)) + (d > 0 ? ' more' : ' less') + ' than ' + ago);
  } else {
    const d = Math.round(100000 / b.php) - Math.round(100000 / a.php);
    sub = '₱1,000 buys ' + gbp(1000 / b.php) + ', ' + (d === 0 ? 'the same as ' + ago : gbp(Math.abs(d) / 100) + (d > 0 ? ' more' : ' less') + ' than ' + ago);
  }
  const trip = tripStart();
  let tl = '';
  if (trip && trip >= a.d && trip < b.d) {
    const t = hOn(trip, pts),
      dv = hVal(b.php) - hVal(t.php),
      same = Math.abs(dv) < (gbpTop() ? 0.005 : 0.0005);
    tl = 'Since ' + hDate(trip) + ': ' + (same ? 'about the same' : hFmt(Math.abs(dv)) + (dv > 0 ? ' more ' : ' less ') + hUnit());
  }
  return (
    '<div class="hbig">' + hFmt(hVal(b.php)) + '<small>' + hUnit() + ' · ' + hDate(b.d, 'wk') + '</small></div>' +
    '<div class="hsub">' + sub + '</div><div class="hsub2">' + tl + '</div>'
  );
}
// every gap says why: weekends, the Manila night gap, offline, no signal yet, a saved rate that isn't the ECB's
function statusHTML(pts) {
  const L = [],
    today = localISO(),
    last = pts.length ? pts[pts.length - 1].d : null,
    wd = new Date(hT(today)).getUTCDay();
  if (!navigator.onLine) {
    if (!Object.keys(H.ecb).length && last) L.push(['◌', 'No signal. Connect once to load the history since ' + hDate(last) + '.']);
    else if (last) L.push(['◌', 'Offline. The history is saved on your phone.']);
  } else if (H.busy) L.push(['◌', 'Checking for new rates…']);
  else if (H.fail && last && last < hWorkday(today) && hAdd(last, 3) < today) L.push(['!', 'History up to ' + hDate(last) + '. Couldn’t reach Frankfurter.']);
  if (last) {
    if (wd === 0 || wd === 6) L.push(['◷', 'No new rate at weekends. Last: ' + hDate(last, 'day') + '.']);
    else if (last < today) L.push(['◷', (last === hAdd(today, -1) || (wd === 1 && last === hAdd(today, -3)) ? H_WDAY[wd] + '’s rate comes' : 'Rates come') + ' at about 4 pm UK time, 11 pm in Manila.']);
  }
  const own = ownPoints().filter((o) => !isECB(o.src) && pts.length && o.d > pts[0].d),
    o = own[own.length - 1];
  if (o) L.push(['○', (D.rate && D.rate.date === o.d ? 'Today’s saved rate, ' : 'The rate saved on ' + hDate(o.d) + ', ') + hFmt(hVal(o.php)) + ', is from ' + esc(o.src) + ', not the ECB. It’s the hollow dot' + (o.d >= (last || '') ? ' at the end.' : '.')]);
  if (HV.range === 'All' && !H.older && !H.olderBusy && pts.length) {
    if (!navigator.onLine) L.push(['◌', 'From ' + hDate(pts[0].d, 'year') + '. Older years load when you’re back online.']);
    else if (H.olderFail) L.push(['!', 'From ' + hDate(pts[0].d, 'year') + '. Older years couldn’t load from Frankfurter.']);
  }
  return L.map((x) => '<p><i aria-hidden="true">' + x[0] + '</i><span>' + x[1] + '</span></p>').join('');
}
// where the newest rate sits between the period's low and high, like the price range strip (Q12)
function stripHTML(pts) {
  const vs = pts.map((x) => hVal(x.php));
  let lo = 0,
    hi = 0;
  vs.forEach((v, i) => {
    if (v < vs[lo]) lo = i;
    if (v > vs[hi]) hi = i;
  });
  const now = vs[vs.length - 1],
    p = Math.min(1, Math.max(0, (now - vs[lo]) / (vs[hi] - vs[lo] || 1))),
    word = p >= 0.85 ? 'Near the high' : p <= 0.15 ? 'Near the low' : 'In the middle';
  return (
    '<div class="hstrip" role="img" aria-label="' + esc(word + ' of the ' + H_PER[HV.range] + '. Low ' + hFmt(vs[lo]) + ', high ' + hFmt(vs[hi]) + '.') + '">' +
    '<b>' + word + ' of the ' + H_PER[HV.range] + '</b>' +
    '<div class="htrack" aria-hidden="true"><span class="hnow" style="left:' + (p * 100).toFixed(1) + '%"></span></div>' +
    '<div class="hends" aria-hidden="true"><span>Low ' + hFmt(vs[lo]) + ' · ' + hDate(pts[lo].d) + '</span><span>High ' + hFmt(vs[hi]) + ' · ' + hDate(pts[hi].d) + '</span></div></div>'
  );
}
// VoiceOver reads the chart as a sentence: "Up 10.4% in a year. High ₱85.35 on 26 October 2026."
function sentence(pts) {
  if (pts.length < 2) return 'Not enough history to draw yet.';
  const vs = pts.map((x) => hVal(x.php)),
    ch = (vs[vs.length - 1] / vs[0] - 1) * 100;
  let hi = 0,
    lo = 0;
  vs.forEach((v, i) => {
    if (v > vs[hi]) hi = i;
    if (v < vs[lo]) lo = i;
  });
  const per = { M: 'in a month', '6M': 'in 6 months', Y: 'in a year', '5Y': 'in 5 years', All: 'since ' + pts[0].d.slice(0, 4) }[HV.range];
  return (Math.abs(ch) < 0.05 ? 'About the same ' : (ch > 0 ? 'Up ' : 'Down ') + Math.abs(ch).toFixed(1) + '% ') + per + '. High ' + hFmt(vs[hi]) + ' on ' + hDate(pts[hi].d, 'full') + '. Low ' + hFmt(vs[lo]) + ' on ' + hDate(pts[lo].d, 'full') + '.';
}
// "Why it moved": how much of the change came from the peso and how much from the pound, each against the US dollar,
// from ECB pesos and dollars per pound at both ends. Hidden if either end is missing; it never guesses
function whyHTML(pts) {
  if (pts.length < 2) return '';
  const a = pts[0],
    b = pts[pts.length - 1];
  if (!(a.usd > 0 && b.usd > 0)) return '';
  const pa = Math.log(b.usd / a.usd), // the pound against the dollar
    pb = Math.log(b.php / b.usd / (a.php / a.usd)), // pesos per dollar: up means the peso weakened
    tot = Math.abs(pa) + Math.abs(pb),
    title = tot < 0.003 ? 'Barely moved' : Math.abs(pb) >= 0.6 * tot ? 'Mostly the peso' : Math.abs(pa) >= 0.6 * tot ? 'Mostly the pound' : 'Both moved',
    peso = (Math.exp(-pb) - 1) * 100,
    pound = (Math.exp(pa) - 1) * 100,
    opp = pa > 0 !== pb > 0 && tot >= 0.003,
    sp = Math.round((Math.abs(pb) / (tot || 1)) * 100),
    per = H_WHY[HV.range] || 'since ' + a.d.slice(0, 4);
  return (
    hdr('Why it moved · ' + per) +
    '<div class="card hwhy"><b>' + title + '</b>' +
    '<p>Against the US dollar, the peso ' + (peso < 0 ? 'weakened' : 'strengthened') + ' ' + Math.abs(peso).toFixed(1) + '% and the pound ' + (pound >= 0 ? 'gained' : 'lost') + ' ' + Math.abs(pound).toFixed(1) + '%.' + (opp ? ' They pulled in opposite directions.' : '') + '</p>' +
    '<div class="hsplit" aria-hidden="true"><span class="hs-peso" style="width:' + sp + '%"></span><span class="hs-pound" style="width:' + (100 - sp) + '%"></span></div>' +
    '<div class="hsplitk"><span>Peso · ' + sp + '%</span><span>Pound · ' + (100 - sp) + '%</span></div></div>' +
    '<p class="foot">Worked out on your phone from ECB rates. The dollar is the yardstick because both are measured against it.</p>'
  );
}
function newsListHTML(pts) {
  const st = pts.length ? pts[0].d : hStart(HV.range, localISO()),
    ck = newsChecked(),
    list = hNotes()
      .filter((n) => n.date >= st && (!ck || n.date <= ck))
      .sort((a, b) => b.date.localeCompare(a.date)),
    show = HV.showAll ? list : list.slice(0, 4),
    stale = ck && (hT(localISO()) - hT(ck)) / 864e5 > NEWS_STALE;
  return (
    hdr('What happened') +
    '<div class="grp tiled hnews" id="hNews">' +
    (list.length
      ? show.map((n) => '<button class="row evrow" data-a="openNews" data-k="' + esc(newsKey(n)) + '"><span class="edt">' + hDate(n.date) + '</span><span class="egl" aria-label="' + (n.side === 'peso' ? 'Peso news' : 'Pound news') + '">' + (n.side === 'peso' ? '●' : '○') + '</span><span class="lbl">' + esc(n.title) + '</span><span class="etag">' + esc(n.tag) + '</span>' + ICON.chev + '</button>').join('') +
        (list.length > 4 && !HV.showAll ? '<button class="row more" data-a="hShowAll"><span class="lbl">Show all ' + list.length + '</span>' + ICON.chev + '</button>' : '')
      : '<div class="row"><span class="lbl hnone">No news notes in this period.</span></div>') +
    '</div>' +
    '<p class="foot" id="hAge">' + (ck ? (stale ? 'News last checked ' + hDate(ck) + ', over a month ago.' : 'News checked ' + hDate(ck, 'year') + '.') : '') + '</p>'
  );
}
function footHTML() {
  const s = window.sukiRateSnap;
  return (
    '<p class="foot hfoot">Rates: European Central Bank reference rates, through Frankfurter. They come on weekdays at about 4 pm UK time, 11 pm in Manila. Pesos from April 2005, when the ECB started publishing them.' +
    (s && hReal(s.to) ? ' Rates from 2016 to ' + hDate(s.to, 'year') + ' come with Suki, so the history works even without Frankfurter.' : '') +
    ' A rate from another source shows as a hollow dot, with its name. No forecasts.</p>'
  );
}

/* ===== The chart ===== */
function drawHistChart() {
  const svg = $('hsvg');
  HGEO = null;
  if (!svg) return;
  const pts = hPoints();
  if (pts.length < 1) return;
  const W = Math.max(200, svg.parentNode.clientWidth || 340),
    Ht = 208,
    L = 4,
    R = W - 42,
    top = 10,
    bot = 148,
    lane = 172;
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + Ht);
  svg.style.height = Ht + 'px';
  const own = ownPoints().filter((o) => o.d > pts[0].d),
    end = [pts[pts.length - 1].d, ...own.map((o) => o.d)].sort().pop(),
    t0 = hT(pts[0].d),
    t1 = Math.max(hT(end), t0 + 864e5),
    step = Math.max(1, Math.ceil(pts.length / 600)),
    drawn = pts.filter((x, i) => i % step === 0 || i === pts.length - 1),
    vs = drawn.map((x) => hVal(x.php)).concat(own.map((o) => hVal(o.php)));
  let mn = Math.min(...vs),
    mx = Math.max(...vs);
  const pad = (mx - mn) * 0.08 || (gbpTop() ? 0.5 : 0.005);
  mn -= pad;
  mx += pad;
  const X = (d) => L + ((hT(d) - t0) / (t1 - t0)) * (R - L),
    Y = (v) => bot - ((v - mn) / (mx - mn)) * (bot - top);
  HGEO = { X, Y, L, R, t0, t1, pts };
  let s = '';
  [0, 0.5, 1].forEach((f) => {
    const y = top + f * (bot - top),
      v = mx - f * (mx - mn);
    s += '<line class="hgrid" x1="' + L + '" x2="' + R + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text class="hax" x="' + (W - 2) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + (gbpTop() ? v.toFixed(v >= 100 ? 0 : 1) : v.toFixed(2)) + '</text>';
  });
  // the news lane, greyed after the day the notes were last checked
  const ck = newsChecked();
  if (ck && hT(ck) < t1) {
    const x = Math.max(L, X(ck));
    s += '<rect class="hlate" x="' + x.toFixed(1) + '" y="' + (lane - 10) + '" width="' + Math.max(0, R - x + 6).toFixed(1) + '" height="20" rx="4"/>';
  }
  const trip = tripStart();
  if (trip && trip >= pts[0].d && trip < pts[pts.length - 1].d) {
    const x = X(trip).toFixed(1);
    s += '<line class="htrip" x1="' + x + '" x2="' + x + '" y1="' + top + '" y2="' + bot + '"/><text class="hax" x="' + (X(trip) - 4).toFixed(1) + '" y="' + (top + 10) + '" text-anchor="end">Trip</text>';
  }
  s += '<polyline class="hline" points="' + drawn.map((x) => X(x.d).toFixed(1) + ',' + Y(hVal(x.php)).toFixed(1)).join(' ') + '"/>';
  const e = pts[pts.length - 1];
  s += '<circle class="hend" cx="' + X(e.d).toFixed(1) + '" cy="' + Y(hVal(e.php)).toFixed(1) + '" r="4"/>';
  own.forEach((o) => (s += '<circle class="hown" cx="' + X(o.d).toFixed(1) + '" cy="' + Y(hVal(o.php)).toFixed(1) + '" r="4.5"><title>' + esc(o.src || 'Saved rate') + '</title></circle>'));
  hNotesIn(pts).forEach((n) => {
    const x = X(n.date).toFixed(1);
    s += n.side === 'peso' ? '<circle class="hdot peso" cx="' + x + '" cy="' + lane + '" r="5"/>' : '<circle class="hdot pound" cx="' + x + '" cy="' + lane + '" r="4.3"/>';
  });
  s += '<text class="hax" x="' + L + '" y="' + (Ht - 4) + '">' + hDate(pts[0].d, 'my') + '</text><text class="hax" x="' + R + '" y="' + (Ht - 4) + '" text-anchor="end">' + hDate(end) + '</text>';
  s += '<g id="hcur" style="display:none"><line class="hcl" id="hcl" y1="' + top + '" y2="' + bot + '"/><circle class="hcd" id="hcd" r="5.5"/></g>';
  svg.innerHTML = s;
}
// the finger on the chart: the headline follows it, and it snaps to a news dot within 12 pt
function hPick(e) {
  const c = $('hchart');
  if (!c || !HGEO) return;
  const r = c.getBoundingClientRect(),
    x = Math.max(HGEO.L, Math.min(HGEO.R, e.clientX - r.left)),
    pts = HGEO.pts;
  let best = null,
    bd = 1e9;
  hNotesIn(pts).forEach((n) => {
    const d = Math.abs(HGEO.X(n.date) - x);
    if (d < bd) {
      bd = d;
      best = n;
    }
  });
  const snap = best && bd <= 12 ? best : null,
    tt = snap ? hT(snap.date) : HGEO.t0 + ((x - HGEO.L) / (HGEO.R - HGEO.L)) * (HGEO.t1 - HGEO.t0);
  let lo = 0,
    hi = pts.length - 1;
  while (lo < hi) {
    const m = (lo + hi) >> 1;
    if (hT(pts[m].d) < tt) lo = m + 1;
    else hi = m;
  }
  let i = lo;
  if (i > 0 && Math.abs(hT(pts[i - 1].d) - tt) < Math.abs(hT(pts[i].d) - tt)) i--;
  // a news day with no rate (a weekend) shows the rate before it
  if (snap && pts[i].d > snap.date && i > 0) i--;
  HSCRUB.d = pts[i];
  HSCRUB.ev = snap;
  const h = $('hHead');
  if (h) h.innerHTML = headHTML(pts);
  const g = $('hcur');
  if (!g) return;
  g.style.display = '';
  const cx = HGEO.X(pts[i].d).toFixed(1);
  $('hcl').setAttribute('x1', cx);
  $('hcl').setAttribute('x2', cx);
  $('hcd').setAttribute('cx', cx);
  $('hcd').setAttribute('cy', HGEO.Y(hVal(pts[i].php)).toFixed(1));
}
function hLift(open) {
  const s = HSCRUB;
  HSCRUB = null;
  const g = $('hcur');
  if (g) g.style.display = 'none';
  const h = $('hHead');
  if (h) h.innerHTML = headHTML(hPoints());
  if (HPEND) {
    HPEND = false;
    rerender();
  }
  if (open && s && s.ev) {
    // the click that follows the lift isn't a tap on the new sheet's dimmed edge
    sbEat = Date.now();
    openSheet('news', { id: newsKey(s.ev) });
  }
}
document.addEventListener('pointerdown', (e) => {
  const c = e.target.closest && e.target.closest('#hchart');
  if (!c || U.tab !== 'history' || c.classList.contains('fade') || (e.pointerType === 'mouse' && e.button !== 0)) return;
  HSCRUB = { id: e.pointerId, d: null, ev: null };
  hPick(e);
});
document.addEventListener('pointermove', (e) => {
  if (HSCRUB && e.pointerId === HSCRUB.id) hPick(e);
});
document.addEventListener('pointerup', (e) => {
  if (HSCRUB && e.pointerId === HSCRUB.id) hLift(true);
});
document.addEventListener('pointercancel', (e) => {
  if (HSCRUB && e.pointerId === HSCRUB.id) hLift(false);
});
// a full redraw (a rate arriving, a new day) waits while a finger is on the chart, so it never snaps away (ui.js)
const histHold = (keep) => U.tab === 'history' && !!HSCRUB && keep && (HPEND = true);

// the page's own parts, redrawn in place: the range knob is never redrawn mid-slide
function histRedraw() {
  if (U.tab !== 'history' || !$('hbody')) return;
  if (HSCRUB) return void (HPEND = true);
  $('hbody').innerHTML = histBody();
  drawHistChart();
}
function histAfter() {
  drawHistChart();
}
let hResizeT = 0;
addEventListener('resize', () => {
  clearTimeout(hResizeT);
  hResizeT = setTimeout(() => U.tab === 'history' && !HSCRUB && drawHistChart(), 120);
});
window.addEventListener('online', () => {
  histRedraw();
  if (U.tab === 'history') histTopUp(true);
});
window.addEventListener('offline', histRedraw);
document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && U.tab === 'history' && histTopUp());

/* ===== Swipe back from anywhere on the page except the chart (the chart claims the finger first) ===== */
let SB = null,
  sbEat = 0,
  SB_GONE = false; // the page left by swiping, so go() doesn't slide Convert in again
function sbUnder() {
  let u = $('under');
  if (u) return u;
  u = document.createElement('div');
  u.id = 'under';
  u.setAttribute('aria-hidden', 'true');
  u.inert = true;
  u.innerHTML = '<div class="wrap"><header class="bar"><span class="side"></span><span class="mt"></span><span class="side r"></span></header><main class="tab-convert narrow">' + scrConvert() + '</main></div><div class="pdim"></div>';
  u.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));
  u.querySelectorAll('[data-a]').forEach((el) => el.removeAttribute('data-a'));
  document.body.appendChild(u);
  return u;
}
function sbClear() {
  const w = document.querySelector('body > .wrap'),
    u = $('under');
  if (w) w.style.transform = w.style.transition = '';
  if (u) u.remove();
  document.body.classList.remove('swiping');
}
document.addEventListener('pointerdown', (e) => {
  SB = null;
  if (U.tab !== 'history' || U.sheet || split() || (e.pointerType === 'mouse' && e.button !== 0)) return;
  // the range control and anything else that owns its gesture gets the finger first (the kit's rule, Q28)
  if (!e.target.closest || !e.target.closest('main') || e.target.closest('#hchart, input, textarea, .pk-seg, [data-own-gesture]')) return;
  SB = { id: e.pointerId, x: e.clientX, y: e.clientY, on: false, vx: 0, lx: e.clientX, lt: performance.now(), dx: 0 };
});
document.addEventListener('pointermove', (e) => {
  if (!SB || e.pointerId !== SB.id || HSCRUB) return;
  const dx = e.clientX - SB.x,
    dy = e.clientY - SB.y;
  if (!SB.on) {
    if (Math.abs(dy) > 10 && Math.abs(dy) > Math.abs(dx)) return void (SB = null);
    if (!(dx > 10 && dx > Math.abs(dy) * 1.2)) return;
    SB.on = true;
    pushClear(); // a push still under way ends at once, so the swipe starts from a settled page
    sbUnder();
    document.body.classList.add('swiping');
  }
  const now = performance.now();
  SB.vx = (e.clientX - SB.lx) / Math.max(1, now - SB.lt);
  SB.lx = e.clientX;
  SB.lt = now;
  SB.dx = Math.max(0, dx);
  const w = document.querySelector('body > .wrap'),
    u = $('under'),
    W = innerWidth;
  if (w) {
    w.style.transition = 'none';
    w.style.transform = 'translateX(' + SB.dx + 'px)';
  }
  // Convert underneath moves a third and lifts its 10% dim as the page goes (Q24, the same as a tapped push)
  if (u && !MOTION.reduced()) {
    const k = Math.min(1, SB.dx / W),
      c = u.querySelector('.wrap'),
      d = u.querySelector('.pdim');
    if (c) c.style.transform = 'translateX(' + -PUSH_UNDER * W * (1 - k) + 'px)';
    if (d) d.style.opacity = String(PUSH_DIM * (1 - k));
  }
});
function sbEnd(e, cancel) {
  if (!SB || e.pointerId !== SB.id) return;
  const s = SB;
  SB = null;
  if (!s.on) return;
  sbEat = Date.now();
  const back = !cancel && (s.dx > innerWidth / 5 || s.vx > 0.5),
    w = document.querySelector('body > .wrap'),
    u = $('under');
  const done = () => {
    sbClear();
    if (back) {
      SB_GONE = true;
      go('convert');
    }
  };
  if (!MOTION.on() || !w || !w.animate) return done();
  // it lets go on the nav spring, like every push and pop (Q24; it was its own 280 ms curve)
  const o = { spring: 'nav', fill: 'forwards' },
    c = u && u.querySelector('.wrap'),
    d = u && u.querySelector('.pdim'),
    a = MOTION.animate(w, [{ transform: 'translateX(' + s.dx + 'px)' }, { transform: back ? 'translateX(' + innerWidth + 'px)' : 'none' }], o);
  if (c) MOTION.animate(c, [{ transform: c.style.transform || 'none' }, { transform: back ? 'none' : 'translateX(' + -PUSH_UNDER * innerWidth + 'px)' }], o);
  if (d) MOTION.animate(d, [{ opacity: d.style.opacity || '0' }, { opacity: back ? 0 : PUSH_DIM }], o);
  if (!a) return done();
  a.onfinish = () => {
    a.cancel();
    done();
  };
}
document.addEventListener('pointerup', (e) => sbEnd(e, false));
document.addEventListener('pointercancel', (e) => sbEnd(e, true));
// the tap that ends a swipe isn't a tap on whatever was under the finger
document.addEventListener('click', (e) => Date.now() - sbEat < 350 && (e.preventDefault(), e.stopPropagation()), true);

/* ===== Sheets: a news note, and what a central bank rate is ===== */
function newsSheet(sd) {
  const n = hNotes().find((x) => newsKey(x) === sd.id);
  if (!n) return null;
  const wd = (new Date(hT(n.date)).getUTCDay() + 6) % 7,
    mon = hAdd(n.date, -wd),
    fri = hAdd(mon, 4),
    week = histSeries().filter((x) => x.d >= mon && x.d <= fri),
    wk = week.length ? hFmt(hVal(week[0].php)) + ' → ' + hFmt(hVal(week[week.length - 1].php)) : n.date < (histSeries()[0] || {}).d ? 'Loads with the older years' : '—',
    host = (n.url || '').split('/')[2] || '';
  // the header says which side; the title goes in the body, so a long one wraps instead of being cut off
  return sheetWrap(
    n.side === 'peso' ? 'Peso news' : 'Pound news',
    '<h3 class="ntitle">' + esc(n.title) + '</h3><p class="ncap">' + hDate(n.date, 'year') + ' · ' + esc(n.tag) + '</p>' +
      '<p class="nbody">' + esc(n.body) + '</p>' +
      '<div class="grp"><div class="row"><span class="lbl">' + (gbpTop() ? '£1' : '₱100') + ' that week</span><span class="amt">' + wk + '</span></div></div>' +
      '<div class="grp tiled nlinks"><button class="row" data-a="openCbRate">' + stile('help', 'blue') + '<span class="lbl"><b>What’s a central bank rate?</b></span>' + ICON.chev + '</button>' +
      (n.url ? '<a class="row" href="' + esc(n.url) + '" target="_blank" rel="noopener">' + stile('book', 'green') + '<span class="lbl"><b>Read the official record</b><small>' + esc(n.src || host) + ' · ' + esc(host.replace(/^www\./, '')) + '</small></span>' + ICON.out + '</a>' : '') +
      '</div>',
    '',
    n.title,
    { cls: 'newssheet' }
  );
}
const cbBody = () =>
  '<p class="nbody">Each country’s central bank sets the interest rate its banks pay to borrow. In the Philippines that’s the Bangko Sentral ng Pilipinas (BSP), and in the UK the Bank of England.</p>' +
  '<p class="nbody">When a central bank raises its rate, saving in that currency pays more, so people tend to want more of it, which can make it stronger. It’s one push among many: in 2026 the BSP raised its rate four times, but expensive oil pulled the peso down harder.</p>' +
  '<p class="foot">Suki’s news notes link to each bank’s own statement. Nothing here is a forecast.</p>';
const cbSheet = () => sheetWrap('What’s a central bank rate?', cbBody(), '', 'What’s a central bank rate?', { cls: 'cbsheet' });

/* ===== Doors and buttons ===== */
Object.assign(ACT, {
  openHistory: () => {
    HV.range = 'Y';
    HV.showAll = false;
    go('history');
    histInit().then(() => {
      histRedraw();
      histTopUp();
    });
  },
  hRange: (el) => {
    const v = el.dataset.v;
    if (HV.range === v || !HIST_RANGES.some((r) => r[0] === v)) return;
    HV.range = v;
    HV.showAll = false;
    segPick($('hSeg'), v);
    histRedraw();
    if (v === 'All') histOlder();
  },
  hShowAll: () => {
    HV.showAll = true;
    histRedraw();
  },
  openNews: (el) => openSheet('news', { id: el.dataset.k }, U.sheet === 'news'),
  openCbRate: () => openSheet('cbrate', {}, !!U.sheet),
});

SCREENS.history = scrHistory;
TAB_TITLE.history = 'Rate history';
