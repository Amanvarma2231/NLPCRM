// Service Worker for NLPCRM (Placeholder)
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installed');
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activated');
});

self.addEventListener('fetch', (event) => {
    // Basic pass-through
    event.respondWith(fetch(event.request));
});
