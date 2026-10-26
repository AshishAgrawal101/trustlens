'use strict';
// Used by the service worker and bounded unit tests. Shared text never becomes a URL or cache entry.
async function receiveSharedText(request) {
  if (request.headers.get('content-type')?.split(';')[0].trim().toLowerCase() !== 'application/x-www-form-urlencoded') throw new Error('Share plain text, or paste it into the guide.');
  if (!request.body) throw new Error('No shared text was received.');
  const reader = request.body.getReader(), chunks = []; let bytes = 0;
  try {
    while (true) {
      const {value, done} = await reader.read(); if (done) break;
      bytes += value.length;
      if (bytes > 256000) { await reader.cancel(); throw new Error('This share is too large. Paste a shorter excerpt.'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const buffer = new Uint8Array(bytes); let offset = 0;
  chunks.forEach(chunk => { buffer.set(chunk, offset); offset += chunk.length; });
  const params = new URLSearchParams(new TextDecoder('utf-8', {fatal:true}).decode(buffer));
  if ([...params.keys()].some(key => !['title', 'text', 'url'].includes(key)) || ['title', 'text', 'url'].some(key => params.getAll(key).length > 1)) throw new Error('Unsupported share format. Paste the message instead.');
  const text = ['title', 'text', 'url'].map(key => params.get(key) || '').filter(Boolean).join('\n\n');
  if (!text.trim() || text.length > 30000) throw new Error('Share between 1 and 30,000 characters.');
  return text;
}
function sharedPage(shell, text) {
  const escaped = text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  if (!shell.includes(' data-share-slot></textarea>')) throw new Error('The offline page needs an update. Open the guide and prepare it again.');
  return shell.replace(' data-share-slot></textarea>', () => ' data-shared="true">' + escaped + '</textarea>');
}
if (typeof module !== 'undefined') module.exports = {receiveSharedText, sharedPage};
