/* Suki · ui.js
   Top bar, tab bar, top tabs and sidebar; sheets; render() and go(); toasts.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Form state =====
   What's typed in each form lives here, so a redraw (a rate arriving, rotating the phone) never loses it.
   Home's form is also kept in localStorage 'suki:draft', so a half-typed purchase survives closing the app. */
const F = { home: {}, edit: {}, obs: {} };

/* ===== Chrome ===== */
function renderBar() {
  const bar = $('bar'),
    tabsMode = MQ.reg.matches && !MQ.wide.matches;
  bar.classList.toggle('tabsmode', tabsMode);
  const T = $('barT');
  T.classList.toggle('tabs', tabsMode);
  T.innerHTML = tabsMode ? topTabs() : esc(TAB_TITLE[U.tab]);
  $('barL').innerHTML =
    U.tab === 'settings' ? '<button class="circ glass" data-a="tab" data-v="home" aria-label="Back to Home">' + ICON.back + '</button>' : '';
  $('barR').innerHTML =
    (navigator.onLine ? '' : '<span class="pill glass" role="status">Offline</span>') +
    (U.tab === 'home' ? '<button class="circ glass" data-a="tab" data-v="settings" aria-label="Settings">' + ICON.gear + '</button>' : '');
}
const tabButtons = (cls, withIcon) =>
  TABS.map(
    (t, i) =>
      '<button class="' + cls + (tabOf(U.tab) === t[0] ? ' on' : '') + '" data-a="tab" data-v="' + t[0] + '" aria-current="' +
      (tabOf(U.tab) === t[0] ? 'page' : 'false') + '" title="' + t[1] + ' (⌘' + (i + 1) + ')">' + (withIcon ? t[2] : '') + '<span>' + t[1] + '</span></button>'
  ).join('');
const topTabs = () => '<nav class="toptabs glass" aria-label="Tabs">' + tabButtons('', false) + '</nav>';
function renderSide() {
  const el = $('side');
  if (!MQ.wide.matches) {
    el.innerHTML = '';
    el.hidden = true;
    return;
  }
  el.hidden = false;
  el.innerHTML =
    '<div class="sbt">Suki</div>' + tabButtons('sbi', true) +
    '<div class="sbgap"></div><button class="sbi' + (U.tab === 'settings' ? ' on' : '') + '" data-a="tab" data-v="settings" aria-current="' + (U.tab === 'settings' ? 'page' : 'false') + '">' + ICON.gear + '<span>Settings</span></button>';
}
function renderDock() {
  if (MQ.reg.matches || U.sheet) {
    $('dock').innerHTML = '';
    return;
  }
  $('dock').innerHTML = '<nav class="tabbar glass" aria-label="Tabs">' + tabButtons('', true) + '</nav>';
}

/* ===== Drawing ===== */
const SCREENS = { home: scrHome, till: scrTill, search: scrSearch, spending: scrSpending, convert: scrConvert, settings: scrSettings };
const NARROW = { till: 1, convert: 1, settings: 1 };
function render(keepScroll) {
  const y = window.scrollY,
    ae = document.activeElement,
    focusId = ae && ae.id && $('app').contains(ae) ? ae.id : null,
    caret = focusId && ae.selectionStart != null ? [ae.selectionStart, ae.selectionEnd] : null;
  closeSwipes();
  $('app').innerHTML = SCREENS[U.tab]();
  $('app').className = 'tab-' + U.tab + (NARROW[U.tab] ? ' narrow' : '');
  renderBar();
  renderSide();
  renderDock();
  renderSheet();
  if (keepScroll) window.scrollTo(0, y);
  // put the cursor back where it was, so a redraw while typing doesn't interrupt
  if (focusId && $(focusId) && !U.sheet) {
    const el = $(focusId);
    try {
      el.focus({ preventScroll: true });
      if (caret && el.setSelectionRange) el.setSelectionRange(caret[0], caret[1]);
    } catch (e) {}
  }
}
const rerender = () => render(true);
function go(tab) {
  if (!SCREENS[tab]) return;
  const same = U.tab === tab;
  U.tab = tab;
  if (!same) window.scrollTo(0, 0);
  // every tab, Settings included, swaps instantly; the launch into Home has its own fade in boot.js
  render(same);
}

/* ===== Sheets =====
   A sheet rises from the bottom on iPhone and opens in the middle on iPad and Mac. One opened from another
   (editing from a purchase's details) goes back to the first when it closes. */
let shownSheet = null;
function openSheet(name, sd, push) {
  if (push && U.sheet) U.stack.push({ sheet: U.sheet, sd: U.sd });
  else if (!push) U.stack = [];
  U.sheet = name;
  U.sd = sd || {};
  rerender();
}
function closeSheet() {
  const prev = U.stack.pop();
  if (prev) {
    U.sheet = prev.sheet;
    U.sd = prev.sd;
  } else {
    U.sheet = null;
    U.sd = {};
  }
  if (!U.sheet) U.obsFor = null;
  rerender();
}
function sheetWrap(title, body, tools, label) {
  return (
    '<div class="scrim" data-a="close"><div class="sheet glass" role="dialog" aria-modal="true" aria-label="' + esc(label || title) + '">' +
    '<div class="shead"><div class="grab"></div><div class="shrow"><h2>' + title + '</h2>' + (tools || '') +
    '<button class="circ glass sm" data-a="close" aria-label="Close">' + ICON.x + '</button></div></div>' + body + '</div></div>'
  );
}
const confirmBody = (text, btn, action, k, extra) =>
  '<p class="note">' + text + '</p>' + (extra || '') +
  '<button class="cta red" data-a="' + action + '" data-k="' + esc(k || '') + '">' + btn + '</button><button class="ghost" data-a="close">Cancel</button>';

function sheetHTML() {
  const sd = U.sd;
  switch (U.sheet) {
    case 'purchase': {
      const p = D.purchases.find((x) => x.id === sd.id);
      if (!p) return null;
      return sheetWrap('Purchase', purchaseDetail(p), '<button class="circ glass sm" data-a="editPurchase" data-k="' + esc(p.id) + '" aria-label="Edit purchase">' + ICON.pencil + '</button>');
    }
    case 'edit': {
      const isNew = !sd.id;
      if (!isNew && !D.purchases.some((x) => x.id === sd.id)) return null;
      return sheetWrap(
        isNew ? 'Log a purchase' : 'Edit purchase',
        '<form class="card form" data-form="edit" novalidate>' + purchaseForm('edit', F.edit) +
          '<p class="err" id="edit-err" role="alert"></p><button type="submit" class="cta">' + (isNew ? 'Save purchase' : 'Save changes') + '</button></form>'
      );
    }
    case 'item': {
      const it = itemById(sd.id);
      if (!it) return null;
      return sheetWrap(esc(it.group), itemDetail(it.id), '', it.name);
    }
    case 'confirm':
      return sheetWrap(esc(sd.title), confirmBody(esc(sd.text), esc(sd.btn), sd.action, sd.k), '', sd.title);
    case 'erase':
      return sheetWrap(
        'Erase all data?',
        confirmBody(
          'This removes ' + plural(D.purchases.length, 'purchase') + ', ' + plural(D.observations.length, 'price note') + ' and the saved rate from this device. It can’t be undone.',
          'Erase everything',
          'eraseYes',
          '',
          '<button class="btn glass wide" data-a="exportBackup" data-v="push">' + ICON.upload + 'Export a backup first</button>'
        )
      );
    case 'backup':
      return sheetWrap(
        'Export a backup',
        '<p class="note">' + (sd.file ? 'Your backup is ready: ' + plural(D.purchases.length, 'purchase') + ', ' + plural(D.observations.length, 'price note') + (D.rate ? ' and the saved rate' : '') + '. Save it to Files so you can find it later.' : 'Preparing your backup…') + '</p>' +
          '<button class="cta" data-a="saveBackup"' + (sd.file ? '' : ' disabled') + '>' + (sd.file ? 'Save backup' : 'Preparing…') + '</button>'
      );
    case 'restore': {
      const n = sd.data,
        row = (k, a, b) => '<div class="row cmp"><span class="lbl">' + k + '</span><span class="v">' + a + '</span><span class="v b">' + b + '</span></div>';
      return sheetWrap(
        'Restore this backup?',
        '<p class="note">Made ' + (sd.when ? esc(sd.when) : 'on an unknown date') + (sd.skipped ? '. ' + plural(sd.skipped, 'damaged record') + ' will be left out' : '') + '. Restoring replaces what’s on this device.</p>' +
          '<div class="grp"><div class="row cmp head"><span class="lbl"></span><span class="v">This device</span><span class="v b">Backup</span></div>' +
          row('Purchases', D.purchases.length, n.purchases.length) + row('Price notes', D.observations.length, n.observations.length) +
          row('Saved rate', D.rate ? D.rate.value.toFixed(2) : 'None', n.rate ? n.rate.value.toFixed(2) : 'None') + '</div>' +
          '<div class="gap"></div><button class="cta red" data-a="restoreYes">Replace with this backup</button><button class="ghost" data-a="close">Cancel</button>'
      );
    }
    case 'notes': {
      const list = D.observations.slice().sort((a, b) => b.date.localeCompare(a.date));
      return sheetWrap(
        'Price notes',
        list.length
          ? '<div class="grp tiled">' +
              list.map((o) => {
                const it = itemById(o.itemId);
                return '<div class="row">' + tile(it ? it.group : '') + '<button class="lbl plain" data-a="openItem" data-k="' + esc(o.itemId) + '" data-v="push"><b>' + esc(o.itemName) + ' · ' + cash(o.price) + '</b><small>' + esc([relDay(o.date), o.location, o.venue, o.note].filter(Boolean).join(' · ')) + '</small></button>' +
                  '<button class="ibtn" data-a="delObs" data-k="' + esc(o.id) + '" aria-label="Delete this price note">' + ICON.bin + '</button></div>';
              }).join('') + '</div><p class="foot">Add notes from any item in Search.</p>'
          : '<div class="grp"><div class="empty">No price notes yet. Open an item in Search and tap Add when you see a price.</div></div>'
      );
    }
  }
  return null;
}
function renderSheet() {
  const layer = $('layer');
  let html = U.sheet ? sheetHTML() : null;
  // a sheet with nothing to show (its purchase was deleted) closes itself, so the tab bar always comes back
  if (U.sheet && !html) {
    const prev = U.stack.pop();
    U.sheet = prev ? prev.sheet : null;
    U.sd = prev ? prev.sd : {};
    html = U.sheet ? sheetHTML() : null;
    if (!html) U.sheet = null;
    renderDock();
  }
  const key = U.sheet ? U.sheet + ':' + (U.sd.id || '') : null;
  if (!html) {
    layer.innerHTML = '';
    shownSheet = null;
    document.body.classList.remove('sheet-open');
    return;
  }
  const old = layer.querySelector('.sheet'),
    top = old ? old.scrollTop : 0;
  layer.innerHTML = html;
  const sh = layer.querySelector('.sheet');
  // redrawing the same sheet keeps its place and doesn't rise again
  if (key === shownSheet) {
    sh.classList.add('still');
    layer.querySelector('.scrim').classList.add('still');
    sh.scrollTop = top;
  } else {
    const f = sh.querySelector('input:not([type=date]),textarea');
    if (U.sheet === 'edit' && !U.sd.id && f) setTimeout(() => f.focus({ preventScroll: true }), 60);
  }
  shownSheet = key;
  document.body.classList.add('sheet-open');
}

/* ===== Toasts ===== */
let toastT = null;
function toast(t) {
  clearTimeout(toastT);
  const o = document.querySelector('.toast');
  if (o) o.remove();
  const el = document.createElement('div');
  el.className = 'toast glass';
  el.setAttribute('role', 'status');
  el.textContent = t;
  document.body.appendChild(el);
  toastT = setTimeout(() => {
    el.classList.add('out');
    setTimeout(() => el.remove(), 250);
  }, 2200);
}
