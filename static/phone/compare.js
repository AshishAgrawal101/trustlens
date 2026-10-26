'use strict';
(() => {
  const get = id => document.getElementById(id);
  function clearComparison() {
    get('compare-results').replaceChildren(); get('compare-status').textContent = '';
  }
  function clearKnown() { clearComparison(); get('known-host').value = ''; }
  get('compare-hosts').addEventListener('click', () => {
    clearComparison();
    try {
      const compared = PocketGuide.compareHosts(get('message').value, get('known-host').value);
      get('compare-status').textContent = compared.rows.length ? 'Compared with ' + compared.known + '. Exact parsed hostnames only; sender identity and safety remain unverified.' : 'No literal HTTP(S) address was found to compare. Hidden links and omitted addresses remain unchecked.';
      if (compared.remaining) get('compare-status').textContent += ' Comparison is incomplete: '+compared.remaining+' additional literal addresses were not inspected or compared.';
      for (const row of compared.rows) {
        const li = document.createElement('li');
        li.textContent = row.host + ' — ' + (row.match === null ? 'Could not compare this address.' : row.match ? 'Same parsed hostname. This does not establish safety.' : 'Different parsed hostname. Legitimate subdomains or tracking can differ; verify independently.');
        get('compare-results').append(li);
      }
    } catch (error) { get('compare-status').textContent = error.message; get('known-host').focus(); }
  });
  get('known-host').addEventListener('input', clearComparison);
  get('message').addEventListener('input', clearComparison);
  document.querySelectorAll('input[name="request"]').forEach(input => input.addEventListener('change', clearComparison));
  get('guide').addEventListener('submit', clearComparison);
  get('clear').addEventListener('click', clearKnown);
  get('example').addEventListener('click', clearKnown);
  window.addEventListener('pagehide', clearKnown);
  window.addEventListener('pageshow', event => { if (event.persisted) clearKnown(); });
})();
