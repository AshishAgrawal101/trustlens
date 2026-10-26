# Independent final image/OCR/QR cleanup review

Read-only review; no app/test/old-report edits. No heavy runtime, inference, protected images, GPU, downloads or native OCR worker was run. Selected constructed/fake-runtime tests: 48 passed in 1.03 seconds across test_image_lifecycle.py, test_image_inference_failure.py, test_image_disagreement.py, test_screenshot_lifecycle.py and test_qr_lifecycle.py.

## Preservation exception is resource-only

Current image.py SHA256 19ba25ed5e3b1ba331c90b9d4f2ef776336bc8da4810115998ce0bc0c6a8fe1f; pinned frozen-v14 fixture SHA256 414bd4a004bbc5c5d78fcd6e1a111259dc0e3695bf7b65d69c425c22da2574b6. Inspected both actual sources and the AST assertion (test_image_lifecycle.py:49). The original first statement is exactly image=decode_image(content). Current _analyze_image (image.py:87–188) replaces that assignment with closing(decode_image(content)) and indents the entire remainder under it. After reversing that wrapper and the contextlib import, the complete module AST equals the pinned original.

This establishes unchanged decoder/orientation/preprocessing, runtime loading/settings, lock placement around scoring, score math, thresholds/policy, report/evidence/limitations and public exception conversion. It does not establish bitwise model execution or new detection accuracy; none was run. The fake successful report matches the frozen function (test_image_lifecycle.py:64). Load/scoring/component failures retain their exceptions while pixels are already closed, and successful fake scoring sees open pixels before report completion/close. No report field retains the image itself.

No InvalidImage/public-response regression found. analyze_image still preserves InvalidImage and ImageModelUnavailable (190–197). Existing fake API tests confirm invalid bytes remain an input error without running a model; failed model checks retain available provenance and expose no fabricated model branch/private exception text. main.py still maps InvalidImage to400 and unavailable analysis to503 on their established paths.

## OCR and QR lifecycle

Screenshot admission (screenshot.py:20–25) checks platform and acquires the nonblocking lock before decoding. A busy request cannot allocate decoded pixels or launch a worker. closing covers thumbnail/save/temp/worker/JSON success and failures; TemporaryDirectory exits before envelope validation. The worker envelope now requires a dict and exact en-US, while retaining blank English text as reviewable and dropping unknown fields. Lock release is unconditional after acquisition (49–50). InvalidImage is explicitly preserved; timeout/read/JSON/declared-language failures return the fixed OcrUnavailable message.

QR (qr.py:24–59) retains its existing busy admission, timeout, temporary path, response/code/control-character bounds and InvalidImage versus unavailable semantics. Explicit closing now disposes the decoded RGB image before parsing downstream response fields, on both success and failure. Tests retain a reference to that image and verify getpixel fails, the temporary file is gone and the lock is released. There is no resource-lifecycle reason to claim decoded text or source identity is verified.

## Scope and residual limits

No concrete new actionable defect was found in these cleanup changes. The explicitly owned decoded RGB images are closed on all inspected exits. This is not a blanket proof that every internal Pillow allocation is explicitly closed: decode_image's temporary exif-transpose/conversion objects and QR's temporary grayscale conversion are unchanged expressions, normally released by Python object lifetime. The approved exception did not rewrite those protected decode/preprocessing expressions. The tests should be described as decoded-image/temporary-file/lock cleanup, not a full memory/process sandbox certificate.

Subprocess timeout behavior and threadpool cancellation do not establish immediate termination of an entire descendant tree or a hard memory cap. Current checks do not certify native OCR installation, model load availability, real inference output or population performance. Root's final native OCR/full-suite/browser receipts remain separate. Preserve the documented count as 33 unchanged protected files plus one reviewed resource-only exception, rather than claiming all34 were unchanged.

Reviewed screenshot.py SHA256 5e921771b6cd575182c6bcae29c99a71ae8818d8f852d88784a50839eaa22d2c; qr.py SHA256 9897d636abd3ab09838c2f2de16cf1cbff762e2741f73cc325c2047302e4c138.
