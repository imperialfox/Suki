/* Suki · storage.js
   Saved data: loading, checking and saving it.
   Everything stays on this device, in the same places Suki has always used, so nothing is lost on updating:
   - IndexedDB database 'suki-db', store 'kv', keys 'purchases', 'observations', 'rate' and 'learned' (Q14)
   - localStorage 'suki:<key>' as the fallback when IndexedDB isn't available
   - localStorage 'suki:lastBackup' (when a backup was last saved), 'suki:draft' (a half-typed purchase),
     'suki:motion' (motion speed, see motion.js), 'suki:logSide' (which side of Home's Log card shows) and
     'suki:smart' (a half-typed Smart add line) and 'suki:noteAnim' (Quick Till's note animation, Q18).
     None of these go into backups.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Data ===== */
const CATS = ['Food & drink', 'Transport', 'Groceries', 'Shopping', 'Accommodation', 'Activities', 'Other'];
const VENUES = ['Palengke', 'Street vendor', 'Carinderia', 'Restaurant', 'Convenience store', 'Supermarket', 'Transport', 'Other'];
const PAYMENTS = ['Cash', 'Revolut', 'Other card', 'Other'];
let D = { purchases: [], observations: [], rate: null, learned: [] };

/* ===== Checking =====
   Anything loaded or restored passes through these, so damaged data can't stop the app starting.
   Records missing what they can't do without (a name and an amount) are dropped; everything else is tidied.
   Fields these don't know about are kept, so a newer version's data survives a trip through this one. */
const str = (x) => (typeof x === 'string' ? x.trim() : typeof x === 'number' ? String(x) : '');
const money = (x) => {
  // "₱459", "PHP 1,250" and "1 000" read as amounts too, so an older or hand-made record isn't lost over its format (Q05)
  const n = typeof x === 'string' ? parseFloat(x.replace(/₱|php/gi, '').replace(/[,\s]/g, '')) : +x;
  // above ₱10,000,000 or below ₱0.01 is a damaged value, not a purchase (Q06)
  if (!(n >= 0.005 && n <= 1e7)) return null;
  return Number.isFinite(n) && n > 0 ? Math.round(n * 100) / 100 : null;
};
function isoDate(x) {
  // a date has to be real: "2026-02-30" isn't, so it's treated like any other bad date (Q06)
  if (typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x)) {
    const d = new Date(x + 'T12:00:00');
    return !isNaN(d) && localISO(d) === x ? x : null;
  }
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
  const out = Object.assign({}, p, {
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
  }, 'said' in p ? { said: str(p.said).slice(0, 500) } : {});
  // the rate's day and source, and "estimated" while it's today's rate standing in for that day's (Q22).
  // Each is dropped if it isn't the right kind of thing, never kept as junk
  if ('rateDate' in p) {
    const d = isoDate(p.rateDate);
    if (d && typeof p.rateDate === 'string' && d === p.rateDate) out.rateDate = d;
    else delete out.rateDate;
  }
  if ('rateSource' in p) {
    const s = str(p.rateSource).slice(0, 60);
    if (s) out.rateSource = s;
    else delete out.rateSource;
  }
  if (p.rateEstimated === true) out.rateEstimated = true;
  else delete out.rateEstimated;
  // saidAt (Q15): when he said it to the Siri Shortcut, "2026-11-21 13:05". Anything else is dropped, not kept as junk
  if ('saidAt' in p) {
    const at = READER.stampOf(p.saidAt);
    if (at) out.saidAt = at;
    else delete out.saidAt;
  }
  return out;
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
// a word Smart add learned (Q14): {id, word, category, label}. The word is its id, so each word is kept once
function cleanWord(w) {
  if (!w || typeof w !== 'object' || Array.isArray(w)) return null;
  const word = str(w.word).toLowerCase().slice(0, 60);
  if (!word || !CATS.includes(w.category)) return null;
  return Object.assign({}, w, { id: word, word, label: str(w.label).slice(0, 200) || word });
}
function cleanLearned(list) {
  const by = new Map();
  (Array.isArray(list) ? list : []).map(cleanWord).filter(Boolean).forEach((w) => by.set(w.word, w));
  return [...by.values()];
}
const learnedMap = () => {
  const o = {};
  D.learned.forEach((w) => (o[w.word] = w.category));
  return o;
};
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
    learned: cleanLearned(d.learned),
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
const KEYS = ['purchases', 'observations', 'rate', 'learned'];
// what in a key's raw value couldn't be read: the whole value, or the records that had to be dropped
function unreadable(k, raw) {
  if (raw === undefined || raw === null) return [];
  if (k === 'rate') return cleanRate(raw) ? [] : [raw];
  if (!Array.isArray(raw)) return [raw];
  const fn = k === 'purchases' ? cleanPurchase : k === 'learned' ? cleanWord : cleanObservation;
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
/* ===== Never save before loading (Q31) =====
   Until the first load has finished, D is the empty starting list, so a save would write that over everything
   saved. save() holds its keys instead; anything added meanwhile (a purchase logged on a slow start) is added to
   the loaded lists, and the held keys are saved once. If loading fails, saves stay held and pull to refresh tries
   loading again. */
let READY = false;
const HELD = new Set(),
  heldWait = [];
// records added before loading finished (by id; a learned word's id is the word), and a newer rate, put into the loaded data.
// known (Q33): ids this window had already loaded or saved, so only what it added since is carried over. Returns the keys it changed
function adoptEarly(early, known) {
  const changed = new Set();
  if (!early || early === D) return changed;
  RECORDS.forEach((k) => {
    const have = new Set(D[k].map((r) => String(r.id))),
      old = (known && known[k]) || new Set(),
      add = cleanList(early[k], k === 'purchases' ? cleanPurchase : k === 'learned' ? cleanWord : cleanObservation).filter(
        (r) => !have.has(String(r.id)) && !old.has(String(r.id))
      );
    if (!add.length) return;
    // purchases are newest first, as Home adds them; notes and words go on the end, as they're added
    D[k] = k === 'purchases' ? add.concat(D[k]) : D[k].concat(add);
    changed.add(k);
  });
  const r = cleanRate(early.rate);
  if (r && (!D.rate || new Date(r.cachedAt) > new Date(D.rate.cachedAt))) {
    D.rate = r;
    changed.add('rate');
  }
  return changed;
}
async function loadData() {
  // a load that starts before the first one finishes (pull to refresh on a slow start) keeps held records too
  const early = !READY;
  try {
    // once loaded, a reload waits its turn behind any save (Q33)
    await (early ? readData(true) : serial(() => readData(false)));
  } catch (e) {
    // nothing was read, so nothing may be saved: held saves wait for the next load (pull to refresh)
    if (!READY) return;
    throw e;
  }
  // a second load that finished after the first: anything it put back is saved too
  if (READY) {
    const again = [...HELD];
    HELD.clear();
    if (again.length) await save(...again);
    return;
  }
  READY = true;
  const keys = [...HELD],
    wait = heldWait.splice(0);
  HELD.clear();
  const ok = keys.length ? await save(...keys) : true;
  wait.forEach((done) => done(ok));
}
async function readData(early) {
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
  const before = D;
  D = cleanData(raw);
  // what's stored now, so a save can tell if another window has saved since (Q33)
  KEYS.forEach((k, i) => (SEEN[k] = sig(idb ? got[i].db : got[i].ls)));
  knowNow();
  if (early) adoptEarly(before).forEach((k) => HELD.add(k));
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
    KEYS.forEach((k) => (SEEN[k] = sig(D[k])));
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
  // before loading has finished there's nothing true to keep, so a restore or Erase changes nothing (Q31)
  if (!READY) return false;
  const s = { at: new Date().toISOString(), why, data: { purchases: D.purchases, observations: D.observations, rate: D.rate, learned: D.learned } };
  const ok = await putKey('safety', s);
  if (ok) SAFETY = s;
  return ok;
}
// save one part (or every part) of D; tells you if saving failed, e.g. when storage is full.
// The warning stays until it's tapped, so a purchase that wasn't saved never looks saved (Q05)
async function save(...keys) {
  if (!keys.length) keys = KEYS;
  // not loaded yet: held, and saved with what's loaded once it lands; this answers when that save has happened (Q31)
  if (!READY) {
    keys.forEach((k) => HELD.add(k));
    return new Promise((done) => heldWait.push(done));
  }
  const ok = await serial(() => writeKeys(keys));
  if (!ok) toast('Couldn’t save. Your device may be out of space, so back up soon.', null, true);
  return ok;
}

/* ===== Other windows (Q33) =====
   Two Safari tabs (or a tab and the Home Screen app on a Mac) share one storage. Each window keeps the list it loaded,
   so a save from a window that hasn't seen the other's purchases would write them away. Not a merge: when another window
   has saved, this one reloads what's stored, keeps only the records it added itself since, and then saves.
   - SEEN: what this window last read or wrote for each key. A save of his records reads the key in the same storage
     transaction and writes only if it's still SEEN, so nothing between the check and the write can slip in.
   - KNOWN: the ids this window has loaded or saved, so a reload can tell what it added itself.
   - Every save tells the other windows (BroadcastChannel 'suki'), and they reload straight away, with a toast.
     Saves and reloads in one window take turns (serial), so a reload never lands in the middle of a save. */
const RECORDS = ['purchases', 'observations', 'learned'];
const SEEN = {},
  KNOWN = {};
const sig = (v) => (v === undefined || v === null ? '∅' : JSON.stringify(v));
const idsOf = (list) => new Set((Array.isArray(list) ? list : []).map((r) => r && String(r.id)));
function knowNow(keys = RECORDS) {
  keys.forEach((k) => RECORDS.includes(k) && (KNOWN[k] = idsOf(D[k])));
}
let CHAIN = Promise.resolve();
function serial(fn) {
  const p = CHAIN.then(fn);
  CHAIN = p.catch(() => {});
  return p;
}
// write one key, but for his records only if nobody has saved it since this window last saw it: true, false, or 'stale'
function putChecked(k, v, check) {
  const want = SEEN[k],
    guard = check && RECORDS.includes(k) && want !== undefined;
  // taken as it's written: the list can change while the write is under way
  let snap = null;
  const take = () => (snap = { sig: sig(v), ids: RECORDS.includes(k) ? idsOf(v) : null }),
    done = (ok) => {
      if (ok && snap) {
        SEEN[k] = snap.sig;
        if (snap.ids) KNOWN[k] = snap.ids;
      }
      return ok;
    };
  return new Promise((resolve) => {
    if (!idb) {
      if (guard && sig(lsGet(k)) !== want) return resolve('stale');
      take();
      return resolve(done(lsSet(k, v)));
    }
    // the fallback spot isn't what SEEN describes, so the next save can't check against it
    let fell = false;
    const fallback = () => {
      if (fell) return;
      fell = true;
      take();
      const ok = lsSet(k, v);
      if (ok && snap.ids) KNOWN[k] = snap.ids;
      SEEN[k] = undefined;
      resolve(ok);
    };
    try {
      const t = idb.transaction('kv', 'readwrite'),
        s = t.objectStore('kv');
      let stale = false;
      const write = () => {
        try {
          take();
          s.put(v, k);
        } catch (e) {
          t.abort();
        }
      };
      if (!guard) write();
      else {
        const r = s.get(k);
        r.onsuccess = () => (sig(r.result) !== want ? (stale = true) : write());
      }
      t.oncomplete = () => resolve(stale ? 'stale' : done(true));
      t.onerror = t.onabort = fallback;
    } catch (e) {
      fallback();
    }
  });
}
// save the keys; if another window saved first, reload and try again (the third try writes without checking)
async function writeKeys(keys) {
  const want = new Set(keys);
  for (let i = 0; i < 3; i++) {
    const list = [...want],
      res = await Promise.all(list.map((k) => putChecked(k, D[k], i < 2)));
    if (!res.includes('stale')) {
      tellOthers(list.filter((k, j) => res[j] === true));
      return !res.includes(false);
    }
    (await syncData()).forEach((k) => want.add(k));
  }
  return false;
}
// read what's stored again and keep what this window added since; returns the keys that still need saving
async function syncData() {
  const before = D,
    known = Object.assign({}, KNOWN),
    old = Object.assign({}, SEEN);
  await readData(false);
  const mine = adoptEarly(before, known),
    theirs = RECORDS.some((k) => SEEN[k] !== old[k]);
  if (theirs) toast('Updated from another window');
  if (theirs || SEEN.rate !== old.rate || mine.size) dataLanded();
  return mine;
}
let CHAN = null;
function tellOthers(keys) {
  if (CHAN && keys.length)
    try {
      CHAN.postMessage({ keys });
    } catch (e) {}
}
function fromOther(keys) {
  if (!READY || !Array.isArray(keys) || !keys.some((k) => KEYS.includes(k))) return;
  serial(async () => {
    const mine = await syncData();
    if (mine.size) await writeKeys([...mine]);
  }).catch(() => {});
}
try {
  CHAN = new BroadcastChannel('suki');
  CHAN.onmessage = (e) => fromOther(e.data && e.data.keys);
} catch (e) {
  CHAN = null;
}
// with no IndexedDB, saves go to localStorage, which tells the other windows itself
window.addEventListener('storage', (e) => {
  const m = !idb && e.key && /^suki:(\w+)$/.exec(e.key);
  if (m && KEYS.includes(m[1])) fromOther([m[1]]);
});

/* ===== Device-only bits (not backed up) ===== */
// Quick Till's note animation (Q18): 'fly' (the starting setting) or 'slot'. Kept as 'suki:noteAnim' only when it's Slot
const noteAnim = () => {
  try {
    return localStorage.getItem('suki:noteAnim') === 'slot' ? 'slot' : 'fly';
  } catch (e) {
    return 'fly';
  }
};
function setNoteAnim(v) {
  try {
    if (v === 'slot') localStorage.setItem('suki:noteAnim', 'slot');
    else localStorage.removeItem('suki:noteAnim');
  } catch (e) {}
}
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
