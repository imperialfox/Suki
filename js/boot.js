/* Suki · boot.js
   Starts the app: loads saved data behind the launch screen, draws Home, then lets the launch screen go.
   Always the last file.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const BOOT = { t0: performance.now(), MIN: 600, CAP: 2500 };
async function boot() {
  layout();
  F.home = loadDraft();
  if (F.home.item || F.home.price || F.home.notes || F.home.location) U.more = !!(F.home.location || F.home.notes || F.home.venue);
  // load, but never keep the launch screen up longer than about 2.5 s
  await Promise.race([loadData().catch(() => {}), new Promise((r) => setTimeout(r, BOOT.CAP))]);
  convFrom('gbp');
  render();
  const wait = MOTION.speed() === 0 ? 0 : Math.max(0, BOOT.MIN - (performance.now() - BOOT.t0));
  setTimeout(() => {
    const s = $('splash');
    if (!s) return;
    if (MOTION.speed() === 0) return s.remove();
    s.classList.add('out');
    setTimeout(() => s.remove(), MOTION.reduced() ? 220 : 420);
  }, wait);
  autoRate();
  checkStorage();
  registerSW();
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
