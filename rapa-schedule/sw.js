const C='rsch-v2',F=['./','index.html','events.json','manifest.webmanifest','icon-192.png','icon-512.png','apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(F)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith('rsch-')&&x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
// 네트워크 우선: 인터넷이 되면 항상 새 파일(특히 events.json)을 받고, 안 될 때만 저장본을 보여준다.
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);e.respondWith(fetch(e.request).then(r=>{if(r.ok&&u.origin===location.origin){const c=r.clone();caches.open(C).then(x=>x.put(u.pathname.endsWith('events.json')?'events.json':e.request,c))}return r}).catch(()=>caches.match(u.pathname.endsWith('events.json')?'events.json':e.request).then(r=>r||caches.match('index.html'))))});
