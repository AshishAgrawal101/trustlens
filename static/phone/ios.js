'use strict';
// Clipboard access is requested only from an explicit button click.
(() => {
  const get = id => document.getElementById(id);
  const paste = get('paste-message'), message = get('message'), status = get('paste-status');
  if (paste && message && status) {
    let version = 0;
    function invalidate() { version++; status.textContent = ''; paste.disabled = false; }
    paste.addEventListener('click', async () => {
      const token = ++version;
      status.textContent = '';
      if (!navigator.clipboard?.readText) {
        status.textContent = 'Paste manually: touch and hold the message field, then choose Paste. This browser does not offer the paste button.';
        message.focus(); return;
      }
      paste.disabled = true; status.textContent = 'Waiting for clipboard permission…';
      let timer;
      try {
        const reading = navigator.clipboard.readText();
        const text = await Promise.race([reading, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), 3000); })]);
        if (token !== version) return;
        if (typeof text !== 'string' || !text.trim()) {
          status.textContent = 'No text was available. Copy the message again, or paste manually into the message field.'; return;
        }
        if (text.length > 30000) {
          status.textContent = 'The copied text exceeds 30,000 characters. Select a shorter passage and paste it manually. Your current text was kept.'; return;
        }
        message.value = text;
        message.dispatchEvent(new Event('input', {bubbles:true}));
        status.textContent = 'Pasted for review. Review and edit the text, then choose request topics; nothing has been checked automatically.';
        message.focus();
      } catch {
        if (token === version) { status.textContent = 'Clipboard access did not complete. Paste manually: touch and hold the message field, then choose Paste. Your current text was kept.'; message.focus(); }
      } finally { clearTimeout(timer); if (token === version) paste.disabled = false; }
    });
    message.addEventListener('input', invalidate);
    for (const id of ['clear', 'example']) get(id)?.addEventListener('click', invalidate);
    get('guide')?.addEventListener('submit', invalidate);
    document.querySelectorAll('input[name="request"]').forEach(input => input.addEventListener('change', invalidate));
    window.addEventListener('pagehide', invalidate);
    window.addEventListener('pageshow', event => { if (event.persisted) invalidate(); });
  }
  const shortcut = get('shortcut');
  if (shortcut) {
    const open = () => { shortcut.open = true; shortcut.querySelector('summary').focus(); };
    document.querySelectorAll('a[href="#shortcut"]').forEach(link => link.addEventListener('click', event => {
      if (window.location?.hash === '#shortcut') event.preventDefault();
      open();
    }));
    window.addEventListener('hashchange', () => { if (window.location?.hash === '#shortcut') open(); });
    if (window.location?.hash === '#shortcut') open();
  }
  const copy = get('copy-ios-recipe'), recipe = get('ios-recipe'), recipeStatus = get('recipe-status');
  if (copy && recipe && recipeStatus) {
    let version = 0;
    copy.addEventListener('click', async () => {
      const token = ++version; let timer;
      copy.disabled = true; recipeStatus.textContent = 'Copying the manual setup instructions…';
      try {
        if (!navigator.clipboard?.writeText) throw new Error('unavailable');
        await Promise.race([navigator.clipboard.writeText(recipe.textContent), new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), 3000); })]);
        if (token === version) recipeStatus.textContent = 'Recipe copied. Build it manually in Shortcuts; this did not install or run a shortcut.';
      } catch { if (token === version) recipeStatus.textContent = 'Select and copy the recipe text below. Clipboard access did not complete.'; }
      finally { clearTimeout(timer); if (token === version) copy.disabled = false; }
    });
    window.addEventListener('pagehide', () => { version++; recipeStatus.textContent = ''; copy.disabled = false; });
  }
})();
