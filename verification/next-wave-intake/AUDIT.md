# Malformed-image intake failure reproduced and fixed

The initial read-only audit used a locally constructed 1×1 PNG of 1,130 bytes containing a compressed zTXt metadata chunk that would expand to 1,048,577 bytes. Pillow 12.3.0 correctly stops it at its unchanged 1 MiB text-chunk guard, raising ValueError. No large image, user asset, final/Arena data, GPU, network, model import or worker launch was used.

Before the fix, the shared decode_image boundary caught OSError and Pillow decompression-bomb exceptions but omitted this metadata ValueError. The actual local ASGI image-analysis and screenshot-extraction routes returned HTTP 500. QR extraction caught the ValueError later and returned HTTP 503 as if its decoder were unavailable. The initial reproduction receipt preserves those outcomes.

Evidence: reproduce_png_metadata.py and png-metadata-reproduction.json pin the pre-fix source files, fixture digest, API status/body and released extraction locks. The reproducer replaced visual runtime loading and subprocess startup with assertion guards, so accidental model/worker execution would fail the audit. That stage changed no application source.

Root explicitly approved the minimal development-only fix in app/analyzers/image.py. It now normalizes the proven Pillow ValueError to InvalidImage, with a separate reraising branch preserving existing explicit InvalidImage messages. No optional exception classes, runtime loading paths, weights, thresholds or Pillow limits changed. The model was not retried.

Seven new regressions in tests/test_png_metadata_limits.py verify the bounded fixture is now rejected by all three actual APIs with HTTP 400, with runtime/worker calls forbidden; the original byte/format/pixel-limit messages and normal decoding remain intact. Existing image-disagreement, upload, file-intake, community, upgrade and provenance tests were also run: 141 passed, 11 skipped in 5.70 seconds. Skips were one opt-in native OCR test and ten C2PA native tests unavailable in the app test interpreter; these checks were not represented as passing.

decoder-fix-preservation.json records the intentional one-file protected-baseline exception: 33 protected files still match v5, while only the reviewed input decoder differs. Old image.py SHA256 was 0e737e47a80e8530b315c6e3d15d87c8518f3d879b7d606e13dff9b7a056ee69; new SHA256 is b92bffafacd442ac4081ad27beac1a7e385291caec2c474ea6184f3b5664ba1c. All seven immutable archive hashes, including v5, and all 104 original-source manifest entries were reverified unchanged. No claim of 34 unchanged protected files applies to this wave.

Skipped: image-model retry, actual OCR/QR workers for this malformed fixture, broader fuzzing and unrelated intake edits.
Risk: this closes the reproduced metadata ValueError path; it is not a claim that arbitrary malformed-image handling is exhaustively verified.
