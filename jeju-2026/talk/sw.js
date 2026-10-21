// 단톡방 바로가기 설치용 서비스 워커: 저장 없이 항상 네트워크에서 가져옵니다.
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (e) { e.respondWith(fetch(e.request)); });
