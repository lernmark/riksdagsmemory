const CACHE_NAME = 'rd-memory-v1';
// Vi cachar bara lokala filer till att börja med för att undvika "Failed to fetch"
const ASSETS = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // Vi använder addAll men fångar upp fel per fil
      return Promise.all(
        ASSETS.map(url => {
          return cache.add(url).catch(err => console.warn(`Kunde inte cacha: ${url}`, err));
        })
      );
    })
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(res => {
      return res || fetch(e.request).then(response => {
        // Valfritt: Här kan du dynamiskt cacha externa filer när de väl hämtas
        return response;
      });
    })
  );
});
