# Remaining advice, secrecy and refusal context audit

Read-only: no app/model/API or historical diagnostic changes. Nineteen new constructed probes were saved before request_evidence execution, SHA256 bc19f071b85e5b32fb61329c85cc90b5b03e761f2f6079c30b606f9c66965931. Current text.py SHA256 b64db071b30e6a72023d75d5babeea6413c74842c0463dff0f0c405dce8f41eb. before-results.json retains exact evidence objects and weighted IDs. Context labels are authored interpretations, not fraud/safety truth labels or an accuracy benchmark.

The earlier public-examples report was inspected only for scope: its two retained misses concern loan/security subject snippets, which are not used in these probes or proposed fixes. Its source-specific counts remain historical. No public-example pattern expansion, final/Arena data, private message or model training was used.

## 1. Secrecy formatting/modal gaps — but do not broaden blindly

`Do not tell anyone about this transfer.` -> ['request:secrecy'] high/.8. Replacing only the first space with NBSP or two spaces -> []. `You must not tell anyone about this transfer.` and `You should not tell anyone about this transfer.` -> []. Positive ordinary `Tell your bank about this transfer.` -> [].

Root cause: secrecy rule text.py:25 still has one literal ASCII space in do-not and omits the modal forms now recognized by other negation guards. These are inconsistent observable outcomes for close wording pairs. Missing secrecy evidence is not a safe conclusion, but can omit useful keep-contact-open guidance. However, simply reusing _PROHIBITION for secrecy will worsen the protective-password false concern below. Any expansion should be paired with a precise privacy-advice guard first; no blanket negative-to-secrecy rule is proposed.

## 2. Protective credential privacy is labelled secret-keeping (highest-value concern)

`Never tell anyone your password.` and `Do not tell anyone your verification code.` -> ['request:secrecy'] high/.8. The code rule correctly suppresses the negated disclosure, but secrecy independently treats any tell-anyone prohibition as pressure to hide a transaction. `Never tell anyone your password. Send me your verification code.` -> ['request:code','request:secrecy']; expected a live code concern without invented secret-keeping pressure. Direct `Tell me your password.` -> ['request:code'] high as control.

The secrecy match ends at recipient wording without considering the explicit protected object. Smallest candidate scope for root review: suppress only the matched tell-anyone secrecy span when the same bounded clause explicitly prohibits disclosure of an existing sensitive credential object. Do not suppress independent tell-family/bank prohibitions, a separate secrecy request, or a later positive code request. Keep the existing independent-secrecy regression in test_sprint_context.py:66. Use exact clause/object grammar and paired deceptive continuations before implementation; a broad “sentence contains password” skip would hide genuine pressure.

## 3. A safer contact route is confused with a ban on contacting the bank

`Do not call your bank using the number in this message.` -> ['request:secrecy'] high/.8, identical to `Do not call your bank about this payment.`. The former advises avoiding an untrusted contact route; the latter discourages independent checking. The finite call-bank pattern ignores this distinction.

This needs a narrowly framed context marker/unknown result if addressed, not a broad suppression of call-bank phrases. Possible scope: exact using-the-number-in-this-message prohibition plus explicit alternative known route, with positive independent prohibition controls. The current single-sentence probe deliberately lacks that alternative, so a general rule should stay cautious. Lower priority than the unambiguous credential-privacy and spacing bugs; document the finite limitation if not fixed.

## 4. Explicit first-person refusal becomes a live sensitive request

`I will not share my password.`, `I won't share my password.`, `I refuse to share my password.`, and `You do not need to share your password.` all -> ['request:code'] high/.8. `I will not share my password. Install TeamViewer.` -> ['request:code','request:remote']. Direct `Please share your password.` remains high; already-supported `You must not share your password.` correctly returns [].

The direct negation guard recognizes do/should/must-not and finite not-asking templates, but does not recognize directly adjacent will-not/won't before the request verb. The smallest general candidate is adjacent will-not/won't only, preserving horizontal-space/hard-line policy and independent later live requests. Pair with will-not-only and will-not-hesitate-to controls so merely containing a negative word cannot hide a request. Refuse-to and do-not-need-to require different grammar; leave them unresolved rather than broadening this into a language model. An unknown refusal-context marker is preferable to claiming sender trust.

## Recommended order and validation

First review exact credential-privacy advice versus independent secret-keeping spans. Then consistent secrecy spacing/modal forms can be considered with those paired controls. Direct adjacent will-not/won't refusal is a separate small candidate. Contact-route, refuse-to and no-need grammar should remain explicit unsupported cases absent a robust narrow contract. No source edits were made or authorized by this audit.

Before any fix, add regressions for later positive clauses, independent secrecy instructions, hard separators, original excerpts, modal not-only/hesitate, protected-object words quoted as examples, and max-input work. Preserve current null risk_index/low confidence/no-model policy. The 19 probes expose targeted finite-context gaps; their concern/miss counts do not estimate performance on ordinary messages, scams or advice in use.
