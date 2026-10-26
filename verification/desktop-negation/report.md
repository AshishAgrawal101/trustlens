# Desktop original-offset negation guard — 2026-10-23

Authorized fix for reproduced parser/advice false concerns, not tuning the later 14 FTC-pattern scenarios. Edited only app/analyzers/text.py and new tests/test_negation_boundaries.py; outputs live in this folder. No probability, risk rule, threshold, existing pattern, legacy sentence splitter, historical-quotation regex or adjacent-reference template was changed.

## Freeze / before and after

Before coding, froze 24 paired acceptance cases in frozen-acceptance.json; SHA256 7cebc270421204c691cd56ef119121c7a5167977d03652d1266a8a0013d75821. Baseline and after topic/evidence projections remain in baseline.json and after.json. Cases cover dollar decimals, dotted domains, HTTP domains, Mr./Dr. honorifics, direct counterparts, cross-family and/or, true sentence/newline/but/semicolon/question/exclamation/comma boundaries, quote/history boundaries, unchanged secrecy and the existing adjacent-code-reference family.

Initial focused regression run: 11 failed,17 passed. The three independently reproduced warnings and their broader paired variations were present before implementation. All24 frozen request sets now match; the preserved code-reference case still emits its existing unknown precaution evidence as validated by the full reference suite.

## Minimal change and limits

Added one private helper called only for existing sensitive-request families. It examines at most240 original characters before a current match, finds a finite explicit negative instruction and verifies its initial verb is one of the existing imperative verbs (plus visit/ask). It only extends negation across an and/or tail or a short ask-person-to tail (80chars). It treats punctuation as a stopping boundary except dots inside alphanumeric tokens and a finite Mr/Mrs/Ms/Dr/Prof honorific list. Quotes, newline, semicolon, but/however and true sentence punctuation stop that scope. Offsets are never transformed, so legacy history/reference matching retains its original text and span contract.

The initial helper prototype was explicitly challenged with negative words that are not supported prohibitions: “There was never a problem … and install …” and “Never mind Mr. Smith and install …”. Both wrongly suppressed the live request in the prototype. Added an imperative-verb prerequisite and paired tests; those warnings are now preserved. No such prototype was handed off as accepted behavior.

This is finite clause handling, not general English negation. The original literal rules remain capable of false concern or misses. Scope beyond240chars, ask constructions beyond80chars, please/then insertions, unlisted abbreviations, URL query punctuation and many other grammatical forms are unsupported. Coordination itself can be ambiguous; no sender intent is established. The code has a shortcut comment. Whole-line suppression was deliberately not introduced because existing independent-live behavior must survive.

Measured residuals are retained in performance-and-residuals.json: negative advice containing a URL query, an and-please insertion and an unlisted St. abbreviation still produces remote/code concerns. No expansion was added to chase them. These are explicit remaining defects/limits for review, not claims of solved general correctness.

## Validation

Thirty new focused tests:24 frozen pairs, three mode propagation checks, max-length bounded-work check and two adversarial noninstruction-negative checks. The final communication regression run covered negation/history/reference/context/guidance/link-coverage/export/address/email/mailto/known-website/API/decision-basis tests:481 passed,1 pre-existing optional skip in2.25s. Full command/result is summarized by tests.txt; root owns full app/native integration. All existing referenced tests were left unchanged.

Max-input samples call request_evidence at30000characters on three repeated advice shapes, three runs each. Median local times: decimal57.384ms, domain54.307ms, honorific45.217ms. Each produced zero weighted findings. The test's loose5second ceiling guards pathological rescanning, not product latency. Raw timings are machine/session-specific and exclude HTTP/browser/native components.

Reproduce matrix: PYTHONPATH=. python verification/desktop-negation/evaluate.py. No14FTC diagnostic rerun or retuning was performed; its original source pins/results remain historical and unchanged.

Skipped browser/model/GPU work and new native image checks. Risk: finite unsupported negative clauses can still be misread, while ambiguous coordinated commands can be suppressed; existing no-warning-is-not-safe guidance remains essential. Root's independent review is still required.
