# Independent v36 raw-URL consistency review

No required fix found.

Compared current source against immutable `TrustLens-professional-20261025-drafts-resource-v35-review.zip`, normalizing only line endings (`diff.json`). `UrlRequest.url` and `.known_website` alone override inherited whitespace stripping with field-level `StringConstraints(strip_whitespace=False)`. Existing 1–4096 raw-character bounds remain; claimed brand and other request models keep their prior trimming. The literal address parser, anatomy producer and inspector controller are unchanged.

Main Link payloads now preserve raw address/reference values exactly. Only an empty or ASCII-space-only optional reference is omitted, matching the unchanged anatomy controller. Control-only references reach the same server parser and fail with fixed private errors; tabs/newlines/BOM are no longer silently removed by one submission path. Ordinary outer ASCII/NBSP whitespace remains accepted by the existing parser policy. This is consistent validation, not a changed hostname, ownership judgment or safety-bypass finding.

Independent narrow execution: **27/27 Python** raw-boundary/API/model tests and **9/9 JavaScript** main-payload/inspector tests pass, zero failures/skips (`python.txt`, `node.txt`). Coverage includes both routes/fields, raw 4096/4097 bounds, controls, normal outer whitespace, reference omission and unchanged non-Link payload trimming. An extra actual-controller probe used normal input events and a fixed 400 response: both raw drafts remained intact, result stayed hidden and error received focus (`error-preservation.json`). No automatic field rewrite or private error echo was observed.

Scope limits: HTML textareas normalize certain physical line endings by browser design; this change preserves values exposed by those controls, not inaccessible original clipboard bytes. Review did not alter browser settings, upload files, visit destinations or rerun the full suite. No source edits by this reviewer; no parser/model, network, storage, export or physical-phone claim follows.
