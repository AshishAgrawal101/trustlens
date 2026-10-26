'use strict';
(() => {
  const get = id => document.getElementById(id);
  const button = get('link-details-open'), result = get('link-details-result'), status = get('link-details-status');
  let generation = 0, controller;
  function clear() {
    generation++; controller?.abort(); button.disabled = false;
    result.replaceChildren(); result.hidden = true; status.textContent = '';
  }
  function row(label, value) {
    const term = document.createElement('dt'), detail = document.createElement('dd');
    term.textContent = label; detail.textContent = String(value); result.append(term, detail);
  }
  button.addEventListener('click', async () => {
    const hadFocus = document.activeElement === button;
    clear();
    if (get('known-website-wrap').hidden) return;
    const token = generation;
    controller = new AbortController(); const active = controller;
    const timer = setTimeout(() => active.abort(), 10000);
    button.disabled = true; status.textContent = 'Inspecting the literal address locally. No destination is opened.';
    try {
      const body = {url:get('content').value};
      const referenceInput = get('known-website').value;
      if (!/^ *$/.test(referenceInput)) body.known_website = referenceInput;
      const response = await fetch('/api/inspect/url', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body), signal:active.signal});
      const data = await response.json();
      if (token !== generation) return;
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check the address and reference, then retry.');
      if (!['http','https'].includes(data.scheme) || typeof data.ascii_host !== 'string' || typeof data.display_unicode_host !== 'string'
          || !Number.isInteger(data.port) || data.port < 0 || data.port > 65535
          || !Number.isInteger(data.path_segment_count) || data.path_segment_count < 0
          || !Number.isInteger(data.query_parameter_count) || data.query_parameter_count < 0
          || ['scheme_assumed','username_present','fragment_present'].some(key => typeof data[key] !== 'boolean')
          || typeof data.notice !== 'string') throw new Error('Address details were unavailable. Retry with the local launcher running.');
      const reference = data.reference_comparison;
      if (reference !== null && (typeof reference?.ascii_host !== 'string' || ['exact_host_match','same_scheme','same_port'].some(key => typeof reference[key] !== 'boolean')))
        throw new Error('The reference comparison was unavailable. Check the known website and retry.');
      row('Connection', data.scheme.toUpperCase() + (data.scheme_assumed ? ' · assumed for parsing' : ''));
      row('Normalized ASCII hostname', data.ascii_host);
      if (data.display_unicode_host !== data.ascii_host) row('Unicode display spelling', data.display_unicode_host);
      row('Port', data.port);
      row('Text before @', data.username_present ? 'Present · not the destination hostname' : 'Not present');
      row('Path segments', data.path_segment_count + ' · contents omitted');
      row('Query fields', data.query_parameter_count + ' · names and values omitted');
      row('Fragment', data.fragment_present ? 'Present · contents omitted' : 'Not present');
      if (reference) {
        row('Reference hostname', reference.ascii_host);
        row('Exact hostname comparison', reference.exact_host_match ? 'Same hostname · safety remains unverified' : 'Different hostname · verify independently');
        row('Reference connection / port', (reference.same_scheme ? 'Same scheme' : 'Different scheme') + ' / ' + (reference.same_port ? 'same port' : 'different port'));
      }
      result.hidden = false; status.textContent = 'Structure inspected locally. Redirects and site ownership were not checked. Private path, query and fragment values are omitted from these details; matching components do not establish safety.';
    } catch (error) {
      if (token === generation) status.textContent = error.name === 'AbortError' ? 'Inspection took too long. Keep the local launcher running and retry.' : error instanceof TypeError ? 'Could not reach the local inspector. Keep the launcher running and retry.' : error.message;
    } finally {
      clearTimeout(timer);
      if (token === generation) {
        button.disabled = false;
        if (hadFocus && (document.activeElement === document.body || document.activeElement === button)) button.focus();
      }
    }
  });
  ['content','known-website'].forEach(id => get(id).addEventListener('input',clear));
  ['clear','example'].forEach(id => get(id).addEventListener('click',clear));
  document.querySelectorAll('[data-mode], [data-demo]').forEach(element => element.addEventListener('click',clear));
  window.addEventListener('pagehide',clear);
  window.addEventListener('pageshow',event => {if(event.persisted)clear();});
})();
