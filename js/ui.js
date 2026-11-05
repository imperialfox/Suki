/* Suki · ui.js
   Top bar, tab bar, top tabs and sidebar; sheets; render() and go(); toasts.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Form state =====
   What's typed in each form lives here, so a redraw (a rate arriving, rotating the phone) never loses it.
   Home's form is also kept in localStorage 'suki:draft', so a half-typed purchase survives closing the app. */
const F = { home: {}, edit: {}, obs: {}, smart: { text: '', over: {} } };

/* ===== Chrome ===== */
function renderBar() {
  const bar = $('bar'),
    tabsMode = MQ.reg.matches && !MQ.wide.matches;
  bar.classList.toggle('tabsmode', tabsMode);
  const T = $('barT');
  T.classList.toggle('tabs', tabsMode);
  T.innerHTML = tabsMode ? topTabs() : esc(TAB_TITLE[U.tab]);
  $('barL').innerHTML =
    // on Mac Settings is a sidebar section, so it has no Back (Q24)
    U.tab === 'settings' && !MQ.wide.matches
      ? '<button class="circ glass" data-a="tab" data-v="home" aria-label="Back to Home">' + ICON.back + '</button>'
      : U.tab === 'help'
        ? '<button class="circ glass" data-a="tab" data-v="settings" aria-label="Back to Settings">' + ICON.back + '</button>'
        : U.tab === 'history'
          ? '<button class="circ glass" data-a="tab" data-v="convert" aria-label="Back to Convert">' + ICON.back + '</button>'
          : '';
  $('barR').innerHTML =
    (navigator.onLine ? '' : '<span class="pill glass" role="status">Offline</span>') +
    (U.tab === 'home' ? '<button class="circ glass" data-a="tab" data-v="settings" aria-label="Settings">' + ICON.gear + '</button>' : '') +
    // Spending's own door to the Log sheet (Q08); with nothing logged, the page's own button does it
    (U.tab === 'spending' && D.purchases.length ? '<button class="circ glass" data-a="newPurchase" aria-label="Log a purchase">' + ICON.plus + '</button>' : '');
}
// the tab lit for the page on screen; on Mac, Settings and Help light only the sidebar's Settings (Q24)
const litTab = () => (MQ.wide.matches && (U.tab === 'settings' || U.tab === 'help') ? null : tabOf(U.tab));
const tabButtons = (cls, withIcon) =>
  TABS.map(
    (t, i) =>
      '<button class="' + cls + (litTab() === t[0] ? ' on' : '') + '" data-a="tab" data-v="' + t[0] + '" aria-current="' +
      (litTab() === t[0] ? 'page' : 'false') + '" title="' + t[1] + ' (' + (APPLE ? '⌘' : 'Ctrl+') + (i + 1) + ')">' + (withIcon ? t[2] : '') + '<span>' + t[1] + '</span></button>'
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
    '<div class="sbgap"></div><button class="sbi' + (U.tab === 'settings' || U.tab === 'help' ? ' on' : '') + '" data-a="tab" data-v="settings" aria-current="' + (U.tab === 'settings' ? 'page' : 'false') + '">' + ICON.gear + '<span>Settings</span></button>';
}
function renderDock() {
  // the tab bar stays under a sheet's dim (Q27, shared default 6); iPad and Mac have none
  if (MQ.reg.matches) {
    $('dock').innerHTML = '';
    return;
  }
  $('dock').innerHTML = '<nav class="tabbar glass" aria-label="Tabs">' + tabButtons('', true) + '</nav>';
}

/* ===== Drawing ===== */
const SCREENS = { home: scrHome, till: scrTill, search: scrSearch, spending: scrSpending, convert: scrConvert, settings: scrSettings };
const NARROW = { till: 1, convert: 1, settings: 1 };
function render(keepScroll) {
  // a redraw waits while a finger is on Rate history's chart, so the chart never snaps away (Q23)
  if (typeof histHold === 'function' && histHold(keepScroll)) return;
  const y = window.scrollY,
    ae = document.activeElement,
    focusId = ae && ae.id && $('app').contains(ae) ? ae.id : null,
    caret = focusId && ae.selectionStart != null ? [ae.selectionStart, ae.selectionEnd] : null;
  closeSwipes();
  landNotes(true); // a Till note still in the air lands now, so a redraw leaves nothing behind (Q18)
  drawerReset(); // the till drawer always comes back shut, with nothing left running (Q19)
  $('app').innerHTML = SCREENS[U.tab]();
  if (U.tab === 'home') growSmart();
  if (U.tab === 'history') histAfter();
  $('app').className = 'tab-' + U.tab + (NARROW[U.tab] ? ' narrow' : '');
  renderBar();
  renderSide();
  renderDock();
  renderSheet();
  SCR.screen(); // Q25 the screen's ID and part names, from the register (register.js)
  if (keepScroll) window.scrollTo(0, y);
  fadeScrollers();
  drawnDay = localISO();
  if (typeof tipsAfterRender === 'function') tipsAfterRender();
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
/* ===== Screen IDs (Q25) =====
   The register (register.js) gives every screen, sheet and overlay a permanent ID. render() ends with SCR.screen(),
   which stamps data-screen on #app and data-name on the named parts in #app, the bar, the dock and the sidebar;
   renderSheet() calls SCR.sheet() for the sheet in #layer. The toast, the tip and the launch screen call SCR.mark().
   A part's name comes from its screen's own parts first, then shared, then its action. A screen with no entry gets
   SK-??? and one console warning (the tests fail on it). Settings › Accessibility › Show screen IDs (suki:screenIds,
   this device only) shows a small label in the top corner. */
const SCR = (() => {
  const BY = {};
  REGISTER.screens.forEach((s) => (BY[s.key] = s));
  const warned = {},
    live = (p) => !p.status || p.status === 'Live';
  const viewKey = () => 'tab:' + U.tab;
  const sheetKey = () => (U.sheet === 'confirm' ? 'sheet:confirm/' + (U.sd.action || '') : 'sheet:' + U.sheet);
  function entry(key) {
    const s = BY[key];
    if (s && s.status === 'Live') return s;
    if (!warned[key]) {
      warned[key] = 1;
      console.warn('No screen ID in js/register.js for ' + key);
    }
    return null;
  }
  const id = (key) => (entry(key) || { id: REGISTER.prefix + '-???' }).id;
  // names by action, looked up by data-a (and data-v) in one pass over the buttons
  const BYACT = {};
  REGISTER.actions.filter(live).forEach((p) => {
    const m = p.sel.match(/^\[data-a="([^"]+)"\](?:\[data-v="([^"]+)"\])?$/);
    if (m) BYACT[m[1] + (m[2] === undefined ? '' : '\u0000' + m[2])] = p.name;
  });
  const OWN = {};
  const own = (s) => OWN[s ? s.id : ''] || (OWN[s ? s.id : ''] = REGISTER.shared.concat(s ? s.parts : []).filter(live));
  function name(s, roots) {
    const parts = own(s);
    roots.forEach((r) => {
      if (!r) return;
      (r.dataset.a ? [r, ...r.querySelectorAll('[data-a]')] : r.querySelectorAll('[data-a]')).forEach((el) => {
        const a = el.dataset.a,
          v = el.dataset.v,
          n = (v !== undefined && BYACT[a + '\u0000' + v]) || BYACT[a];
        if (n) el.dataset.name = n;
      });
      parts.forEach((p) => {
        if (r.matches(p.sel)) r.dataset.name = p.name;
        r.querySelectorAll(p.sel).forEach((el) => (el.dataset.name = p.name));
      });
    });
  }
  function stamp(el, key) {
    const s = entry(key);
    el.dataset.screen = s ? s.id : REGISTER.prefix + '-???';
    return s;
  }
  function screen() {
    const s = stamp($('app'), viewKey());
    name(s, [$('app'), $('bar'), $('dock'), $('side')]);
    label();
  }
  // the overlay on top (Q27): the kit's alert, else the top sheet (the kit's on iPhone, Suki's own on iPad and Mac)
  function top() {
    if (!U.sheet) return null;
    const L = $('layer');
    return [...L.querySelectorAll('.pk-alert:not(.pk-leaving)')].pop() || [...L.querySelectorAll('.pk-sheet.sheet:not(.pk-leaving)')].pop() || L.querySelector('#own .scrim .sheet');
  }
  function sheet() {
    const el = top();
    if (el) name(stamp(el, sheetKey()), [el]);
    label();
  }
  // something drawn outside render(): the toast, the tip, the launch screen
  function mark(el, key) {
    if (el) name(stamp(el, key), [el]);
  }
  const idsOn = () => {
    try {
      return localStorage.getItem('suki:screenIds') === 'on';
    } catch (e) {
      return false;
    }
  };
  function setIds(on) {
    try {
      if (on) localStorage.setItem('suki:screenIds', 'on');
      else localStorage.removeItem('suki:screenIds');
    } catch (e) {}
  }
  // the screen's ID, then the open sheet's
  function label() {
    let el = $('scrid');
    if (!idsOn()) {
      if (el) el.remove();
      return;
    }
    if (!el) {
      el = document.createElement('div');
      el.id = 'scrid';
      el.setAttribute('aria-hidden', 'true');
      document.body.appendChild(el);
    }
    const sh = top();
    el.textContent = $('app').dataset.screen + (sh && sh.dataset.screen ? ' · ' + sh.dataset.screen : '');
  }
  // parts drawn in place without a redraw (Search's results, the Till's change, Smart add's preview…) get their
  // names too: one pass after each batch of changes
  let pend = false;
  const again = () => {
    pend = false;
    const a = $('app');
    if (a.dataset.screen) name(BY[viewKey()] || null, [a]);
    const sh = top();
    if (sh) name(BY[sheetKey()] || null, [sh]);
  };
  if (typeof MutationObserver === 'function') {
    const mo = new MutationObserver(() => pend || ((pend = true), queueMicrotask(again)));
    ['app', 'layer'].forEach((k) => $(k) && mo.observe($(k), { childList: true, subtree: true }));
  }
  return { viewKey, sheetKey, id, screen, sheet, top, mark, label, idsOn, setIds, BY };
})();
/* ===== Door rules (Q24) =====
   Tabs swap instantly. Three pages are pushed: Settings from Home's gear, Help from Settings and Rate history from
   Convert. Every door to them moves the same way, and Back (or the tab they belong to) pops them:
   - iPhone: the pushed page slides in over a still copy of the page left behind, which moves a third left and dims
     10% (PUSH_UNDER, PUSH_DIM, after Vocal Sessions' D22), both on the nav spring. Back is the same in reverse.
   - iPad and Mac: they zoom in and out.
   - Mac: Settings is a sidebar section, so Home ⇄ Settings switches like a tab (only Help zooms from it).
   - Reduce Motion: a short fade. Motion off: at once. After a swipe back the page is already there (SB_GONE). */
const PUSH_UNDER = 0.33,
  PUSH_DIM = 0.1,
  PUSHES = { 'home>settings': 'push', 'settings>help': 'push', 'convert>history': 'push', 'settings>home': 'pop', 'help>settings': 'pop', 'history>convert': 'pop' };
function doorKind(from, to) {
  if (MQ.wide.matches && ((from === 'home' && to === 'settings') || (from === 'settings' && to === 'home'))) return null;
  return PUSHES[from + '>' + to] || null;
}
// a still copy of the page as it is now, ids and actions removed: under the pushed page, or over the page popped to
function pageStill(id) {
  const w = document.querySelector('body > .wrap');
  if (!w) return null;
  const s = document.createElement('div'),
    c = w.cloneNode(true),
    d = document.createElement('div'),
    m = c.querySelector('main');
  s.id = id;
  s.setAttribute('aria-hidden', 'true');
  s.inert = true;
  c.style.transform = c.style.transition = '';
  c.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));
  c.querySelectorAll('[data-a]').forEach((el) => el.removeAttribute('data-a'));
  c.querySelectorAll('[data-screen]').forEach((el) => el.removeAttribute('data-screen')); // one screen ID on the page (Q25)
  if (m && window.scrollY) m.style.transform = 'translateY(' + -window.scrollY + 'px)';
  d.className = 'pdim';
  if (id === 'over') s.append(d, c);
  else s.append(c, d);
  document.body.appendChild(s);
  return s;
}
let PUSH = null;
function pushClear() {
  const p = PUSH;
  PUSH = null;
  if (p) {
    clearTimeout(p.t);
    p.a.forEach((x) => x && x.cancel());
    p.st.remove();
  }
  document.body.classList.remove('pushing');
}
function pushPlay(kind, st) {
  const w = document.querySelector('body > .wrap');
  if (!w || !st) return pushClear();
  const W = innerWidth,
    under = 'translateX(' + -PUSH_UNDER * W + 'px)',
    off = 'translateX(' + W + 'px)',
    c = st.querySelector('.wrap'),
    d = st.querySelector('.pdim'),
    o = { spring: 'nav', fill: 'both' };
  document.body.classList.add('pushing');
  const a =
    kind === 'push'
      ? [MOTION.animate(w, [{ transform: off }, { transform: 'none' }], o), MOTION.animate(c, [{ transform: 'none' }, { transform: under }], o), MOTION.animate(d, [{ opacity: 0 }, { opacity: PUSH_DIM }], o)]
      : [MOTION.animate(w, [{ transform: under }, { transform: 'none' }], o), MOTION.animate(c, [{ transform: 'none' }, { transform: off }], o), MOTION.animate(d, [{ opacity: PUSH_DIM }, { opacity: 0 }], o)];
  PUSH = { a, st, t: setTimeout(pushClear, MOTION.dur('nav') + 400) };
  if (a[0]) a[0].onfinish = () => PUSH && PUSH.a === a && pushClear();
}
function go(tab) {
  if (!SCREENS[tab]) return;
  const same = U.tab === tab,
    from = U.tab,
    kind = same ? null : doorKind(from, tab),
    gone = kind === 'pop' && from === 'history' && SB_GONE;
  if (SB_GONE) SB_GONE = false;
  pushClear();
  // the still is taken before the redraw (and before the scroll moves), so it costs no extra frame
  const st = kind && !gone && MOTION.on() && !split() ? pageStill(kind === 'push' ? 'under' : 'over') : null;
  U.tab = tab;
  if (!same) {
    window.scrollTo(0, 0);
    U.shown = SHOW_STEP;
  }
  // the launch into Home has its own fade in boot.js
  render(same);
  if (!kind || gone) return;
  if (!MOTION.on()) return void MOTION.animate($('app'), [{ opacity: 0 }, { opacity: 1 }], { fade: true });
  if (split()) MOTION.animate($('app'), kind === 'push' ? [{ transform: 'scale(.94)', opacity: 0 }, { transform: 'none', opacity: 1 }] : [{ transform: 'scale(1.04)', opacity: 0 }, { transform: 'none', opacity: 1 }], { spring: 'nav', fade: true });
  else pushPlay(kind, st);
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
let shownSheet = null,
  shownDepth = 0, // how many sheets deep the one on screen is (0 = none), so a close can be told from an open
  backTop = 0; // where the sheet underneath was scrolled to, for going back to it
function openSheet(name, sd, push) {
  if (push && U.sheet) {
    const s = document.querySelector('#own .scrim .sheet');
    U.stack.push({ sheet: U.sheet, sd: U.sd, top: s ? s.scrollTop : 0 });
  } else if (!push) U.stack = [];
  U.sheet = name;
  U.sd = sd || {};
  rerender();
}
function closeSheet() {
  const prev = U.stack.pop();
  if (prev) {
    U.sheet = prev.sheet;
    U.sd = prev.sd;
    backTop = prev.top || 0;
  } else {
    U.sheet = null;
    U.sd = {};
  }
  if (!U.sheet) U.obsFor = null;
  rerender();
}
// o.lock: a sheet that can only be left with its own buttons (no ✕, no tapping outside, no dragging down); o.tall, o.cls
function sheetWrap(title, body, tools, label, o) {
  o = o || {};
  return (
    '<div class="scrim"' + (o.lock ? '' : ' data-a="close"') + '><div class="sheet glass' + (o.lock ? ' locked' : '') + (o.tall ? ' tall' : '') + (o.cls ? ' ' + o.cls : '') + '" role="dialog" aria-modal="true" aria-label="' + esc(label || title) + '">' +
    (title === null
      ? ''
      : '<div class="shead">' + (o.lock ? '' : '<div class="grab"></div>') + '<div class="shrow"><h2>' + title + '</h2>' + (tools || '') +
        (o.lock ? '' : '<button class="circ glass sm" data-a="close" aria-label="Close">' + ICON.x + '</button>') + '</div></div>') +
    body + '</div></div>'
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
      const isNew = !sd.id,
        check = sd.smart != null; // a purchase from Smart add's list, being checked: Done puts it back, unsaved (Q14)
      if (!isNew && !D.purchases.some((x) => x.id === sd.id)) return null;
      return sheetWrap(
        check ? 'Check purchase' : isNew ? 'Log a purchase' : 'Edit purchase',
        '<form class="card form" data-form="edit" novalidate>' + purchaseForm('edit', F.edit) +
          '<p class="err" id="edit-err" role="alert"></p><button type="submit" class="cta">' + (check ? 'Done' : isNew ? 'Save purchase' : 'Save changes') + '</button></form>' +
          (F.edit.said ? '<p class="said">You typed: “' + esc(F.edit.said) + '”</p>' : '')
      );
    }
    case 'learned':
      // Settings › Your data, and a door from Smart add (Q14). Each word can be forgotten; they're kept in backups
      return sheetWrap(
        'Words Suki has learned',
        (D.learned.length
          ? '<div class="grp tiled">' +
            D.learned.slice().reverse().map((w) => '<div class="row">' + tile(w.category) + '<span class="lbl"><b>' + esc(w.label) + '</b><small>' + esc(w.category) + (w.label.toLowerCase() !== w.word ? ' · “' + esc(w.word) + '”' : '') + '</small></span><button class="ibtn" data-a="forgetWord" data-k="' + esc(w.word) + '" aria-label="Forget ' + esc(w.label) + '">' + ICON.x + '</button></div>').join('') +
            '</div>'
          : '<div class="grp"><div class="empty">Nothing yet. Change a category in Smart add and Suki remembers the word for next time.</div></div>') +
          '<p class="foot">Smart add uses these first when it picks a category. They’re kept in backups.</p>'
      );
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
          'This removes ' + plural(D.purchases.length, 'purchase') + ', ' + plural(D.observations.length, 'price note') + (D.learned.length ? ', ' + plural(D.learned.length, 'learned word') + ',' : '') + ' and the saved rate from this device. It can’t be undone.',
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
      // an alert (Q27, D08): what's here and what's in the backup, in words, since an alert holds no table
      const n = sd.data,
        list = (a) => (a.length > 1 ? a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1] : a[0]),
        has = (d) => list([plural(d.purchases.length, 'purchase'), plural(d.observations.length, 'price note')].concat(d.learned.length ? [plural(d.learned.length, 'learned word')] : [], d.rate ? ['a saved rate'] : []));
      return sheetWrap(
        'Restore this backup?',
        confirmBody(
          'Made ' + (sd.when ? esc(sd.when) : 'on an unknown date') + (sd.skipped ? ', with ' + plural(sd.skipped, 'damaged record') + ' left out' : '') + '. This device has ' + has(D) + '; the backup has ' + has(n) + '. Restoring replaces what’s on this device.',
          'Replace with this backup',
          'restoreYes'
        )
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
      const step = tintSteps(spent);
      let cells = '';
      for (let i = 0; i < lead; i++) cells += '<span></span>';
      for (let d = 1; d <= last; d++) {
        const iso = m.slice(0, 8) + String(d).padStart(2, '0');
        cells +=
          '<button class="cday' + (spent[iso] ? ' has t' + step[iso] : '') + (iso === t ? ' today' : '') + (U.calD === iso ? ' on' : '') + '" data-a="calDay" data-v="' + iso + '" aria-label="' + esc(longDate(iso)) + (spent[iso] ? ', ' + cash(spent[iso]) : '') + '"' + (U.calD === iso ? ' aria-pressed="true"' : '') + '>' + d + '</button>';
      }
      const day = U.calD ? D.purchases.filter((p) => p.date === U.calD).sort(byNewest) : [],
        mTotal = Object.values(spent).reduce((a, b) => a + b, 0);
      return sheetWrap(
        monthName(m),
        '<div class="calhead"><span class="small">' + (mTotal ? cash(Math.round(mTotal * 100) / 100) + ' this month' : 'Nothing logged this month') + '</span><span><button class="circ glass sm" data-a="calStep" data-v="-1" aria-label="Earlier month">' + ICON.back + '</button><button class="circ glass sm fwd" data-a="calStep" data-v="1" aria-label="Later month">' + ICON.back + '</button></span></div>' +
          '<div class="calgrid"><div class="cdows" aria-hidden="true"><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span></div><div class="cdays">' + cells + '</div>' +
          (mTotal ? '<div class="tkey" aria-hidden="true">Less <i class="t1"></i><i class="t2"></i><i class="t3"></i> More</div>' : '') +
          '</div>' +
          (U.calD
            ? hdr(dayHeading(U.calD), day.length ? '<span class="hint">' + cash(sum(day)) + '</span>' : '') +
              (day.length ? '<div class="grp tiled">' + day.map((p) => purchaseRow(p, { push: true, meta: p.location || p.venue || p.category })).join('') + '</div>' : '<div class="grp"><div class="empty">Nothing logged on this day.</div></div>')
            : '<p class="foot">' + (mTotal ? 'Stronger days are the ones you spent more on, compared with the rest of this month. ' : '') + 'Tap a day to see what you bought.</p>') +
          // a picked day (today or earlier) can be logged on, with its date filled in; saving comes back here (Q08)
          (U.calD && U.calD <= t
            ? '<div class="grp tiled spaced"><button class="row more" data-a="newPurchase" data-v="' + U.calD + '"><span class="lbl">Log a purchase on ' + (U.calD === t ? 'today' : esc(shortDate(U.calD))) + '</span>' + ICON.chev + '</button></div>'
            : ''),
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
          hdr('Note animation') +
          '<div class="segc" id="noteSeg" role="group" aria-label="Note animation" style="--n:2;--i:' + (noteAnim() === 'slot' ? 1 : 0) + '"><span class="knob glass" aria-hidden="true"></span>' +
          [['fly', 'Fly'], ['slot', 'Slot']].map((o) => '<button data-a="setNoteAnim" data-v="' + o[0] + '" aria-pressed="' + (noteAnim() === o[0]) + '">' + o[1] + '</button>').join('') + '</div>' +
          '<p class="foot">How a note you tap on Quick Till goes into the cash box: Fly arcs it in, Slot slides it into a slot under the box. With Reduce motion on, the amount just changes.</p>' +
          hdr('Slow motion') +
          '<div class="grp"><label class="row toggle"><span class="lbl"><b>Slow motion</b></span><input type="checkbox" role="switch" data-a="slowMotion"' + (MOTION.speed() > 1 ? ' checked' : '') + '><span class="sw-ui" aria-hidden="true"></span></label></div>' +
          '<p class="foot">Plays every movement four times slower, for checking how things move.</p>' +
          hdr('Screen IDs') +
          '<div class="grp"><label class="row toggle"><span class="lbl"><b>Show screen IDs</b></span><input type="checkbox" role="switch" data-a="screenIds"' + (SCR.idsOn() ? ' checked' : '') + '><span class="sw-ui" aria-hidden="true"></span></label></div>' +
          '<p class="foot">Shows each screen’s ID in the top corner, such as SK-001, for pointing at a screen in a note. These settings stay on this device and aren’t saved in backups.</p>'
      );
    }
    case 'welcome':
      return sheetWrap(null, welcomeBody(), '', 'Welcome to Suki', { lock: true, tall: true, cls: 'welsheet' });
    case 'siri':
      return sheetWrap('Log by voice with Siri', siriBody(), '', 'Log by voice with Siri', { cls: 'siri' });
    // Rate history's news notes and the plain-words help they link to (Q23, history.js)
    case 'news':
      return newsSheet(sd);
    case 'cbrate':
      return cbSheet();
    case 'ahs':
      return sheetWrap('Add to Home Screen', ahsBody(sd.safari), '', 'Add Suki to your Home Screen', { lock: !!sd.safari, cls: 'ahs' });
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
              }).join('') + '</div><p class="foot">Add notes from any item in <button class="tlink" data-a="goSearch">Search</button>.</p>'
          : '<div class="grp"><div class="empty">No price notes yet. <button class="tlink" data-a="goSearch">Open Search</button>, pick an item and tap Add when you see a price.</div></div>'
      );
    }
  }
  return null;
}
/* ===== Which sheets are on screen (Q27) =====
   U.stack and U.sheet are the sheets open, bottom first. A yes or no question (ALERTS) is the kit's alert, over the
   sheet underneath it if there is one (D08). The sheets go to the parts kit's sheet on iPhone (HOST, below) and stay
   Suki's own centred sheet on iPad and Mac (ownSheets(), S01). Erase all data stays a sheet on kit 1.2.0 (S03). */
const ALERTS = { confirm: 1, putback: 1, restore: 1 };
const levelKey = (e) => e.sheet + ':' + (e.sd.id || e.sd.action || '') + ':' + (e.sd.k || '');
// the markup for a sheet that isn't the top one (the sheet under an alert)
function htmlAt(e) {
  const s = U.sheet,
    d = U.sd;
  U.sheet = e.sheet;
  U.sd = e.sd;
  try {
    return sheetHTML();
  } finally {
    U.sheet = s;
    U.sd = d;
  }
}
function renderSheet() {
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
  const lv = U.stack.map((e) => ({ sheet: e.sheet, sd: e.sd })).concat(html ? [{ sheet: U.sheet, sd: U.sd }] : []),
    alertTop = !!(html && ALERTS[U.sheet]),
    sheets = alertTop ? lv.slice(0, -1) : lv,
    sheetHtml = !sheets.length ? null : alertTop ? htmlAt(sheets[sheets.length - 1]) : html;
  HOST.alert(alertTop ? html : null, alertTop ? levelKey(lv[lv.length - 1]) : null);
  let fresh;
  if (MQ.reg.matches) {
    HOST.sheets([], null);
    fresh = ownSheets(sheets, sheetHtml);
  } else {
    ownSheets([], null);
    fresh = HOST.sheets(sheets, sheetHtml);
  }
  document.body.classList.toggle('sheet-open', sheets.length > 0);
  if (fresh && !alertTop) {
    const f = fresh.querySelector('input:not([type=date]),textarea');
    if (U.sheet === 'edit' && !U.sd.id && f) setTimeout(() => f.focus({ preventScroll: true }), 60);
    if (U.sheet === 'welcome') welcomeArrive();
  }
  SCR.sheet(); // Q25 the sheet's (or alert's) screen ID and part names
}

/* ===== iPad and Mac: Suki's own centred sheet (S01) =====
   It opens in the middle of the screen in #own, inside #layer. One opened from another goes back to the first when it
   closes. Returns the sheet when it has just appeared (not redrawn in place), for focusing its first field. */
function ownSheets(list, html) {
  const layer = $('own'),
    e = list[list.length - 1];
  if (!e) html = null;
  const key = e ? levelKey(e) : null,
    depth = html ? list.length : 0,
    was = layer.querySelector('.scrim'),
    // fewer sheets than before: the top one is closing, to the page or to the sheet underneath (Q11)
    closing = !!(was && shownSheet && depth < shownDepth),
    old = layer.querySelector('.sheet'),
    top = old ? old.scrollTop : 0,
    // a different sheet over one already open (Edit from a purchase, Log from a calendar day…): it arrives over the
    // old one, which waits behind it under the same dim until it's covered (Q24)
    over = !!(html && was && shownSheet && key !== shownSheet && !closing);
  if (closing) sheetAway(was, depth > 0);
  if (key !== shownSheet) sheetUnderGo();
  shownDepth = depth;
  if (!html) {
    layer.innerHTML = '';
    shownSheet = null;
    return null;
  }
  if (over) sheetUnderKeep(was);
  layer.innerHTML = html;
  const sh = layer.querySelector('.sheet');
  // the dim is already there, so the new one doesn't fade in from nothing; while the old sheet waits behind, the
  // old dim is the one showing, so it's never doubled
  if (over || (UNDER_SC && key === shownSheet)) {
    const sc = layer.querySelector('.scrim');
    sc.classList.add('still');
    if (UNDER_SC) sc.style.background = 'transparent';
  }
  // redrawing the same sheet keeps its place and doesn't rise again; going back to the sheet underneath finds it
  // simply there, where it was scrolled to, while the closing one slides off over it
  const same = key === shownSheet || closing;
  if (same) {
    sh.classList.add('still');
    layer.querySelector('.scrim').classList.add('still');
    sh.scrollTop = key === shownSheet ? top : backTop;
  }
  shownSheet = key;
  return same ? null : sh;
}

/* ===== A sheet over a sheet on iPad and Mac (Q24) =====
   The old sheet and its dim move to #leaving (which nothing can tap), beneath the new one (.under, z-index 39), and
   stay exactly where they were until the new sheet has popped over them (or faded, with Reduce Motion); then they go.
   Any other sheet change before that ends the wait at once. Motion off: nothing waits. On iPhone the kit's sheets
   stack by themselves (HOST). */
let UNDER_SC = null;
function sheetUnderKeep(sc) {
  const out = $('leaving'),
    sp = MOTION.speed();
  if (!out || sp === 0) return;
  const sh = sc.querySelector('.sheet'),
    top = sh ? sh.scrollTop : 0;
  sc.classList.add('still', 'under');
  if (sh) sh.classList.add('still');
  sc.removeAttribute('data-a');
  sc.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'));
  out.appendChild(sc);
  if (sh) sh.scrollTop = top;
  UNDER_SC = sc;
  const ms = (MOTION.reduced() ? MOTION.reducedMs() : MOTION.ms('--dur-appear', 250)) * sp;
  clearTimeout(sheetUnderKeep.t);
  sheetUnderKeep.t = setTimeout(sheetUnderGo, ms + 40);
}
function sheetUnderGo() {
  clearTimeout(sheetUnderKeep.t);
  const sc = UNDER_SC;
  UNDER_SC = null;
  if (!sc) return;
  sc.remove();
  const top = $('own').querySelector('.scrim');
  if (top) top.style.background = '';
}

/* ===== A centred sheet leaving, on iPad and Mac (Q11, S01) =====
   The closing sheet moves to #leaving (which nothing can tap) and shrinks to .94 and fades over --dur-close, from
   wherever it was. Going back to a sheet underneath, the dim stays and only the top sheet goes. Reduce Motion: the
   kit's --dur-reduced fade. Motion off: it simply goes. Every close path ends here, because they all redraw: ✕,
   Cancel, the dim, Escape, and closing after a save or a delete. A second close mid-way just starts another one. */
function sheetAway(sc, toPrev) {
  const sh = sc.querySelector('.sheet'),
    sp = MOTION.speed(),
    out = $('leaving');
  if (!sh || !out || sp === 0 || !sh.animate) return;
  const cs = getComputedStyle(sh),
    tr = cs.transform === 'none' ? 'translateY(0px)' : cs.transform,
    op = cs.opacity,
    top = sh.scrollTop,
    dimFrom = getComputedStyle(sc).backgroundColor,
    red = MOTION.reduced(),
    ms = (red ? MOTION.reducedMs() : MOTION.ms('--dur-close', 170)) * sp;
  // hold it exactly where it is (half-arrived), then let it go from there
  sc.classList.add('still');
  sh.classList.add('still');
  sh.classList.remove('drag', 'back');
  sh.style.transform = tr;
  sh.style.opacity = op;
  sc.removeAttribute('data-a');
  sc.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'));
  if (toPrev) sc.style.background = 'transparent';
  out.appendChild(sc);
  sh.scrollTop = top;
  let a;
  if (red) a = sc.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ms, easing: 'ease-out', fill: 'forwards' });
  else {
    a = sh.animate([{ transform: tr, opacity: op }, { transform: 'scale(.94)', opacity: 0 }], { duration: ms, easing: 'ease-in', fill: 'forwards' });
    if (!toPrev) sc.animate([{ backgroundColor: dimFrom }, { backgroundColor: 'rgba(0,0,0,0)' }], { duration: ms, easing: 'ease-out', fill: 'forwards' });
  }
  const done = () => sc.remove();
  a.onfinish = done;
  a.oncancel = done;
  setTimeout(done, ms + 400);
}

/* ===== Q27 The sheet host: Suki's sheets and alerts on the parts kit =====
   Suki still decides which sheets are open (U.stack, U.sheet, renderSheet()) and draws their contents; the host shows
   them with the kit's parts, inside #layer (the kit's root):
   - On iPhone, each sheet in the kit's sheet (Parts.sheet, part 41): it rises from the bottom on the sheet spring,
     leaves in 350 ms speeding up, is dragged from its head or from its content when that's at the top, and closes
     on a flick past 700 pt/s (D14: no shrinking), with 46 corners (D17) and strong glass (D15). Suki's own head
     (.shead: title, tools, ✕) takes the kit's head's place, and its content goes in the kit's body, which scrolls.
     A sheet opened from a sheet rises over it and the first waits underneath, still open; closing the top one shows
     it again, drawn afresh. Closing a sheet the kit's way (a flick, the dim, Escape) is closeSheet().
   - A yes or no question as the kit's alert (Parts.confirm, part 48, D08), on every device: the sheet's title, its
     .note as the message, its red .cta as the action and Cancel. The action runs Suki's own button (fire()).
   - A locked sheet (the welcome card, Add to Home Screen in Safari) can only be left with its own buttons: no
     grabber, and the dim, a drag and Escape do nothing.
   The kit measures a sheet as it opens; when Suki draws it again with content of another height, it's opened again
   in place, with no movement (refill). */
const HOST = (() => {
  let st = []; // the kit's sheets on screen, bottom first: { key, level, ctl, id }
  let al = null; // the alert on screen: { key, id, k, done }
  let seq = 0;
  // run one of Suki's actions as if its button had been tapped: a hidden button with the same data- attributes
  function fire(src) {
    const b = document.createElement('button');
    [...src.attributes].forEach((a) => /^data-/.test(a.name) && b.setAttribute(a.name, a.value));
    b.hidden = true;
    document.body.appendChild(b);
    b.click();
    b.remove();
  }
  const text = (el) => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');
  const titleOf = (sh) => text(sh.querySelector('.shead h2, h2'));
  function parse(h) {
    const t = document.createElement('div');
    t.innerHTML = h || '';
    return t.querySelector('.sheet');
  }
  // Suki's head (its grabber aside: the kit's is used) where the kit's title and ✕ were
  function head(ctl, sh) {
    const el = ctl.el,
      hd = sh.querySelector(':scope > .shead'),
      kh = el.querySelector(':scope > .pk-sheet-head');
    if (!kh) return;
    kh.querySelectorAll(':scope > :not(.pk-grabber)').forEach((x) => x.remove());
    if (hd) kh.appendChild(hd);
    kh.classList.toggle('sk-own', !!hd);
    el.classList.toggle('sk-nohead', !hd);
  }
  // the sheet's content, without its head; a tall sheet (the welcome card) fills the screen from the start
  function inner(sh) {
    const c = sh.cloneNode(true),
      hd = c.querySelector(':scope > .shead');
    if (hd) hd.remove();
    return sh.classList.contains('tall') ? '<div class="sk-tall">' + c.innerHTML + '</div>' : c.innerHTML;
  }
  // Suki's sheet (.sheet) into the kit's: its classes and labels on the kit's element, its head in the kit's head
  function dress(ctl, sh) {
    const el = ctl.el;
    sh.classList.forEach((c) => c !== 'glass' && el.classList.add(c));
    el.classList.add('sk-sheet');
    ['aria-label', 'aria-modal'].forEach((a) => sh.hasAttribute(a) && el.setAttribute(a, sh.getAttribute(a)));
    head(ctl, sh);
  }
  // the kit's sheet's height for what it holds now
  function natural(ctl) {
    const kh = ctl.el.querySelector(':scope > .pk-sheet-head');
    return Math.min(window.innerHeight - Parts.N.topInset, (kh ? kh.offsetHeight : 0) + ctl.body.scrollHeight);
  }
  // no movement: whatever the kit started (the rise, the dim fading in) jumps to its end
  function still(ctl) {
    [ctl.el, ...document.querySelectorAll('#layer .pk-dim')].forEach((x) =>
      x.getAnimations().forEach((a) => {
        try {
          a.finish();
        } catch (e) {}
      })
    );
  }
  function open(sh, key, level, now) {
    const id = ++seq;
    const ctl = Parts.sheet({
      key: key.split(':')[0],
      name: sh.getAttribute('aria-label') || titleOf(sh) || 'Sheet',
      html: inner(sh),
      onClose: (why) => gone(id, why),
    });
    dress(ctl, sh);
    if (now) still(ctl);
    else rise(ctl.el);
    return { key, level, ctl, id };
  }
  // Kit 1.2.0 measures a sheet that fits its content by styling it in place first, so its rise from below the screen
  // starts from where it ends and it simply appears (sheets with stops rise). Until a kit version fixes it, the host
  // starts it again from below the screen, on the kit's own transition; this goes when the kit's fix is pinned.
  function rise(el) {
    if (!Parts.motion.on()) return;
    const y = el.style.getPropertyValue('--pk-y');
    el.style.transition = 'none';
    el.style.setProperty('--pk-y', el.offsetHeight + 8 + 'px');
    void el.offsetWidth;
    el.style.transition = '';
    el.style.setProperty('--pk-y', y);
  }
  // take a sheet away at once (no movement), without telling Suki
  function drop(ctl) {
    ctl.close('app');
    ctl.el.remove();
    document.querySelectorAll('#layer .pk-dim:not(.pk-on)').forEach((d) => d.remove());
  }
  // a sheet leaving, or covered by the one opened over it, isn't "the sheet" any more: it loses .sheet (only
  // .sheet .note styles by it) and can't be reached, so code and tests that look for .sheet find the top one
  function cover(el, on) {
    el.classList.toggle('sheet', !on);
    el.classList.toggle('sk-covered', on);
    el.inert = on;
  }
  const shut = (e) => {
    cover(e.ctl.el, true);
    Parts.motion.speed() ? e.ctl.close('app') : drop(e.ctl);
  };
  // the kit closed a sheet itself (a flick, the dim, Escape): Suki closes it too
  function gone(id, why) {
    const i = st.findIndex((e) => e.id === id);
    if (i < 0 || why === 'app') return;
    st.splice(i).forEach((e) => cover(e.ctl.el, true));
    if (why === 'drag' && typeof tipDone === 'function') tipDone('sheet');
    if (U.sheet && !ALERTS[U.sheet]) closeSheet();
  }
  // the same sheet drawn again: its content changes, its scroll stays; a new height opens it again in place
  function refill(i, h) {
    const e = st[i],
      sh = parse(h);
    if (!sh) return;
    const c = e.ctl,
      top = c.body.scrollTop,
      oldH = c.el.offsetHeight;
    head(c, sh.cloneNode(true)); // the head moves into the kit's sheet; sh stays whole in case it opens again
    c.body.innerHTML = inner(sh);
    c.body.scrollTop = top;
    // only the top sheet is opened again (it's the last thing in the kit's layer, so nothing is covered)
    if (i !== st.length - 1 || al || Math.abs(natural(c) - oldH) <= 2) return;
    drop(c);
    st[i] = open(sh, e.key, e.level, true);
    st[i].ctl.body.scrollTop = top;
  }
  // list: the sheets that should be on screen, bottom first; h: the top one's markup. Returns the top sheet's element
  // when it has just opened
  function sheets(list, h) {
    let keep = 0;
    while (keep < st.length && st[keep].level < list.length && st[keep].key === levelKey(list[st[keep].level])) keep++;
    st
      .splice(keep)
      .reverse()
      .forEach(shut);
    let fresh = null;
    if (list.length) {
      const L = list.length - 1,
        t = st[st.length - 1],
        sh = t && t.level === L ? null : parse(h);
      if (t && t.level === L) refill(st.length - 1, h);
      else if (sh) {
        st.push(open(sh, levelKey(list[L]), L, false));
        fresh = st[st.length - 1].ctl.el;
      }
    }
    st.forEach((e, i) => cover(e.ctl.el, i < st.length - 1));
    return fresh;
  }
  // an alert Suki no longer wants: its Cancel, quietly
  function cancelAlert() {
    if (al) al.done = true;
    const el = [...document.querySelectorAll('#layer .pk-alert:not(.pk-leaving)')].pop();
    if (!el) return;
    const b = el.querySelector('[data-a=no]');
    if (b) b.click();
    if (!Parts.motion.speed()) {
      el.remove();
      document.querySelectorAll('#layer .pk-dim:not(.pk-on)').forEach((d) => d.remove());
    }
  }
  // h: the alert's markup (a sheetWrap with confirmBody), or null for none; key: which one
  function alert(h, key) {
    if (!h) {
      if (al && !al.done) cancelAlert();
      al = null;
      return;
    }
    if (al && al.key === key && !al.done) return;
    if (al && !al.done) cancelAlert();
    const sh = parse(h),
      id = ++seq,
      act = sh.querySelector('.cta.red'),
      no = sh.querySelector('button.ghost[data-a=close]');
    al = { key, id, k: U.sheet, done: false };
    Parts.confirm({
      title: titleOf(sh),
      message: text(sh.querySelector('.note')),
      action: text(act),
      cancel: no ? text(no) : 'Cancel',
      red: true,
      name: sh.getAttribute('aria-label') || titleOf(sh),
    }).then((yes) => {
      if (!al || al.id !== id || al.done) return;
      al.done = true;
      if (yes && act) fire(act);
      else if (U.sheet === al.k) closeSheet();
    });
  }
  // a locked sheet on top keeps its dim, drag and Escape from closing it
  const lockedTop = () => {
    const t = st[st.length - 1];
    return !!(t && !al && t.ctl.el.classList.contains('locked'));
  };
  document.addEventListener(
    'pointerdown',
    (e) => {
      if (e.target.closest && e.target.closest('.pk-sheet.locked') && !e.target.closest('button, a, input, textarea, select, label')) e.stopPropagation();
    },
    true
  );
  document.addEventListener(
    'click',
    (e) => {
      const d = e.target.classList && e.target.classList.contains('pk-dim') ? e.target : null;
      if (d && d.nextElementSibling && d.nextElementSibling.classList.contains('locked')) {
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  // Escape: the kit closes the newest overlay (so Suki's own Escape leaves it alone: kitEscape)
  const ESC = new WeakSet();
  window.addEventListener(
    'keydown',
    (e) => {
      if (e.key !== 'Escape' || !Parts.open) return;
      if (lockedTop()) {
        e.stopPropagation();
        e.preventDefault();
        return;
      }
      ESC.add(e);
    },
    true
  );
  return {
    sheets,
    alert,
    fire,
    // the kit's sheet on top now (its body scrolls), for tests and for keeping its place
    top: () => (st.length ? st[st.length - 1].ctl : null),
    count: () => st.length,
    alertOpen: () => !!(al && !al.done),
    kitEscape: (e) => ESC.has(e),
  };
})();

/* ===== Rows arriving and leaving (Q11) =====
   Lists are drawn with innerHTML, so a change is measured before the redraw and played after it (FLIP), right where
   the change happens (saving, deleting, Undo):
     const before = rowsBefore();  …change D and redraw…  rowsAfter(before);
   A purchase that's new to the list settles in (MOTION.land, rows 45 ms apart); rows, "Show all" rows, headers and
   the group under each glide from where they were on the gentle spring; a row that went (deleted, or pushed out of
   Recent) fades and shrinks where it was. Rows in a sheet that is itself closing go with the sheet. Nothing here blocks
   a tap: the copies that fade sit in #leaving. Motion off: nothing is measured. */
const ROW_SEL = '.row[data-a=openPurchase][data-k], .row.more[data-a]';
function rowsBefore() {
  if (!MOTION.speed()) return null;
  const m = { rows: new Map(), heads: new Map(), ids: new Set(D.purchases.map((p) => p.id)), sheet: U.sheet ? levelKey({ sheet: U.sheet, sd: U.sd }) : null };
  ['app', 'layer'].forEach((where) => {
    const root = $(where);
    if (!root) return;
    const seen = {};
    root.querySelectorAll(ROW_SEL).forEach((r) => {
      const host = r.closest('.sw') || r,
        id = r.dataset.a === 'openPurchase' ? r.dataset.k : null,
        k = where[0] + (id ? 'p' + id : 'm' + r.dataset.a + (r.dataset.v || ''));
      if (seen[k]) return;
      seen[k] = 1;
      m.rows.set(k, { host, id, rect: host.getBoundingClientRect() });
    });
    root.querySelectorAll('.hdr').forEach((h) => {
      const k = where[0] + (h.querySelector('h2') || h).textContent;
      if (!m.heads.has(k)) m.heads.set(k, h.getBoundingClientRect().top);
    });
  });
  return m;
}
function rowsAfter(b) {
  if (!b) return;
  const now = rowsBefore(),
    added = new Set(D.purchases.filter((p) => !b.ids.has(p.id)).map((p) => p.id)),
    sameSheet = (U.sheet ? levelKey({ sheet: U.sheet, sd: U.sd }) : null) === b.sheet,
    seen = (r) => r.bottom > 0 && r.top < innerHeight,
    shift = new Map();
  if (!now) return;
  // headers, and the group right under each, glide to where they are now
  ['app', 'layer'].forEach((where) =>
    $(where).querySelectorAll('.hdr').forEach((h) => {
      const k = where[0] + (h.querySelector('h2') || h).textContent;
      if (!b.heads.has(k) || !now.heads.has(k)) return;
      const dy = b.heads.get(k) - now.heads.get(k);
      if (Math.abs(dy) < 1) return;
      const g = h.nextElementSibling && h.nextElementSibling.classList.contains('grp') ? h.nextElementSibling : null;
      [h, g].forEach((e) => e && MOTION.animate(e, [{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }], { spring: 'gentle' }));
      if (g) shift.set(g, dy);
    })
  );
  let n = 0;
  now.rows.forEach((v, k) => {
    const w = b.rows.get(k);
    if (!w) {
      // only what's new settles in: a sheet coming back into view keeps its rows still
      if (v.id && added.has(v.id) && seen(v.rect)) MOTION.land(v.host, n++);
      return;
    }
    const dy = w.rect.top - v.rect.top - (shift.get(v.host.closest('.grp')) || 0);
    if (Math.abs(dy) > 1) MOTION.animate(v.host, [{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }], { spring: 'gentle' });
  });
  b.rows.forEach((w, k) => {
    if (now.rows.has(k) || !w.id || !seen(w.rect) || (k[0] === 'l' && !sameSheet)) return;
    rowGoes(w, k[0] === 'l');
  });
}
// a copy of the row that went fades and shrinks where the row was
function rowGoes(w, inSheet) {
  const out = $('leaving'),
    c = w.host.cloneNode(true),
    g = w.host.parentElement,
    r = w.rect;
  if (!out) return;
  c.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'));
  c.classList.add('rowghost');
  Object.assign(c.style, {
    left: r.left + 'px',
    top: r.top + 'px',
    width: r.width + 'px',
    height: r.height + 'px',
    zIndex: inSheet ? 42 : 14,
    borderRadius: (g && g.firstElementChild === w.host ? '20px 20px ' : '0 0 ') + (g && g.lastElementChild === w.host ? '20px 20px' : '0 0'),
  });
  out.appendChild(c);
  const a = MOTION.leave(c);
  if (!a) return c.remove();
  a.onfinish = a.oncancel = () => c.remove();
  setTimeout(() => c.remove(), 220 * MOTION.speed() + 400);
}

/* ===== Toasts (Q27: the parts kit's, part 49, D16) =====
   undo: a function that puts back what was just removed; the toast then shows an Undo button. Every toast drops in
   from the top over 500 ms, stays 3 s (the kit's timing.toast, Undo too) and goes over 350 ms; one at a time. A longer
   message wraps onto a second line (.sk-long).
   sticky: a warning that stays until it's tapped (OK), Suki's own (S04, Q05); other toasts drop in below it. */
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
    SCR.mark(w, 'overlay:toast');
    document.body.appendChild(w);
    document.body.classList.add('has-sticky');
    return;
  }
  const c = Parts.toast(t, undo ? { undo } : {}),
    el = c.el;
  // the one it replaced is on its way out: it's no longer "the toast"
  document.querySelectorAll('#layer .pk-toast.pk-leaving.toast').forEach((x) => x.classList.remove('toast', 'undo'));
  el.classList.add('toast');
  if (undo) el.classList.add('undo');
  const span = el.querySelector(':scope > span');
  if (span && span.scrollWidth > span.clientWidth + 1) el.classList.add('sk-long');
  SCR.mark(el, 'overlay:toast');
  return c;
}
