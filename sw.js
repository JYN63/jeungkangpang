// 증강팡 서비스 워커: 게임 파일을 저장해 두고(오프라인에서도 실행), 인터넷이 되면 게임 화면은 늘 새 버전으로
const CACHE = 'jkp-v36';
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png", "fonts/fonts.css"];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const mine = url.origin === location.origin, font = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!mine && !font) return;   // 랭킹(Firebase) 같은 바깥 요청은 저장하지 않고 그대로 보낸다
  if (mine && /version\.json$/.test(url.pathname)) return;   // 새 버전 확인은 늘 서버에 직접
  if (req.mode === 'navigate' || (mine && /\/(index\.html)?$/.test(url.pathname))) {
    // 게임 화면은 새 버전부터: 인터넷이 되면 바로 새로 받고(3초 넘으면 저장본), 안 되면 저장본으로
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = await c.match('index.html');
      const net = fetch(req, {cache: 'no-cache'}).then(res => { if (res && res.ok) c.put('index.html', res.clone()); return res; });
      if (!hit) return net;
      return Promise.race([net.catch(() => hit), new Promise(r => setTimeout(() => r(hit), 3000))]);
    }));
    return;
  }
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(req, {ignoreSearch: true});
    const net = fetch(req).then(res => { if (res && (res.ok || res.type === 'opaque')) c.put(req, res.clone()); return res; }).catch(() => hit);
    return hit || net;   // 아이콘·글꼴은 저장된 걸 바로 쓰고, 뒤에서 새로 받아 둔다
  }));
});
