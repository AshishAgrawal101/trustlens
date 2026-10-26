# Explicit Message/Call draft transfer

## Demonstrated gap and approved scope

The main controller's normal mode switch clears its draft and result. A user who entered caller wording in Message could not change to Call without recopying it. Root approved a separate explicit transfer action, rather than retaining history or silently carrying content between all input types.

Implemented only in `static/draft-transfer.js`, `static/index.template.html`, `static/styles.css`, `frontend.py` and `tests/draft_transfer.test.cjs`. `static/app.js`, backend/Pocket logic and the immutable v5 archive were not edited by this worker.

## Behavior

- With nonblank Message or Call wording of at most 30,000 UTF-16 units, the page offers Use as call transcript / Use as message. Other input modes cannot use this action, including editable QR/OCR text that still requires review.
- The explicit click captures the exact wording in the current synchronous handler, clicks the existing target mode button, restores the text and dispatches a normal input event. The established controller handles cancellation, result/export erasure, counts and form state. No check starts automatically.
- A fixed status announces the new mode and need to review/check; the textarea receives focus. The original constructed-demo label survives transfer and clears normally after an edit.
- Native mode buttons still clear drafts as before. Transfer stores no history, local/session storage, URLs, clipboard copy, cache entry or network request. Clear and page lifecycle erase current content/status using the existing controller.
- The renderer embeds this helper after the existing main scripts, preserving the self-contained served page. Main print rules still expose only the original input-free checklist.

## Verification

`node --test tests/draft_transfer.test.cjs`: six passing regressions. They load the actual main controller before the helper and exercise ordinary mode/input listeners, exact whitespace round trip, explicit-only behavior, request endpoint after transfer, pending request cancellation/stale rejection, original export invalidation, constructed labels, mode/length guards and Clear/pagehide/persisted-pageshow cleanup.

`node --check static/draft-transfer.js`: passed. `frontend.render_frontend()` embeds the helper and leaves no external transfer-script placeholder. Browser layout, keyboard and screen-reader behavior for this new action remain for root to verify; this worker used no browser session. A test DOM double is not physical-device evidence.

## Read-only accessibility/modal review

Concrete candidate reported to root: desktop Practice disables the focused answer button and reveals Next without moving focus. This can drop keyboard focus/restart the dialog tab sequence. Pocket already focuses its feedback. Suggested minimal fix is focusable feedback plus explicit focus, or a deliberate Next focus after feedback. Root owns `app.js` and will decide/fix/test it.

The main dialogs use native `showModal()`/`close()`, labeled dialog headings and native buttons. Their native focus trapping/return behavior was not replaced by custom code. Result/error headings receive explicit focus; the keyboard submit path calls native `reportValidity()`. No source-only review establishes a complete screen-reader, modal or browser-validation certification.

A minor usability observation: native required text fields accept whitespace, while the backend rejects the trimmed empty value. This yields an actionable server error rather than a silent check; avoiding that round trip could be separate work. No unverified bug or broader validation rewrite was implemented here.

## Limits

The helper intentionally solves only Message↔Call correction. It does not transfer email headers, URLs, files or unreviewed extraction, and it is not a saved-draft/history feature. Cancel/abort dismisses the client request; server work already running may continue. No model/rule/accuracy claim changes.
