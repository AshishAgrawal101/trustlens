# Reliability and draft-transfer wave — October 23, 2026

Current development handoff. Builds on the [iPhone/visual wave](IPHONE-VISUAL-20261023.md), whose v5 archive and external extraction receipt remain unchanged. This wave adds one focused usability feature and fixes independently reproduced reliability errors. It does not replace the frozen hackathon entry.

## Changes

- **Move wording between Message and Call.** An explicit action appears for a nonblank eligible draft. It preserves exact whitespace and the constructed-example label, clears old results/exports through ordinary mode/input events, and focuses the new field. It never checks automatically, stores history, or transfers OCR/QR/email/image input. Ordinary mode tabs retain their existing reset behavior.
- **HTML email text respects inline words and block boundaries.** Inline formatting no longer splits “verification” or turns “Do not” into different words. Block elements and line breaks separate text. Script/style contents stay excluded. This is bounded source parsing, not a browser/CSS rendering engine.
- **Duplicate Subject headers remain ambiguous.** Every supplied subject is checked as separate text, and the report prominently says the email needs manual review. No single displayed subject is assumed. Existing attachment, MIME and authentication limits remain.
- **Malformed PNG metadata gets an input error.** A constructed 1,130-byte PNG that expands past Pillow's existing text-metadata limit previously returned 500 for image/screenshot or misleading 503 for QR. Shared decoding now returns 400 with a fixed readable message across all three routes. Pixel/byte/metadata limits remain in place; no model or subprocess runs for this fixture.
- **Malformed responses cannot expose partial reports.** The main controller validates fields it consumes before setting result/export state. Unreadable JSON gets fixed feedback, rather than decoder fragments. Malformed extraction notices cannot enter review state. Drafts stay available and controls recover.
- **Practice retains keyboard position.** Selecting an answer now focuses its explanation; Tab reaches Next and Enter continues to the next scenario. This avoids losing focus when the selected choice becomes disabled.

## Verification

**728 Python tests and 121 JavaScript tests passed, zero failures/skips.** This includes actual native Windows OCR and the separate native C2PA signing/tampering test environment. The wave adds 38 Python and 10 JavaScript regressions. These are software checks and new paired regression cases, not population scam/image accuracy.

- [Full Python XML](../verification/reliability-next/pytest-final.xml), [Node output](../verification/reliability-next/node-final.txt), [integration receipt](../verification/reliability-next/integration-receipt.json).
- [Email reproduction, frozen before results and fix report](../verification/next-wave-communication/report.md): earlier FTC-pattern diagnostics remain unchanged; no misses were relabeled or tuned away.
- [Tiny PNG audit](../verification/next-wave-intake/AUDIT.md) and [live server smoke](../verification/reliability-next/live-smoke.json). Backend fixture tests do not claim browser file upload permission.
- [Draft-transfer controller report](../verification/draft-transfer/HANDOFF.md), [independent response review](../verification/reliability-next/response-review.md).

Ordinary Edge review verified exact text transfer without automatic analysis at320px, split-word advice with no false warning, duplicate-subject incomplete wording/actions at390px, and actual keyboard practice progression. Screenshots are in verification/reliability-next/. Clipboard reads, native shares and external delivery were not performed. Pocket assets match v5 byte-for-byte; its previous offline rehearsal stays historical evidence rather than a newly claimed physical-phone test.

## Preservation and delivery

[Preservation audit](../verification/next-wave-intake/decoder-fix-preservation.json): all seven earlier archive hashes and 104 original-source entries match. Of34 protected baseline files,33 remain byte-identical; the sole reviewed exception is the small shared input-decoder error fix in app/analyzers/image.py. No model-loading/inference code, weights, thresholds, trust material or resource gates changed. No downloads, GPU work, cloud content calls, automation changes, publication, messaging or submission occurred.

New source bundle: TrustLens-professional-20261023-reliability-v6-review.zip. Its matching external receipt records final digest, every manifest entry and extracted-source checks; the external receipt is authoritative for packaging completion.

Physical iPhone/Android installation, Shortcuts execution, native share delivery, browser file selection, print preview, clean dependency installation and full assistive-technology checks remain unverified. Phone use still needs a trusted reachable secure origin. No automatic Messages/SMS monitoring or accepted image model is claimed.
