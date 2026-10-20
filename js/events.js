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
function updateTill() {
  const o = $('tillOut'),
    b = $('tillLog');
  if (o) o.innerHTML = tillOut();
  if (b) b.disabled = !(tillState().bill > 0);
}
function setTillCash(v) {
  U.till.cash = v;
  const el = $('till-cash');
  if (el) el.value = v;
  updateTill();
}
function updateSearch() {
  $('results').innerHTML = searchResults();
  $('examples').hidden = !!U.q;
  const c = document.querySelector('#app .searchbox .clr');
  if (c) c.hidden = !U.q;
}
function updateSpending() {
  const list = spendingList();
  $('spendSum').innerHTML = spendSummary(list);
  $('spendList').innerHTML = spendRows(list);
  const c = document.querySelector('#app .searchbox .clr');
  if (c) c.hidden = !U.filter;
}
const fmtAmt = (n) => (Math.round(n * 100) / 100).toString();

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
  if (!(price > 0)) return formError(form, 'Add an amount above ₱0.', 'price');
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
    const r = D.rate ? D.rate.value : null;
    D.purchases.unshift(Object.assign({ id: newId() }, p, { gbpAtPurchase: r ? Math.round((p.price / r) * 100) / 100 : null, rateAtPurchase: r }));
    if (form === 'home') {
      F.home = { category: p.category, payment: p.payment };
      saveDraft({});
      rerender();
    } else {
      if (U.sd.fromTill) U.till = { bill: '', cash: '' };
      closeSheet();
    }
    toast('Purchase saved');
    await save('purchases');
    return;
  }
  if (form === 'obs') {
    const id = el.dataset.k,
      v = F.obs,
      price = amount(v.price);
    if (!(price > 0)) return formError('obs', 'Add the price you saw.', 'price');
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
  } else if (t.dataset.conv) convInput(t.dataset.conv, t.value);
}
document.addEventListener('input', onField);
document.addEventListener('change', (e) => {
  if (e.target.matches('select,input[type=date]')) onField(e);
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
  close: () => closeSheet(),
  more: () => {
    U.more = !U.more;
    rerender();
  },
  openPurchase: (el) => {
    if (split() && U.tab === 'spending' && !U.sheet) {
      U.sel = el.dataset.k;
      return rerender();
    }
    openSheet('purchase', { id: el.dataset.k });
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
    const id = el.dataset.k;
    D.purchases = D.purchases.filter((p) => p.id !== id);
    if (U.sel === id) U.sel = null;
    U.stack = [];
    U.sheet = null;
    U.sd = {};
    rerender();
    toast('Purchase deleted');
    await save('purchases');
  },
  openItem: (el) => {
    const id = el.dataset.k;
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
    D.observations = D.observations.filter((o) => o.id !== el.dataset.k);
    if (U.sheet === 'confirm') closeSheet();
    else rerender();
    toast('Price note deleted');
    await save('observations');
  },
  example: (el) => {
    U.q = el.dataset.v;
    const q = $('q');
    if (q) q.value = U.q;
    updateSearch();
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
    rerender();
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
  clearFilters: () => {
    U.filter = '';
    U.cat = 'all';
    rerender();
  },
  csv: () => exportCSV(),
  cashExact: () => setTillCash(U.till.bill),
  cashAdd: (el) => setTillCash(fmtAmt((amount(U.till.cash) || 0) + +el.dataset.v)),
  cashClear: () => setTillCash(''),
  tillLog: () => {
    const t = tillState();
    if (!(t.bill > 0)) return;
    F.edit = { item: '', price: fmtAmt(t.bill), category: 'Food & drink', date: localISO(), payment: 'Cash' };
    openSheet('edit', { fromTill: true });
  },
  refreshRate: () => refreshRate(true),
  copyConv: () => copyConv(),
  quickGbp: (el) => {
    convInput('gbp', el.dataset.v);
    const g = $('conv-gbp');
    if (g) g.value = el.dataset.v;
    window.scrollTo({ top: 0, behavior: MOTION.on() ? 'smooth' : 'auto' });
  },
  exportBackup: (el) => exportBackup(el.dataset.v === 'push'),
  saveBackup: () => saveBackup(),
  importPick: () => $('importIn').click(),
  restoreYes: () => restoreYes(),
  erase: () => openSheet('erase'),
  eraseYes: () => eraseYes(),
  openNotes: () => openSheet('notes'),
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

/* ===== Keyboard (iPad keyboards and Mac) ===== */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (U.sheet) {
      e.preventDefault();
      closeSheet();
    } else if (swOpen) closeSwipes();
    return;
  }
  if ((e.metaKey || e.ctrlKey) && /^[1-5]$/.test(e.key) && !U.sheet) {
    e.preventDefault();
    go(TABS[+e.key - 1][0]);
  }
});
