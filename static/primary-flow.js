'use strict';
// Grouping and explanatory copy only; analysis/review stays in the existing controller.
(() => {
  const get = id => document.getElementById(id);
  const modes = [...document.querySelectorAll('[data-mode]')];
  function sync() {
    const mode = modes.find(button => button.getAttribute('aria-pressed') === 'true')?.dataset.mode || 'text';
    get('visual-modes').open = ['url','email','call','qr'].includes(mode);
    get('screenshot-sample-help').hidden = mode !== 'screenshot';
    if (mode === 'text') get('mode-guide').textContent = 'Paste the exact request. Check it, review the evidence, then choose a step you can take.';
    else if (mode === 'image') get('mode-guide').textContent = 'Upload a photo. TrustLens reads any Content Credentials, then two AI models look for the patterns image generators leave behind.';
    else if (mode === 'screenshot') get('mode-guide').textContent = 'Choose a screenshot. Read it locally, correct the recognized words, then confirm before checking. Nothing opens automatically.';
  }
  [...modes, ...document.querySelectorAll('[data-demo]'), get('clear')].forEach(button => button.addEventListener('click', sync));
  window.addEventListener('pageshow', event => { if (event.persisted) sync(); });
  sync();
})();
