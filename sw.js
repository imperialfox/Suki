const CACHE = 'suki-shell-v5';
const SHELL = ['./','./index.html','./styles.css','./enhancements.css','./app.js','./enhancements.js','./manifest.json','./icon.svg','./icon-512.png','./apple-touch-icon.png'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      try {
        const response = await fetch(request, { signal: controller.signal });
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put('./index.html', copy));
        }
        return response;
      } catch {
        return await caches.match('./index.html') || await caches.match('./');
      } finally {
        clearTimeout(timeout);
      }
    })());
    return;
  }
  event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(response => {
    if (response.ok && SHELL.some(path => url.pathname.endsWith(path.replace('./','')))) {
      const copy = response.clone();
      caches.open(CACHE).then(cache => cache.put(request, copy));
    }
    return response;
  }).catch(() => caches.match('./index.html'))));
});
