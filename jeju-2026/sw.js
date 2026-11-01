// 가이드북 서비스 워커 (11/1 개편): 링크를 누르면 언제나 바로 열리게
// - 페이지(index.html)는 먼저 인터넷에서 새로 받고, 4초 안에 안 오거나 실패하면 폰에 저장해 둔 마지막 판을 즉시 보여준다.
// - 새로 받은 판은 저장해 두어 다음에 끊겨도 열린다.
// - 오류 코드(503)를 돌려주지 않는다: 카톡 안 브라우저가 '해당 페이지를 찾을 수 없습니다'로 바꿔 버리기 때문.
var CACHE = 'jeju-2026-v2';
var PAGE = './';
self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.add(new Request(PAGE, { cache: 'reload' })); }).catch(function () {}));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); }));
});
function retryPage() {
  var html = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>제주 부부수양회 가이드북</title><body style="margin:0;font-family:sans-serif;background:#fdf8ec;color:#1d2b6b;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center">' +
    '<div style="padding:24px"><h2>가이드북을 여는 중입니다…</h2><p>인터넷 연결이 잠시 약합니다.<br>자동으로 다시 시도합니다.</p>' +
    '<p><button onclick="location.reload()" style="font-size:18px;padding:14px 28px;border:0;border-radius:12px;background:#d0135f;color:#fff;font-weight:800">다시 열기</button></p></div>' +
    '<script>setTimeout(function(){location.reload()},3000)</script></body>';
  return new Response(html, { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' } });
}
function isPage(req, url) {
  return req.mode === 'navigate' || (url.origin === self.location.origin && /\/jeju-2026\/(index\.html)?$/.test(url.pathname));
}
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;  // 바깥 주소(날씨·지도 등)는 브라우저가 직접
  if (isPage(req, url)) {
    e.respondWith(new Promise(function (resolve) {
      var done = false, cached = null;
      var finish = function (r) { if (!done && r) { done = true; resolve(r); } };
      caches.open(CACHE).then(function (c) { return c.match(PAGE); }).then(function (r) { cached = r || null; }).catch(function () {});
      var net = fetch(req.url, { cache: 'no-store', credentials: 'same-origin' }).then(function (r) {
        if (r && r.ok) {
          var copy = r.clone();
          caches.open(CACHE).then(function (c) { return c.put(PAGE, copy); }).catch(function () {});
          finish(r);
        } else return fetch(req).then(function (r2) { finish(r2 && r2.ok ? r2 : (cached || r2)); });
      }).catch(function () {
        return fetch(req).then(function (r2) { finish(r2.ok ? r2 : cached || retryPage()); }).catch(function () { finish(cached || retryPage()); });
      });
      // 4초 안에 안 오면 저장된 판을 먼저 보여 준다 (새 판은 받는 대로 저장 → 다음에 열 때 반영)
      setTimeout(function () { if (cached) finish(cached.clone()); }, 4000);
      // 15초가 지나도 아무것도 없으면 다시 열기 화면
      setTimeout(function () { finish(retryPage()); }, 15000);
      net.catch(function () {});
    }));
    return;
  }
  var fresh = /\.(txt|json|webmanifest)$/.test(url.pathname);
  if (fresh) e.respondWith(fetch(req.url, { cache: 'no-store', credentials: 'same-origin' }).catch(function () { return fetch(req); }));
  // 그림·음악 등은 브라우저 기본 동작
});
// 새 안내 알림을 누르면 앱의 안내 탭을 연다
self.addEventListener('notificationclick', function (e) {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window' }).then(function (cs) {
    for (var i = 0; i < cs.length; i++) if ('focus' in cs[i]) { cs[i].navigate('./#prep'); return cs[i].focus(); }
    return self.clients.openWindow('./#prep');
  }));
});
