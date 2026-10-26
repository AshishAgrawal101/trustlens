'use strict';
(async () => {
  const status = document.getElementById('share-status'), button = document.getElementById('try-share');
  const worker = navigator.serviceWorker?.controller;
  if (!worker) { status.textContent = 'The offline receiver is not controlling this page. Return to Pocket, prepare offline access, then reopen this demo.'; return; }
  const channel = new MessageChannel(); let timer;
  try {
    const response = await new Promise((resolve, reject) => {
      timer = setTimeout(() => reject(new Error('Receiver did not respond')), 5000);
      channel.port1.onmessage = event => resolve(event.data);
      worker.postMessage({type:'POCKET_STATUS'}, [channel.port2]);
    });
    if (response?.cache !== document.getElementById('pocket-version').getAttribute('content') || response.ready !== true) throw new Error('Current receiver is not ready');
    status.textContent = 'Current offline receiver verified. The example will be handled on this device; nothing has been analyzed yet.';
    button.disabled = false;
  } catch { status.textContent = 'The current offline receiver is not ready. Return to Pocket and prepare it again before trying this demo.'; }
  finally { clearTimeout(timer); channel.port1.close(); channel.port2.close(); }
})();
