// Holography Bench service worker: keeps the simulators available offline after the first visit.
// Change VERSION whenever a file in site/ changes, so installed copies pick up the update.
const VERSION = "holobench-v1.1.0";
const FILES = ["./", "index.html", "inline.html", "offaxis.html", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png"];

self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES))); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== VERSION).map(x => caches.delete(x))))
    .then(() => self.clients.claim()));
});
// pages: network first (updates arrive when online); other files: cache first
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  if (req.mode === "navigate") {
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(VERSION).then(x => x.put(req, c)); return r; })
      .catch(() => caches.match(req).then(h => h || caches.match("index.html"))));
    return;
  }
  e.respondWith(caches.match(req).then(h => h || fetch(req)));
});
