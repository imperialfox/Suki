/* Suki · gestures.js (pull to refresh, sheet dragging and scroll guards come from Vocal Sessions)
   Pull to refresh and the update check, scrolling (the top bar turning to glass), rotating and resizing,
   going online and offline, dragging sheets down to close them.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Pull to refresh (Home and Spending) =====
   Pull down at the top: the page follows your finger with resistance and the spinner's spokes appear.
   Past the threshold, let go: it holds, re-reads your data and checks for a newer version of Suki
   (loading it if there is one), then eases back. */
const PTR = { y: null, x: 0, on: false, d: 0, busy: false, lock: null },
  PT_TRIG = 56,
  PT_HOLD = 56;
(() => {
  const sp = $('spin');
  for (let i = 0; i < 8; i++) {
    const e = document.createElement('i');
    e.style.transform = 'rotate(' + i * 45 + 'deg)';
    sp.appendChild(e);
  }
})();
const ptrOK = () => !U.sheet && (U.tab === 'home' || U.tab === 'spending') && window.scrollY <= 0 && !PTR.busy;
function ptrPaint(d, armed) {
  $('app').style.transform = d ? 'translateY(' + d + 'px)' : '';
  const sp = $('spin');
  sp.style.opacity = d > 8 ? 1 : 0;
  const p = Math.min(1, d / PT_TRIG);
  [...sp.children].forEach((s, i) => {
    s.style.opacity = PTR.busy ? 1 - i * 0.11 : p * 8 > i ? (armed ? 1 - i * 0.09 : 0.75) : 0;
  });
}
document.addEventListener(
  'touchstart',
  (e) => {
    PTR.y = null;
    if (e.touches.length !== 1 || !ptrOK() || e.target.closest('[data-own-gesture],input,textarea,select')) return;
    for (let n = e.target; n && n !== document.body; n = n.parentElement) if (n.scrollTop > 0) return;
    PTR.y = e.touches[0].clientY;
    PTR.x = e.touches[0].clientX;
    PTR.on = false;
    PTR.lock = null;
    PTR.d = 0;
    $('app').classList.remove('ptr-snap');
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (PTR.y === null || e.touches.length !== 1) return;
    const t = e.touches[0],
      dy = t.clientY - PTR.y,
      dx = t.clientX - PTR.x;
    if (PTR.lock === null) {
      if (dy <= 0 || Math.abs(dx) > Math.abs(dy)) {
        if (Math.abs(dx) > 6 || dy < -6) PTR.lock = 'no';
        return;
      }
      if (dy > 6) PTR.lock = 'pull';
    }
    if (PTR.lock === 'no') return;
    if (window.scrollY > 0) {
      PTR.y = null;
      return;
    }
    if (e.cancelable) e.preventDefault();
    if (PTR.lock !== 'pull') return;
    PTR.on = true;
    PTR.d = Math.max(0, 170 * (1 - 1 / (Math.max(0, dy) / 360 + 1)));
    ptrPaint(PTR.d, PTR.d >= PT_TRIG);
  },
  { passive: false }
);
function ptrEnd() {
  if (PTR.y === null) return;
  PTR.y = null;
  if (!PTR.on) return;
  PTR.on = false;
  const a = $('app');
  a.classList.add('ptr-snap');
  if (PTR.d < PT_TRIG) {
    ptrPaint(0);
    return;
  }
  PTR.busy = true;
  $('ptr').classList.add('go');
  ptrPaint(PT_HOLD, true);
  refreshApp().then((r) => {
    if (r === 'reload') return;
    $('ptr').classList.remove('go');
    PTR.busy = false;
    ptrPaint(0);
    setTimeout(() => a.classList.remove('ptr-snap'), 450);
  });
}
document.addEventListener('touchend', ptrEnd);
document.addEventListener('touchcancel', ptrEnd);
const cmpVer = (a, b) => {
  const x = a.split('.').map(Number),
    y = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    const d = (x[i] || 0) - (y[i] || 0);
    if (d) return d;
  }
  return 0;
};
async function refreshApp() {
  const t0 = Date.now();
  let newer = null;
  await loadData();
  try {
    const r = await fetch(location.href.split('#')[0], { cache: 'reload' });
    const m = (await r.text()).match(/APP_VERSION='([\d.]+)'/);
    if (m && cmpVer(m[1], APP_VERSION) > 0) newer = m[1];
  } catch (e) {}
  autoRate();
  await new Promise((r) => setTimeout(r, Math.max(0, 700 - (Date.now() - t0))));
  if (newer) {
    toast('Updating to Suki ' + newer + '…');
    setTimeout(() => location.reload(), 800);
    return 'reload';
  }
  rerender();
  return 'ok';
}

/* ===== Scrolling: the top bar turns to glass. The tab bar always stays full size ===== */
window.addEventListener(
  'scroll',
  () => {
    if (swOpen) closeSwipes();
    const y = window.scrollY,
      sc = y > 36;
    $('bar').classList.toggle('scrolled', sc);
    document.body.classList.toggle('scrolled', sc);
  },
  { passive: true }
);

/* ===== Rotating and resizing ===== */
Object.values(MQ).forEach((m) => {
  const f = () => {
    layout();
    rerender();
  };
  if (m.addEventListener) m.addEventListener('change', f);
  else if (m.addListener) m.addListener(f);
});

/* ===== Online and offline ===== */
function netChange() {
  renderBar();
  const l = $('rateLine');
  if (l) l.textContent = rateLine();
  if (navigator.onLine) autoRate();
}
window.addEventListener('online', netChange);
window.addEventListener('offline', netChange);

/* ===== Sheets keep scrolling to themselves =====
   When a sheet can't scroll any further that way (or the swipe is on the dimmed page around it), the page behind
   stays put. iOS ignores overscroll-behavior once nothing inside can scroll, so touches and the wheel are checked here. */
const overlayOpen = () => !!$('layer').firstElementChild;
function canScrollIn(el, dy) {
  for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
    if (n.classList.contains('scrim') || n.id === 'layer') return false;
    const oy = getComputedStyle(n).overflowY;
    if ((oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight + 1) {
      if (dy > 0 ? n.scrollTop + n.clientHeight < n.scrollHeight - 1 : n.scrollTop > 0) return true;
    }
    if (n.classList.contains('sheet')) return false;
  }
  return false;
}
let OT = null;
document.addEventListener(
  'touchstart',
  (e) => {
    OT = overlayOpen() && e.touches.length === 1 ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : null;
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!OT || e.touches.length !== 1 || !overlayOpen()) return;
    const t = e.touches[0],
      dx = t.clientX - OT.x,
      dy = OT.y - t.clientY;
    OT.x = t.clientX;
    OT.y = t.clientY;
    if (Math.abs(dy) <= Math.abs(dx)) return;
    if (!canScrollIn(e.target, dy) && e.cancelable) e.preventDefault();
  },
  { passive: false }
);
document.addEventListener(
  'wheel',
  (e) => {
    if (!overlayOpen() || !e.deltaY || Math.abs(e.deltaY) < Math.abs(e.deltaX)) return;
    if (!canScrollIn(e.target, e.deltaY)) e.preventDefault();
  },
  { passive: false }
);

/* ===== Drag a sheet down by its header to close it, like iOS ===== */
let SD = null;
document.addEventListener(
  'touchstart',
  (e) => {
    const h = e.target.closest('.shead');
    SD = null;
    if (!h || e.touches.length !== 1 || e.target.closest('button')) return;
    SD = { sh: h.closest('.sheet'), y: e.touches[0].clientY, dy: 0 };
  },
  { passive: true }
);
document.addEventListener(
  'touchmove',
  (e) => {
    if (!SD || e.touches.length !== 1) return;
    SD.dy = Math.max(0, e.touches[0].clientY - SD.y);
    if (e.cancelable) e.preventDefault();
    SD.sh.classList.add('drag');
    SD.sh.style.transform = SD.dy ? 'translateY(' + SD.dy + 'px)' : '';
  },
  { passive: false }
);
function sheetDragEnd() {
  if (!SD) return;
  const { sh, dy } = SD;
  SD = null;
  sh.classList.remove('drag');
  if (!dy) return;
  sh.classList.add('back');
  if (dy > 90) {
    sh.style.transform = 'translateY(110%)';
    setTimeout(() => {
      if (U.sheet) closeSheet();
    }, 200);
  } else {
    sh.style.transform = '';
    setTimeout(() => sh.classList.remove('back'), 340);
  }
}
document.addEventListener('touchend', sheetDragEnd);
document.addEventListener('touchcancel', sheetDragEnd);
