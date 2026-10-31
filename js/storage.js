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
  // "₱459", "PHP 1,250" and "1 000" read as amounts too, so an older or hand-made record isn't lost over its format (Q05)
  const n = typeof x === 'string' ? parseFloat(x.replace(/₱|php/gi, '').replace(/[,\s]/g, '')) : +x;
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
// one key read from both places: what IndexedDB holds (undefined if nothing) and what the localStorage fallback holds
function readBoth(k) {
  return new Promise((resolve) => {
    const ls = lsGet(k);
    if (!idb) return resolve({ db: undefined, ls });
    try {
      const r = idb.transaction('kv', 'readonly').objectStore('kv').get(k);
      r.onsuccess = () => resolve({ db: r.result, ls });
      r.onerror = () => resolve({ db: undefined, ls });
    } catch (e) {
      resolve({ db: undefined, ls });
    }
  });
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
/* ===== Keeping data safe (Q05) =====
   - STORE_WARN: the storage database wouldn't open, so saves go to the smaller localStorage spot. Home says so.
   - Anything saved that Suki can't read is copied to 'rescue' before anything saves over it; Settings can save it as a file.
   - A restore or Erase first keeps what was on the phone in 'safety', so it can be put back. */
let STORE_WARN = false,
  RESCUE = [],
  SAFETY = null;
const KEYS = ['purchases', 'observations', 'rate'];
// what in a key's raw value couldn't be read: the whole value, or the records that had to be dropped
function unreadable(k, raw) {
  if (raw === undefined || raw === null) return [];
  if (k === 'rate') return cleanRate(raw) ? [] : [raw];
  if (!Array.isArray(raw)) return [raw];
  const fn = k === 'purchases' ? cleanPurchase : cleanObservation;
  return raw.filter((r) => !fn(r));
}
// records from the fallback spot that IndexedDB doesn't have (saved while it wouldn't open), merged in by id
function mergeIn(dbList, lsList) {
  if (!Array.isArray(lsList) || !lsList.length) return { list: dbList, added: 0 };
  const base = Array.isArray(dbList) ? dbList.slice() : [];
  const ids = new Set(base.map((r) => r && String(r.id)));
  let added = 0;
  lsList.forEach((r) => {
    if (r && typeof r === 'object' && !ids.has(String(r.id))) {
      base.push(r);
      added++;
    }
  });
  return { list: base, added };
}
async function loadData() {
  if (!idb) idb = await openDB();
  STORE_WARN = !idb && 'indexedDB' in window;
  const got = await Promise.all(KEYS.map(readBoth)),
    raw = {};
  let merged = 0;
  KEYS.forEach((k, i) => {
    const g = got[i];
    if (!idb || g.db === undefined) return (raw[k] = g.ls);
    if (k === 'rate') {
      // the newer of the two rates
      const a = cleanRate(g.db),
        b = cleanRate(g.ls);
      raw[k] = a && b && new Date(b.cachedAt) > new Date(a.cachedAt) ? g.ls : g.db;
      return;
    }
    const m = mergeIn(g.db, g.ls);
    raw[k] = m.list;
    merged += m.added;
  });
  D = cleanData(raw);
  const [rescue, safety] = await Promise.all([getKey('rescue'), getKey('safety')]);
  RESCUE = Array.isArray(rescue) ? rescue : [];
  SAFETY = safety && typeof safety === 'object' && safety.data ? safety : null;
  // copy what couldn't be read somewhere safe before anything can save over it
  const lost = [];
  KEYS.forEach((k) => unreadable(k, raw[k]).forEach((r) => lost.push({ key: k, raw: r })));
  if (lost.length) {
    RESCUE = RESCUE.concat([{ at: new Date().toISOString(), items: lost }]);
    await putKey('rescue', RESCUE);
  }
  // fallback records now safely in IndexedDB: the fallback copies can go
  if (idb && merged) {
    const ok = await Promise.all(KEYS.map((k) => putKey(k, D[k])));
    if (!ok.includes(false))
      KEYS.forEach((k) => {
        try {
          localStorage.removeItem('suki:' + k);
        } catch (e) {}
      });
  }
}
const rescueCount = () => RESCUE.reduce((n, r) => n + ((r && r.items && r.items.length) || 0), 0);
const rescueDue = () => RESCUE.some((r) => r && !r.saved);
// keep what's on the phone before a restore or Erase; false if it couldn't be kept (then nothing should change)
async function keepSafetyCopy(why) {
  const s = { at: new Date().toISOString(), why, data: { purchases: D.purchases, observations: D.observations, rate: D.rate } };
  const ok = await putKey('safety', s);
  if (ok) SAFETY = s;
  return ok;
}
// save one part (or every part) of D; tells you if saving failed, e.g. when storage is full.
// The warning stays until it's tapped, so a purchase that wasn't saved never looks saved (Q05)
async function save(...keys) {
  if (!keys.length) keys = ['purchases', 'observations', 'rate'];
  const ok = await Promise.all(keys.map((k) => putKey(k, D[k])));
  if (ok.includes(false)) toast('Couldn’t save. Your device may be out of space, so back up soon.', null, true);
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
