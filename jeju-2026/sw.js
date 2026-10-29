// 바로가기 설치용 서비스 워커: 항상 최신 내용을 네트워크에서 가져옵니다.
// 페이지·글자 파일은 폰의 임시 저장본(최대 10분)을 건너뛰고 매번 새로 받아, 고친 내용이 바로 보이게 합니다.
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  var fresh = req.mode === 'navigate' || (url.origin === self.location.origin && /\.(html|txt|json|webmanifest)$|\/$/.test(url.pathname));
  e.respondWith((fresh ? fetch(req.url, { cache: 'no-store', credentials: 'same-origin' }) : fetch(req)).catch(function () { return new Response('오프라인입니다. 인터넷에 연결한 뒤 다시 열어주세요.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } }); }));
});
// 새 안내 알림을 누르면 앱의 안내 탭을 연다
self.addEventListener('notificationclick', function (e) {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window' }).then(function (cs) {
    for (var i = 0; i < cs.length; i++) if ('focus' in cs[i]) { cs[i].navigate('./#prep'); return cs[i].focus(); }
    return self.clients.openWindow('./#prep');
  }));
});
