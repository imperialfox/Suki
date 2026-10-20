/* Suki · rate.js
   The GBP → PHP reference rate (from api.frankfurter.app; only the currencies are sent, never your records)
   and the linked converter boxes.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const RATE_URL = 'https://api.frankfurter.app/latest?from=GBP&to=PHP';
const RATE_STALE = 12 * 3600e3; // refresh quietly on opening if the saved rate is older than this
let rateBusy = false;

async function refreshRate(manual) {
  if (rateBusy) return;
  rateBusy = true;
  const b = $('refreshRate');
  if (b) {
    b.disabled = true;
    b.classList.add('busy');
  }
  try {
    const ctl = new AbortController(),
      t = setTimeout(() => ctl.abort(), 8000);
    const r = await fetch(RATE_URL, { cache: 'no-store', signal: ctl.signal });
    clearTimeout(t);
    if (!r.ok) throw new Error('rate ' + r.status);
    const j = await r.json(),
      v = Number(j && j.rates && j.rates.PHP);
    if (!(v > 0)) throw new Error('no rate');
    D.rate = cleanRate({ value: v, date: j.date, cachedAt: new Date().toISOString(), source: 'Frankfurter reference rate' });
    await save('rate');
    convFrom(U.conv.last);
    rateBusy = false;
    rerender();
    if (manual) toast('Rate updated: £1 = ' + cash(v));
  } catch (e) {
    rateBusy = false;
    rerender();
    if (manual) toast(D.rate ? 'Couldn’t refresh, so the saved rate is still in use' : 'Couldn’t load a rate. Try again when you’re online.');
  }
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
