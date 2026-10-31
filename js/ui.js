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
      (tabOf(U.tab) === t[0] ? 'page' : 'false') + '" title="' + t[1] + ' (' + (APPLE ? '⌘' : 'Ctrl+') + (i + 1) + ')">' + (withIcon ? t[2] : '') + '<span>' + t[1] + '</span></button>'
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
  fadeScrollers();
  drawnDay = localISO();
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
  if (!same) {
    window.scrollTo(0, 0);
    U.shown = SHOW_STEP;
  }
  // every tab, Settings included, swaps instantly; the launch into Home has its own fade in boot.js
  render(same);
}

/* ===== A new day: when the date moves on (coming back to the app, or a check each minute), redraw in place so
   "Today", the bars and the calendar move on too. It waits while a sheet is open or a box has the cursor (Q03). ===== */
let drawnDay = null;
function dayCheck() {
  if (!drawnDay || localISO() === drawnDay || document.visibilityState === 'hidden') return false;
  const ae = document.activeElement;
  if (U.sheet || (ae && ae.matches && ae.matches('input,textarea,select'))) return false;
  rerender();
  return true;
}
setInterval(dayCheck, 60000);
document.addEventListener('visibilitychange', dayCheck);

/* ===== A row that scrolls sideways fades at the edge that has more to see ===== */
function fadeScrollers(root) {
  (root ? [root] : document.querySelectorAll('.scroller')).forEach((s) => {
    const more = s.scrollWidth - s.clientWidth;
    s.classList.toggle('fl', more > 2 && s.scrollLeft > 2);
    s.classList.toggle('fr', more > 2 && s.scrollLeft < more - 2);
  });
}
document.addEventListener('scroll', (e) => e.target.classList && e.target.classList.contains('scroller') && fadeScrollers(e.target), { capture: true, passive: true });

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
      return sheetWrap(esc(BROWSE.find((b) => b[0] === browseOf(it))[1]), itemDetail(it.id), '', it.name);
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
    case 'rescue':
      return sheetWrap(
        'Recovered data',
        '<p class="note">' + plural(rescueCount(), 'record') + ' saved on this device couldn’t be read, so ' + (rescueCount() === 1 ? 'it was' : 'they were') + ' kept here instead of being lost. Your other purchases and notes are fine.</p>' +
          '<button class="cta" data-a="saveRescue">Save a copy</button>' +
          (RESCUE.some((r) => r && r.saved) ? '<button class="ghost red" data-a="clearRescue">Clear it</button>' : '<p class="foot">Once you’ve saved a copy, you can clear it from here.</p>')
      );
    case 'putback': {
      if (!SAFETY) return null;
      const s = SAFETY.data,
        n = (s.purchases || []).length,
        o = (s.observations || []).length;
      return sheetWrap(
        'Put back what was here?',
        confirmBody(
          'Before your last ' + (SAFETY.why === 'erase' ? 'erase' : 'restore') + ' (' + whenAgo(new Date(SAFETY.at)).replace(/^./, (c) => c.toLowerCase()) + ') this device had ' + plural(n, 'purchase') + ' and ' + plural(o, 'price note') + '. Putting them back replaces what’s here now, which is kept so you can swap back.',
          'Put them back',
          'putBackYes'
        )
      );
    }
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
    case 'calendar': {
      // a month: days you spent on are tinted, today is outlined; tap a day to see what you bought (Q03)
      const m = U.calM || localISO().slice(0, 8) + '01',
        first = atNoon(m),
        lead = (first.getDay() + 6) % 7,
        last = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate(),
        t = localISO(),
        spent = {};
      D.purchases.forEach((p) => p.date.slice(0, 7) === m.slice(0, 7) && (spent[p.date] = (spent[p.date] || 0) + (+p.price || 0)));
      let cells = '';
      for (let i = 0; i < lead; i++) cells += '<span></span>';
      for (let d = 1; d <= last; d++) {
        const iso = m.slice(0, 8) + String(d).padStart(2, '0');
        cells +=
          '<button class="cday' + (spent[iso] ? ' has' : '') + (iso === t ? ' today' : '') + (U.calD === iso ? ' on' : '') + '" data-a="calDay" data-v="' + iso + '" aria-label="' + esc(longDate(iso)) + (spent[iso] ? ', ' + cash(spent[iso]) : '') + '"' + (U.calD === iso ? ' aria-pressed="true"' : '') + '>' + d + '</button>';
      }
      const day = U.calD ? D.purchases.filter((p) => p.date === U.calD).sort(byNewest) : [],
        mTotal = Object.values(spent).reduce((a, b) => a + b, 0);
      return sheetWrap(
        monthName(m),
        '<div class="calhead"><span class="small">' + (mTotal ? cash(Math.round(mTotal * 100) / 100) + ' this month' : 'Nothing logged this month') + '</span><span><button class="circ glass sm" data-a="calStep" data-v="-1" aria-label="Earlier month">' + ICON.back + '</button><button class="circ glass sm fwd" data-a="calStep" data-v="1" aria-label="Later month">' + ICON.back + '</button></span></div>' +
          '<div class="calgrid"><div class="cdows" aria-hidden="true"><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span></div><div class="cdays">' + cells + '</div></div>' +
          (U.calD
            ? hdr(dayHeading(U.calD), day.length ? '<span class="hint">' + cash(sum(day)) + '</span>' : '') +
              (day.length ? '<div class="grp tiled">' + day.map((p) => purchaseRow(p, { push: true, meta: p.location || p.venue || p.category })).join('') + '</div>' : '<div class="grp"><div class="empty">Nothing logged on this day.</div></div>')
            : '<p class="foot">Tap a day to see what you bought.</p>'),
        '',
        'Calendar'
      );
    }
    case 'access': {
      const opts = [['auto', 'Match iPhone'], ['on', 'On'], ['off', 'Off']],
        i = Math.max(0, opts.findIndex((o) => o[0] === MOTION.reducePref()));
      return sheetWrap(
        'Accessibility',
        hdr('Reduce motion') +
          '<div class="segc" id="reduceSeg" role="group" aria-label="Reduce motion" style="--n:3;--i:' + i + '"><span class="knob glass" aria-hidden="true"></span>' +
          opts.map((o) => '<button data-a="setReduce" data-v="' + o[0] + '" aria-pressed="' + (MOTION.reducePref() === o[0]) + '">' + o[1] + '</button>').join('') + '</div>' +
          '<p class="foot">Things fade instead of sliding, zooming or springing. Match iPhone follows Settings › Accessibility › Motion on your iPhone.</p>' +
          hdr('Slow motion') +
          '<div class="grp"><label class="row toggle"><span class="lbl"><b>Slow motion</b></span><input type="checkbox" role="switch" data-a="slowMotion"' + (MOTION.speed() > 1 ? ' checked' : '') + '><span class="sw-ui" aria-hidden="true"></span></label></div>' +
          '<p class="foot">Plays every movement four times slower, for checking how things move. Both settings stay on this device and aren’t saved in backups.</p>'
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
// undo: a function that puts back what was just removed; the toast then shows an Undo button and stays a little longer.
// sticky: a warning that stays until it's tapped (OK); other toasts drop in below it instead of replacing it (Q05)
function toast(t, undo, sticky) {
  if (sticky) {
    const s = document.querySelector('.toast.sticky');
    if (s) s.remove();
    const w = document.createElement('div');
    w.className = 'toast glass sticky';
    w.setAttribute('role', 'alert');
    const span = document.createElement('span');
    span.textContent = t;
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'OK';
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      w.remove();
      document.body.classList.remove('has-sticky');
    });
    w.append(span, b);
    document.body.appendChild(w);
    document.body.classList.add('has-sticky');
    return;
  }
  clearTimeout(toastT);
  const o = document.querySelector('.toast:not(.sticky)');
  if (o) o.remove();
  const el = document.createElement('div');
  el.className = 'toast glass' + (undo ? ' undo' : '');
  el.setAttribute('role', 'status');
  const s = document.createElement('span');
  s.textContent = t;
  el.appendChild(s);
  if (undo) {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = 'Undo';
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      clearTimeout(toastT);
      el.remove();
      undo();
    });
    el.appendChild(b);
  }
  document.body.appendChild(el);
  toastT = setTimeout(() => {
    el.classList.add('out');
    setTimeout(() => el.remove(), 250);
  }, undo ? 4500 : 2200);
}
