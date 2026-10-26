'use strict';
// Fixed steps depend on the user's choices, never on private text.
const PocketGuide = (() => {
  const steps = {
    money: ['Pause before paying', 'Confirm the amount, reason and payment instructions through a person or organization you already trust. Never use a new contact route supplied in the request.'],
    code: ['Keep account access private', 'Do not send passwords or read a security code to an unexpected caller. Open the account through its official app or an address you already know.'],
    device: ['Keep control of your device', 'Do not install software or allow remote access for an unexpected request. Contact support through a known official route.'],
    secret: ['Bring in someone you trust', 'Pause the conversation. Talk privately with a trusted person before responding to pressure, secrecy or a threat.']
  };
  function nextSteps(selected) {
    const keys = new Set(selected);
    return [...Object.entries(steps).filter(([key]) => keys.has(key)).map(([, value]) => value),
      ['Verify independently', 'Use a known official app, website or trusted contact record. A familiar name, caller ID or image does not establish identity.']];
  }
  const hiddenAddressCharacter = /[\p{Cc}\p{Cf}\p{Cs}]/u;
  function hostCoverage(text) {
    if (typeof text !== 'string' || text.length > 30000) throw new Error('Review up to 30,000 characters at a time.');
    const found = [];
    let count = 0;
    for (const match of text.matchAll(/https?:\/\/(?:[^\s<>"']|\p{Cf})+/giu)) {
      if (++count > 12) continue;
      let raw = match[0].replace(/[.,;!?)}]+$/, '');
      if (raw.endsWith(']') && !/^https?:\/\/\[[^\]]+\]$/i.test(raw)) raw = raw.replace(/\]+$/, '');
      try {
        if (hiddenAddressCharacter.test(match[0])) throw new Error();
        const url = new URL(raw);
        if (!['http:', 'https:'].includes(url.protocol) || !url.hostname) continue;
        const notes = [];
        if (url.username || url.password) notes.push('Text before @ is not the destination.');
        if (url.protocol === 'http:') notes.push('This address uses HTTP. HTTPS would still not prove it safe.');
        if (url.hostname.includes('xn--')) notes.push('Internationalized hostname; check its exact spelling independently.');
        found.push({host: url.hostname, notes});
      } catch { found.push({host: 'Unreadable web address', notes: ['Check the original wording manually; no destination was visited.']}); }
    }
    return {items:found, remaining:Math.max(0,count-12)};
  }
  function hosts(text) { return hostCoverage(text).items; }
  function summary(selected) {
    return 'TrustLens Pocket — input-free next steps\nUser-selected request topics; no automatic scam verdict.\n\n'
      + nextSteps(selected).map(([title, detail]) => title + '\n' + detail).join('\n\n')
      + '\n\nNo message text, addresses or contact details are included. No warning proves fraud or safety.';
  }
  function compareHosts(text, known) {
    if (typeof known === 'string' && hiddenAddressCharacter.test(known)) throw new Error('Enter a known website without hidden control or formatting characters.');
    if (typeof known !== 'string' || !known.trim() || known.length > 4096 || /[\s\\\x00-\x1f\x7f]/.test(known.trim())) throw new Error('Enter a known website without spaces or backslashes.');
    let reference;
    try {
      const value = known.trim();
      if (/^https?:/i.test(value) && !/^https?:\/\/[^/\\?#\s]/i.test(value)) throw new Error();
      if (/^[a-z][a-z0-9+.-]*:/i.test(value) && !value.includes('://') && !/^[^/?#]+:[0-9]+(?:[/?#]|$)/.test(value)) throw new Error();
      const address = value.includes('://') ? value : 'https://' + value;
      const authority = address.slice(address.indexOf('://') + 3).split(/[/?#]/, 1)[0];
      if (authority.includes('@')) throw new Error();
      reference = new URL(address);
      if (!['http:', 'https:'].includes(reference.protocol) || !reference.hostname || reference.username || reference.password) throw new Error();
    } catch { throw new Error('Enter an HTTP(S) website you already know, without login details or text before @.'); }
    const expected = reference.hostname.replace(/\.$/, '');
    const coverage = hostCoverage(text);
    return {known:expected, remaining:coverage.remaining, rows:coverage.items.map(item => ({host:item.host, match:item.host === 'Unreadable web address' ? null : item.host.replace(/\.$/, '') === expected}))};
  }
  return {nextSteps, hosts, hostCoverage, summary, compareHosts};
})();
if (typeof module !== 'undefined') module.exports = PocketGuide;
