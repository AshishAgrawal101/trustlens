# First sprint integration — October 22, 2026

This is a completed first increment of the local-only 48-hour plan, not completion of the sprint or a new trained-model release. The current local app includes the changes below.

- More explicit payment, passcode, personal-information and screen-sharing requests match the shared rules. A negated request joined by a bare “and” or “or” remains negated, while a later positive request can still warn.
- Duplicate address headers and malformed MIME/encoding produce an incomplete email result, retaining readable warnings and a manual-review action. Pasted authentication headers remain untrusted.
- Clicking the already selected mode preserves a draft, OCR corrections and the current request. Clear removes private preview filenames. Deliberately loading a demo still replaces the previous input and invalidates its result.
- When both image services are unavailable, the interface says so. Available model or Content Credentials results survive a failure of the other service. C2PA is a provenance check, not an extra model vote.

## Verification

The integrated run passed **188 app Python tests**, zero skipped, including native Windows OCR and actual C2PA signing/tampering. Nine additional synthetic image-comparison preflight tests also passed: **197 total**, 26.05 seconds. The preflight tests live in local audit artifacts and are not part of the source bundle. **17 offline JavaScript controller tests passed**; these use a DOM double, not a browser.

Six live local API cases passed after restarting the verified app process: a wire request, negated payment advice, a call asking for a passcode, duplicate email senders, invalid base64, and a readable password request inside an ambiguous email. The served/embedded page matches its source and sends `Cache-Control: no-store`.

All 53 original baseline files remain unchanged in the original package. Eight frozen image/model/C2PA files in this build match it byte for byte. The provenance wrapper and communication/UI code changed; image weights, preprocessing, decision policy and the native credential worker did not.

The independently authored 48-case constructed challenge was frozen before the communication worker inspected the rules. Required warning families improved from **19/30 to 26/30**. Unwanted warnings remained **2/13** among explicit negative controls, with no new unwanted warnings in that subset. These subsets do not partition all 48 cases. The cases informed fixes and are now regression evidence, not a population-accuracy benchmark. Remaining misses include contextual code references and a displayed email-address/mailto mismatch; remaining false warnings include quoted historical requests and conditional safety advice.

Local audit receipts: `artifacts/sprint48/pytest-first-wave.xml`, `integration-first-wave.json`, `communication-audit.md`, and `product-fix.json`. Artifacts are excluded from the distributable archive.

## Model comparison status and limits

No extra image model was fitted, scored or installed. The proposed cached CLIP/Community/PE comparison failed preflight: approximately 9.03 GB estimated peak RAM exceeded its 2.85 GB allowance, and a historical training STOP required scope review. All 24 historical OS locks were actually free. The STOP remains unchanged and the old training run remains retired. A separate memory-bounded protocol is being designed before any execution.

Inputs remain local. No cloud model or automatic majority vote was added. Real-browser visual, keyboard and screen-reader checks remain blocked by saved browser policy; API/DOM tests do not establish those checks. No new real-world accuracy, final/Arena release acceptance, user study or hackathon eligibility claim is made.
