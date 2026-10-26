# Read-only intake reliability audit

2026-10-24 improvement wave. No app edits, native OCR run, model imports/inference, real/private image access, browser upload attempts, downloads or GPU work. Reproductions used an in-memory2x2PNG and temporary process-local mocks against production helper/ASGI route. Every patch was reverted by context exit; the screenshot lock was released in finally.

## Reproduced findings for root selection

**P2 — screenshot busy admission occurs after pixel decoding, with no explicit image close.** Acquire `screenshot._lock`, wrap `screenshot.decode_image` with a counting wrapper that calls the real decoder, then call `extract_screenshot(tiny_png)`. It raises the intended busy OcrUnavailable but decode_count is1; the returned image still permits getpixel. The implementation also lacks explicit RGB close on success, timeout, unsupported-platform or JSON failure paths. Busy calls can therefore each perform up to the existing20MP decode before refusal, defeating the worker lock as a decode-resource gate. Python reference counting often releases unreferenced objects promptly, but retained exception/traceback references can extend lifetime; there is no deterministic close guarantee. QR already acquires its lock before decoding and uses a context manager. Recommend the same lock-beforedecode/context-managed-image pattern for screenshots, retaining InvalidImage400 and fixed busy503. Regression should hold the lock and assert decoder not called, then assert close/lockrelease on successful and failed worker paths. No need to change shared decoder/model policy.

**P2 — malformed OCR worker envelopes can produce500 or silently bypass English-language contract.** With a tiny valid PNG and subprocess.run mocked to return exit0:

| stdout JSON | Actual production screenshot route result |
|---|---|
| `[]` |500 Internal Server Error (TypeError at data['text'])|
| `null` |500 Internal Server Error (TypeError)|
| `{"text":"ok","language":{"bad":"shape"}}` |200 with object-valued language|
| `{"text":"ok","language":"fr-FR"}` |200, although downstream rules and worker promise en-US|

The lock was released in every reproduced case. Native worker source normally emits a fixed dictionary/en-US, so this is a fail-closed worker transport/regression boundary, not evidence an uploaded file can directly choose stdout. Recommend validate dictionary shape, string text bounded30000 and exact supported en-US language before acceptance; malformed/unsupported worker output should produce fixed OcrUnavailable503, with no private response echo. Treat blank but valid English text separately as reviewable no-readable-text, preserving current manual fallback. Add negative list/null/object/non-English cases paired with a correct en-US envelope. A broad TypeError catch alone would avoid500 but still accept false language/schema claims.

## Other reviewed boundaries

All upload routes close UploadFile in finally and read shared limits+1. UploadLimitMiddleware includes media, image, screenshot, QR and email-file paths and enforces whole streamed multipart limits before downstream analysis. It preserves fixed413 and closes partial parser resources on this installed Starlette. No new body-echo or truncated-analysis failure was found.

QR uses lock-beforedecode, context-managed decoded image, temp directory and subprocess timeout. Its response envelope catches TypeError/AttributeError and treats malformed worker responses unavailable; control text/code count/aggregate length is bounded. Media closes shared decoded RGB before original header parsing, returns an exact metadata allowlist and handles optional EXIF failure conservatively. GPS absence is not privacy proof; current scope must retain the earlier distinction between Pillow internally parsing EXIF and coordinates not being displayed/returned. No new media partial-evidence defect was reproduced.

Media has no process sandbox/concurrency admission beyond the existing threadpool and shared per-file cap. Multiple requests may each allocate a maximum-size decode; that is a resource limitation, not a newly reproduced crash or permission to introduce a broader framework here. subprocess.run timeouts kill/reap the directly launched worker; this review does not certify an entire descendant process tree or hard memory bound. HTTP cancellation does not establish the thread operation stopped immediately. Keep such claims out of capability text.

Targeted regression suite media/upload/file-intake/malformedPNG was run successfully after reproductions. This review does not measure OCR recognition quality, image-origin accuracy, actual browser/device behavior or load-test capacity. Source files remain unchanged; root selects any fix before edits.
