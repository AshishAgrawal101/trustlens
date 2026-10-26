'use strict';
// Opt-in literal suggestions only; the user applies each topic and reviews next steps.
const PocketSuggestions = (() => {
  const rules = [
    ['money', 'Pay or move money', /\b(?:(?:buy|purchase)\s+gift\s*cards?|(?:send|transfer|pay)\s+[$£€]\s*\d[\d,]*|(?:send|transfer)\s+(?:money|bitcoin|crypto))\b/i],
    ['code', 'Share a code or account details', /\b(?:read\s+me|send\s+me|share|provide)\s+(?:(?:your|the|a)\s+)?(?:security\s+code|verification\s+code|one-time\s+code|password|passcode|bank\s+account\s+number)\b/i],
    ['device', 'Install something or allow access', /\b(?:(?:install|download)\s+(?:AnyDesk|TeamViewer)|(?:enable|allow)\s+remote\s+access)\b/i],
    ['secret', 'Act urgently or keep it secret', /\b(?:keep\s+(?:this|it)\s+(?:a\s+)?secret|act\s+now)\b/i]
  ];
  function suggest(text) {
    if (typeof text !== 'string' || text.length > 30000) throw new Error('Review up to 30,000 characters at a time.');
    const found = new Map();
    // shortcut: suppress entire lines containing advice, history or quotes; same-line live requests may be missed.
    for (const sentence of text.split(/[\r\n]/)) {
      if (/["“”‘’]|(?:^|[\s:(])'/.test(sentence) || /\b(?:not|no|never|[a-z]+n['’]t|cannot|without|avoid|if|example|training|workshop|said|told|asked|yesterday|last week)\b/i.test(sentence)) continue;
      for (const [topic, label, pattern] of rules) {
        if (found.has(topic)) continue;
        const match = sentence.match(pattern);
        if (match) found.set(topic, {topic, label, snippet:match[0].slice(0,120)});
      }
    }
    return rules.filter(([topic]) => found.has(topic)).map(([topic]) => found.get(topic));
  }
  return {suggest};
})();
if (typeof module !== 'undefined') module.exports = PocketSuggestions;

if (typeof document !== 'undefined') (() => {
  const get = id => document.getElementById(id);
  const topics = [...document.querySelectorAll('input[name="request"]')];
  let controls = [];
  function clearSuggestions() {
    controls = []; get('suggestion-results').replaceChildren(); get('suggestion-status').textContent = '';
  }
  function refreshControls() {
    for (const {button, input, label} of controls) {
      button.disabled = input.checked;
      button.textContent = input.checked ? 'Topic already selected' : 'Apply topic';
      button.setAttribute('aria-label', button.textContent + ': ' + label);
    }
  }
  get('suggest-topics').addEventListener('click', () => {
    clearSuggestions();
    try {
      const rows = PocketSuggestions.suggest(get('message').value);
      get('suggestion-status').textContent = rows.length
        ? 'Possible topics from short English literal matches, not a fraud verdict. Review each excerpt, then apply only topics that fit. No topics were changed.'
        : 'No supported literal request matched. This does not establish safety; choose the topics yourself when needed.';
      for (const row of rows) {
        const input = topics.find(input => input.value === row.topic);
        const item = document.createElement('li'), label = document.createElement('strong'), quote = document.createElement('p'), button = document.createElement('button');
        label.textContent = row.label; quote.textContent = 'Matched wording: “' + row.snippet + '”'; button.type = 'button';
        button.addEventListener('click', () => {
          input.checked = true; input.dispatchEvent(new Event('change', {bubbles:true})); refreshControls();
          get('suggestion-status').textContent = 'Topic selected: ' + row.label + '. Review your choices before showing next steps; this is not a fraud verdict.'; input.focus();
        });
        controls.push({button, input, label:row.label}); item.append(label, quote, button); get('suggestion-results').append(item);
      }
      refreshControls();
    } catch (error) { get('suggestion-status').textContent = error.message; get('message').focus(); }
  });
  topics.forEach(input => input.addEventListener('change', refreshControls));
  get('message').addEventListener('input', clearSuggestions);
  get('guide').addEventListener('submit', clearSuggestions);
  get('clear').addEventListener('click', clearSuggestions);
  get('example').addEventListener('click', clearSuggestions);
  window.addEventListener('pagehide', clearSuggestions);
  window.addEventListener('pageshow', event => { if (event.persisted) clearSuggestions(); });
})();
