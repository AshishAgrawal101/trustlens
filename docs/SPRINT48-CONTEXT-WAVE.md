# Context and email increment — October 23

This increment improves specific observed communication failures. It does not change the frozen image classifier or signed Content Credentials checker.

## Implemented and verified

- Recognize a request to disclose “the code we just sent” when the same bounded clause supplies security/account context. Ordinary source and discount codes remain negative controls.
- Treat explicit conditional “if someone asks …, hang up/stop” advice as uncertain context instead of a present request. Later independent requests still produce evidence.
- Compare a displayed email address domain with the single primary `mailto:` recipient domain. Query text is not treated as visible message content; aliases, multiple recipients and ownership are not inferred.
- Use “Payment request to verify” rather than calling every matched payment request unusual. A request alone does not establish fraud.

The integrated source suite passed **221 Python tests, zero skipped**, including native Windows OCR and real signed/tampered Content Credentials. Command: `python -m pytest -q tests ai_detector`, with the existing credentials Python and `TRUSTLENS_TEST_NATIVE_OCR=1` configured. The unchanged frontend retains the previous **17 passing offline controller tests**; those tests use a DOM double, not a browser.

## Measured comparison and remaining failures

On the already examined 48-case constructed challenge, required evidence families improved from 26/30 after the first increment to **28/30**, and unwanted warnings on 13 negative controls decreased from 2 to **1**. Two code-reference misses and a historical-quotation warning remain. These are constructed development checks, not population accuracy.

A separate 24-case, 12-pair context set was frozen before its first predictions. Its author knew the earlier rules and failure categories, so it is not a statistically independent real-world benchmark. The initial API evaluation returned all 24 responses, with **16/24 scenario contracts passing**: five cases had unwanted historical/advisory warnings, two missed code references, and one used an unsupported “unusual” payment title. Root reviewed the returned summaries, evidence titles and actions. No identity, fraud or safety guarantee was found. The payment title was corrected afterward and tested separately; the original 16/24 result and all responses remain preserved. This set is now examined development/regression evidence.

The remaining contextual failures justify evaluating a separate local language classifier. No language model has been integrated or shown to improve these results. No fresh image release evaluation or changed model installation occurred.

## Limits and audit records

Real-browser visual and keyboard checks remain blocked by the saved browser policy. API and offline tests do not establish visual quality. Image benchmark and release limitations remain in `submission/EVALUATION.md`.

Local-only receipts under `artifacts/sprint48/`: `communication-context-implementation.json`, `context-evaluation-freeze.json`, `context-evaluation.json`, `context-responses.json`, `pytest-context-final.xml`, and `integration-context-wave.json`. These audit artifacts are excluded from the source archive. Earlier reports are preserved.
