/* Suki · locate.js
   Location when logging (Q16):
   - A new purchase's Location starts as the place of the newest purchase that day that has one (dayTown).
   - The arrow inside Location fills the town you're in (ACT.locate). The position is read once, on the tap, and
     compared with the town outlines in towns.js on the phone: nothing is sent anywhere, and it works offline.
   Plain script (not a module), loaded after events.js. */

// how far from the nearest town outline still counts as "near you" (on a beach, a boat, a bridge)
const NEAR_KM = 40;
const LOC_MSG = {
  off: 'Location is off for Suki. Type the town, or allow it in Settings.',
  none: 'No town found near you. Type it in instead.',
  fail: 'Couldn’t find where you are. Type the town in instead.',
};

/* ===== The town from that day ===== */
// the newest purchase on that day with a place (purchases are kept newest first)
function townOn(day) {
  const p = D.purchases.find((x) => x.date === day && String(x.location || '').trim());
  return p ? String(p.location).trim() : '';
}
// v.locFrom: 'auto' (filled from that day), 'near' (the arrow) or 'typed' (his own, so Suki stops filling it in).
// An auto-filled place follows the data: it's worked out again on every draw, so it's never stale.
function dayTown(v) {
  if (v.locFrom === 'near' || v.locFrom === 'typed') return;
  if (!v.locFrom && String(v.location || '').trim()) return; // a place already there that Suki didn't fill
  const t = townOn(isoDate(v.date) || localISO());
  if (t) {
    v.location = t;
    v.locFrom = 'auto';
  } else if (v.locFrom === 'auto') {
    v.location = '';
    delete v.locFrom;
  }
}
// the few words after "Location" saying where the place came from
function locSource(v) {
  if (!String(v.location || '').trim()) return '';
  if (v.locFrom === 'near') return 'near you';
  if (v.locFrom === 'auto') return (isoDate(v.date) || localISO()) === localISO() ? 'from earlier today' : 'from that day';
  return '';
}

/* ===== The town you're in ===== */
// towns.js holds encoded polylines; they're read into numbers the first time the arrow is tapped
let TOWNS = null;
function decodeRing(s) {
  const pts = [];
  let i = 0,
    lat = 0,
    lng = 0;
  const next = () => {
    let b,
      shift = 0,
      r = 0;
    do {
      b = s.charCodeAt(i++) - 63;
      r |= (b & 0x1f) << shift;
      shift += 5;
    } while (b >= 0x20 && i <= s.length);
    return r & 1 ? ~(r >> 1) : r >> 1;
  };
  while (i < s.length) {
    lat += next();
    lng += next();
    pts.push(lat / 1e3, lng / 1e3);
  }
  return pts;
}
function towns() {
  if (TOWNS) return TOWNS;
  const src = (window.sukiTowns && window.sukiTowns.towns) || [];
  TOWNS = [];
  src.forEach((t) =>
    t[2].forEach((s) => {
      const p = decodeRing(s);
      if (p.length < 8) return;
      let a = 0,
        bb = [90, 180, -90, -180];
      for (let k = 0, j = p.length - 2; k < p.length; j = k, k += 2) {
        a += p[j + 1] * p[k] - p[k + 1] * p[j];
        bb = [Math.min(bb[0], p[k]), Math.min(bb[1], p[k + 1]), Math.max(bb[2], p[k]), Math.max(bb[3], p[k + 1])];
      }
      TOWNS.push({ name: t[0], p, bb, area: Math.abs(a / 2) });
    })
  );
  return TOWNS;
}
function inRing(lat, lng, p) {
  let c = false;
  for (let k = 0, j = p.length - 2; k < p.length; j = k, k += 2)
    if (p[k] > lat !== p[j] > lat && lng < ((p[j + 1] - p[k + 1]) * (lat - p[k])) / (p[j] - p[k]) + p[k + 1]) c = !c;
  return c;
}
// km from a point to the nearest edge of a ring (flat-earth sums: plenty at this scale)
function kmToRing(lat, lng, p) {
  const kx = 111.32 * Math.cos((lat * Math.PI) / 180),
    ky = 110.57;
  let best = Infinity;
  for (let k = 0, j = p.length - 2; k < p.length; j = k, k += 2) {
    const ax = (p[j + 1] - lng) * kx,
      ay = (p[j] - lat) * ky,
      bx = (p[k + 1] - lng) * kx,
      by = (p[k] - lat) * ky,
      dx = bx - ax,
      dy = by - ay,
      l = dx * dx + dy * dy,
      u = l ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / l)) : 0,
      x = ax + u * dx,
      y = ay + u * dy;
    best = Math.min(best, x * x + y * y);
  }
  return Math.sqrt(best);
}
// the town a position is in; else the nearest one within NEAR_KM; else null
function townAt(lat, lng) {
  if (!isFinite(lat) || !isFinite(lng)) return null;
  const all = towns();
  let hit = null;
  all.forEach((t) => {
    if (lat < t.bb[0] || lat > t.bb[2] || lng < t.bb[1] || lng > t.bb[3]) return;
    if ((!hit || t.area < hit.area) && inRing(lat, lng, t.p)) hit = t; // the smaller one wins: a town inside another
  });
  if (hit) return hit.name;
  const pad = NEAR_KM / 100; // a box well past 40 km, to skip far towns quickly
  let near = null,
    km = NEAR_KM;
  all.forEach((t) => {
    if (lat < t.bb[0] - pad || lat > t.bb[2] + pad || lng < t.bb[1] - pad || lng > t.bb[3] + pad) return;
    const d = kmToRing(lat, lng, t.p);
    if (d <= km) {
      km = d;
      near = t;
    }
  });
  return near ? near.name : null;
}

// the arrow: iPhone asks for permission the first time it's tapped (never at launch)
let locating = false;
ACT.locate = (el) => {
  const form = el.dataset.k,
    v = F[form];
  if (!v || locating) return;
  if (!navigator.geolocation) return toast(LOC_MSG.fail);
  const before = v.location;
  const busy = (on) =>
    document.querySelectorAll('.locbtn[data-k="' + form + '"]').forEach((b) => {
      b.classList.toggle('busy', on);
      if (on) b.setAttribute('aria-busy', 'true');
      else b.removeAttribute('aria-busy');
    });
  // the purchase is still the one he tapped for, and he hasn't typed a place meanwhile
  const same = () => F[form] === v && (form !== 'edit' || U.sheet === 'edit') && !(v.locFrom === 'typed' && v.location !== before);
  locating = true;
  busy(true);
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      locating = false;
      busy(false);
      if (!same()) return;
      const name = townAt(pos.coords.latitude, pos.coords.longitude);
      if (!name) return toast(LOC_MSG.none);
      v.location = name;
      v.locFrom = 'near';
      if (form === 'home') saveDraft(F.home);
      rerender();
      // the box tints briefly, so he sees what changed
      const f = $(form + '-location');
      if (f && f.animate && MOTION.speed() > 0)
        f.animate([{ backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--hl').trim() }, {}], { duration: 700 * MOTION.speed(), easing: 'ease-out' });
    },
    (err) => {
      locating = false;
      busy(false);
      if (!same()) return;
      toast(err && err.code === 1 ? LOC_MSG.off : LOC_MSG.fail);
    },
    { enableHighAccuracy: false, timeout: 15000, maximumAge: 300000 }
  );
};
