# Local QR and email-file intake

Added an APIRouter in app/intake.py, local QR extraction in app/analyzers/qr.py plus qr_worker.py, byte-preserving email parsing in app/analyzers/email.py, optional requirements-qr.txt, and dedicated tests. Root owns registration in main.py and frontend integration.

POST /api/extract/qr accepts multipart `file` and returns `{text, codes, review_required: true, notice}`. Text is the newline-joined unique decoded values. No URL is opened and no verdict is produced; the user must review before a separate message check. Invalid/no-readable-code input returns 400; missing decoder, busy reader, transport/native failure or timeout returns 503. The existing JPEG/PNG/WebP, 64 MiB and 20-million-pixel validation is reused. Images are reduced to a maximum 3000-pixel side and converted to grayscale in a temporary directory, deleted on success/error/timeout. A single worker is allowed at once, with a 15-second timeout, one OpenCV processing thread, OpenCL disabled, at most 16 unique codes and 30,000 decoded characters. Hidden C0/C1 controls (except ordinary line/tab whitespace) and bidirectional override/isolate controls are rejected for manual entry. The worker blocks Python socket/network and process-launch events. There is no visual-model import, GPU, download or image-origin scoring.

The worker uses the app Python environment's installed packages through the base interpreter, avoiding the Windows venv redirector so timeout termination targets the actual worker. Missing OpenCV is explicit unavailability; it does not silently select another environment. Exact installed cv2 is 5.0.0, from opencv-python-headless 5.0.0.93; optional requirements-qr.txt pins that existing distribution. Nothing was downloaded or installed.

POST /api/analyze/email-file accepts multipart `file`, reads at most 250,001 bytes and rejects empty, unsupported NUL-containing binary and over-250,000-byte files. BytesParser preserves MIME transfer encodings and declared character sets; both paste and byte entrypoints share the existing analysis. UTF-8/base64, Latin-1/quoted-printable and encoded headers were tested. Attachments, including attached forwarded mail, remain unscanned and count toward the upload limit. Links are inspected as text without fetching. Unknown or invalid character encoding is explicitly incomplete while readable warning signs remain. Excessively nested MIME gets an actionable error in both byte and pasted paths; root's existing pasted route now maps that ValueError to 400.

## Frozen native QR diagnostic

protocol.json SHA256 `f425616db5bd03c4fc50dd22c246e2003196bd23cf534d09e8e81a350f8d5e25` froze the fixtures, exact transforms, safe known payloads, app/worker/native-extension identities, limits and expected results before decoding. No tuning or replay followed a failure. The safe generated payloads were a reserved example.org URL and a library-meeting sentence. Two already admitted COCO originals were hash-verified and used as ordinary-photo controls; their incidental QR presence is unannotated, so they have no labeled-match result. No final, Arena or user assets were read.

| Frozen case | Native result |
|---|---|
| Clean QR | Exact payload |
| 90° and 17° rotation | Exact payloads |
| Half and double nearest-neighbor scale | Exact payloads |
| Gaussian blur radius 1 and 3 | Exact payloads |
| Fixed perspective transform | Exact payload |
| JPEG quality 45 | Exact payload |
| Central 20% occlusion | No readable code; retained failure |
| Two distinct QR codes | Both exact payloads |
| Blank white image | No readable code, expected |
| Two admitted ordinary photographs | No readable code; presence ground truth unknown |

Eleven of twelve labeled fixture expectations matched. This is a small decoding diagnostic, not scam accuracy, image-origin accuracy, a performance guarantee or population generalization. Maximum full extraction latency including startup was 0.391 seconds in this run. All fourteen workers exited and were reaped. Maximum retained worker working-set peak was 42,725,376 bytes and private-commit peak was 804,990,976 bytes. These are worker measurements, not combined server-plus-worker limits. Production QR intake enforces dimensions, output, concurrency and timeout, but has no hard RSS/commit Job cap; auxiliary import thread pools were not separately measured. The earlier stopped visual-model attempt was not retried.

## Adversarial checks and limits

117 targeted tests passed in 5.85 seconds, including existing email/link/community regressions and new native single/multiple/plain-text/active-scheme/control-character QR fixtures; malformed images and invalid JSON/types/binary output; limits; busy behavior; encoding; unscanned attachments; binary email rejection; and deeply nested MIME. The actual subprocess.run timeout transport was tested with a sleeping surrogate at 0.2 seconds while asserting production timeout configuration is 15 seconds. That worker was killed and reaped, temporary files removed and the lock released. Synthetic timeout tests are separate from the frozen QR robustness results.

Known limits remain: unreadable, damaged or small codes can be missed; reducing a large photograph can lose fine detail; multi-code decoding cannot prove that every visible code was found. QR text can contain a dangerous destination even when decoding succeeds. Native OpenCV is trusted installed code, not a security sandbox. Message-file analysis does not authenticate mail servers or scan attachments. Source/worker pins and per-case outcomes are retained in protocol.json/results.json; tests-receipt.json pins files at that test run. The later email-coverage slice and its final email source pin are recorded separately in verification/email-coverage/.

Skipped: new dependencies, network destinations, OCR on ordinary photos, visual-model retries, live mail access, attachment execution/scanning and claims of scam-detection accuracy.
Risk: QR decoding requires the optional OpenCV package in the running app environment; failure returns unavailable rather than a safety result.
