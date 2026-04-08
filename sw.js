const CACHE_NAME = 'peters-site-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/LOVE.jpg',
    '/NANCY.jpeg',
    '/AKUA.jpeg',
    '/BARTHO.jpeg',
    '/HARUNA.jpeg',
    '/NDEOGO.jpeg',
    '/MICHEAL.jpeg',
    '/EKUA.jpeg',
    '/SANJA.jpeg',
    '/GHANA.jpeg',
    '/PROF.jpeg',
    '/TAILOR.jpeg',
    '/ANDAM.jpeg',
    '/ESMI.jpeg',
    '/AKUA_GHANA.jpeg',
    '/HARUNA_SEIBA.jpeg',
    '/NANA_FOSU_US.jpeg',
    '/EMERITUS_KOJO_POLY.jpeg'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            if (response) {
                return response;
            }
            return fetch(event.request);
        })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
});
