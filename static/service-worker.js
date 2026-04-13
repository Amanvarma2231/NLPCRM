const CACHE_NAME = 'nlpcrm-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/dashboard',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/test_screens/dashboard.png',
    '/manifest.json'
];

// Install Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Service Worker: Caching critical assets');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate & Cleanup old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('Service Worker: Clearing old cache');
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Stale-While-Revalidate Strategy
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                // Update cache with the new response
                if (networkResponse && networkResponse.status === 200) {
                    const cacheCopy = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, cacheCopy);
                    });
                }
                return networkResponse;
            }).catch(() => {
                // Offline fallback if needed
                console.log('Fetch failed, serving from cache if available');
            });

            return cachedResponse || fetchPromise;
        })
    );
});
