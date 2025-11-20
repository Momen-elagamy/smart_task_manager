/**
 * Enhanced Service Worker for Progressive Web App
 * Features: Offline support, background sync, push notifications
 */

const CACHE_VERSION = 'v2.0.0';
const CACHE_NAME = `smart-task-manager-${CACHE_VERSION}`;

// Assets to cache
const STATIC_ASSETS = [
    '/',
    '/dashboard/',
    '/tasks/',
    '/projects/',
    '/chat/',
    '/static/css/main.css',
    '/static/css/theme.css',
    '/static/js/main.js',
    '/static/js/api.js',
    '/static/js/chat.js',
    '/static/js/theme.js',
];

self.addEventListener('install', event => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(STATIC_ASSETS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    if (request.method !== 'GET') return;
    
    // API requests - network first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(request))
        );
        return;
    }
    
    // Static assets - cache first
    event.respondWith(
        caches.match(request)
            .then(response => response || fetch(request))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(cacheName => cacheName !== CACHE_NAME)
                          .map(cacheName => caches.delete(cacheName))
            );
        }).then(() => self.clients.claim())
    );
});

// Push notifications
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const options = {
        body: data.body || 'New notification',
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png',
        vibrate: [200, 100, 200],
    };
    event.waitUntil(
        self.registration.showNotification(data.title || 'Smart Task Manager', options)
    );
});

// Notification click
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data || '/dashboard/')
    );
});