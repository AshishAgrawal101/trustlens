# Screenshot / QR review revocation fix

## Cause and change

The required review checkbox was checked only at submission. Changing it did not invalidate the current report or pending request. Added exactly one existing-controller event registration in `static/app.js`: `reviewed` change calls `clearResult()`. No new abstraction, HTML, other script, backend, storage, cloud request or classification change.

This uses existing abort/generation and export guards: withdrawing confirmation hides current output and loading, clears safe print/copy feedback and current report, clears coverage/cross-check and selected manual/verification steps, and prevents late responses from reviving the result. The extracted/corrected text, selected file, one preview URL, source mode and review controls remain. Confirming again clears stale state but does not submit; an explicit new check is required. A check while unchecked still uses existing review-required validation. Already dispatched clipboard writes cannot be recalled, but their late completion cannot restore feedback.

## Test evidence

New `tests/review_revocation.test.cjs` reuses the existing controller DOM harness and loads actual VerificationPlan. Six cases cover completed result/export/plan invalidation, pending request abort plus late success after rechecking, and pending clipboard completion for both Screenshot and QR. Preview URL/source retention and separate reconsent submission are asserted. The first four behavioral regressions failed before the listener: `review-red.txt`. No earlier test was weakened.

Focused controller/privacy/coverage/verification suite: **41 passed, 0 failed/skipped** (`review-green.txt`). Full Node at this concurrent integration checkpoint: **431 total, 430 passed, 1 failed** (`review-node-full.txt`). The failure is the existing `frontend_professional.test.cjs:42` literal `/Offline guidance is limited/` assertion after root's separate phone-support copy change; it is unrelated to checkbox behavior and was reported to root. Do not treat this checkpoint as full green. Root owns that copy/test integration and final rerun.

## Scope and limits

Changed only `static/app.js`, new `tests/review_revocation.test.cjs` and these `review-*` receipts. No browser file upload, native OCR/QR run, keyboard browser confirmation or physical-phone test performed. DOM-controller tests exercise constructed extraction responses; root owns browser verification and final packaging. Existing v21 archives remain untouched.
