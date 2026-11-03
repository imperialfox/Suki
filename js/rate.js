/* Suki · rate.js
   The GBP → PHP reference rate and the linked converter boxes.
   The rate comes from the first of these that answers with a sensible number (only the currencies are sent,
   never your records):
     1. Frankfurter, European Central Bank rate  api.frankfurter.dev (v2)
     2. Frankfurter, European Central Bank rate  api.frankfurter.app (v1, the address Suki used up to 2.2)
     3. Currency API                             cdn.jsdelivr.net, then its mirror on currency-api.pages.dev
   A rate outside RATE_RANGE is rejected, so a bad reply can never replace a good saved rate.
   Why the last check failed is kept for this session (RATE_CHECK) and shown in Settings.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const RATE_SOURCES = [
  { name: 'Frankfurter (ECB)', url: 'https://api.frankfurter.dev/v2/providers/ecb/rate/GBP/PHP', read: (j) => [j.rate, j.date] },
  { name: 'Frankfurter (ECB)', url: 'https://api.frankfurter.app/latest?from=GBP&to=PHP', read: (j) => [j.rates && j.rates.PHP, j.date] },
  { name: 'Currency API', url: 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/gbp.min.json', read: (j) => [j.gbp && j.gbp.php, j.date] },
  { name: 'Currency API', url: 'https://latest.currency-api.pages.dev/v1/currencies/gbp.min.json', read: (j) => [j.gbp && j.gbp.php, j.date] },
];
const RATE_RANGE = [30, 120]; // pesos per pound; anything outside this is a bad reply, not a real rate
const RATE_TIMEOUT = 6000; // per source
const RATE_STALE = 12 * 3600e3; // refresh quietly on opening if the saved rate is older than this
let rateBusy = false;
// the last check this session: {at, ok, source, fails: [{source, why}]}; not saved
let RATE_CHECK = null;

// the short address shown in Settings: frankfurter.dev, jsdelivr.net, currency-api.pages.dev
const hostOf = (u) => u.split('/')[2].replace(/^(api|cdn|latest)\./, '');
async function rateFrom(src) {
  const ctl = new AbortController(),
    t = setTimeout(() => ctl.abort(), RATE_TIMEOUT);
  let r, j;
  try {
    r = await fetch(src.url, { cache: 'no-store', signal: ctl.signal });
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
  const [raw, date] = src.read(j || {}),
    v = Number(raw);
  if (raw === undefined || raw === null || !Number.isFinite(v)) throw new Error('no peso rate in the reply');
  if (v < RATE_RANGE[0] || v > RATE_RANGE[1]) throw new Error('rate out of range (' + v + ')');
  return { value: v, date: /^\d{4}-\d{2}-\d{2}/.test(date || '') ? String(date).slice(0, 10) : localISO() };
}

async function refreshRate(manual) {
  if (rateBusy) return;
  if (!navigator.onLine) {
    rerender();
    if (manual) toast(D.rate ? 'You’re offline. Using your saved rate.' : 'You’re offline and no rate is saved yet. Connect once to load one.');
    return;
  }
  rateBusy = true;
  const b = $('refreshRate');
  if (b) {
    b.disabled = true;
    b.classList.add('busy');
  }
  const fails = [];
  let got = null,
    src = null;
  for (const s of RATE_SOURCES) {
    // two timeouts in a row means no real connection, so the rest aren't tried (about 12 s instead of 24) (Q06)
    if (fails.filter((f) => f.why === 'timed out').length >= 2) {
      fails.push({ source: 'the rest', why: 'not tried after two timed out' });
      break;
    }
    try {
      got = await rateFrom(s);
      src = s;
      break;
    } catch (e) {
      fails.push({ source: hostOf(s.url), why: e.message });
    }
  }
  RATE_CHECK = { at: new Date().toISOString(), ok: !!got, source: src && src.name, fails };
  if (got) {
    D.rate = cleanRate({ value: got.value, date: got.date, cachedAt: new Date().toISOString(), source: src.name });
    await save('rate');
    convFrom(U.conv.last);
  }
  rateBusy = false;
  rerender();
  if (!manual) return;
  if (got) toast('Rate updated: £1 = ' + cash(got.value));
  else toast(D.rate ? 'Couldn’t reach the rate service, so the saved rate is still in use' : 'Couldn’t reach the rate service. Try again in a moment.');
}
function autoRate() {
  if (!navigator.onLine) return;
  if (!D.rate || Date.now() - new Date(D.rate.cachedAt) > RATE_STALE) refreshRate(false);
}

/* ===== Linked boxes: typing in either one fills in the other ===== */
const plain2 = (n) => n.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
function convFrom(which) {
  const r = D.rate;
  if (!r) return;
  const other = which === 'gbp' ? 'php' : 'gbp',
    n = amount(U.conv[which]);
  U.conv[other] = n === null || n < 0 ? '' : plain2(which === 'gbp' ? n * r.value : n / r.value);
}
function convInput(which, value) {
  U.conv[which] = value;
  U.conv.last = which;
  convFrom(which);
  const o = which === 'gbp' ? 'php' : 'gbp',
    el = $('conv-' + o);
  if (el) el.value = U.conv[o];
}
function convText() {
  const r = D.rate;
  if (!r) return '';
  const g = amount(U.conv.gbp),
    p = amount(U.conv.php);
  if (g === null || p === null) return '';
  const pair = U.conv.last === 'php' ? cash(p) + ' ≈ ' + gbp(g) : gbp(g) + ' ≈ ' + cash(p);
  return pair + ' (reference rate £1 = ' + cash(r.value) + ', ' + shortDate(r.date) + ')';
}
async function copyConv() {
  const s = convText();
  if (!s) return toast('Enter an amount first');
  try {
    await navigator.clipboard.writeText(s);
    toast('Copied');
  } catch (e) {
    toast(s);
  }
}

/* ===== The rate for the day the money was spent (Q22) =====
   A purchase dated before today gets the last ECB rate published before that date: the day before's,
   or the weekday before a weekend or holiday (Frankfurter answers those with the weekday before). So a
   Monday-morning purchase in Manila gets Friday's, because Monday's appears at about 23:00 there.
   Today's and future dates keep today's saved rate. Saving never waits: the purchase is saved with today's
   rate marked "estimated", then the day's rate is filled in (fixRates), now or the next time there's signal.
   A correction only adds to a purchase (rateAtPurchase, gbpAtPurchase, rateDate, rateSource); its price,
   date and words are never touched, and only purchases marked rateEstimated are ever corrected. */
const DAY_SOURCES = [
  { name: 'Frankfurter (ECB)', url: (d) => 'https://api.frankfurter.dev/v2/providers/ecb/rate/GBP/PHP?date=' + d, read: (j) => [j.rate, j.date] },
  { name: 'Frankfurter (ECB)', url: (d) => 'https://api.frankfurter.dev/v1/' + d + '?from=GBP&to=PHP', read: (j) => [j.rates && j.rates.PHP, j.date] },
  { name: 'Currency API', url: (d) => 'https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@' + d + '/v1/currencies/gbp.min.json', read: (j) => [j.gbp && j.gbp.php, j.date] },
  { name: 'Currency API', url: (d) => 'https://' + d + '.currency-api.pages.dev/v1/currencies/gbp.min.json', read: (j) => [j.gbp && j.gbp.php, j.date] },
];
const DAY_BACK = 10; // a reply for a day more than this before the one asked for is the wrong day, not a holiday
const DAY_CACHE = {}; // rates found this session, by the day asked for
let fixBusy = false,
  fixAgain = false;

// the day to ask the ECB for: the day before the purchase, or null for today and later (today's saved rate)
const rateDayFor = (date) => (isoDate(date) && date < localISO() ? addDays(date, -1) : null);

// the rate for one day, from the first source that answers sensibly; throws if none does
async function dayRate(day) {
  let timeouts = 0;
  for (const s of DAY_SOURCES) {
    if (timeouts >= 2) break;
    try {
      const got = await rateFrom({ url: s.url(day), read: s.read });
      // a reply for a later day, or one from long before, isn't that day's rate
      if (got.date > day || got.date < addDays(day, -DAY_BACK)) throw new Error('wrong day (' + got.date + ')');
      return { value: got.value, date: got.date, source: s.name };
    } catch (e) {
      if (e.message === 'timed out') timeouts++;
    }
  }
  throw new Error('no rate for ' + day);
}

function setRate(p, r, estimated) {
  p.rateAtPurchase = r ? r.value : null;
  p.gbpAtPurchase = r ? Math.round((p.price / r.value) * 100) / 100 : null;
  if (r && r.date) p.rateDate = r.date;
  else delete p.rateDate;
  if (r && r.source) p.rateSource = r.source;
  else delete p.rateSource;
  if (estimated) p.rateEstimated = true;
  else delete p.rateEstimated;
  return p;
}
// a new purchase, or one whose date changed: the right rate if it's known, else today's, estimated
function stampRate(p) {
  const ask = rateDayFor(p.date);
  if (ask && DAY_CACHE[ask]) return setRate(p, DAY_CACHE[ask], false);
  return setRate(p, D.rate, !!ask);
}

// fill in the day's rate on every purchase still marked estimated. Never blocks a save; quiet when it fails
async function fixRates() {
  if (fixBusy) return void (fixAgain = true);
  if (!navigator.onLine || !D.purchases.some((p) => p.rateEstimated)) return;
  fixBusy = true;
  let changed = 0;
  try {
    const days = [...new Set(D.purchases.filter((p) => p.rateEstimated).map((p) => rateDayFor(p.date)))];
    for (const day of days) {
      if (!navigator.onLine) break;
      let got = day && DAY_CACHE[day];
      if (day && !got) {
        try {
          got = DAY_CACHE[day] = await dayRate(day);
        } catch (e) {
          continue;
        }
      }
      // looked at again after the wait: a purchase deleted, edited or restored meanwhile is judged as it is now
      const use = got || D.rate;
      D.purchases.forEach((p) => {
        if (!use || !p.rateEstimated || rateDayFor(p.date) !== day) return;
        setRate(p, use, false);
        changed++;
      });
    }
  } finally {
    fixBusy = false;
  }
  if (changed) {
    await save('purchases');
    showFixed();
  }
  if (fixAgain) {
    fixAgain = false;
    fixRates();
  }
}
// redraw so totals and details show the corrected rate, unless he's typing (the next redraw catches up)
function showFixed() {
  const ae = document.activeElement;
  if (ae && ae.matches && ae.matches('input,textarea,select')) return;
  rerender();
}
// coming back to the app: an iPhone may have missed the online event while Suki was in the background
document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && fixRates());
