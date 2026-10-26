# Desktop next-product heuristic audit

Scope: source inspection of the main desktop template, controller, primary-flow, draft-transfer, verification-plan and stylesheet. No browser or human study was run. Existing v7 artifacts were not changed. This pass changes only this report; implementation scope is pending root coordination.

## Proposed useful improvement: readable original during OCR review

The screenshot journey requires users to review/correct extracted text and explicitly confirm it. However, the only original-image preview is `#preview`, fixed at 68 by 68 CSS pixels with `object-fit:cover`. A tall message screenshot is cropped to a small square. This makes the required comparison impractical within the app, especially for small text or OCR substitutions. Source: static/styles.css original #preview rule; template #preview-wrap; app.js extraction success/inputState.

Proposal sent to root: an explicit local original-image comparison disclosure using the existing object URL, full aspect ratio, and bounded keyboard-operable sizing/zoom if needed. No extra file read, server call, storage, export, automatic analysis or checkbox bypass. Keep the thumbnail and filename/reset lifecycle compatible. Standalone script/markup/CSS/tests can avoid touching root-owned app.js. Root approval required only for shared-file coordination, not additional human authorization.

Acceptance checks: full screenshot is available without cropping; closed comparison is not a keyboard trap; open/close and sizing controls are keyboard operable; Clear, mode change, replacement, page exit and persisted restore collapse/remove preview state; late OCR cannot revive removed content; editing recognized text still unchecks review; print still includes only input-free summary. Real-browser sizing/focus verification remains necessary after implementation.

## Other inspected paths

- Keyboard Ctrl/Cmd+Enter calls native reportValidity before submission and excludes IME composition/Alt/Shift. Native required textarea/review checkbox blocks normal invalid submission; controller additionally rejects missing review confirmation. Editing OCR text resets the confirmation. No review bypass found in these paths.
- Errors are focusable alerts, submit state is recovered in finally, request generations prevent Clear/mode changes from repainting stale results, and Cancel is client dismissal without a server-termination claim.
- Results focus a heading, give actions before detailed evidence, distinguish observations/inferences/unknowns, and state no-warning is not safety. Fixed user-selected plans are explicitly separate from detected findings and exports.
- Native dialogs provide modal keyboard behavior; practice feedback and selected recovery headings receive explicit focus. Source review cannot certify screen-reader announcement order, native focus restoration, zoom layout or contrast in every browser.
- Normal mode changes intentionally clear drafts; explicit Message/Call transfer offers one deliberate preservation path. This is existing behavior, not proposed history or automatic persistence.

No additional blocking defect was established in this bounded source pass. Do not describe this heuristic audit as accessibility certification or evidence from actual users.
