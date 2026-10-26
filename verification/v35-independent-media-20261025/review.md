# Independent Media single-flight review

No required fix found in the bounded change.

Compared `app/analyzers/media_context.py`, `app/intake.py` and `static/media-context.js` with immutable `TrustLens-professional-20261025-email-media-v34-review.zip`, normalizing only line endings. The metadata implementation is retained behind `_inspect_media()`; `inspect_media()` adds a nonblocking process-local lock and fixed `MediaUnavailable` error. Admission occurs before `decode_image()` and the second Pillow/EXIF pass, and `finally` releases the lock for success, validation failures and unexpected exceptions. A rejected concurrent call never owns/releases another call’s lock. No new schema fields, metadata extraction, image model, scoring or private error text were introduced.

`app/intake.py` retains capped read and `finally` upload closure before dispatching the public guarded function to the existing threadpool. It maps only the new busy exception to 503. The UI maps that status to fixed wait/retry guidance, keeps selection/caption/preview and restores controls; it does not render arbitrary backend detail. Existing generation guards still prevent a canceled or replaced inspection from resurfacing. Caption-note retention from v34 is unaffected. Existing serial inspection reports and validator behavior remain supported by the unchanged implementation and serial tests.

Independent narrow checks: `python.txt` records **34/34** media admission/context tests passing, including a held real tiny-image decode, rejected second decode, normal retry, decoder/metadata failures releasing admission and upload closure/private 503. `node.txt` records **5/5** busy UI plus caption-preservation tests passing. No source edits by this reviewer, no browser upload or external image, no model loading/network.

## Resource and evidence limits

This is **one admitted media inspection per Python process**, not whole-server memory containment. Multipart parsing and capped byte reads happen before this lock; other processes, image/QR/OCR endpoints and request/threadpool buffers are separate. There is no new hard execution timeout or worker termination. Client Cancel stops waiting and invalidates UI; a running inspection can continue holding admission until it exits. Those boundaries are consistent with the fixed UI wording and should remain explicit in release notes. This review does not establish arbitrary EXIF/Pillow safety, native phone behavior or production-load capacity.
