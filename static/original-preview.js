'use strict';
// One existing image/object URL; this viewer never reads, stores or exports a file.
(() => {
  const get = id => document.getElementById(id), image = get('preview');
  const disclosure = get('original-preview'), frame = get('original-frame');
  const sizes = [[get('original-fit'),100],[get('original-150'),150],[get('original-200'),200]];
  function size(percent) {
    image.style.width = percent + '%';
    sizes.forEach(([button,value]) => button.setAttribute('aria-pressed',String(value === percent)));
    frame.scrollTop = 0; frame.scrollLeft = 0;
    get('original-status').textContent = percent === 100 ? 'Fit to frame width.' : percent + '% of frame width. Scroll the image to compare details.';
  }
  function reset() { disclosure.open = false; size(100); }
  sizes.forEach(([button,percent]) => button.addEventListener('click',() => {
    if (get('preview-wrap').hidden || !image.getAttribute('src')) return;
    size(percent); frame.focus();
  }));
  get('file').addEventListener('change',reset);
  [...document.querySelectorAll('[data-mode]'),...document.querySelectorAll('[data-demo]'),get('clear'),get('example')].forEach(button => button.addEventListener('click',reset));
  image.addEventListener('error',() => {
    if (!get('preview-wrap').hidden && image.getAttribute('src')) get('original-status').textContent = 'This browser could not display the image. Choose another file or compare it in your image viewer. Text extraction can still fail separately.';
  });
  window.addEventListener('pagehide',reset);
  window.addEventListener('pageshow',event => { if (event.persisted) reset(); });
  reset();
})();
