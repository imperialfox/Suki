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
        'This is a backup of the Suki app: your purchases, price notes and the saved exchange rate.',
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
  const data = cleanData(raw),
    skipped =
      raw.purchases.length - data.purchases.length + (Array.isArray(raw.observations) ? raw.observations.length - data.observations.length : 0);
  const d = new Date(raw.exportedAt);
  openSheet('restore', { data, skipped, when: isNaN(d) ? '' : 'on ' + fileDate(d) + (raw.device ? ' on ' + raw.device : '') });
}
async function restoreYes() {
  if (U.sheet !== 'restore' || !U.sd.data) return;
  D = U.sd.data;
  U.sel = U.item = null;
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  go('home');
  toast('Backup restored');
  await save();
}

/* ===== Erase everything ===== */
async function eraseYes() {
  D = { purchases: [], observations: [], rate: null };
  F.home = {};
  saveDraft({});
  U.sel = U.item = null;
  U.stack = [];
  U.sheet = null;
  U.sd = {};
  rerender();
  toast('Everything erased');
  await save();
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
