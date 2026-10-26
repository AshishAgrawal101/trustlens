'use strict';
const byId = id => document.getElementById(id);
let selected = [], installPrompt = null, resultVersion = 0;
function guideAvailable() { return typeof PocketGuide !== 'undefined' && PocketGuide && ['nextSteps', 'hostCoverage', 'summary'].every(key => typeof PocketGuide[key] === 'function'); }
function guideUnavailable() {
  byId('guide-submit').disabled = true;
  byId('share-notice').textContent = 'The local guide could not load. Keep the trusted app reachable and reload, or use the fixed context checks linked above. Your text was not analyzed.';
}
const inputs = () => [...document.querySelectorAll('input[name="request"]')];
function clearResult() {
  resultVersion++;
  selected = [];
  byId('result').hidden = true;
  ['actions', 'hosts', 'host-coverage', 'copy-status', 'result-note'].forEach(id => byId(id).replaceChildren());
}
function clearPrivate() {
  byId('message').value = '';
  byId('message').textContent = '';
  inputs().forEach(input => { input.checked = false; });
  clearResult();
  clearRecovery();
  byId('share-notice').textContent = 'Private text and results cleared. Clipboard content and copies outside this app are not changed.';
}
byId('clear').addEventListener('click', () => { clearPrivate(); byId('message').focus(); });
byId('message').addEventListener('input', clearResult);
inputs().forEach(input => input.addEventListener('change', clearResult));
byId('example').addEventListener('click', () => {
  clearPrivate();
  byId('message').value = 'This is account support. Read me your security code now and keep this call secret.';
  byId('share-notice').textContent = 'Constructed example. Identify the requests yourself; it has not been analyzed automatically.';
  byId('message').focus();
});
byId('guide').addEventListener('submit', event => {
  event.preventDefault();
  clearResult();
  if (!guideAvailable()) { guideUnavailable(); return; }
  if (byId('message').value.length > 30000) {
    byId('share-notice').textContent = 'Review up to 30,000 characters at a time.';
    byId('message').focus(); return;
  }
  selected = inputs().filter(input => input.checked).map(input => input.value);
  for (const [title, detail] of PocketGuide.nextSteps(selected)) {
    const item = document.createElement('li'), strong = document.createElement('strong'), p = document.createElement('p');
    strong.textContent = title; p.textContent = detail; item.append(strong, p); byId('actions').append(item);
  }
  const coverage = PocketGuide.hostCoverage(byId('message').value), hosts = coverage.items;
  byId('host-coverage').textContent = coverage.remaining ? 'Address review is incomplete. Only the first 12 literal HTTP(S) addresses were inspected. Remaining addresses not inspected: '+coverage.remaining+'. Use a known official route instead of opening them.' : '';
  for (const {host, notes} of hosts) {
    const li = document.createElement('li'); li.textContent = [host, ...notes].join(' — '); byId('hosts').append(li);
  }
  if (!hosts.length) { const li = document.createElement('li'); li.textContent = 'No literal HTTP(S) address found. A hidden link or missing address can still matter.'; byId('hosts').append(li); }
  byId('result-note').textContent = selected.length ? 'These steps reflect the requests you selected. They do not prove fraud or verify the sender.' : 'No request topics selected. That does not establish safety. If you are unsure, verify before acting.';
  byId('result').hidden = false;
  byId('result-title').focus();
});
byId('copy').addEventListener('click', async () => {
  const summary = PocketGuide.summary(selected), version = ++resultVersion;
  let timer;
  try {
    await Promise.race([navigator.clipboard.writeText(summary), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Clipboard timed out')), 3000); })]);
    if (version === resultVersion && !byId('result').hidden) byId('copy-status').textContent = 'Copied fixed steps. Message text and addresses are omitted.';
  }
  catch { if (version === resultVersion && !byId('result').hidden) byId('copy-status').textContent = 'Clipboard is unavailable. Use Download steps instead.'; }
  finally { clearTimeout(timer); }
});
function downloadSteps(summary, filename) {
  const url = URL.createObjectURL(new Blob([summary], {type:'text/plain;charset=utf-8'}));
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
byId('download').addEventListener('click', () => downloadSteps(PocketGuide.summary(selected), 'trustlens-pocket-steps.txt'));
async function shareChecklist(text, button, status, current) {
  if (button.disabled) return;
  if (typeof navigator.share !== 'function') {
    status.textContent = 'Device sharing is unavailable here. Use Copy or Download instead.';
    return;
  }
  button.disabled = true;
  status.textContent = 'Choose a destination in your device’s share sheet. Only fixed, input-free steps are included.';
  try {
    await navigator.share({title:'TrustLens — safer next steps', text});
    if (current()) status.textContent = 'Share request handed to your device. Delivery is not verified.';
  } catch (error) {
    if (current()) status.textContent = error.name === 'AbortError' ? 'Sharing cancelled. You can still copy or download the steps.' : 'Device sharing did not complete. Use Copy or Download instead.';
  } finally { button.disabled = false; }
}
byId('share-steps').addEventListener('click', () => {
  if (byId('result').hidden) return;
  const version = ++resultVersion;
  return shareChecklist(PocketGuide.summary(selected), byId('share-steps'), byId('copy-status'), () => version === resultVersion && !byId('result').hidden);
});
const recoveryPlans = {
  money: {title:'Contact the payment provider promptly', steps:['Use your bank’s app or a known number. Explain what happened and ask whether the transfer can be stopped or reversed.', 'Keep transaction records. Do not pay someone who promises to recover the money for a fee. Recovery is not guaranteed.']},
  account: {title:'Secure the affected account', steps:['Contact the account provider through its official app or a known address.', 'Change exposed and reused passwords from a trusted device. Review account activity and unfamiliar sessions.']},
  device: {title:'End the remote-access session', steps:['Disconnect the device from the internet to end remote access. Use another trusted device to contact relevant providers.', 'Update security software and run a scan before using the affected device for sensitive accounts.']},
  link: {title:'Stop before entering information', steps:['Close the page. Do not install its downloads or enter personal information.', 'If you entered credentials, choose the account checklist. If you installed software, choose the device-access checklist. Update security software and scan.']}
};
let recoverySelection = null, recoveryVersion = 0;
function clearRecovery() {
  recoveryVersion++; recoverySelection = null;
  byId('recovery-result').hidden = true;
  ['recovery-title', 'recovery-steps', 'recovery-status'].forEach(id => byId(id).replaceChildren());
  Object.keys(recoveryPlans).forEach(key => { byId('recovery-'+key).ariaPressed = 'false'; });
}
Object.entries(recoveryPlans).forEach(([key, plan]) => byId('recovery-'+key).addEventListener('click', () => {
  clearRecovery(); recoverySelection = plan;
  byId('recovery-'+key).ariaPressed = 'true';
  byId('recovery-title').textContent = plan.title;
  plan.steps.forEach(step => { const li = document.createElement('li'); li.textContent = step; byId('recovery-steps').append(li); });
  byId('recovery-result').hidden = false; byId('recovery-title').focus();
}));
function recoverySummary(plan) {
  return 'TrustLens Pocket — recovery checklist\nGeneral U.S. guidance in English. Recovery is not guaranteed.\n\n'+plan.title+'\n\n'+plan.steps.join('\n\n')+'\n\nExternal FTC guide: https://consumer.ftc.gov/articles/what-do-if-you-were-scammed\nNo message text or incident details are included.';
}
byId('recovery-copy').addEventListener('click', async () => {
  if (!recoverySelection) return;
  const version = ++recoveryVersion, summary = recoverySummary(recoverySelection); let timer;
  try {
    await Promise.race([navigator.clipboard.writeText(summary), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Clipboard timed out')), 3000); })]);
    if (version === recoveryVersion) byId('recovery-status').textContent = 'Copied this fixed checklist. No incident details included.';
  } catch { if (version === recoveryVersion) byId('recovery-status').textContent = 'Clipboard is unavailable. Use Download checklist instead.'; }
  finally { clearTimeout(timer); }
});
byId('recovery-download').addEventListener('click', () => {
  if (recoverySelection) downloadSteps(recoverySummary(recoverySelection), 'trustlens-pocket-recovery.txt');
});
byId('share-recovery').addEventListener('click', () => {
  if (!recoverySelection) return;
  const version = ++recoveryVersion;
  return shareChecklist(recoverySummary(recoverySelection), byId('share-recovery'), byId('recovery-status'), () => version === recoveryVersion && recoverySelection !== null);
});
async function prepareOffline() {
  if (!guideAvailable()) { guideUnavailable(); return; }
  if (!('serviceWorker' in navigator) || !window.isSecureContext) {
    byId('connection').querySelector('strong').textContent = 'Use the guide in this page';
    byId('offline-status').textContent = 'Offline installation is unavailable here. Use a supported browser on HTTPS or a loopback development address. The checklist still works while this page is open.'; return;
  }
  if (byId('prepare').disabled) return;
  byId('prepare').disabled = true;
  byId('reload-companion').hidden = true;
  byId('connection').querySelector('strong').textContent = 'Preparing offline access…';
  let timer, finished = false, stopWatching = () => {};
  try {
    await Promise.race([(async () => {
      const registration = await navigator.serviceWorker.register('/phone/sw.js', {scope:'/phone/'});
      if (finished) return;
      // An update needs the server; an already complete matching shell can still work offline.
      try { await registration.update(); } catch {}
      if (finished) return;
      const worker = registration.installing || registration.waiting || registration.active;
      if (!worker) throw new Error('No offline worker');
      await new Promise((resolve, reject) => {
        const check = () => {
          if (worker.state === 'activated') resolve();
          else if (worker.state === 'redundant') reject(new Error('Offline worker failed'));
        };
        worker.addEventListener('statechange', check);
        stopWatching = () => worker.removeEventListener('statechange', check);
        check();
      });
      if (finished) return;
      stopWatching();
      await new Promise((resolve, reject) => {
        const channel = new MessageChannel();
        stopWatching = () => { channel.port1.close(); channel.port2.close(); };
        channel.port1.onmessage = event => {
          const status = event.data;
          if (status?.cache === byId('pocket-version').getAttribute('content') && status.ready === true) resolve();
          else reject(new Error(status?.ready === true && typeof status.cache === 'string' ? 'updated-shell' : 'Offline shell is incomplete or out of date'));
        };
        worker.postMessage({type:'POCKET_STATUS'}, [channel.port2]);
      });
    })(), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Offline preparation timed out')), 15000); })]);
    byId('offline-status').textContent = 'Offline shell prepared. Installation and receiving shares still depend on this browser and device. No message is cached.';
    byId('connection').querySelector('strong').textContent = 'Offline guide prepared';
  } catch (error) {
    byId('connection').querySelector('strong').textContent = 'Offline access is not ready';
    byId('offline-status').textContent = 'Offline preparation failed. Keep this page open or retry when the local app is reachable. Your message was not saved.';
    if (error.message === 'updated-shell') {
      byId('offline-status').textContent = 'A different companion version is prepared. Reload to use it; this clears the message in this page. Copy anything you need first.';
      byId('reload-companion').hidden = false;
    }
  } finally { finished = true; clearTimeout(timer); stopWatching(); byId('prepare').disabled = false; }
}
byId('prepare').addEventListener('click', prepareOffline);
byId('reload-companion').addEventListener('click', () => window.location.reload());
window.addEventListener('beforeinstallprompt', event => {
  event.preventDefault(); installPrompt = event; byId('install').hidden = false;
});
byId('install').addEventListener('click', async () => {
  if (!installPrompt) return;
  const prompt = installPrompt; installPrompt = null; byId('install').hidden = true;
  try { await prompt.prompt(); await prompt.userChoice; }
  catch { byId('offline-status').textContent = 'Installation did not complete. You can still use the guide here.'; }
});
if (byId('message').dataset.shared === 'true') {
  byId('share-notice').textContent = 'Shared text received on this device. Review and edit it, then choose the requests you see. Nothing has been analyzed yet.';
  history.replaceState(null, '', '/phone/');
}
window.addEventListener('pagehide', clearPrivate);
window.addEventListener('pageshow', event => { if (event.persisted) clearPrivate(); });
function openShortcut() {
  const id = {'#recovery':'recovery', '#practice':'practice', '#android':'android'}[window.location?.hash];
  if (!id) return;
  const panel = byId(id); panel.open = true;
  panel.querySelector('summary').focus();
}
byId('nav-recovery').addEventListener('click', event => {
  if (window.location?.hash === '#recovery') event.preventDefault();
  byId('recovery').open = true; byId('recovery').querySelector('summary').focus();
});
byId('nav-practice').addEventListener('click', event => {
  if (window.location?.hash === '#practice') event.preventDefault();
  byId('practice').open = true; byId('practice').querySelector('summary').focus();
});
byId('nav-review').addEventListener('click', event => {
  if (window.location?.hash === '#message') event.preventDefault();
  byId('message').focus();
});
window.addEventListener('hashchange', openShortcut);
openShortcut();
if (guideAvailable()) {
  byId('guide-submit').disabled = false;
  byId('prepare').disabled = false;
  prepareOffline();
} else {
  guideUnavailable();
  byId('prepare').disabled = true;
  byId('offline-status').textContent = 'Offline readiness was not checked because the local guide could not load. Reload with the trusted app reachable, or use the fixed context checks.';
}
