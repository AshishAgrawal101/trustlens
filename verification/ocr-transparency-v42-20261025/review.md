# Bounded native OCR transparency result

Four frozen constructed cases ran once each sequentially through unchanged production extract_screenshot / Windows English OCR. No retries. Font Arial44 at900x150, fixed nonprivate phrase 'Send me your verification code.'; exact input/font hashes and elapsed times retained in results.json.

Observed outcomes:
- Black opaque letters on transparent black background: successful OCR envelope, empty text.
- Exact white alpha-composite reference: exact phrase recognized.
- White opaque letters on transparent black background: exact phrase recognized already.
- Exact opaque black composite reference: exact phrase recognized.

Each call took approximately0.53–0.55seconds on this computer. No unavailable errors/null worker statuses occurred. Empty output remains an observed blank recognition, not an engine failure or proof the source lacks text. No accuracy rate/generalization is warranted from these four fixtures.

Decision implication: reusing QR's unconditional white-background normalization in Screenshot is not justified. It fixes the black-on-transparent sample but removes contrast from an input whose white letters are already readable under current decoding. A white composite of white letters and transparent background is visually white, so it cannot preserve this supported contrast; no fifth OCR call was made or claimed. Both sides must remain explicit rather than selecting whichever produces a desired warning.

Smallest future workflow proposal: user-controlled extraction background (current/default vs white) or manual advice to export the screenshot on a contrasting opaque background, with separate explicit Read/review/confirm and no auto-choice/auto-analysis. Any policy requires its own design/acceptance; no implementation was authorized here. Shared decoder/model pipeline and current Screenshot behavior remain unchanged. No models/GPU/download/browser upload/private inputs used; exactly four native OCR calls stayed under existing lock/30second timeout.
