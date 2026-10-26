// Directory fragments contain only a tool choice. Input never travels in a URL.
'use strict';
(() => {
  function route() {
    const hash=window.location?.hash||'',match=/^#check=(text|screenshot|url|email|call|qr|image)$/.exec(hash);
    if(!match||match[0]!==hash)return;
    const button=[...document.querySelectorAll('[data-mode]')].find(item=>item.dataset.mode===match[1]);
    if(!button)return;
    if(button.getAttribute('aria-pressed')!=='true')button.click();
    const workspace=document.getElementById('workspace');workspace.focus();workspace.scrollIntoView({block:'start'});
  }
  window.addEventListener('hashchange',route);
  route();
})();
