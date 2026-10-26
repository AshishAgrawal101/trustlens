'use strict';
// Explicit in-page transfer only: ordinary mode/input events retain the controller's reset guards.
(() => {
  const get = id => document.getElementById(id), content = get('content');
  const modes = [...document.querySelectorAll('[data-mode]')];
  const current = () => modes.find(button => button.getAttribute('aria-pressed') === 'true')?.dataset.mode;
  function refresh() {
    const mode = current();
    get('draft-transfer').hidden = !['text','call'].includes(mode) || !content.value.trim() || content.value.length > 30000;
    get('transfer-draft').textContent = mode === 'call' ? 'Use as message' : 'Use as call transcript';
    get('transfer-status').textContent = '';
  }
  get('transfer-draft').addEventListener('click', () => {
    const mode = current(), text = content.value;
    if (!['text','call'].includes(mode) || !text.trim() || text.length > 30000) return;
    const target = mode === 'text' ? 'call' : 'text', constructed = !get('example-note').hidden;
    modes.find(button => button.dataset.mode === target).click();
    content.value = text;
    content.dispatchEvent(new Event('input', {bubbles:true}));
    get('example-note').hidden = !constructed;
    content.focus();
    get('transfer-status').textContent = target === 'call'
      ? 'Wording moved to Call. Review the transcript, then check it. No analysis started.'
      : 'Wording moved to Message. Review it, then check it. No analysis started.';
  });
  content.addEventListener('input', refresh);
  [...modes, ...document.querySelectorAll('[data-demo]'), get('clear'), get('example')].forEach(button => button.addEventListener('click', refresh));
  window.addEventListener('pagehide', refresh);
  window.addEventListener('pageshow', event => { if (event.persisted) refresh(); });
  refresh();
})();
