/* Suki · events.js
   Taps and typing: every button action, the forms, swipe to delete (from Vocal Sessions), blocking zoom,
   and keyboard shortcuts.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Swipe to delete ===== */
let swT = null,
  swOpen = null,
  swJustMoved = 0;
function closeSwipes(except) {
  document.querySelectorAll('.sw.open').forEach((s) => {
    if (s !== except) {
      s.classList.remove('open');
      s.querySelector('.fg').style.transform = '';
    }
  });
  if (!except) swOpen = null;
}
document.addEventListener(
  'touchstart',
  (e) => {
    const s = e.target.closest('.sw');
    if (swOpen && swOpen !== s) closeSwipes();
    if (!s || e.touches.length !== 1) return (swT = null);
    const t = e.touches[0];
    swT = { s, x: t.clientX, y: t.clientY, dx: 0, base: s.classList.contains('open') ? -88 : 0, lock: null };
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!swT) return;
    const t = e.touches[0],
      dx = t.clientX - swT.x,
      dy = t.clientY - swT.y;
    if (swT.lock === null) {
      if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
      swT.lock = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
    }
    if (swT.lock !== 'x') return;
    swT.dx = dx;
    swT.s.classList.add('dragging');
    const x = Math.max(-120, Math.min(0, swT.base + dx));
    swT.s.querySelector('.fg').style.transform = 'translateX(' + x + 'px)';
  },
  { passive: true }
);
function swEnd() {
  if (!swT) return;
  const s = swT.s;
  s.classList.remove('dragging');
  if (swT.lock === 'x') {
    swJustMoved = Date.now();
    const open = swT.base + swT.dx < -44;
    s.classList.toggle('open', open);
    s.querySelector('.fg').style.transform = open ? 'translateX(-88px)' : '';
    swOpen = open ? s : null;
    if (open) tipDone('swipe');
  }
  swT = null;
}
document.addEventListener('touchend', swEnd);
document.addEventListener('touchcancel', swEnd);

/* ===== No zooming (iOS ignores user-scalable=no, so pinches are blocked here) ===== */
['gesturestart', 'gesturechange', 'gestureend'].forEach((t) => document.addEventListener(t, (e) => e.preventDefault(), { passive: false }));
document.addEventListener(
  'touchmove',
  (e) => {
    if (e.touches.length > 1) e.preventDefault();
  },
  { passive: false }
);
// double-tap zoom is turned off by touch-action:manipulation in the CSS, which keeps quick taps working

/* ===== Small screen updates (so typing is never interrupted by a full redraw) ===== */
// Quick Till changes its words in place and redraws only the cash pieces that changed (Q13); the figure never animates
function updateTill() {
  const o = $('tillOut'),
    b = $('tillLog'),
    x = $('cashClear');
  if (b) b.disabled = !(tillState().bill > 0);
  if (x) x.hidden = !U.till.cash;
  if (!o) return;
  if (!$('cashRow')) return void (o.innerHTML = tillOut());
  const v = tillView();
  $('tillEb').textContent = v.eb;
  $('tillEb').className = 'eyebrow' + (v.red ? ' red' : '');
  $('tillFig').textContent = v.fig;
  $('tillFig').className = v.cls;
  $('tillSmall').textContent = v.small;
  renderCash(v.cash);
}
// the ✕ in the cash box doesn't take the cursor, so the keyboard stays up if it was
document.addEventListener('pointerdown', (e) => {
  if (e.target.closest('#cashClear')) e.preventDefault();
});
function setTillCash(v) {
  U.till.cash = v;
  const el = $('till-cash');
  if (el) el.value = v;
  updateTill();
}
function updateSearch() {
  $('results').innerHTML = searchResults();
  const c = document.querySelector('#app .searchbox .clr');
  if (c) c.hidden = !U.q;
}
function updateSpending() {
  const list = spendingList();
  U.shown = SHOW_STEP;
  $('spendSum').innerHTML = spendSummary(list);
  $('spendBrk').innerHTML = spendBreakdown();
  $('spendList').innerHTML = spendRows(list);
  const c = document.querySelector('#app .searchbox .clr');
  if (c) c.hidden = !U.filter;
}
const fmtAmt = (n) => (Math.round(n * 100) / 100).toString();

/* ===== Spending over time (Q03) ===== */
// the segmented control's knob squishes as it lands (from Vocal Sessions)
function squish(k) {
  if (k) MOTION.animate(k, [{ scale: '1 1' }, { scale: '1.22 .86' }, { scale: '.96 1.04' }, { scale: '1 1' }], { ms: 450, easing: 'ease-out' });
}
// redraw the numbers, chart, breakdown and list for a new period; step says which way time moved
function spendingChanged(step) {
  const keep = $('spendSum');
  if (!keep) return rerender();
  rerender();
  const st = $('spendSum');
  if (step && st) MOTION.animate(st.querySelector('.tot'), [{ transform: 'translateX(' + (step > 0 ? 24 : -24) + 'px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { fade: true });
  // the bars arrive in a small staggered ripple, Suki's one signature movement on this page
  document.querySelectorAll('#chart .bfill').forEach((b, i) =>
    MOTION.animate(b, [{ transform: 'scaleY(.55)', opacity: 0.4 }, { transform: 'none', opacity: 1 }], { spring: 'ripple', delay: MOTION.stagger(i, 'bar') / Math.max(1, document.querySelectorAll('#chart .bfill').length / 10) })
  );
}
// tap or slide across the bars to read one day (scrubbing follows the finger instantly, no easing)
let chartDrag = null;
function chartPick(e) {
  const ch = $('chart');
  if (!ch) return;
  const cols = ch.querySelectorAll('.col');
  if (!cols.length) return;
  const r = ch.querySelector('.cols').getBoundingClientRect(),
    i = Math.max(0, Math.min(cols.length - 1, Math.floor(((e.clientX - r.left) / r.width) * cols.length)));
  if (U.bar === i && e.type === 'pointerdown') return (chartDrag.clear = true);
  if (U.bar === i) return;
  U.bar = i;
  barChanged();
}
// the headline and the list follow the picked bar together (Q10); the list fades back in so the change is seen
function barChanged() {
  const list = spendingList(),
    s = $('spendSum'),
    l = $('spendList');
  if (s) s.innerHTML = spendSummary(list);
  if (!l) return;
  l.innerHTML = spendRows(list);
  MOTION.animate(l, [{ opacity: 0.35 }, { opacity: 1 }], { ms: 180, easing: 'ease-out' });
}
// tapping anywhere else clears the picked bar, except the headline, a sheet, a purchase in the narrowed list
// (or Show more under it) and the purchase's details beside the list on iPad and Mac (Q10)
const KEEPS_BAR = '#spendSum, #layer, .sheet, #spendList .tiled, #spendList .morerows, .split .pane';
// the headline goes back at once; the list widens only once the tap has landed, so whatever was tapped
// (the filter's ✕, Export as CSV under the list) doesn't jump away from under the finger
let widenT = null;
function widenListSoon() {
  const s = $('spendSum');
  if (s) s.innerHTML = spendSummary(spendingList());
  const run = () => {
    clearTimeout(widenT);
    document.removeEventListener('click', later);
    const l = $('spendList');
    if (U.bar != null || !l || !$('pickLine')) return;
    l.innerHTML = spendRows(spendingList());
    MOTION.animate(l, [{ opacity: 0.35 }, { opacity: 1 }], { ms: 180, easing: 'ease-out' });
  };
  const later = () => setTimeout(run, 0);
  clearTimeout(widenT);
  document.addEventListener('click', later, { once: true });
  // a scroll or a long press sends no click
  widenT = setTimeout(run, 700);
}
document.addEventListener('pointerdown', (e) => {
  if (!e.target.closest('#chart')) {
    if (U.bar != null && U.tab === 'spending' && !e.target.closest(KEEPS_BAR)) {
      U.bar = null;
      widenListSoon();
    }
    return;
  }
  chartDrag = { id: e.pointerId, x: e.clientX, y: e.clientY, clear: false };
  chartPick(e);
});
document.addEventListener('pointermove', (e) => {
  if (!chartDrag || e.pointerId !== chartDrag.id) return;
  if (Math.abs(e.clientX - chartDrag.x) > 6) chartDrag.clear = false;
  chartPick(e);
});
const chartUp = (e) => {
  if (!chartDrag || e.pointerId !== chartDrag.id) return;
  if (chartDrag.clear) {
    U.bar = null;
    barChanged();
  }
  chartDrag = null;
};
document.addEventListener('pointerup', chartUp);
document.addEventListener('pointercancel', (e) => {
  if (chartDrag && e.pointerId === chartDrag.id) chartDrag = null;
});

/* ===== Saving forms ===== */
function formError(form, msg, f) {
  const e = $(form + '-err');
  if (e) e.textContent = msg;
  const el = f && $(form + '-' + f);
  if (el) {
    el.focus();
    el.setAttribute('aria-invalid', 'true');
  }
}
function readPurchase(form) {
  const v = F[form],
    item = String(v.item || '').trim(),
    price = amount(v.price);
  if (!item) return formError(form, 'Add what you bought.', 'item');
  if (price === null && String(v.price || '').trim()) return formError(form, 'Check the amount. Use numbers and one dot, like 1,250.50.', 'price');
  if (!(cents(price) > 0)) return formError(form, 'Add an amount above ₱0.', 'price');
  if (price > 10000000) return formError(form, 'That amount looks too big. Check the number.', 'price');
  return {
    item: item.slice(0, 200),
    price: Math.round(price * 100) / 100,
    category: CATS.includes(v.category) ? v.category : 'Food & drink',
    date: isoDate(v.date) || localISO(),
    location: String(v.location || '').trim(),
    venue: VENUES.includes(v.venue) ? v.venue : '',
    payment: PAYMENTS.includes(v.payment) ? v.payment : 'Cash',
    notes: String(v.notes || '').trim(),
  };
}
async function submitForm(form, el) {
  if (form === 'home' || form === 'edit') {
    const p = readPurchase(form);
    if (!p) return;
    if (form === 'edit' && U.sd.id) {
      const old = D.purchases.find((x) => x.id === U.sd.id);
      if (!old) return closeSheet();
      Object.assign(old, p, { edited: new Date().toISOString() });
      old.gbpAtPurchase = old.rateAtPurchase ? Math.round((old.price / old.rateAtPurchase) * 100) / 100 : null;
      closeSheet();
      toast('Changes saved');
      await save('purchases');
      return;
    }
    const r = D.rate ? D.rate.value : null,
      before = rowsBefore(),
      added = Object.assign({ id: newId() }, p, { gbpAtPurchase: r ? Math.round((p.price / r) * 100) / 100 : null, rateAtPurchase: r });
    D.purchases.unshift(added);
    if (form === 'home') {
      F.home = { category: p.category, payment: p.payment };
      saveDraft({});
      savedTick();
      rerender();
      savedPop();
    } else {
      if (U.sd.fromTill) U.till = { bill: '', cash: '' };
      closeSheet();
    }
    // the new row settles into whatever list it lands in (Q11)
    rowsAfter(before);
    toast('Purchase saved', () => undoSave(added.id));
    await save('purchases');
    return;
  }
  if (form === 'obs') {
    const id = el.dataset.k,
      v = F.obs,
      price = amount(v.price);
    if (!(cents(price) > 0)) return formError('obs', price === null && String(v.price || '').trim() ? 'Check the price. Use numbers and one dot.' : 'Add the price you saw.', 'price');
    const it = itemById(id);
    D.observations.push({
      id: newId(),
      itemId: id,
      itemName: it ? it.name : id,
      price: Math.round(price * 100) / 100,
      date: isoDate(v.date) || localISO(),
      location: String(v.location || '').trim(),
      venue: VENUES.includes(v.venue) ? v.venue : '',
      note: String(v.note || '').trim(),
    });
    F.obs = {};
    U.obsFor = null;
    rerender();
    toast('Price note saved');
    await save('observations');
  }
}
// Undo on "Purchase saved": it goes again, shrinking out of its list (Q11)
async function undoSave(id) {
  if (!D.purchases.some((p) => p.id === id)) return;
  const before = rowsBefore();
  D.purchases = D.purchases.filter((p) => p.id !== id);
  if (U.sel === id) U.sel = null;
  rerender();
  rowsAfter(before);
  toast('Purchase removed');
  await save('purchases');
}
// Home's Save button shows "✓ Saved" for about 1.4 s (longer in Slow motion), then goes back in place
let savedT = null;
function savedTick() {
  savedUntil = Date.now() + 1400 * Math.max(1, MOTION.speed());
  clearTimeout(savedT);
  savedT = setTimeout(() => {
    savedUntil = 0;
    const b = $('homeSave');
    if (b && b.classList.contains('saved')) {
      b.classList.remove('saved');
      b.textContent = 'Save purchase';
    }
  }, savedUntil - Date.now());
}
function savedPop() {
  const t = document.querySelector('#homeSave.saved .tk');
  if (t) MOTION.animate(t, [{ transform: 'scale(.4)', opacity: 0 }, { transform: 'none', opacity: 1 }], { spring: 'ripple', fade: true });
}
document.addEventListener('submit', (e) => {
  const f = e.target.closest('form[data-form]');
  if (!f) return;
  e.preventDefault();
  submitForm(f.dataset.form, f);
});

/* ===== Typing ===== */
function onField(e) {
  const t = e.target;
  if (t.dataset.form && t.dataset.f) {
    F[t.dataset.form][t.dataset.f] = t.value;
    // typing in (or clearing) Location is his: Suki stops filling it in for this purchase (Q16)
    if (t.dataset.f === 'location' && (t.dataset.form === 'home' || t.dataset.form === 'edit')) F[t.dataset.form].locFrom = 'typed';
    t.removeAttribute('aria-invalid');
    const err = $(t.dataset.form + '-err');
    if (err) err.textContent = '';
    if (t.dataset.form === 'home') saveDraft(F.home);
  } else if (t.id === 'q') {
    U.q = t.value;
    updateSearch();
  } else if (t.id === 'filter') {
    U.filter = t.value;
    updateSpending();
  } else if (t.dataset.till) {
    U.till[t.dataset.till] = t.value;
    updateTill();
    if (t.dataset.till === 'cash' && t.value) tipDone('till');
  } else if (t.dataset.conv) convInput(t.dataset.conv, t.value);
}
document.addEventListener('input', onField);
document.addEventListener('change', (e) => {
  if (e.target.matches('select,input[type=date]')) onField(e);
  if (e.target.dataset.a === 'slowMotion') MOTION.setSpeed(e.target.checked ? 4 : 1);
  if (e.target.dataset.a === 'tipsToggle') setTips(e.target.checked);
});
$('importIn').addEventListener('change', (e) => {
  const f = e.target.files && e.target.files[0];
  e.target.value = '';
  if (f) readBackupFile(f);
});

/* ===== Buttons ===== */
const ACT = {
  tab: (el) => {
    if (U.tab === el.dataset.v && el.closest('.tabbar,.toptabs,.side-nav')) return window.scrollTo({ top: 0, behavior: MOTION.on() ? 'smooth' : 'auto' });
    go(el.dataset.v);
  },
  close: () => !document.querySelector('#layer .sheet.locked') && closeSheet(),
  // onboarding (Q07)
  welcomeGo: () => {
    OB.welcome = true;
    obSave();
    closeSheet();
  },
  ahsGot: () => closeSheet(),
  ahsLater: () => {
    closeSheet();
    toast('It’ll show again next time you open Suki in Safari');
  },
  tipX: () => TIPCUR && tipDone(TIPCUR),
  showWelcome: () => openSheet('welcome'),
  openAhs: () => openSheet('ahs', {}),
  openHelp: () => go('help'),
  more: () => {
    U.more = !U.more;
    rerender();
  },
  openPurchase: (el) => {
    if (split() && U.tab === 'spending' && !U.sheet) {
      U.sel = el.dataset.k;
      return rerender();
    }
    openSheet('purchase', { id: el.dataset.k }, el.dataset.v === 'push');
  },
  editPurchase: (el) => {
    const p = D.purchases.find((x) => x.id === el.dataset.k);
    if (!p) return;
    F.edit = { item: p.item, price: fmtAmt(p.price), category: p.category, date: p.date, location: p.location, venue: p.venue, payment: p.payment, notes: p.notes };
    openSheet('edit', { id: p.id }, U.sheet === 'purchase');
  },
  delPurchase: (el) => {
    closeSwipes();
    const p = D.purchases.find((x) => x.id === el.dataset.k);
    if (!p) return;
    openSheet(
      'confirm',
      { title: 'Delete this purchase?', text: '“' + p.item + '” (' + cash(p.price) + ') will be removed from this device. You can only get it back from a backup.', btn: 'Delete purchase', action: 'delPurchaseYes', k: p.id },
      !!U.sheet
    );
  },
  delPurchaseYes: async (el) => {
    const id = el.dataset.k,
      at = D.purchases.findIndex((p) => p.id === id),
      gone = D.purchases[at],
      before = rowsBefore();
    D.purchases = D.purchases.filter((p) => p.id !== id);
    if (U.sel === id) U.sel = null;
    U.stack = [];
    U.sheet = null;
    U.sd = {};
    rerender();
    // the row shrinks away and the rows below close the gap; Undo plays the arrival again (Q11)
    rowsAfter(before);
    toast('Purchase deleted', gone && (async () => {
      if (D.purchases.some((p) => p.id === gone.id)) return;
      const b = rowsBefore();
      D.purchases.splice(Math.min(at, D.purchases.length), 0, gone);
      rerender();
      rowsAfter(b);
      toast('Purchase restored');
      await save('purchases');
    }));
    await save('purchases');
  },
  // the price range strip (Q12): a dot lights itself and its row; tapping it again clears it
  pickDot: (el) => {
    U.dot = U.dot === el.dataset.dot ? null : el.dataset.dot;
    showDot();
  },
  openItem: (el) => {
    const id = el.dataset.k;
    U.dot = null;
    if (split() && U.tab === 'search' && !U.sheet) {
      if (U.item !== id) U.obsFor = null;
      U.item = id;
      return rerender();
    }
    U.obsFor = null;
    openSheet('item', { id }, el.dataset.v === 'push');
  },
  obsForm: (el) => {
    U.obsFor = el.dataset.k;
    F.obs = { date: localISO() };
    rerender();
    const f = $('obs-price');
    if (f) f.focus();
  },
  obsCancel: () => {
    U.obsFor = null;
    F.obs = {};
    rerender();
  },
  delObs: (el) => {
    const o = D.observations.find((x) => x.id === el.dataset.k);
    if (!o) return;
    openSheet('confirm', { title: 'Delete this price note?', text: o.itemName + ', ' + cash(o.price) + ' on ' + shortDate(o.date) + '.', btn: 'Delete note', action: 'delObsYes', k: o.id }, !!U.sheet);
  },
  delObsYes: async (el) => {
    const at = D.observations.findIndex((o) => o.id === el.dataset.k),
      gone = D.observations[at];
    D.observations = D.observations.filter((o) => o.id !== el.dataset.k);
    if (U.sheet === 'confirm') closeSheet();
    else rerender();
    toast('Price note deleted', gone && (async () => {
      if (D.observations.some((o) => o.id === gone.id)) return;
      D.observations.splice(Math.min(at, D.observations.length), 0, gone);
      rerender();
      toast('Price note restored');
      await save('observations');
    }));
    await save('observations');
  },
  // Search's category chips, and the "Show all" rows that lead to them (Q02)
  scat: (el) => {
    U.scat = el.dataset.v;
    rerender();
    if (el.classList.contains('more')) window.scrollTo({ top: 0, behavior: MOTION.on() ? 'smooth' : 'auto' });
    const c = document.querySelector('#browse .chip.on');
    if (c && c.scrollIntoView) c.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    fadeScrollers();
  },
  // log a purchase of this item, starting from its name and a fitting category
  logItem: (el) => {
    const it = itemById(el.dataset.k);
    if (!it) return;
    const b = browseOf(it),
      cat = { transport: 'Transport', market: 'Groceries', essentials: 'Shopping', services: 'Other' }[b] || 'Food & drink';
    F.edit = { item: b === 'food' || b === 'market' ? it.name : it.english, price: '', category: cat, date: localISO(), payment: 'Cash' };
    openSheet('edit', {}, !!U.sheet);
    setTimeout(() => {
      const p = $('edit-price');
      if (p) p.focus({ preventScroll: true });
    }, 80);
  },
  clearQ: () => {
    U.q = '';
    const q = $('q');
    if (q) {
      q.value = '';
      q.focus();
    }
    updateSearch();
  },
  cat: (el) => {
    U.cat = el.dataset.v;
    U.bar = null;
    U.shown = SHOW_STEP;
    rerender();
  },
  // the range switch: the knob slides in place, then the numbers, bars and list below change (Q03)
  range: (el) => {
    if (U.range === el.dataset.v) return;
    U.range = el.dataset.v;
    U.roff = 0;
    U.bar = null;
    U.shown = SHOW_STEP;
    const seg = $('rangeSeg');
    if (seg) {
      seg.style.setProperty('--i', RANGES.findIndex((r) => r[0] === U.range));
      seg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.v === U.range));
      squish(seg.querySelector('.knob'));
    }
    spendingChanged(0);
  },
  rangeStep: (el) => {
    const step = +el.dataset.v;
    U.roff = Math.max(0, (U.roff || 0) + step);
    U.bar = null;
    U.shown = SHOW_STEP;
    spendingChanged(step);
  },
  // Search's "Show all N in Spending" (Q09): All time, filtered by the same words, so it shows the same N
  searchToSpend: () => {
    Object.assign(U, { range: 'all', roff: 0, bar: null, cat: 'all', filter: U.q.trim(), shown: SHOW_STEP });
    go('spending');
  },
  // Q08 · doors: Home's two figures, one Log sheet from many places, and words that name a place
  toSpend: (el) => {
    Object.assign(U, { range: el.dataset.v === 'day' ? 'day' : 'all', roff: 0, bar: null, cat: 'all', filter: '', shown: SHOW_STEP });
    go('spending');
  },
  // the same Log sheet as Quick Till's "Log this bill": data-v sets the date (a calendar day), data-item the name
  newPurchase: (el) => {
    const item = el.dataset.item || '',
      date = isoDate(el.dataset.v) || localISO();
    F.edit = { item, price: '', category: 'Food & drink', date, payment: 'Cash' };
    openSheet('edit', {}, !!U.sheet);
    if (item)
      setTimeout(() => {
        const p = $('edit-price');
        if (p) p.focus({ preventScroll: true });
      }, 80);
  },
  goRefresh: () => {
    go('convert');
    refreshRate(true);
  },
  goConvert: () => go('convert'),
  goSearch: () => {
    U.stack = [];
    U.sheet = null;
    U.sd = {};
    U.obsFor = null;
    go('search');
  },
  calendar: () => {
    const t = localISO();
    U.calM = t.slice(0, 8) + '01';
    U.calD = D.purchases.some((p) => p.date === t) ? t : null;
    openSheet('calendar');
  },
  calStep: (el) => {
    const d = atNoon(U.calM);
    d.setMonth(d.getMonth() + +el.dataset.v);
    U.calM = localISO(d).slice(0, 8) + '01';
    U.calD = null;
    rerender();
    const g = document.querySelector('.sheet .calgrid');
    // earlier months come in moving right to left, later ones left to right (Ivan's rule for time)
    if (g) MOTION.animate(g, [{ transform: 'translateX(' + (+el.dataset.v < 0 ? 28 : -28) + 'px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { fade: true });
  },
  calDay: (el) => {
    U.calD = U.calD === el.dataset.v ? null : el.dataset.v;
    rerender();
  },
  // Spending's period label opens the calendar on that period's month (Q10): All on this month, D and a picked day
  // with that day picked. The picked bar stays, so closing the calendar comes back to the same view.
  calFromSpend: () => {
    const per = period(),
      t = localISO(),
      pk = pickedBar(spendingList()),
      day = U.range === 'day' ? per.from : pk && !pk.weekly ? pk.b.from : null,
      at = day || (pk ? pk.b.from : U.range === 'all' || per.to > t ? t : per.to);
    U.calM = (at > t ? t : at).slice(0, 8) + '01';
    U.calD = day;
    openSheet('calendar');
  },
  clearBar: () => {
    U.bar = null;
    barChanged();
  },
  clearFilter: () => {
    U.filter = '';
    const f = $('filter');
    if (f) {
      f.value = '';
      f.focus();
    }
    updateSpending();
  },
  moreRows: () => {
    U.shown = (U.shown || SHOW_STEP) + SHOW_STEP;
    $('spendList').innerHTML = spendRows(spendingList());
    fadeScrollers();
  },
  clearFilters: () => {
    U.filter = '';
    U.cat = 'all';
    U.bar = null;
    U.shown = SHOW_STEP;
    rerender();
  },
  csv: () => exportCSV(),
  cashExact: () => {
    setTillCash(U.till.bill);
    tipDone('till');
  },
  cashAdd: (el) => {
    setTillCash(fmtAmt((amount(U.till.cash) || 0) + +el.dataset.v));
    tipDone('till');
  },
  cashClear: () => setTillCash(''),
  tillLog: () => {
    const t = tillState();
    if (!(t.bill > 0)) return;
    F.edit = { item: '', price: fmtAmt(t.bill), category: 'Food & drink', date: localISO(), payment: 'Cash' };
    openSheet('edit', { fromTill: true });
  },
  refreshRate: () => refreshRate(true),
  copyConv: () => copyConv(),
  quickConv: (el) => {
    const c = el.dataset.c === 'php' ? 'php' : 'gbp';
    convInput(c, el.dataset.v);
    const g = $('conv-' + c);
    if (g) g.value = el.dataset.v;
    window.scrollTo({ top: 0, behavior: MOTION.on() ? 'smooth' : 'auto' });
  },
  // the two boxes trade places (FLIP: redraw in the new order, then slide each from where it was)
  swapConv: () => {
    const before = {};
    document.querySelectorAll('#convCard .cbox').forEach((b) => (before[b.dataset.c] = b.getBoundingClientRect().top));
    U.conv.top = U.conv.top === 'php' ? 'gbp' : 'php';
    rerender();
    document.querySelectorAll('#convCard .cbox').forEach((b) => {
      const dy = before[b.dataset.c] - b.getBoundingClientRect().top;
      if (dy) MOTION.animate(b, [{ transform: 'translateY(' + dy + 'px)' }, { transform: 'none' }], { fade: true });
    });
    const sw = document.querySelector('#convCard .swap svg');
    if (sw) MOTION.animate(sw, [{ transform: 'rotate(-180deg)' }, { transform: 'none' }]);
    const f = $('conv-' + U.conv.top);
    if (f) f.focus({ preventScroll: true });
  },
  exportBackup: (el) => exportBackup(el.dataset.v === 'push'),
  saveBackup: () => saveBackup(),
  importPick: () => $('importIn').click(),
  restoreYes: () => restoreYes(),
  erase: () => openSheet('erase'),
  eraseYes: () => eraseYes(),
  openNotes: () => openSheet('notes'),
  openRescue: () => openSheet('rescue'),
  saveRescue: () => saveRescue(),
  clearRescue: () => openSheet('confirm', { title: 'Clear recovered data?', text: 'The copy you saved stays wherever you saved it.', btn: 'Clear it', action: 'clearRescueYes' }, true),
  clearRescueYes: () => clearRescue(),
  putBack: () => openSheet('putback'),
  putBackYes: () => putBack(),
  openAccess: () => openSheet('access'),
  setReduce: (el) => {
    MOTION.setReduce(el.dataset.v);
    const seg = $('reduceSeg');
    if (seg) {
      seg.style.setProperty('--i', ['auto', 'on', 'off'].indexOf(el.dataset.v));
      seg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.v === el.dataset.v));
      squish(seg.querySelector('.knob'));
    }
  },
};
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-a]');
  // a tap that ends a swipe isn't a tap on the row
  if (Date.now() - swJustMoved < 350 && !(el && el.classList.contains('swdel'))) {
    e.preventDefault();
    return;
  }
  if (swOpen && !(el && el.classList.contains('swdel'))) {
    closeSwipes();
    e.preventDefault();
    return;
  }
  if (!el || el.disabled || el.getAttribute('aria-disabled') === 'true') return;
  // the dimmed area around a sheet closes it; taps inside the sheet don't
  if (el.classList.contains('scrim') && e.target !== el) return;
  const f = ACT[el.dataset.a];
  if (!f) return;
  e.preventDefault();
  f(el, e);
});

/* ===== The price range strip's dots and rows (Q12) =====
   A row in You paid or Your price notes lights its dot (a You paid row still opens the purchase, so the dot is lit
   when you come back); a tap anywhere else clears it, except on a sheet opened over the item (the purchase, or
   deleting a note), so coming back finds it as it was. Only classes and the label change, in place: nothing moves,
   so the tap that clears it always lands where it was aimed. */
document.addEventListener('click', (e) => {
  if (e.target.closest('#leaving') || e.target.closest('.sdot')) return;
  const d = e.target.closest('[data-dot]'),
    a = e.target.closest('[data-a]');
  // a button inside the row (the bin) is its own tap; the scrim around the whole sheet doesn't count
  if (d && (!a || a === d || a.contains(d))) {
    U.dot = d.dataset.dot;
    showDot();
  } else if (U.dot && !(U.sheet && U.sheet !== 'item')) {
    U.dot = null;
    showDot();
  }
  // capture: this sees the tap before its action runs, so a close on the purchase sheet still counts as "over the item"
}, true);
function showDot() {
  document.querySelectorAll('.strip').forEach((strip) => {
    if (strip.closest('#leaving')) return;
    const root = strip.closest('.sheet') || strip.closest('.pane') || document.body;
    let lit = null;
    root.querySelectorAll('[data-dot]').forEach((el) => {
      const on = el.dataset.dot === U.dot;
      if (el.classList.contains('sdot')) {
        el.classList.toggle('on', on);
        el.setAttribute('aria-pressed', on);
        if (on) lit = el;
      } else el.classList.toggle('lit', on);
    });
    const l = strip.querySelector('.slabel');
    if (!l) return;
    l.textContent = lit ? lit.dataset.label : '';
    l.classList.toggle('on', !!lit);
    if (lit) {
      l.style.left = lit.dataset.x + '%';
      l.style.setProperty('--x', lit.dataset.x + '%');
    }
  });
}

/* ===== Keyboard (iPad keyboards and Mac) ===== */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (U.sheet && !document.querySelector('#layer .sheet.locked')) {
      e.preventDefault();
      closeSheet();
    } else if (swOpen) closeSwipes();
    return;
  }
  if ((APPLE ? e.metaKey : e.ctrlKey) && /^[1-5]$/.test(e.key) && !U.sheet) {
    e.preventDefault();
    go(TABS[+e.key - 1][0]);
  }
});
