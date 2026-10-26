# Professional upgrade: implemented and bounded

This development version implements the plan in `tasks/professional-upgrade-plan.md` with three GPT-6.1 Sol / low subagents: communication quality, product quality and image evaluation. Root implemented Pocket, capability reporting, integration and review fixes. The original frozen entry and previous development review ZIP remain unchanged. This version is recommended for continued local rehearsal, not represented as a production release or accepted entry replacement.

## Useful changes

- Main checker: direct landing-to-checker route; contextual intake instructions; explicit on-demand component configuration panel; unknown state after failed/malformed configuration responses; clearer mobile targets/wrapping; error focus and busy state; availability-refresh focus recovery without stealing focus from another field. Configured is visibly distinct from a successful runtime check.
- Communication: requests to settle an outstanding balance now receive a guarded verification prompt and payment advice, with existing negation/advice/teaching context guards. A legitimate sensitive request may also warn; this is not a fraud classifier.
- Pocket: separate mobile-first checklist, fixed request-specific next steps, literal hostname inspection, safe exports, private clearing, bounded local share receiver and installable web app manifest. Its prepared shell and guide worked with the server stopped. It is human-guided, not automatic message detection. See `ANDROID-COMPANION.md` for phone setup and privacy limits.
- Subagent review fixes: aligned capability defaults with runtime asset paths; qualified phone sharing privacy; repaired failed-offline-preparation headings; exposed the 12-address display limit; added clipboard timeout fallback and preserved keyboard focus after capability refresh.

## Measured evidence

474 Python tests passed, zero failures/errors/skips, including native Windows OCR and actual C2PA signing/tampering. The full count is 465 app tests plus nine detector-policy tests. 31 Node tests passed across desktop controllers, new product states and Pocket logic/share/erasure/clipboard behavior. These verify software contracts, not field accuracy.

The communication worker froze two short real public scam excerpts (FBI/IC3 toll example and FTC USPS example), four constructed ordinary/advice controls, and one constructed legitimate payment request before baseline predictions. The selected public excerpts went from 0/2 to 1/2 warnings after the narrow balance-request fix; ordinary/advice controls remained 0/4 warnings. The USPS statement-only excerpt remains a miss. The legitimate sensitive request warns intentionally and would be a false positive if one incorrectly treated the app as a binary fraud classifier. This tiny examined diagnostic establishes no population accuracy. Inputs, baseline, after-results, citations and residuals remain in `verification/professional-communication/`.

Four actual admitted development images—two genuine COCO photographs and two generated OpenFake originals—were SHA-verified under a frozen protocol. The one contained visual-model attempt stopped during imports at the live RAM guard; it was terminated and reaped, never decoded/scored the images, and was not retried. Visual outcomes remain null. A distinct contained C2PA-only native worker check completed on those same four originals: all returned absent embedded credentials, without SDK errors/timeouts. This exercised the production native worker, with an in-process stdio adapter; its normal subprocess wrapper was not exercised by that real-image diagnostic (native wrapper/crypto regressions were tested separately). Absence says nothing about genuine/AI/fraud origin. Exact resource, provenance, license and runtime limitations are in `verification/professional-images/REPORT.md` and its receipts.

## Browser verification and remaining gaps

Ordinary Edge control verified the new capability panel and actual configuration response, balance-request result/payment advice, Pocket navigation, user-selected code/payment steps, literal host behind @, Clear and result invalidation, automatic shell preparation, and loading/using Pocket with the local server stopped. Pocket's clipboard pending-permission fallback visibly appeared. At 320/390 pixels Pocket showed no document horizontal overflow; the main app's previous 320/768/1440 checks are historical and the final main interface receives a new narrow-layout check in the browser receipt. Proof images are in `verification/professional-product/`.

No bypass of the saved extension file-upload denial occurred. Interactive screenshot/OCR-review/image uploads, physical Android installation/share sheet, full screen-reader conformance and clean-machine dependency installation remain unverified. The native image model remains resource-limited and has not passed release acceptance. No new model, threshold, GPU job, payload download, final/Arena evaluation, cloud content service, automation resume, publication or submission occurred.

## Running and reviewing

Use the existing setup and `python serve.py`; the launcher chooses its own free loopback port. This session's development app runs at http://127.0.0.1:8766/ and Pocket at `/phone/`. The model files and local runtime configuration are intentionally excluded from the source archive. `/api/capabilities` reports configured assets without loading them. Source archiving uses `scripts/package.py`, writes a new professional review filename and refuses to overwrite an existing review archive. Retain the package receipt/checksum beside it.

The original entry remains SHA256 `18cfcb73f3691deeb3c81fff3aea4b9bf593ed57ed4f2870800283f5e73fb105`; the previous development review remains `7c6870b4ed2abecd871708b93fb75d28ac1591a138e784eb4360fb6b48a35cee`. Scheduled work remains paused. No production/1000x/hackathon-win claim is made.
