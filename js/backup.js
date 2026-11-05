/* Suki · backup.js
   Backups (export, check, restore), erasing everything, and the CSV export.
   File naming and the share-sheet save come from Vocal Sessions.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Saving a file: the share sheet on iPhone and iPad (Save to Files), a download elsewhere ===== */
function downloadFile(file) {
  const u = URL.createObjectURL(file),
    a = document.createElement('a');
  a.href = u;
  a.download = file.name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 4000);
}
async function shareFile(file) {
  const touch = navigator.maxTouchPoints > 0;
  if (touch && navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: file.name });
      return 'shared';
    } catch (e) {
      if (e && e.name === 'AbortError') return 'cancelled';
    }
  }
  downloadFile(file);
  return 'downloaded';
}
function deviceName() {
  const u = navigator.userAgent || '';
  if (/iPad/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1)) return 'iPad';
  if (/iPhone|iPod/.test(u)) return 'iPhone';
  if (/Macintosh/.test(u)) return 'Mac';
  if (/Android/.test(u)) return 'Android';
  return 'computer';
}
const ym = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0');
// one file per month per device: backing up again this month replaces this month's file in Files
const backupName = (d) => 'Suki backup · ' + ym(d) + ' · ' + deviceName() + '.json';

/* ===== Export ===== */
function backupJSON(now) {
  return JSON.stringify(
    {
      README: [
        'This is a backup of the Suki app: your purchases, price notes, the saved exchange rate and the words Smart add has learned.',
        'To restore it, open Suki › Settings › Restore a backup and choose this file.',
      ],
      app: 'Suki',
      schemaVersion: 1,
      appVersion: APP_VERSION,
      exportedAt: now.toISOString(),
      device: deviceName(),
      purchases: D.purchases,
      observations: D.observations,
      rate: D.rate,
      learned: D.learned,
    },
    null,
    2
  );
}
// two steps, so the share sheet opens straight from a tap (iOS needs that): Preparing, then Save backup
function exportBackup(push) {
  openSheet('backup', {}, push);
  const sd = U.sd;
  setTimeout(() => {
    if (U.sheet !== 'backup' || U.sd !== sd) return;
    const now = new Date();
    sd.file = new File([backupJSON(now)], backupName(now), { type: 'application/json' });
    rerender();
  }, 250);
}
async function saveBackup() {
  const f = U.sd.file;
  if (!f) return;
  const r = await shareFile(f);
  if (r === 'cancelled') return;
  try {
    localStorage.setItem('suki:lastBackup', new Date().toISOString());
  } catch (e) {}
  if (U.sheet === 'backup') closeSheet();
  else rerender();
  toast(r === 'shared' ? 'Backup saved' : 'Backup downloaded');
}

/* ===== Restore ===== */
async function readBackupFile(file) {
  let raw;
  try {
    raw = JSON.parse(await file.text());
  } catch (e) {
    toast('That file isn’t a Suki backup');
    return;
  }
  if (!raw || typeof raw !== 'object' || (raw.app !== 'Suki' && !Array.isArray(raw.purchases)) || !Array.isArray(raw.purchases)) {
    toast('That file isn’t a Suki backup');
    return;
  }
  const data = cleanData(raw);
  // a backup from before Smart add (Q14) has no learned words: the ones on this device stay
  if (!Array.isArray(raw.learned)) data.learned = D.learned.slice();
  const skipped =
      raw.purchases.length - data.purchases.length + (Array.isArray(raw.observations) ? raw.observations.length - data.observations.length : 0);
  // a backup with nothing usable in it would only empty the phone, so it's turned away (Q05)
  if (!data.purchases.length && !data.observations.length) {
    toast(skipped ? 'Nothing in that backup can be read, so nothing has changed.' : 'That backup is empty, so nothing has changed.', null, true);
    return;
  }
  const d = new Date(raw.exportedAt);
  openSheet('restore', { data, skipped, when: isNaN(d) ? '' : 'on ' + fileDate(d) + (raw.device ? ' on ' + raw.device : '') });
}
async function restoreYes() {
  if (U.sheet !== 'restore' || !U.sd.data) return;
  const data = U.sd.data;
  // what's on the phone is kept first; if it can't be kept, nothing changes (Q05)
  if (!(await keepSafetyCopy('restore'))) return safetyFailed();
  D = data;
  U.sel = U.item = null;
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  go('home');
  toast('Backup restored', putBack);
  await save();
}

// the safety copy couldn't be kept: nothing changes, and the question that asked (an alert since Q27) is closed
function safetyFailed() {
  if (ALERTS[U.sheet]) closeSheet();
  toast('Couldn’t keep a safety copy of what’s here, so nothing has changed.', null, true);
}

/* ===== Erase everything ===== */
async function eraseYes() {
  if (!(await keepSafetyCopy('erase'))) return toast('Couldn’t keep a safety copy of what’s here, so nothing has changed.', null, true);
  D = { purchases: [], observations: [], rate: null, learned: [] };
  F.home = {};
  F.smart = { text: '', over: {} };
  saveDraft({});
  saveSmart();
  U.sel = U.item = null;
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  rerender();
  toast('Everything erased', putBack);
  await save();
}

/* ===== Putting back what was there before the last restore or Erase (Q05) =====
   It swaps: what's here now becomes the safety copy, so putting back can itself be undone. */
async function putBack() {
  if (!SAFETY) return;
  const before = SAFETY;
  if (!(await keepSafetyCopy(before.why))) return safetyFailed();
  const keep = D.learned;
  D = cleanData(before.data);
  // a safety copy from before Smart add (Q14) has no learned words: the ones here stay
  if (!Array.isArray(before.data.learned)) D.learned = keep;
  U.sel = U.item = null;
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  rerender();
  toast('Put back what was there before');
  await save();
}

/* ===== Recovered data: what Suki couldn't read, saved as a file (Q05) ===== */
function rescueFile() {
  const now = new Date();
  return new File(
    [JSON.stringify({ README: ['Records Suki couldn’t read, kept so nothing is lost. Send this to whoever helps with the app, or keep it.'], app: 'Suki', kind: 'recovered', exportedAt: now.toISOString(), recovered: RESCUE }, null, 2)],
    'Suki recovered data · ' + localISO(now) + '.json',
    { type: 'application/json' }
  );
}
async function saveRescue() {
  if (!RESCUE.length) return;
  const r = await shareFile(rescueFile());
  if (r === 'cancelled') return;
  RESCUE = RESCUE.map((x) => Object.assign({}, x, { saved: true }));
  await putKey('rescue', RESCUE);
  rerender();
  toast(r === 'shared' ? 'Recovered data saved' : 'Recovered data downloaded');
}
async function clearRescue() {
  RESCUE = [];
  await putKey('rescue', []);
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  rerender();
  toast('Recovered data cleared');
}

/* ===== CSV (opens in Numbers or Excel) ===== */
function exportCSV() {
  const list = spendingList();
  const cols = [
    ['Date', (p) => p.date],
    ['Item', (p) => p.item],
    ['Amount (PHP)', (p) => p.price.toFixed(2)],
    ['Category', (p) => p.category],
    ['Location', (p) => p.location],
    ['Where bought', (p) => p.venue],
    ['Paid with', (p) => p.payment],
    ['Notes', (p) => p.notes],
    ['GBP at the time', (p) => (p.rateAtPurchase ? (p.price / p.rateAtPurchase).toFixed(2) : '')],
    ['Rate (PHP per GBP)', (p) => (p.rateAtPurchase ? String(p.rateAtPurchase) : '')],
  ];
  // a leading = + - or @ would be read as a formula by spreadsheets, so those get a ' in front
  const cell = (v) => {
    v = String(v == null ? '' : v);
    if (/^[=+\-@]/.test(v)) v = "'" + v;
    return '"' + v.replace(/"/g, '""') + '"';
  };
  const text = '﻿' + [cols.map((c) => cell(c[0])).join(',')].concat(list.map((p) => cols.map((c) => cell(c[1](p))).join(','))).join('\r\n');
  const name = 'Suki purchases · ' + localISO() + '.csv';
  shareFile(new File([text], name, { type: 'text/csv' })).then((r) => {
    if (r !== 'cancelled') toast(plural(list.length, 'purchase') + ' exported');
  });
}
