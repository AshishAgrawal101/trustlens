# Independent communication parser audit — 2026-10-24

Read-only audit. No app, model, old frozen contract or historical result was changed. Twenty-one fresh constructed probes were frozen before prediction: constructed-cases.json SHA256 43d6ef849261caef86af23719cca3bb5b569a2cfebbcea894b35254f72403c0e. Current text.py SHA256 ff1e610d2d8d95fde3160544c68a865cdbe44a340878e99c48891cee2362c0a7. communication-results.json retains exact request_evidence outputs, severity, weight and original excerpts. Ten probes differ from authored expectations; this is a targeted defect count, not accuracy on messages in use. No final/Arena/private-image source was used.

## 1. Horizontal whitespace breaks negative advice (highest priority)

`Do not share your password.` -> [] correctly. Replacing only the word separator with NBSP, two spaces or a tab yields ['request:code'] (high, weight .8) in each case. `Please share your password.` -> ['request:code'] as direct control. This is a copied-formatting equivalence defect, not a disputed interpretation.

Root cause: both the bounded original-offset guard (text.py:32) and direct negation prefix (117) spell `do not` with one literal ASCII space. Existing tests cover ordinary-space English advice but not these equivalent separators. Small scope proposal: change fixed negative phrase separators to one-or-more horizontal whitespace, consistently in both guards; do not use unrestricted whitespace across hard boundaries. Preserve original excerpts, quote/history behavior and independent later live clauses. Add pair plus hard-line negative/live controls before fixing. This should be first because it can falsely accuse safety advice.

## 2. Common negative auxiliaries are treated as positive disclosure

`You should share your password.` -> ['request:code']; `You should not share your password.` and `You must not share your password.` produce the same high evidence. `You should not share your password. Install TeamViewer.` -> ['request:code','request:remote']; expected only remote.

Root cause: finite negation vocabulary excludes should-not/must-not. Small scope proposal: recognize only directly adjacent `should not`/`must not` (with horizontal separators) in the existing negative-prefix grammar, plus paired independent-live and `should not hesitate to share`/`not only` controls to prevent overbroad suppression. A full parser is unnecessary for these narrow direct prohibitions. Keep unfamiliar negation unresolved.

## 3. Sensitive noun phrases miss nonbreaking spaces

`Send your bank account number.` -> ['request:personal']; `Send your bank<U+00A0>account<U+00A0>number.` -> []. `Do not send your bank<U+00A0>account<U+00A0>number.` and ordinary meeting-agenda control -> [].

Root cause: personal rule (20) has literal ASCII spaces inside finite sensitive noun phrases, unlike verification-code's whitespace matcher. Small scope proposal: use the same horizontal-separator grammar inside these already-supported phrases, without adding new sensitive terms, normalizing URLs or joining lines. This is a positive miss with a close formatting-equivalent direct control, not an indirect-language diagnostic retune.

## 4. Typographic nonbreaking hyphen defeats an existing code phrase

`Read me the six-digit code.` -> ['request:code']; replacing the single ASCII hyphen with U+2011 NON-BREAKING HYPHEN -> []. Negated `Never read anyone the six<U+2011>digit code.` and ordinary six-digit order statement remain [].

Root cause: finite six/6-digit and one-time patterns (11) accept ASCII hyphen/space only. Small scope proposal: admit U+2010/U+2011 typographic hyphens only in those already-supported compound phrases, with direct/advice/ordinary controls. Do not normalize all punctuation or broaden plain “code” into generic software/source-code requests.

## 5. Explicit conditional refusal remains a high request

`If someone asks you to share your password, stop.` -> ['context:code'] unknown, weight0. Changing only the refusal to `do not reply` -> ['request:code'] high, weight.8. A subsequent `Install TeamViewer.` yields ['request:code','request:remote']; expected unknown code context plus high remote. Standalone direct disclosure control remains high.

Root cause: conditional advice (106) explicitly accepts only hang-up/stop/end-the-call endings. Small scope proposal if prioritized: add the exact stop-equivalent endings `do not reply`/`do not respond` within the same bounded if-asked frame, leaving following independent requests detectable. Test positive instruction after a comma/but/period and ambiguous nonrefusal clauses. This expands a documented finite grammar; it is lower priority than straightforward whitespace defects.

## Existing tests and unresolved scope

Inspected test_request_context.py, test_sprint_requests.py, test_end_call_advice.py and the current history/negation/source-offset implementation. Existing tests accurately cover their constructed cases; passing them does not claim these new forms are handled. New probes preserve those cases and do not relabel old diagnostics. Native OCR wrapping remains a previously documented separate ambiguity: global line joining can borrow sensitive words across unrelated paragraphs and is not proposed here. Root should authorize exact implementation scope and new regressions before any source edit.
