# Candidate: keep file facts while writing caption-planning notes

The clearest remaining desktop workflow friction is in Media context. The page explicitly invites an optional caption **for your own planning**, says it is not uploaded, parsed or verified, and asks users to separate file facts from the story. However, any caption keystroke calls the full `invalidate()` in `static/media-context.js`: it erases all file facts/questions and aborts an outstanding file-only inspection. A person who inspects the image first and then starts considering its caption must inspect the unchanged file again. This does not represent a stale metadata report: the result never depended on the caption.

## Reproduced without file upload

Used the actual controller and established `tests/media_context.test.cjs` synthetic DOM/file/report helpers in a read-only Node probe. Completed inspection: result visible, 16 fact nodes, one request. One caption input event: result hidden, zero fact nodes, still one request, same preview retained. This confirms the destructive interaction, not browser geometry or actual native file processing. No browser upload, model, network or application edit was performed.

This is deliberately tested current behavior, so changing it is a product-contract decision, not silently fixing a failing test: `media_context.test.cjs` names caption cancellation, and `media_controller_extra.test.cjs` asserts its abort behavior.

## Bounded recommendation

Separate caption-note edits from file-inspection invalidation. Keep existing completed facts and an outstanding file-only inspection when a valid caption note changes. Retain the explicit “not uploaded, parsed or verified” help. Do not incorporate caption words into file facts, questions, verdicts or request bodies. File replacement, native-invalid form events, explicit Cancel, Clear and lifecycle exit must retain their existing abort/generation/erasure semantics. Clear must still remove caption and preview as well as results. A caption edit after Cancel may clear only its acknowledgement if preserving that current status convention is desired; it must not imply inspection resumed.

Minimal implementation: `static/media-context.js`, focused new regression tests and narrowly justified updates to the two old caption-abort assertions. No parser/schema/endpoint/model or Pocket change, no new page or feature controls. Existing `invalidate()`, generation guard, `FormData` file-only construction and `clear()` remain the helpers; do not add another state framework.

Acceptance: completed facts survive caption typing without another request; pending response remains admissible after caption typing and still contains file only; native-invalid, Clear/file replacement/Cancel/exit still make late responses inert; caption never reaches FormData or output; no auto-inspection on note input; existing filename/preview/object-URL release and fixed errors remain intact. Test both before/after inspection and Cancel acknowledgements. All media/controller suites should remain green with the intentional contract changes identified.

Priority is moderate: this removes unnecessary repeated local uploads and interrupted inspection in the page’s intended file → story workflow. It is a stronger usability increment than another example or small style patch, but is not a release-blocking privacy or correctness vulnerability. No code was changed.
