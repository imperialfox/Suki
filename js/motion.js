/* Suki · motion.js (Suki's own helpers on the parts kit's springs; the kit runs the motion since Q27, D18)
   ===== Motion: Suki's helpers, on the parts kit's springs =====
   Everything that moves uses these, so the whole app feels made by the same hand.
   - Springs come from the parts kit (Parts.motion, js/parts-kit.js): gentle (rows, capsules, fades), nav (pushes,
     swiping back), ripple (peeks, small pops) and the kit's own (press, release, snap, sheet …). The kit publishes them
     on <html> as --ease-<name> / --dur-<name>, and only the kit writes those, --pk-speed, .motion-off and
     .motion-reduced. A spring that differs from the kit's is a line in js/parts.settings.js (springs: {…}) with its
     decision ID; there are none today. JS uses MOTION.animate().
   - Stagger: words 30 ms apart, rows 45 ms, chart bars 30 ms.
   - EASE (Q26): pop, knob and out, the fixed curves for a timed move, matching app.css's --ease-pop/-knob/-out.
   - Land and leave (Q11; land was "settle" until Q27, S02): how a row arrives in a list and how it goes.
   - Reduce Motion (the iOS setting, or forced on or off in Settings › Accessibility): the kit's
     Parts.motion.setReduced. This device's choice is kept in localStorage 'suki:reduceMotion' ('on' / 'off', absent
     = Match iPhone) and handed to the kit at start-up, because the kit doesn't save it. Its fades are the kit's
     --dur-reduced (100 ms, D20): reducedMs().
   - Speed: 1 normally, 4 for slow motion while tuning, 0 for motion off (the tests use 0): Parts.motion.setSpeed,
     kept in localStorage 'suki:motion', never in backups.
   - Distance blur: kept from Vocal Sessions for later use; Suki doesn't use it yet. */
const MOTION = (() => {
  const PM = Parts.motion;
  // the springs in use (the kit's, with any of the app's springs: {…} lines on top)
  const SPRINGS = PM.springs();
  const STAGGER = { word: 30, row: 45, bar: 30 };
  // fixed curves for a timed move that isn't a spring: the same three as app.css's --ease-pop, --ease-knob and
  // --ease-out (Q26). Don't write a new cubic-bezier( in code: use one of these or a spring (tests/test_values.py)
  const EASE = { pop: 'cubic-bezier(.3,1.7,.45,1)', knob: 'cubic-bezier(.3,1.35,.5,1)', out: 'cubic-bezier(.2,.8,.2,1)' };
  const BLUR_MAX = 1.5; // px. Ivan chose 1.5 over 2 so far lyrics stay recognisable
  const KEY = 'suki:motion';
  const RKEY = 'suki:reduceMotion'; // auto (match iPhone), on or off. This device only, never in backups
  const curve = PM.curve;
  const C = {};
  Object.keys(SPRINGS).forEach((k) => (C[k] = curve(SPRINGS[k].z, SPRINGS[k].f)));

  // this device's choices, handed to the kit at start-up (the kit doesn't save them)
  const read = (k) => {
    try {
      return localStorage.getItem(k);
    } catch (e) {
      return null;
    }
  };
  let rpref = 'auto';
  function load() {
    const s = read(KEY);
    PM.setSpeed(s !== null && !isNaN(+s) ? Math.max(0, Math.min(8, +s)) : 1);
    const r = read(RKEY);
    rpref = r === 'on' || r === 'off' ? r : 'auto';
    PM.setReduced(rpref === 'on' ? true : rpref === 'off' ? false : null);
  }
  load();

  const speed = () => PM.speed();
  const reduced = () => PM.reduced();
  const on = () => PM.on();
  const dur = (name) => (C[name] ? C[name].ms : C.gentle.ms) * speed();
  const ease = (name) => (C[name] || C.gentle).ease;
  // the delay for item i, for MOTION.animate's delay (which applies the speed itself, so this doesn't)
  const stagger = (i, kind) => i * (STAGGER[kind] || STAGGER.row);
  // a named duration from the stylesheet (--dur-close and the like) in ms, before the speed
  const ms = (name, dflt) => {
    const m = /^([\d.]+)(ms|s)$/.exec(getComputedStyle(document.documentElement).getPropertyValue(name).trim());
    return m ? +m[1] * (m[2] === 's' ? 1000 : 1) : dflt;
  };
  // (D20) the kit's Reduce Motion fade (--dur-reduced, 100 ms) in ms, before the speed: every fade that replaces
  // movement under Reduce Motion uses it
  const reducedMs = () => ms('--dur-reduced', 100);

  // the kit writes the CSS variables and classes; this re-reads this device's choices and asks it to
  function publish() {
    load();
  }
  function setSpeed(n) {
    const v = Math.max(0, Math.min(8, +n || 0));
    try {
      if (v === 1) localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, String(v));
    } catch (e) {}
    PM.setSpeed(v);
  }
  function setReduce(v) {
    rpref = v === 'on' || v === 'off' ? v : 'auto';
    try {
      if (rpref === 'auto') localStorage.removeItem(RKEY);
      else localStorage.setItem(RKEY, rpref);
    } catch (e) {}
    PM.setReduced(rpref === 'on' ? true : rpref === 'off' ? false : null);
  }

  // el.animate on a spring. With motion off or Reduce Motion it jumps to the end (or fades, if asked)
  function animate(el, frames, o) {
    o = o || {};
    if (!el || !el.animate) return null;
    if (!on()) {
      if (reduced() && o.fade && speed() > 0)
        return el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: reducedMs() * speed(), easing: 'ease-out' });
      return null;
    }
    const name = o.spring || 'gentle';
    return el.animate(frames, {
      duration: o.ms ? o.ms * speed() : dur(name),
      delay: (o.delay || 0) * speed(),
      easing: o.ms ? o.easing || EASE.out : ease(name),
      fill: o.fill || 'none',
    });
  }

  // "Land" (Q11; "settle" until Q27, S02, so --ease-settle means only the kit's spring): Suki's own movement, a small
  // drop into place like a coin set down on a counter. Kept for things that land: a saved purchase arriving in its
  // list (12 px), and the Till's notes and coins (Q13, 10 px). i staggers them 45 ms apart. Reduce Motion: a fade.
  // Motion off: nothing.
  function land(el, i, drop) {
    return animate(el, [{ transform: 'translateY(-' + (drop || 12) + 'px)', opacity: 0 }, { transform: 'none', opacity: 1 }], { spring: 'ripple', delay: stagger(i || 0, 'row'), fill: 'backwards', fade: true });
  }
  // something going away where it was: it fades and shrinks to .94 in 220 ms (a row), or to `to` in `ms` (the Till's
  // notes and coins: .6 in 160 ms); only fades with Reduce Motion (the kit's --dur-reduced).
  // Returns the animation (null with motion off), ending on its last frame so the caller can remove the element.
  function leave(el, ms, to) {
    const sp = speed();
    if (!el || !el.animate || sp === 0) return null;
    if (reduced()) return el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: reducedMs() * sp, easing: 'ease-out', fill: 'forwards' });
    return el.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(' + (to || 0.94) + ')' }], { duration: (ms || 220) * sp, easing: 'ease-in', fill: 'forwards' });
  }

  // a spring that starts moving: from and to are {x, y, …} in px, v is the finger's speed in px/s (3.12, the floating
  // window's corner snap). o: {spring, frame(p), done()}. Returns a function that stops it. With motion off it jumps.
  function spring(from, to, v, o) {
    o = o || {};
    let stop = false;
    if (!on()) {
      if (o.frame) o.frame(to);
      if (o.done) o.done();
      return () => {};
    }
    const s = SPRINGS[o.spring] || SPRINGS.gentle,
      w = 2 * Math.PI * s.f,
      wd = w * Math.sqrt(1 - s.z * s.z),
      T = Math.log(500) / (s.z * w);
    const ax = Object.keys(to).map((k) => {
      const A = from[k] - to[k];
      return { k, A, B: (((v && v[k]) || 0) + s.z * w * A) / wd };
    });
    const t0 = performance.now();
    const step = (now) => {
      if (stop) return;
      const t = (now - t0) / 1000 / speed(),
        e = Math.exp(-s.z * w * t),
        p = {};
      let left = 0;
      ax.forEach((a) => {
        p[a.k] = to[a.k] + e * (a.A * Math.cos(wd * t) + a.B * Math.sin(wd * t));
        left = Math.max(left, e * (Math.abs(a.A) + Math.abs(a.B)));
      });
      if (t >= T || left < 0.3) {
        if (o.frame) o.frame(to);
        if (o.done) o.done();
        return;
      }
      if (o.frame) o.frame(p);
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    return () => (stop = true);
  }
  /* The iOS way (Q19, the till drawer), from Apple's "Designing Fluid Interfaces" and "Animate with springs":
     - iosSpring(duration, bounce): SwiftUI's spring(duration:bounce:) in this file's terms, {z, f} like SPRINGS.
       Frequency = 1 / duration, damping ratio = 1 - bounce. Bounce 0 settles with no overshoot.
     - project(v): how far something coasts at v pt/s with iOS's fast deceleration (0.99), to decide where it settles.
     - rubber(x, dim): iOS's stretch past an end: x pt of finger gives this much movement, never more than dim. */
  const iosSpring = (duration, bounce) => ({ z: 1 - bounce, f: 1 / duration });
  const DECEL = 0.99;
  const project = (v) => ((v / 1000) * DECEL) / (1 - DECEL);
  const rubber = (x, dim) => dim * (1 - 1 / ((x * 0.55) / dim + 1));

  /* Home's Log card switching sides (Q14), after iPhone Duo's fold. The card stays put and only its contents change.
     One thing is the hinge, the box you type in: it slides from its old spot to its new one. Everything else dissolves
     through a blur that grows with distance from the hinge (cubic), rows 28 ms apart, and the new side resolves out of
     blur and slight dimness, rows 45 ms apart. Only rows are blurred, never the card. Reduce Motion: a plain
     crossfade. Motion off: nothing. A switch mid-way removes the copy at once (smart.js), so nothing is left behind.
     If frames drop badly during a fold (over 120 ms between two, twice), later folds use the crossfade. */
  let foldLite = false;
  function foldRows(face) {
    const out = [];
    [...face.children].forEach((c) => {
      if (c.id === 'smartOut' || c.id === 'smartSugg' || c.classList.contains('more')) out.push(...c.children);
      else out.push(c);
    });
    return out.filter((el) => el.getBoundingClientRect().height > 0);
  }
  function fold(wrap, ghost, neu) {
    const k = speed();
    if (!ghost || !neu || !neu.animate || k === 0) return;
    const gone = () => ghost.isConnected && ghost.remove();
    wrap.appendChild(ghost);
    if (reduced() || foldLite) {
      const rm = reducedMs() * k;
      ghost.animate([{ opacity: 1 }, { opacity: 0 }], { duration: rm, easing: 'ease-out', fill: 'forwards' }).onfinish = gone;
      neu.animate([{ opacity: 0 }, { opacity: 1 }], { duration: rm, easing: 'ease-out', fill: 'backwards' });
      setTimeout(gone, rm + 300);
      return;
    }
    const hingeOf = (face) => face.querySelector('textarea, input'),
      oldH = hingeOf(ghost),
      newH = hingeOf(neu),
      span = Math.max(1, wrap.offsetHeight),
      blurAt = (el, h) => {
        const d = Math.min(1, Math.abs(el.getBoundingClientRect().top - h.getBoundingClientRect().top) / span);
        return 1 + 9 * d * d * d + 3 * d;
      };
    if (oldH && newH) {
      const a = oldH.getBoundingClientRect(),
        b = newH.getBoundingClientRect();
      newH.animate([{ transform: 'translateY(' + (a.top - b.top) + 'px)' }, { transform: 'none' }], { duration: 420 * k, easing: 'cubic-bezier(.3,1.25,.5,1)' });
      oldH.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 120 * k, delay: 60 * k, fill: 'forwards' });
    }
    const hOld = oldH && oldH.closest('.fld');
    const rowsOld = foldRows(ghost);
    rowsOld.forEach((el, i) => {
      if (el === oldH || el === hOld) {
        [...el.children].forEach((c) => c !== oldH && c.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 140 * k, fill: 'forwards' }));
        return;
      }
      const bl = oldH ? blurAt(el, oldH) : 4;
      el.animate([{ opacity: 1, filter: 'blur(0px)', transform: 'none' }, { opacity: 0, filter: 'blur(' + bl.toFixed(1) + 'px)', transform: 'translateY(-3px) scale(.985)' }], { duration: 240 * k, delay: i * 28 * k, easing: 'ease-in', fill: 'forwards' });
    });
    const ms = (rowsOld.length * 28 + 300) * k;
    setTimeout(gone, ms);
    const hNew = newH && newH.closest('.fld');
    foldRows(neu).forEach((el, i) => {
      if (el === newH || el === hNew) {
        if (el !== newH) [...el.children].forEach((c) => c !== newH && c.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 260 * k, delay: 140 * k, fill: 'backwards' }));
        return;
      }
      const bl = newH ? blurAt(el, newH) : 4;
      el.animate([{ opacity: 0, filter: 'blur(' + bl.toFixed(1) + 'px) brightness(.82)', transform: 'translateY(5px)' }, { opacity: 1, filter: 'blur(0px) brightness(1)', transform: 'none' }], { duration: 440 * k, delay: (110 + i * 45) * k, easing: EASE.out, fill: 'backwards' });
    });
    // watch the frames while it plays; two long gaps and the next fold is a crossfade
    let last = performance.now(),
      slow = 0;
    const end = last + ms;
    const tick = (now) => {
      if (now - last > 120) slow++;
      last = now;
      if (slow >= 2) foldLite = true;
      else if (now < end && ghost.isConnected) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  // distance blur: d is how many lines away from the focus (0 = in focus)
  const blur = (d) => (d <= 0 || reduced() ? 0 : +((BLUR_MAX * Math.min(d, 5)) / 5).toFixed(2));
  const dim = (d) => (d <= 0 ? 1 : +Math.max(0.3, 0.55 - 0.05 * d).toFixed(2));
  const dimLabel = (d) => (d <= 0 ? 1 : +Math.max(0.45, 0.7 - 0.05 * d).toFixed(2)); // labels only dim, never blur

  return {
    SPRINGS,
    STAGGER,
    EASE,
    BLUR_MAX,
    curve,
    on,
    reduced,
    dur,
    ease,
    stagger,
    animate,
    land,
    reducedMs,
    ms,
    leave,
    fold,
    spring,
    iosSpring,
    project,
    rubber,
    setSpeed,
    setReduce,
    reducePref: () => rpref,
    speed,
    publish,
    blur,
    dim,
    dimLabel,
  };
})();
