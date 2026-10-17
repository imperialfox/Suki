const CACHE = 'suki-shell-v3';
const SHELL = ['./','./index.html','./styles.css','./app.js','./manifest.json','./icon.svg'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r=e.request; if(r.method!=='GET') return; const u=new URL(r.url); if(u.origin!==self.location.origin)return;
  e.respondWith(caches.match(r).then(cached=>cached||fetch(r).then(res=>{if(res.ok&&(r.mode==='navigate'||SHELL.some(p=>u.pathname.endsWith(p.replace('./',''))))){const copy=res.clone();caches.open(CACHE).then(c=>c.put(r,copy));}return res;}).catch(()=>caches.match('./index.html'))));
});
