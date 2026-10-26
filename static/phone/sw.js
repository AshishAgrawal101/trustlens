'use strict';
importScripts('/phone/share.js');
const CACHE = 'trustlens-pocket-v35';
const SHELL = ['/phone/', '/phone/phone.css', '/phone/guide.js', '/phone/phone.js', '/phone/share.js', '/phone/manifest.webmanifest', '/phone/icon.svg', '/phone/icon-192.png', '/phone/icon-512.png', '/phone/share-demo.html', '/phone/share-demo.js', '/phone/compare.js', '/phone/suggestions.js', '/phone/practice.js', '/phone/ios.js', '/phone/ios.html', '/phone/ios.css', '/phone/context.html', '/phone/workspace/claims.html', '/phone/workspace/numbers.html', '/phone/workspace/quotes.html', '/static/claim-review.css', '/static/claim-review.js', '/static/numbers-context.css', '/static/numbers-context.js', '/static/quote-context.css', '/static/quote-context.js', '/static/source-context.js', '/static/unicode-notice.js'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil((async () => {
  for (const key of await caches.keys()) if (key.startsWith('trustlens-pocket-') && key !== CACHE) await caches.delete(key);
  await self.clients.claim();
})()));
self.addEventListener('message', event => {
  if (event.data?.type !== 'POCKET_STATUS' || !event.ports[0]) return;
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    const ready = (await Promise.all(SHELL.map(url => cache.match(url)))).every(Boolean);
    event.ports[0].postMessage({cache:CACHE, ready});
  })().catch(() => event.ports[0].postMessage({cache:CACHE, ready:false})));
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (event.request.method === 'POST' && url.pathname === '/phone/share') {
    event.respondWith((async () => {
      try {
        const text = await receiveSharedText(event.request);
        const shell = await (await caches.open(CACHE)).match('/phone/');
        if (!shell) throw new Error('Offline access is not ready. Open the guide and paste the message.');
        return new Response(sharedPage(await shell.text(), text), {headers:{'Content-Type':'text/html;charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"}});
      } catch {
        return new Response('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Share not received — TrustLens</title><h1>Share not received</h1><p>The share was empty, too large, unsupported, or offline access was not ready. No message was analyzed or saved.</p><a href="/phone/">Open the guide and paste your message</a></html>', {status:400,headers:{'Content-Type':'text/html;charset=utf-8','Cache-Control':'no-store'}});
      }
    })()); return;
  }
  if (event.request.method !== 'GET' || url.search || !SHELL.includes(url.pathname)) return;
  event.respondWith(caches.open(CACHE).then(async cache => (await cache.match(url.pathname)) || fetch(event.request)));
});
