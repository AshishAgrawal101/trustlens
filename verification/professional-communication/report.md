# Communication diagnostic — 2026-10-23

This is a tiny selected development diagnostic, not a held-out benchmark or estimate of scam detection accuracy. Seven cases were frozen before baseline scoring and editing. Public scam labels come from the publishing authority; the analyzer still only identifies wording. No spam corpus was relabeled as fraud. No supplied link was opened, resolved or reputation-checked; only the authoritative source pages were retrieved. No model, download, GPU, or cloud content API was used.

## Frozen inputs and provenance

`frozen-cases.json` SHA-256: `AA866B4302EC208FC05554D608122828A8F3636E711CFCD52038FF95033E20AE`.

- FBI/IC3, April 12, 2024: https://www.ic3.gov/PSA/2024/PSA240412 . The final sentence of its explicitly quoted reported toll scam is reproduced verbatim (13 words). The supplied historical destination is inert test data and was never visited.
- FTC, June 2023, page 2 example: https://www.ftc.gov/system/files/ftc_gov/pdf/texts-spotlight-final.pdf . Only the opening USPS sentence is reproduced (20 words), verified in the indexed accessible excerpt. This is an excerpt, not the complete original message. The absence of its later link/request makes detection harder and limits interpretation.
- Four ordinary/advice controls and one legitimate sensitive request are newly constructed, explicitly labeled. They are not evidence of real benign message distributions.

Copyright: short attributed excerpts only, under 25 words from each source. No claim to redistribute the complete source documents. The government publications provide public educational examples; no private user message was accessed.

## Baseline and result

`baseline.json` was produced before implementation. `after.json` preserves the resulting evidence IDs, risk level and uncertainty. Public scam excerpt warnings: 0/2 before, 1/2 after. Ordinary/advice controls: 0/4 warned before and after. The legitimate payment request warns after the change, by design: a request worth verifying is not a fraud label. That case is an explicit false positive if the product were incorrectly treated as a binary scam classifier.

The remaining miss is the USPS excerpt: a delivery-problem statement without a sensitive request does not match. It still receives the existing unverified-sender/no-safety-guarantee wording. No general delivery-problem rule was added because benign notices can contain the same claim. Other paraphrases, languages, obfuscations, implied requests and sender impersonation remain unsupported. This in-sample change cannot establish generalization.

## Smallest useful change

Added one medium-severity pattern for settling a balance, reusing existing negation, completed teaching quotation and conditional safety-advice handling. Guidance reuses Pause the payment without adding another action object. The null risk index, low confidence and rules-only provenance remain unchanged. Call and email share the same analyzer, so they gain this wording check too.

Caller audit: main.py text/call endpoints, email.py body/subject analysis and report aggregation, guidance.py action selection, and all request/context/history/reference test callers. No schema, API, export, dependency or config change was needed.

## Validation

RED: dedicated regressions first failed on the two positive balance requests (2 failed, 6 passed). Existing conditional advice creates zero-weight context evidence, so the control assertion checks absence of weighted warnings rather than absence of all evidence.

GREEN and regression command:

`python -m pytest tests/test_professional_requests.py tests/test_community.py tests/test_context_history.py tests/test_end_call_advice.py tests/test_guidance_context.py tests/test_link_evidence.py tests/test_reference_context.py tests/test_request_context.py tests/test_sprint_context.py tests/test_sprint_requests.py tests/test_upgrade.py -q`

Result: 405 passed, 1 skipped in 1.63s. Eight dedicated tests cover positive wording, direct negation, conditional advice, neutral statements, unchanged uncertainty and private-input-free sharing. The pre-existing skip remains a skip.

Reproduce from development root with that root on PYTHONPATH: `python verification/professional-communication/evaluate.py`. The evaluator prints identifiers/findings, not message text; its only fixtures are public excerpts and constructed controls.

Skipped: broader corpus collection, model work, external reputation calls and population accuracy claims. Full app/browser integration is owned by the coordinating worker. Risk: legitimate balance requests trigger a guarded verification prompt, and real scams can still match nothing.
