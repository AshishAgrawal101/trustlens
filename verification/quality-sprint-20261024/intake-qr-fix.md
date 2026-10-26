# QR explicit pixel cleanup

Two new lifecycle tests failed before the fix: retained decoded RGB pixels remained usable after successful and unsuccessful worker exit. Replaced the QR helper's plain image context manager with contextlib.closing, preserving its lock, timeout, temporary directory, decoder/error/code/control-text contracts and all limits. Tests now require getpixel to fail after close, temporary files removed and lock released. No native QR worker or model is used by these two tests.

Combined QR lifecycle, screenshot lifecycle, existing file-intake and malformedPNG tests:58passed,zero skips in4.91seconds. Existing file-intake tests include native generated QR fixtures; no image-origin models, private images, GPU or downloads occurred.

Read-only caller audit: screenshot now explicitly closes via closing; media_context explicitly closes decoded RGB before header access; provenance explicitly closes its initial validation image before credentials processing. Protected image.py::_analyze_image still holds its decoded image without an explicit finally close, including runtime-failure paths; it was not edited or executed in this review. Its model flow needs separate root approval and tests using a fake runtime if cleanup is pursued. ai_detector/prepare_cf_subset.py has a different same-named decoder and is outside this app intake slice.

Only qr.py, the new QR lifecycle test and this owned receipt changed. No protected decoder/runtime/model/trust source changed.
