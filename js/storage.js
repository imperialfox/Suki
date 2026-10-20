/* Suki · storage.js
   Saved data: loading, checking and saving it.
   Everything stays on this device, in the same places Suki has always used, so nothing is lost on updating:
   - IndexedDB database 'suki-db', store 'kv', keys 'purchases', 'observations' and 'rate'
   - localStorage 'suki:<key>' as the fallback when IndexedDB isn't available
   - localStorage 'suki:lastBackup' (when a backup was last saved), 'suki:draft' (a half-typed purchase),
     'suki:motion' (motion speed, see motion.js). None of these three go into backups.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Data ===== */
const CATS = ['Food & drink', 'Transport', 'Groceries', 'Shopping', 'Accommodation', 'Activities', 'Other'];
const VENUES = ['Palengke', 'Street vendor', 'Carinderia', 'Restaurant', 'Convenience store', 'Supermarket', 'Transport', 'Other'];
const PAYMENTS = ['Cash', 'Revolut', 'Other card', 'Other'];
let D = { purchases: [], observations: [], rate: null };

/* ===== Checking =====
   Anything loaded or restored passes through these, so damaged data can't stop the app starting.
   Records missing what they can't do without (a name and an amount) are dropped; everything else is tidied.
   Fields these don't know about are kept, so a newer version's data survives a trip through this one. */
const str = (x) => (typeof x === 'string' ? x.trim() : typeof x === 'number' ? String(x) : '');
const money = (x) => {
  const n = typeof x === 'string' ? parseFloat(x.replace(/,/g, '')) : +x;
  return Number.isFinite(n) && n > 0 ? Math.round(n * 100) / 100 : null;
};
function isoDate(x) {
  if (typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x) && !isNaN(new Date(x + 'T12:00:00'))) return x;
  const d = new Date(x);
  return x && !isNaN(d) ? localISO(d) : null;
}
const localISO = (d = new Date()) =>
  d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
const newId = () =>
  (window.crypto && crypto.randomUUID && crypto.randomUUID()) || 'p' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

function cleanPurchase(p) {
  if (!p || typeof p !== 'object' || Array.isArray(p)) return null;
  const item = str(p.item),
    price = money(p.price);
  if (!item || price === null) return null;
  const num = (x) => (Number.isFinite(+x) && +x > 0 && x !== null && x !== '' ? +x : null);
  return Object.assign({}, p, {
    id: str(p.id) || newId(),
    item: item.slice(0, 200),
    price,
    date: isoDate(p.date) || localISO(),
    category: CATS.includes(p.category) ? p.category : 'Other',
    location: str(p.location),
    venue: str(p.venue),
    payment: str(p.payment),
    notes: str(p.notes),
    gbpAtPurchase: num(p.gbpAtPurchase),
    rateAtPurchase: num(p.rateAtPurchase),
  });
}
function cleanObservation(o) {
  if (!o || typeof o !== 'object' || Array.isArray(o)) return null;
  const price = money(o.price),
    itemId = str(o.itemId);
  if (!itemId || price === null) return null;
  const it = itemById(itemId);
  return Object.assign({}, o, {
    id: str(o.id) || newId(),
    itemId,
    itemName: str(o.itemName) || (it ? it.name : itemId),
    price,
    date: isoDate(o.date) || localISO(),
    location: str(o.location),
    venue: str(o.venue),
    note: str(o.note),
  });
}
function cleanRate(r) {
  if (!r || typeof r !== 'object') return null;
  const value = +r.value;
  if (!Number.isFinite(value) || value <= 0) return null;
  const cached = new Date(r.cachedAt);
  return {
    value,
    date: str(r.date) || localISO(),
    cachedAt: isNaN(cached) ? new Date().toISOString() : cached.toISOString(),
    source: str(r.source) || 'Frankfurter reference rate',
  };
}
// a list of records: each one checked, and repeated ids given new ones so edits and deletes stay exact
function cleanList(list, fn) {
  const seen = new Set();
  return (Array.isArray(list) ? list : [])
    .map(fn)
    .filter(Boolean)
    .map((r) => {
      if (seen.has(r.id)) r.id = newId();
      seen.add(r.id);
      return r;
    });
}
function cleanData(d) {
  d = d && typeof d === 'object' ? d : {};
  return {
    purchases: cleanList(d.purchases, cleanPurchase),
    observations: cleanList(d.observations, cleanObservation),
    rate: cleanRate(d.rate),
  };
}

/* ===== IndexedDB, with localStorage as the fallback ===== */
let idb = null;
function openDB() {
  return new Promise((resolve) => {
    if (!('indexedDB' in window)) return resolve(null);
    let r;
    try {
      r = indexedDB.open('suki-db', 1);
    } catch (e) {
      return resolve(null);
    }
    r.onupgradeneeded = () => {
      if (!r.result.objectStoreNames.contains('kv')) r.result.createObjectStore('kv');
    };
    r.onsuccess = () => resolve(r.result);
    r.onerror = () => resolve(null);
    r.onblocked = () => resolve(null);
  });
}
function lsGet(k) {
  try {
    return JSON.parse(localStorage.getItem('suki:' + k) || 'null');
  } catch (e) {
    return null;
  }
}
function lsSet(k, v) {
  try {
    localStorage.setItem('suki:' + k, JSON.stringify(v));
    return true;
  } catch (e) {
    return false;
  }
}
function getKey(k) {
  return new Promise((resolve) => {
    if (!idb) return resolve(lsGet(k));
    try {
      const r = idb.transaction('kv', 'readonly').objectStore('kv').get(k);
      r.onsuccess = () => resolve(r.result === undefined ? lsGet(k) : r.result);
      r.onerror = () => resolve(lsGet(k));
    } catch (e) {
      resolve(lsGet(k));
    }
  });
}
function putKey(k, v) {
  return new Promise((resolve) => {
    if (!idb) return resolve(lsSet(k, v));
    try {
      const t = idb.transaction('kv', 'readwrite');
      t.objectStore('kv').put(v, k);
      t.oncomplete = () => resolve(true);
      t.onerror = t.onabort = () => resolve(lsSet(k, v));
    } catch (e) {
      resolve(lsSet(k, v));
    }
  });
}
async function loadData() {
  if (!idb) idb = await openDB();
  const [purchases, observations, rate] = await Promise.all(['purchases', 'observations', 'rate'].map(getKey));
  D = cleanData({ purchases, observations, rate });
}
// save one part (or every part) of D; tells you if saving failed, e.g. when storage is full
async function save(...keys) {
  if (!keys.length) keys = ['purchases', 'observations', 'rate'];
  const ok = await Promise.all(keys.map((k) => putKey(k, D[k])));
  if (ok.includes(false)) toast('Couldn’t save. Your device may be out of space.');
  return !ok.includes(false);
}

/* ===== Device-only bits (not backed up) ===== */
function lastBackup() {
  const v = localStorage.getItem('suki:lastBackup'),
    d = v ? new Date(v) : null;
  return d && !isNaN(d) ? d : null;
}
const backupDue = () => {
  const d = lastBackup();
  return D.purchases.length + D.observations.length > 0 && (!d || Date.now() - d > 14 * 864e5);
};
function loadDraft() {
  try {
    const d = JSON.parse(localStorage.getItem('suki:draft') || 'null');
    return d && typeof d === 'object' ? d : {};
  } catch (e) {
    return {};
  }
}
function saveDraft(d) {
  try {
    if (d && Object.values(d).some((v) => v)) localStorage.setItem('suki:draft', JSON.stringify(d));
    else localStorage.removeItem('suki:draft');
  } catch (e) {}
}
