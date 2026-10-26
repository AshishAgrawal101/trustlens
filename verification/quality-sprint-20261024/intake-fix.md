# Screenshot lifecycle and transport fix

Root authorized only screenshot.py/new lifecycle tests after the read-only audit. Fifteen new constructed tests were run before implementation:14failed,1passed, reproducing busy decode, unclosed pixels and malformed envelope acceptance/errors. No native OCR/model calls occurred.

The helper now acquires the screenshot lock before decoding. Busy requests return immediately without decoder/worker execution. The decoded RGB image is wrapped in contextlib.closing, ensuring an explicit close on successful worker execution, malformed output, nonzero exit, timeout or other errors. Temp directory and lock finally semantics remain. InvalidImage has its own exception branch before ValueError handling, preserving malformed-input400 rather than converting it into unavailable503.

A successful worker envelope must be a dictionary with exact en-US language and string text of at most30000characters. Blank English text remains reviewable for manual fallback. Harmless extra keys are tolerated and not returned. Malformed top-level types, invalid language/text and missing values produce fixed OcrUnavailable messages without input/output echo; existing informative overlength/nonzero-exit messages remain fixed. No worker/native contract, shared decoder, model, threshold or trust source was changed.

During the first attempted fix, the lifecycle test showed Pillow's image context manager alone does not close the pixel core of the RGB image produced by convert. Replacing it with explicit closing corrected the resource guarantee. The same observation applies to the preexisting QR helper's context-manager pattern and was reported to root as separate scope; QR was not edited.

Final targeted run:83passed,zero skips across15new screenshot lifecycle tests, malformedPNG limits, fileintake anduploadlimits in6.64seconds. Regression tests cover success,blanktext, extra keys,busy nodecode/noworker, malformedJSONenvelopetypes, language,textbound,timeout/nonzeroexit,tempcleanup,imageclose and lockrelease. Native OCR recognition quality, actualbrowserupload and wholeprocess-tree memory containment were not tested or claimed.
