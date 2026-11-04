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
  tipDone('pull');
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
  if (!navigator.onLine) return;
  autoRate();
  // purchases saved offline with an estimated rate get their day's rate now (Q22)
  fixRates();
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
    if (!h || e.touches.length !== 1 || e.target.closest('button') || h.closest('.sheet.locked')) return;
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
    tipDone('sheet');
    // it carries on down from where the finger let go (Q11: the close slides it the rest of the way)
    sh.classList.remove('back');
    if (U.sheet) closeSheet();
  } else {
    sh.style.transform = '';
    setTimeout(() => sh.classList.remove('back'), 340);
  }
}
document.addEventListener('touchend', sheetDragEnd);
document.addEventListener('touchcancel', sheetDragEnd);

/* ===== The till drawer (Q19) =====
   An Easter egg: nothing points to it, there's no tip and it isn't in Help. Pull the cash box (or the slot line under
   it) down and let go: it settles at whichever end it would coast to. Swipe up to shut it; once it's shut, the rest of
   the same swipe scrolls the page, and a flick glides on. Shut hard, it knocks the counter: only the cash box nudges up.
   The iOS way, as Ivan chose in the note press prototype (1 Nov 2026, "the ios way is great"):
   - It follows the finger exactly, can be caught mid-movement, and stretches past open with iOS's rubber band.
   - Open or shut is decided by where it would coast to (MOTION.project, deceleration 0.99): past halfway, it opens.
   - The swipe's speed is read over its last tenth of a second, up to the moment of release.
   - Springs are a length and a bounce (MOTION.iosSpring): opening 0.45 s, with bounce only from a flick (up to 0.15;
     a tap, Space, Enter or VoiceOver opens with none); shutting 0.35 s with none, cut off at shut.
   A tap still types: only a drag past 6 pt is the drawer's. Sideways, or after holding still in the box, the drag is
   left to the text (selecting, moving the cursor: 2.24.1). It starts shut every time: a redraw shuts it (drawerReset,
   from render()), and so does typing in either box. iPhone upright, iPad and Mac only; on its side there's no drawer.
   Reduce Motion: a 0.2 s fade, no spring and no knock. The page's glide stays.
   Q20 fills it (screens.js drawerFill, events.js fillDrawer) and makes the contents jiggle; Q21 adds the two-finger haul
   (below drawerEnd). */
const DRAWER = {
  open: 106, // pt, open height
  claim: 6, // pt a drag must travel before it's the drawer's
  hold: 500, // ms held still in the cash box before a drag is left to the text cursor
  window: 100, // ms of the swipe its speed is read over
  maxV: 2500, // pt/s, the fastest swipe read
  snapV: 1200, // pt/s, the fastest carried into the spring
  openFor: 0.45, // s, the opening spring
  flickBounce: 0.15, // the most bounce a flick gives it
  bouncePer: 8000, // pt/s of flick per 1 of bounce
  shutFor: 0.35, // s, the shutting spring (no bounce)
  stretch: 40, // pt, the most it stretches past open
  knockAt: 0.3, // how hard a shut must be to knock (speed ÷ 1000 pt/s)
  knockFast: 600, // pt/s, swiped shut on the way into a scroll
  knockFull: 1500, // pt/s, the hardest knock
  knockMs: 200,
  fade: 200, // ms, Reduce Motion
  lineFor: 900, // ms the line stays after shutting
  glideFrom: 120, // pt/s, the slowest flick that glides on
  glideDecel: 0.998, // per ms, like an iOS scroll
  haul: 120, // pt the two-finger haul takes it past open, where it stops (Q21)
  pull: 0.035, // pt of drawer per pt of finger while hauling: about ten 350 pt swipes to the back
};
// rest: where an open drawer sits (open, or as far as it was hauled); haul: the two-finger pull in progress (Q21)
const DR = { h: 0, open: false, drag: null, raf: 0, glide: 0, hide: 0, eat: false, fade: null, rest: DRAWER.open, haul: null };
const drawerOK = () => U.tab === 'till' && !U.sheet && !(MQ.land.matches && !MQ.reg.matches) && !!$('tillDrawer');
const drawerBox = () => document.querySelector('#app .cashbox');
function drawerSet(v) {
  DR.h = v;
  const d = $('tillDrawer'),
    c = drawerBox();
  if (d) d.style.height = Math.max(0, v).toFixed(2) + 'px';
  if (c) c.style.setProperty('--open', Math.min(1, Math.max(0, v) / DRAWER.open).toFixed(3));
  drawerPeek();
}
// the contents feel the drawer move (Q20, open and shut only): coins lag a frame and settle, and the notes sway about
// 1.6° and right themselves, each on top of where it stands. Motion on only: Reduce Motion has no jiggle
function drawerJiggle(dir) {
  if (!MOTION.on()) return;
  document.querySelectorAll('#tillTray .tcup i:not(.going)').forEach((c, i) => {
    const base = c.style.transform && c.style.transform !== 'none' ? c.style.transform : '';
    MOTION.animate(c, [{ transform: (base + ' translateY(' + (dir * 1.6).toFixed(1) + 'px)').trim() }, { transform: base || 'none' }], { spring: 'ripple', delay: 16 + (i % 3) * 12 });
  });
  document.querySelectorAll('#tillTray .tslot i:not(.going)').forEach((n, i) => {
    const base = n.style.transform && n.style.transform !== 'none' ? n.style.transform : '';
    MOTION.animate(n, [{ transform: (base + ' rotateZ(' + ((i % 2 ? 1 : -1) * 1.6).toFixed(1) + 'deg)').trim() }, { transform: base || 'none' }], { spring: 'ripple', delay: 24 + (i % 4) * 10 });
  });
}
// the slot line: shown now, and hidden again ms later unless the drawer is open or held
function drawerLine(ms) {
  const hd = $('tillHdl');
  clearTimeout(DR.hide);
  if (hd) hd.classList.add('on');
  if (ms)
    DR.hide = setTimeout(() => {
      if (!DR.open && !DR.drag && $('tillHdl')) $('tillHdl').classList.remove('on');
    }, ms * Math.max(1, MOTION.speed()));
}
function drawerStop() {
  cancelAnimationFrame(DR.raf);
  DR.raf = 0;
  if (DR.fade) {
    DR.fade.cancel();
    DR.fade = null;
  }
}
// how fast the swipe was over its last tenth of a second, up to now (pt/s, down is positive)
function drawerSpeed(d, now) {
  const s = d.samples;
  if (s.length < 2) return 0;
  let i = s.length - 1;
  while (i > 0 && now - s[i - 1].t <= DRAWER.window) i--;
  if (i === s.length - 1) i--;
  const a = s[i],
    b = s[s.length - 1],
    dt = (now - a.t) / 1000;
  return dt > 0 ? (b.raw - a.raw) / dt : 0;
}
// shut hard, the drawer knocks the counter: only the cash box moves, up 1–2.2 pt at the instant it hits
function drawerKnock(k) {
  if (!MOTION.on()) return;
  MOTION.animate(drawerBox(), [{ transform: 'none' }, { transform: 'translateY(' + (-(0.8 + k * 1.4)).toFixed(2) + 'px)', offset: 0.3 }, { transform: 'none' }], { ms: DRAWER.knockMs, easing: 'ease-out' });
  drawerJiggle(-1); // and the coins jump
}
// open or shut it, carrying the finger's speed (v0, pt/s) into the spring. Open, it goes to where it rests: open, or as
// far as it was hauled (Q21); `at` moves that spot (a one-finger push on a hauled drawer). Shut, the haul is forgotten
function drawerSnap(open, v0, at) {
  drawerStop();
  DR.open = open;
  DR.rest = open ? Math.max(DRAWER.open, Math.min(DRAWER.open + DRAWER.haul, at === undefined ? DR.rest : at)) : DRAWER.open;
  const hd = $('tillHdl'),
    tray = $('tillTray'),
    to = open ? DR.rest : 0;
  if (hd) {
    hd.setAttribute('aria-expanded', String(open));
    hd.setAttribute('aria-label', open ? 'Close till drawer' : 'Open till drawer');
  }
  if (open) drawerLine();
  else drawerLine(DRAWER.lineFor);
  if (!MOTION.on()) {
    // Reduce Motion: it fades in, or fades out and then closes. Motion off (the tests): straight there
    const sp = MOTION.speed();
    if (!sp || !tray || !MOTION.reduced()) return drawerSet(to);
    if (open) {
      const from = DR.h;
      drawerSet(to);
      if (from < 0.5) tray.animate([{ opacity: 0 }, { opacity: 1 }], { duration: DRAWER.fade * sp, easing: 'ease-out' });
      return;
    }
    if (DR.h < 0.5) return drawerSet(0);
    const f = tray.animate([{ opacity: 1 }, { opacity: 0 }], { duration: DRAWER.fade * sp, easing: 'ease-out', fill: 'forwards' });
    DR.fade = f;
    f.onfinish = () => {
      if (DR.fade !== f) return;
      DR.fade = null;
      drawerSet(0);
      f.cancel();
    };
    return;
  }
  if (Math.abs(to - DR.h) > 4) drawerJiggle(open ? -1 : 1);
  const s = open ? MOTION.iosSpring(DRAWER.openFor, Math.min(DRAWER.flickBounce, Math.max(0, v0 || 0) / DRAWER.bouncePer)) : MOTION.iosSpring(DRAWER.shutFor, 0),
    w = 2 * Math.PI * s.f,
    k = open ? 0 : Math.max(0, Math.min(1, -(v0 || 0) / 1000));
  let x = DR.h,
    v = v0 || 0,
    last = performance.now();
  const step = (now) => {
    if (!$('tillDrawer')) return void (DR.raf = 0);
    const dt = Math.max(0, Math.min(0.032, (now - last) / 1000)) / MOTION.speed();
    last = now;
    v += (-w * w * (x - to) - 2 * s.z * w * v) * dt;
    x += v * dt;
    // a drawer can't travel past shut: it stops dead there, and knocks the counter if it came in hard
    const done = !open && x <= 0 ? true : Math.abs(x - to) < 0.2 && Math.abs(v) < 4;
    if (done) {
      DR.raf = 0;
      drawerSet(to);
      if (!open && k > DRAWER.knockAt) drawerKnock(k);
      return;
    }
    drawerSet(x);
    DR.raf = requestAnimationFrame(step);
  };
  DR.raf = requestAnimationFrame(step);
}
function drawerShut() {
  if (DR.open || DR.h > 0) drawerSnap(false);
}
// a redraw always brings the drawer back shut, with nothing left running (render() calls this before it redraws)
function drawerReset() {
  drawerStop();
  glideStop();
  clearTimeout(DR.hide);
  Object.assign(DR, { h: 0, open: false, drag: null, eat: false, rest: DRAWER.open, haul: null });
}

/* the chain: the rest of a swipe that shut it scrolls the page; let go mid-flick and the page glides on, slowing like
   an iOS scroll. Any new touch, click or wheel stops it */
function glideStop() {
  cancelAnimationFrame(DR.glide);
  DR.glide = 0;
}
function glide(v) {
  glideStop();
  if (Math.abs(v) < DRAWER.glideFrom) return;
  let y = window.scrollY,
    last = performance.now();
  const step = (now) => {
    const dt = Math.max(0, Math.min(32, now - last)),
      max = document.scrollingElement.scrollHeight - innerHeight;
    last = now;
    y += (v * dt) / 1000;
    v *= Math.pow(DRAWER.glideDecel, dt);
    const end = y <= 0 || y >= max;
    window.scrollTo(0, Math.max(0, Math.min(max, y)));
    if (end || Math.abs(v) < 20) return void (DR.glide = 0);
    DR.glide = requestAnimationFrame(step);
  };
  DR.glide = requestAnimationFrame(step);
}
['wheel', 'touchstart', 'pointerdown'].forEach((t) => addEventListener(t, glideStop, { passive: true, capture: true }));

document.addEventListener('pointerdown', (e) => {
  const el = e.target.closest && e.target.closest('#app .cashbox, #tillHdl, #tillDrawer');
  if (el && haulDown(e, el)) return;
  if (!el || DR.drag || e.button > 0 || e.target.closest('#cashClear') || !drawerOK()) return;
  drawerStop(); // caught mid-movement, where the finger lands
  drawerLine();
  const now = performance.now();
  DR.drag = {
    el,
    id: e.pointerId,
    x0: e.clientX,
    y0: e.clientY,
    y: e.clientY,
    h0: DR.h,
    t0: now,
    box: el.classList.contains('cashbox'),
    focused: document.activeElement === $('till-cash'),
    sy: window.scrollY,
    moved: false,
    dead: false,
    scrolled: false,
    hit: false,
    lastRaw: DR.h,
    samples: [{ t: now, raw: DR.h }],
  };
});
document.addEventListener('pointermove', (e) => {
  if (DR.haul) return haulMove(e);
  const d = DR.drag;
  if (!d || e.pointerId !== d.id) return;
  d.y = e.clientY;
  const dy = e.clientY - d.y0,
    dx = e.clientX - d.x0,
    now = performance.now();
  if (!d.moved) {
    if (Math.abs(dy) < DRAWER.claim && Math.abs(dx) < DRAWER.claim) return;
    // sideways, or after a hold in the box, the finger is working on the text (2.24.1), so the drawer lets it go
    if (Math.abs(dx) > Math.abs(dy) || (d.box && now - d.t0 > DRAWER.hold)) {
      DR.drag = null;
      if (DR.h > 0) drawerSnap(DR.open);
      else drawerLine(DRAWER.lineFor);
      return;
    }
    d.moved = true;
    try {
      d.el.setPointerCapture(d.id);
    } catch (err) {}
  }
  const raw = d.h0 + dy,
    top = Math.max(DRAWER.open, d.h0),
    nh = raw > top ? top + MOTION.rubber(raw - top, DRAWER.stretch) : Math.max(0, raw),
    over = raw < 0 ? -raw : 0;
  // once it's shut, whatever is left of the swipe up scrolls the page, in the same gesture
  if (over > 0 || d.scrolled) {
    window.scrollTo(0, d.sy + over);
    d.scrolled = over > 0;
  }
  d.samples.push({ t: now, raw });
  if (d.samples.length > 24) d.samples.shift();
  // swiped shut fast on the way into a scroll: the knock, at the moment it shuts
  if (!d.hit && d.lastRaw > 0 && raw <= 0) {
    d.hit = true;
    const speed = -drawerSpeed(d, now);
    if (speed > DRAWER.knockFast) drawerKnock(Math.min(1, speed / DRAWER.knockFull));
  }
  d.lastRaw = raw;
  drawerSet(nh);
});
function drawerEnd(e) {
  if (DR.haul) return haulEnd(e);
  const d = DR.drag;
  if (!d || e.pointerId !== d.id) return;
  DR.drag = null;
  if (!d.moved) {
    // a tap in the box types, and typing shuts the drawer; a tap on the drawer lets it carry on from where it was
    // caught; the handle's own click opens or shuts it
    if (d.box && e.type === 'pointerup') drawerShut();
    else if (DR.h > 0 && d.el.id !== 'tillHdl') drawerSnap(DR.open); // back to where it rests, hauled or not
    if (!DR.open) drawerLine(DRAWER.lineFor);
    return;
  }
  DR.eat = true; // the click that follows a drag isn't a tap on the handle
  setTimeout(() => (DR.eat = false), 50);
  if (d.box && !d.focused && document.activeElement === $('till-cash')) $('till-cash').blur();
  const v = Math.max(-DRAWER.maxV, Math.min(DRAWER.maxV, drawerSpeed(d, performance.now())));
  if (DR.h <= 0.5 && d.lastRaw < 0) {
    drawerSnap(false, 0);
    glide(-v);
    return;
  }
  // settle at whichever end it would coast to. A hauled drawer stays as far out as it was left: only the give past
  // that springs back, and a push up that doesn't shut it leaves it where the push ended (Q21)
  const stay = DR.h + MOTION.project(v) > DRAWER.open / 2;
  drawerSnap(stay, Math.max(-DRAWER.snapV, Math.min(DRAWER.snapV, v)), stay && d.h0 > DRAWER.open + 1 ? Math.min(DR.h, d.h0) : undefined);
}

/* ===== The haul (Q21): the Easter egg inside the Easter egg =====
   With the drawer fully open, hold it with one finger and swipe down with another, hand over hand, swapping fingers as
   long as one stays down. One finger never starts it (so a mouse can't). It's heavy and steady on purpose (Ivan, "I
   want the user to work for it"): 0.035 pt of drawer per pt of finger, straight, with a hard stop 120 pt past open, so
   about ten long swipes reach the back, where "Designed by Ivan" is (screens.js tillDrawer, .tmark). Any finger moving
   down adds; moving up only counts once a single finger is left. Let go and it stays where it was left (DR.rest).
   Deliberately un-iOS: iOS never makes you work against a heavy pull. As the Easter egg, that's the point. */
const hauled = (raw) => Math.min(DRAWER.haul, raw * DRAWER.pull);
// a second finger on the open drawer starts the haul, or joins it; true when the haul took the finger
function haulDown(e, el) {
  if (!DR.haul) {
    const d = DR.drag;
    if (!d || d.id === e.pointerId || !DR.open || DR.fade || DR.h < DRAWER.open - 1 || !drawerOK() || e.target.closest('#cashClear')) return false;
    drawerStop();
    DR.haul = { ptrs: new Map([[d.id, d.y]]), raw: Math.max(0, DR.h - DRAWER.open) / DRAWER.pull };
    DR.drag = null;
    DR.rest = DRAWER.open + hauled(DR.haul.raw); // caught at the end of the opening spring: from where it is, at most 1 pt
    drawerSet(DR.rest);
  }
  DR.haul.ptrs.set(e.pointerId, e.clientY);
  try {
    el.setPointerCapture(e.pointerId);
  } catch (err) {}
  drawerLine();
  return true;
}
function haulMove(e) {
  const H = DR.haul;
  if (!H.ptrs.has(e.pointerId)) return;
  const dy = e.clientY - H.ptrs.get(e.pointerId);
  H.ptrs.set(e.pointerId, e.clientY);
  if (dy > 0 || H.ptrs.size === 1) H.raw = Math.max(0, Math.min(DRAWER.haul / DRAWER.pull, H.raw + dy));
  DR.rest = DRAWER.open + hauled(H.raw);
  drawerSet(DR.rest);
}
function haulEnd(e) {
  const H = DR.haul;
  if (!H.ptrs.has(e.pointerId)) return;
  H.ptrs.delete(e.pointerId);
  if (H.ptrs.size) return;
  DR.haul = null; // it stays where it was left
  DR.eat = 'haul'; // and the fingers lifting aren't a tap on the line or in the box
  setTimeout(() => DR.eat === 'haul' && (DR.eat = false), 300);
}
document.addEventListener('pointerup', drawerEnd);
document.addEventListener('pointercancel', drawerEnd);
document.addEventListener('click', (e) => {
  if (!e.target.closest || !e.target.closest('#tillHdl') || DR.eat || !drawerOK()) return;
  drawerSnap(!DR.open);
});
// typing in either box shuts it
document.addEventListener('input', (e) => {
  if (e.target.matches && e.target.matches('#till-bill, #till-cash')) drawerShut();
});
document.addEventListener('focusin', (e) => {
  if (!e.target.matches || !e.target.matches('#till-bill, #till-cash')) return;
  // the fingers of a haul lifting can land as a tap in the box: no cursor, and the drawer stays where it was left
  if (DR.haul || DR.eat === 'haul') return e.target.blur();
  if (!DR.drag) drawerShut();
});
// on its side there's no drawer: turning the phone shuts it at once
addEventListener('resize', () => {
  if ((DR.open || DR.h > 0) && MQ.land.matches && !MQ.reg.matches) {
    drawerReset();
    drawerSet(0);
    const hd = $('tillHdl');
    if (hd) {
      hd.classList.remove('on');
      hd.setAttribute('aria-expanded', 'false');
      hd.setAttribute('aria-label', 'Open till drawer');
    }
  }
});
