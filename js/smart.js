/* Suki · smart.js
   Smart add (Q14): the second side of Home's Log card. Type, say or paste a purchase in one line, see what Suki
   understood, and save it in one tap. The form stays: a pill on the "Log a purchase" heading switches sides, and
   Suki remembers the last side on this device ('suki:logSide', not in backups).
   - The reader is js/reader.js. This file draws the side, the preview and the "Words Suki has learned" sheet, and
     handles their taps. Typing only redraws the suggestions and the preview (#smartSugg, #smartOut), never the page.
   - F.smart = {text, over}: the line, and changes made in the preview (keyed by the purchase's place in the list,
     cleared when the line changes). The line is kept in 'suki:smart' so it survives closing the app (not in backups).
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

let LOGSIDE = 'form';
try {
  if (localStorage.getItem('suki:logSide') === 'smart') LOGSIDE = 'smart';
} catch (e) {}
let SMART_LAST = []; // what the preview shows now
function saveSmart() {
  try {
    if (F.smart.text.trim()) localStorage.setItem('suki:smart', F.smart.text);
    else localStorage.removeItem('suki:smart');
  } catch (e) {}
}
function loadSmart() {
  try {
    F.smart = { text: localStorage.getItem('suki:smart') || '', over: {} };
  } catch (e) {}
}

/* ===== The two sides ===== */
const SIDE_ICON = {
  smart: GL('<path d="M4 7h16M4 12h10M4 17h7"/><path d="m16 16 2 2 3.5-4"/>'),
  form: GL('<rect x="4" y="4" width="16" height="5" rx="1.5"/><rect x="4" y="12" width="7" height="5" rx="1.5"/><rect x="13" y="12" width="7" height="5" rx="1.5"/>'),
};
// the pill names the other side: on the form it offers Smart add, on Smart add it offers the full form
const sidePill = () =>
  '<button class="sidepill" id="sidePill" data-a="logSide" aria-label="' + (LOGSIDE === 'smart' ? 'Switch to the full form' : 'Switch to Smart add') + '">' +
  (LOGSIDE === 'smart' ? SIDE_ICON.form + 'Full form' : SIDE_ICON.smart + 'Smart add') + '</button>';
const formFace = () =>
  '<form class="card form face" data-form="home" novalidate>' + purchaseForm('home', F.home, U.more) + '<p class="err" id="home-err" role="alert"></p>' + saveBtn() + '</form>';
const smartFace = () =>
  '<div class="card form smart face" id="smartCard">' +
  '<textarea class="inp" id="smartText" rows="1" placeholder="jeep to sm 14" autocomplete="off" autocapitalize="none" spellcheck="false" enterkeyhint="enter" aria-label="Type a purchase" aria-describedby="smartHint">' + esc(F.smart.text) + '</textarea>' +
  '<p class="small sh" id="smartHint">Type, paste or use the keyboard mic. One purchase per line.</p>' +
  '<div id="smartSugg">' + suggHTML() + '</div><div id="smartOut">' + smartOut() + '</div></div>';
const logCard = () => hdr('Log a purchase', sidePill()) + '<div class="logwrap" id="logwrap">' + (LOGSIDE === 'smart' ? smartFace() : formFace()) + '</div>';
// the box grows with what's typed, up to about six lines
function growSmart() {
  const t = $('smartText');
  if (!t) return;
  t.style.height = 'auto';
  t.style.height = Math.min(160, t.scrollHeight + 2) + 'px';
}

// switching sides: the card stays put and only its contents change (MOTION.fold)
function switchSide(to, focus) {
  if (to === LOGSIDE) return;
  const wrap = $('logwrap');
  LOGSIDE = to;
  try {
    localStorage.setItem('suki:logSide', to);
  } catch (e) {}
  if (!wrap) return rerender();
  // interrupted mid-way: the copy still fading goes at once, and the side now showing is the one to leave from
  wrap.querySelectorAll('.lghost').forEach((g) => g.remove());
  const old = wrap.querySelector('.face');
  let ghost = null;
  if (old) {
    old.getAnimations({ subtree: true }).forEach((a) => a.cancel());
    ghost = old.cloneNode(true);
    const a = old.querySelectorAll('input,select,textarea'),
      b = ghost.querySelectorAll('input,select,textarea');
    a.forEach((x, i) => (b[i].value = x.value));
    ghost.classList.add('lghost');
    ghost.removeAttribute('data-form');
    ghost.querySelectorAll('[id],[data-a],[data-form],[name]').forEach((e) => ['id', 'data-a', 'data-form', 'name'].forEach((k) => e.removeAttribute(k)));
    ghost.removeAttribute('id');
    ghost.setAttribute('aria-hidden', 'true');
    ghost.inert = true;
  }
  wrap.innerHTML = to === 'smart' ? smartFace() : formFace();
  const pill = $('sidePill');
  if (pill) pill.outerHTML = sidePill();
  growSmart();
  if (to === 'smart' && focus) {
    const t = $('smartText');
    if (t) t.focus({ preventScroll: true });
  }
  if (ghost) MOTION.fold(wrap, ghost, wrap.querySelector('.face'));
}

/* ===== Reading the line ===== */
const keyCache = {};
// the same thing: the same price-list item (whole words), or the same words
function thingOf(item) {
  if (item in keyCache) return keyCache[item];
  const h = wordMatch(item);
  return (keyCache[item] = h && h.whole ? 'id:' + h.id : 'w:' + READER.toks(item).join(' '));
}
// Your usual: the middle of your last three of the same thing, at the same place first
function usualFor(p) {
  if (!p.item) return null;
  const k = thingOf(p.item),
    same = D.purchases.filter((h) => thingOf(h.item) === k),
    here = p.location ? same.filter((h) => String(h.location || '').toLowerCase() === p.location.toLowerCase()) : [],
    past = (here.length ? here : same).slice().sort(byNewest).slice(0, 3).map((h) => h.price).sort((a, b) => a - b);
  return past.length ? { price: past[Math.floor((past.length - 1) / 2)], n: past.length } : null;
}
// how the price sits against the typical range: a plain statement, never a warning colour. Whole-word matches only
function versus(p) {
  const m = p.match;
  if (!m || !m.whole || m.low == null || p.price == null) return '';
  const range = pesoRange(m.low, m.high);
  if (p.price > m.high * 1.25) return 'More than the typical ' + range;
  if (p.price < m.low * 0.75) return 'Less than the typical ' + range;
  return 'Within the typical ' + range;
}
function smartRead() {
  const f = F.smart;
  if (f.overText !== f.text) (f.over = {}), (f.overText = f.text);
  const list = READER.read(f.text, new Date(), learnedMap(), D.rate ? D.rate.value : 0);
  list.forEach((p, i) => {
    // Q16: the day's town, when the line names no place
    if (!p.location) {
      const t = townOn(p.date);
      if (t) (p.location = t), (p.locAuto = true);
    }
    if (p.price == null) {
      const u = usualFor(p);
      if (u) (p.price = u.price), (p.priceFrom = 'usual'), (p.usualN = u.n), (p.flags = p.flags.filter((x) => x !== 'amount'));
    }
    const o = f.over[i];
    if (o) {
      Object.assign(p, o);
      if ('item' in o) p.match = READER.matchInfo(p.item);
    }
  });
  SMART_LAST = list;
  return list;
}
const smartReady = (p) => p.price != null && cents(p.price) > 0 && !!p.item;

/* ===== Suggestions: while typing a line's words, before any number, three of his own purchases ===== */
let SUGG = [];
function suggHTML() {
  const line = F.smart.text.split(/\n/).pop(),
    q = READER.toks(line).join(' ');
  SUGG = [];
  if (/\d/.test(line) || q.length < 2) return '';
  const seen = new Set();
  D.purchases.slice().sort(byNewest).forEach((h) => {
    if (SUGG.length >= 3) return;
    const words = READER.toks(h.item + ' ' + (h.said || '')).join(' '),
      key = [h.item, h.location, h.price].join('|');
    if ((words.startsWith(q) || (' ' + words).includes(' ' + q)) && !seen.has(key)) {
      seen.add(key);
      SUGG.push(h);
    }
  });
  if (!SUGG.length) return '';
  return (
    '<div class="sec">From your purchases</div><div class="grp tiled">' +
    SUGG.map((h, i) => '<button class="row" data-a="smartSugg" data-k="' + i + '">' + tile(h.category) + '<span class="lbl"><b>' + esc(h.item) + '</b><small>' + esc([h.location, relDay(h.date)].filter(Boolean).join(' · ')) + '</small></span><span class="amt">' + peso(h.price) + '</span></button>').join('') +
    '</div>'
  );
}

/* ===== The preview ===== */
const learnedLink = () => '<button class="textlink" data-a="openLearned">Words Suki has learned' + (D.learned.length ? ' · ' + D.learned.length : '') + '</button>';
function smartOut() {
  const list = smartRead();
  if (!list.length) {
    // just saved: the button stays where he tapped, saying so (Q11's Saved)
    if (Date.now() < savedUntil) return '<button type="button" class="cta ink saved" id="homeSave" data-side="smart"><span class="tk">' + ICON.tick + '</span>Saved</button>' + learnedLink();
    return '<p class="small sh">Suki picks out the amount, item, category, day, place and how you paid, and shows you before anything is saved.</p>' + learnedLink();
  }
  const ready = list.every(smartReady),
    many = list.length > 1;
  return (
    '<div class="sec">' + (many ? list.length + ' purchases found' : 'Suki read') + '</div>' +
    (many ? previewMany(list) : previewOne(list[0])) +
    '<p class="err" id="smartErr" role="alert"></p>' +
    '<button type="button" class="cta ink' + (ready ? '' : ' dim') + '" id="smartSave" data-a="smartSave">' + (many ? 'Save ' + list.length + ' purchases' : 'Save purchase') + '</button>' +
    (many ? '' : '<button class="textlink" data-a="smartToForm">Edit in the form</button>') +
    '<p class="said">Your words are kept with each purchase.</p>' + learnedLink()
  );
}
const kv = (k, v, cls) => '<div class="row kv' + (cls ? ' ' + cls : '') + '"><span class="k">' + k + '</span><span class="v">' + v + '</span></div>';
function previewOne(p) {
  let h =
    '<div class="grp sprev"><div class="row shead1">' + tile(p.category) + '<span class="lbl"><b>' + (p.item ? esc(p.item) : '<span class="faint">What was it?</span>') + '</b></span>' +
    '<span class="amt">' + (p.price != null ? esc(peso(p.price)) : '<span class="faint">₱ —</span>') + '</span></div>';
  // it asks only what's missing
  if (p.price == null) h += '<label class="row kv ask"><span class="k">How much?</span><input class="kvin" id="smartPrice" inputmode="decimal" placeholder="₱0.00" autocomplete="off"></label>';
  else if (p.priceFrom === 'usual')
    h += '<label class="row kv ask"><span class="k">Your usual<small>' + (p.usualN > 1 ? 'from your last ' + p.usualN : 'from last time') + '</small></span><input class="kvin" id="smartPrice" inputmode="decimal" value="' + esc(fmtAmt(p.price)) + '" autocomplete="off"></label>';
  if (!p.item) h += '<label class="row kv ask"><span class="k">What was it?</span><input class="kvin wide" id="smartItem" placeholder="e.g. Snacks" autocomplete="off"></label>';
  h += '<label class="row kv' + (p.catFrom === 'guess' ? ' guess' : '') + '"><span class="k">Category</span><select class="kvsel" data-smart-cat="0" aria-label="Category">' + opts(CATS, p.category) + '</select></label>';
  if (p.catFrom === 'tie')
    h += '<div class="either"><p>' + esc(p.tie[0]) + ' or ' + esc(p.tie[1]) + '?</p>' + p.tie.map((c) => '<button class="chip' + (p.picked === c ? ' on' : '') + '" data-a="smartPick" data-v="0" data-k="' + esc(c) + '">' + esc(c) + '</button>').join('') + '</div>';
  h += kv('When', esc(relDay(p.date)) + (p.future ? ' <span class="badge warn">In the future</span>' : ''), p.future ? 'warn' : '');
  if (p.location) h += kv('Location' + (p.locAuto ? '<small>' + (p.date === localISO() ? 'from earlier today' : 'from that day') + '</small>' : ''), esc(p.location));
  if (p.venue) h += kv('Where bought', esc(p.venue));
  h += kv('Paid with', esc(p.payment || 'Cash'));
  if (p.notes) h += kv('Note', esc(p.notes), p.flags.includes('pounds') ? 'warn' : '');
  h += '</div>';
  if (p.catFrom === 'guess') h += '<p class="small sh">Suki had no clue for the category, so it’s tinted. Pick one and it remembers the word.</p>';
  if (p.catFrom === 'learned') h += '<p class="small sh">Category from a word Suki has learned.</p>';
  if (p.match) h += priceLink(p.match, versus(p));
  return h;
}
const priceLink = (m, vs) =>
  '<div class="grp tiled spaced"><button class="row" data-a="openItem" data-k="' + esc(m.id) + '">' + tile(itemById(m.id).group, false, m.id) +
  '<span class="lbl"><b>' + esc(vs || m.name + ' prices') + '</b><small>' + (vs ? esc(m.name) + ' prices' : m.low != null ? 'Usually ' + pesoRange(m.low, m.high) : 'What you paid and your notes') + '</small></span>' + ICON.chev + '</button></div>';
function flagOf(p) {
  if (p.price == null) return 'How much?';
  if (!p.item) return 'What was it?';
  if (p.catFrom === 'tie') return p.tie.join(' or ') + '?';
  if (p.catFrom === 'guess') return 'Check category';
  if (p.future) return 'In the future';
  if (p.flags.includes('pounds')) return 'From pounds';
  if (p.priceFrom === 'usual') return 'Your usual';
  return '';
}
function previewMany(list) {
  return (
    '<div class="grp tiled">' +
    list.map((p, i) => {
      const f = flagOf(p);
      return '<button class="row" data-a="smartCheck" data-v="' + i + '">' + tile(p.category) + '<span class="lbl"><b>' + esc(p.item || 'What was it?') + '</b><small>' + (f ? '<span class="badge warn">' + esc(f) + '</span> ' : '') + esc([p.category, relDay(p.date), p.location].filter(Boolean).join(' · ')) + '</small></span><span class="amt">' + (p.price != null ? esc(peso(p.price)) : '—') + '</span>' + ICON.chev + '</button>';
    }).join('') +
    '</div><p class="small sh">Tap a purchase to check or change it.</p>'
  );
}
// typing redraws only the suggestions and the preview, so the box keeps the cursor and the keyboard stays up
function updateSmart() {
  const s = $('smartSugg'),
    o = $('smartOut');
  if (s) s.innerHTML = suggHTML();
  if (o) o.innerHTML = smartOut();
}

/* ===== Learning: a changed category remembers the word (kept in backups) ===== */
async function learnWord(p, cat) {
  if (!p || !p.learnKey || !CATS.includes(cat)) return;
  const w = cleanWord({ word: p.learnKey, category: cat, label: p.item });
  if (!w) return;
  D.learned = D.learned.filter((x) => x.word !== w.word).concat([w]);
  toast('Suki will remember “' + w.label + '” as ' + cat);
  await save('learned');
}
function smartLearn(i, cat) {
  const p = SMART_LAST[i];
  if (!p) return;
  F.smart.over[i] = Object.assign(F.smart.over[i] || {}, { category: cat, catFrom: 'learned', picked: cat });
  learnWord(p, cat);
  updateSmart();
}

/* ===== Saving ===== */
async function smartSave() {
  const list = SMART_LAST,
    err = $('smartErr');
  if (!list.length) return;
  const bad = list.findIndex((p) => !smartReady(p));
  if (bad >= 0) {
    if (err) err.textContent = list.length > 1 ? 'Check the purchases marked “How much?” or “What was it?”.' : list[bad].item ? 'Add how much it was.' : 'Say what it was.';
    const f = $(list[bad].item ? 'smartPrice' : 'smartItem');
    if (f) f.focus();
    return;
  }
  if (list.some((p) => p.price > 10000000)) {
    if (err) err.textContent = 'That amount looks too big. Check the number.';
    return;
  }
  const r = D.rate ? D.rate.value : null,
    before = rowsBefore(),
    ids = [];
  list.forEach((p) => {
    const price = cents(+p.price),
      added = {
        id: newId(),
        item: p.item.slice(0, 200),
        price,
        category: CATS.includes(p.category) ? p.category : 'Food & drink',
        date: isoDate(p.date) || localISO(),
        location: String(p.location || '').trim(),
        venue: VENUES.includes(p.venue) ? p.venue : '',
        payment: PAYMENTS.includes(p.payment) ? p.payment : 'Cash',
        notes: String(p.notes || '').trim(),
        said: String(p.said || '').slice(0, 500),
        gbpAtPurchase: r ? Math.round((price / r) * 100) / 100 : null,
        rateAtPurchase: r,
      };
    D.purchases.unshift(added);
    ids.push(added.id);
  });
  F.smart = { text: '', over: {} };
  saveSmart();
  savedTick();
  rerender();
  savedPop();
  rowsAfter(before);
  toast(ids.length > 1 ? ids.length + ' purchases saved' : 'Purchase saved', () => undoSaves(ids));
  await save('purchases');
}
async function undoSaves(ids) {
  if (!D.purchases.some((p) => ids.includes(p.id))) return;
  const before = rowsBefore();
  D.purchases = D.purchases.filter((p) => !ids.includes(p.id));
  if (ids.includes(U.sel)) U.sel = null;
  rerender();
  rowsAfter(before);
  toast(ids.length > 1 ? ids.length + ' purchases removed' : 'Purchase removed');
  await save('purchases');
}

/* ===== Taps ===== */
Object.assign(ACT, {
  logSide: () => switchSide(LOGSIDE === 'smart' ? 'form' : 'smart', true),
  smartSave: () => smartSave(),
  smartPick: (el) => smartLearn(+el.dataset.v, el.dataset.k),
  // tapping a suggestion fills the line with what he said then (or its name, place and price)
  smartSugg: (el) => {
    const h = SUGG[+el.dataset.k];
    if (!h) return;
    const lines = F.smart.text.split(/\n/);
    lines[lines.length - 1] = h.said || [h.item, h.location ? 'in ' + h.location : '', fmtAmt(h.price)].filter(Boolean).join(' ');
    F.smart.text = lines.join('\n');
    saveSmart();
    const t = $('smartText');
    if (t) {
      t.value = F.smart.text;
      growSmart();
      t.focus({ preventScroll: true });
    }
    updateSmart();
  },
  // the one purchase goes into the form, on the form's side
  smartToForm: () => {
    const p = SMART_LAST[0];
    if (!p) return;
    F.home = {
      item: p.item,
      price: p.price != null ? fmtAmt(p.price) : '',
      category: p.category,
      date: p.date,
      location: p.location || '',
      venue: p.venue || '',
      payment: p.payment || 'Cash',
      notes: p.notes || '',
      said: p.said,
    };
    if (p.location) F.home.locFrom = p.locAuto ? 'auto' : 'typed';
    U.more = !!(p.location || p.venue || (p.payment && p.payment !== 'Cash') || p.notes || p.date !== localISO());
    saveDraft(F.home);
    F.smart = { text: '', over: {} };
    saveSmart();
    switchSide('form');
  },
  // a purchase in a batch opens the usual Log sheet, to check it; Done puts the changes back in the preview
  smartCheck: (el) => {
    const i = +el.dataset.v,
      p = SMART_LAST[i];
    if (!p) return;
    F.edit = { item: p.item, price: p.price != null ? fmtAmt(p.price) : '', category: p.category, date: p.date, location: p.location || '', venue: p.venue || '', payment: p.payment || 'Cash', notes: p.notes || '', said: p.said };
    if (p.location) F.edit.locFrom = p.locAuto ? 'auto' : 'typed';
    openSheet('edit', { smart: i });
  },
  openLearned: () => openSheet('learned', {}, !!U.sheet),
  forgetWord: async (el) => {
    const w = D.learned.find((x) => x.word === el.dataset.k);
    if (!w) return;
    D.learned = D.learned.filter((x) => x !== w);
    rerender();
    toast('Suki forgot “' + w.label + '”');
    await save('learned');
  },
});
// Done on a batch purchase's Log sheet: back into the preview, nothing saved yet
function smartChecked() {
  const i = U.sd.smart,
    was = SMART_LAST[i],
    p = readPurchase('edit');
  if (!p || !was) return;
  if (p.category !== was.category) learnWord(was, p.category);
  F.smart.over[i] = Object.assign({}, p, { said: was.said, flags: [], catFrom: p.category !== was.category ? 'learned' : was.catFrom === 'tie' || was.catFrom === 'guess' ? 'words' : was.catFrom, future: p.date > localISO(), priceFrom: null, locAuto: F.edit.locFrom === 'auto' });
  closeSheet();
}

/* ===== Typing in the preview ===== */
document.addEventListener('input', (e) => {
  const t = e.target;
  if (t.id === 'smartText') {
    F.smart.text = t.value;
    saveSmart();
    growSmart();
    updateSmart();
  } else if (t.id === 'smartPrice' || t.id === 'smartItem') {
    // what he types here changes only the line he's on and the button, so the box keeps the cursor
    const o = (F.smart.over[0] = F.smart.over[0] || {}),
      p = SMART_LAST[0];
    if (!p) return;
    if (t.id === 'smartPrice') {
      const v = formAmount(t.value);
      o.price = v > 0 ? v : null;
      o.priceFrom = null;
      p.price = o.price;
    } else p.item = o.item = t.value.trim().slice(0, 200);
    const b = $('smartSave'),
      er = $('smartErr');
    if (b) b.classList.toggle('dim', !smartReady(p));
    if (er) er.textContent = '';
  }
});
document.addEventListener('change', (e) => {
  const t = e.target;
  if (t.dataset && t.dataset.smartCat != null) smartLearn(+t.dataset.smartCat, t.value);
});
