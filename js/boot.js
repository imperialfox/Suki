/* Suki · boot.js
   Starts the app: loads saved data behind the launch screen, draws Home, then lets the launch screen go.
   Always the last file.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const BOOT = { t0: performance.now(), MIN: 600, CAP: 2500 };
async function boot() {
  SCR.mark($('splash'), 'overlay:launch');
  layout();
  F.home = loadDraft();
  loadSmart();
  if (F.home.item || F.home.price || F.home.notes || F.home.location) U.more = !!(F.home.location || F.home.notes || F.home.venue);
  // load, but never keep the launch screen up longer than about 2.5 s. Saves wait for it either way (Q31)
  const loading = loadData().catch(() => {});
  await Promise.race([loading, new Promise((r) => setTimeout(r, BOOT.CAP))]);
  convFrom('gbp');
  render();
  // still loading: Home says so, and the open tab redraws when the data lands (Q31)
  if (!READY) loading.then(dataLanded);
  const wait = MOTION.speed() === 0 ? 0 : Math.max(0, BOOT.MIN - (performance.now() - BOOT.t0));
  setTimeout(() => {
    const s = $('splash');
    if (!s) return onboardStart();
    if (MOTION.speed() === 0) {
      s.remove();
      return onboardStart();
    }
    s.classList.add('out');
    setTimeout(() => s.remove(), MOTION.reduced() ? 220 : 420);
    // the welcome sheet rises as the launch screen fades (Q07)
    setTimeout(onboardStart, MOTION.reduced() ? 200 : 300);
  }, wait);
  autoRate();
  fixRates();
  checkStorage();
  registerSW();
}

// the data has landed after the launch screen went: redraw, but not under an open sheet or a box being typed in,
// where it waits (saving from either redraws anyway). If loading failed, Home keeps its loading line (Q31)
function dataLanded() {
  if (!READY) return;
  const ae = document.activeElement;
  if (U.sheet || (ae && ae.matches && ae.matches('input,textarea,select'))) return setTimeout(dataLanded, 300);
  convFrom(U.conv.last || 'gbp');
  rerender();
}

/* ===== Settings › About details ===== */
function checkStorage() {
  if (!(navigator.storage && navigator.storage.estimate)) return (STORAGE_USED = 'Not shown by this browser');
  navigator.storage
    .estimate()
    .then((i) => {
      const u = i.usage || 0;
      STORAGE_USED = u < 1048576 ? Math.max(1, Math.round(u / 1024)) + ' KB' : (u / 1048576).toFixed(1) + ' MB';
    })
    .catch(() => (STORAGE_USED = 'Not shown by this browser'))
    .then(() => {
      const e = $('storageUsed');
      if (e) e.textContent = STORAGE_USED;
    });
}
function registerSW() {
  const show = (t) => {
    SW_STATE = t;
    const e = $('swStatus');
    if (e) e.textContent = t;
  };
  const local = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
  if (!('serviceWorker' in navigator) || !(location.protocol === 'https:' || local)) return show('Not available here');
  navigator.serviceWorker
    .register('sw.js')
    .then((reg) => {
      show(navigator.serviceWorker.controller || reg.active ? 'Ready' : 'Getting ready…');
      navigator.serviceWorker.ready.then(() => show('Ready'));
    })
    .catch(() => show('Not available right now'));
}
boot();
